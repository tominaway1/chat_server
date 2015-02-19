from socket import *
from select import *
import time
import sys
	
#initiate values
BUFFER=1024
BLOCK_TIME=60
#TIME_OUT=60*30 handled in client
LAST_HOUR=60*60


#create arrays

#array of current users
current_Users=[]

#dictionary of all possible users and associated passwords
userDictionary={}

#dictionary for blocked IP addresses and associated username
blocked_Users={}

#Dictionary of current IP address associated to online username
IPUsers={}

#Dictionary of usernames to current IP address
UsersIP={}

#Dictionary of Username and [login/activity] times
loginTime={}

#create dictionary of blocked users for every user
user_block={}

#private messageing
private_message={}




def setup():
	file =open('user_pass.txt',"r")
	for line in file:
		(username,password)=line.split()
		userDictionary[username]=password
	#pick server number
	serverPort=int(sys.argv[1])
	#make socket
	serverSocket=socket(AF_INET,SOCK_STREAM)
	#Specifies that the rules used in validating addresses supplied to 
	#bind() should allow reuse of local addresses
	serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	#bind socket to a port number
	serverSocket.bind(('127.0.0.1',serverPort))   #by default, I set host to localhost
	#have socket listen
	serverSocket.listen(1)
	print 'The Server is ready to recieve on port ' + str(serverPort)
	#add server socket to socket list
	current_Users.append(serverSocket)
	return serverSocket

def validate(sockfd,addr,messageback):
	#Check if user is already logged in
	alreadyLoggedIn=False
	if messageback in IPUsers.values():
		alreadyLoggedIn=True
	if alreadyLoggedIn:
		message="User Already logged in\n"
		sockfd.send(message)
		return True

	#check to see if username is blocked
	if blocked_Users.has_key(messageback):
		temp=blocked_Users[messageback]
		founduser=False
		for array in temp:
			if(array[0][0]==addr[0]):
				if (time.time()-float(array[1])<BLOCK_TIME):
					message="Too many failed attempts\n"
					sockfd.send(message)
					founduser=True
				#else:
				#	blocked_Users[messageback].remove(array)
		if founduser:
			return True
	return False


def checkBlock(sender,reciever):
	#checks to see if a reciever blocked a sender
	if reciever in user_block:
		array=user_block[reciever]
		if sender in array:
			return False
		else:
			return True
	return True


def login(serverSocket,sockfd,addr):
	try:
		i=0
		istrue=True
		item=serverSocket
		
		#prompt for username
		message="Username:"
		sockfd.send(message)
		messageback=sockfd.recv(BUFFER)
		messageback1=messageback.split()
		
		if len(messageback1)==0:
			login(serverSocket,sockfd,addr)
			return

		if validate(sockfd,addr,messageback1[0]):
			login(serverSocket,sockfd,addr)
			return

		#if valid username prompt password
		if userDictionary.has_key(messageback1[0]):	
			password=userDictionary[messageback1[0]]			
			while(i<3 and istrue):
				message="Password:"
				sockfd.send(message)
				messageback=sockfd.recv(BUFFER)
				messageback2=messageback.split()
				if len(messageback2)==0:
					i=i+1
					if i==3:
						sockfd.close()
						break
					continue
				istrue=not messageback2[0]==password	
				i=i+1								

			#handle successful login
			if not istrue:
				message="Welcome to simple chat server!\nCommand:"
				sockfd.send(message)
				current_Users.append(sockfd)
				IPUsers[sockfd]=messageback1[0]
				UsersIP[messageback1[0]]=sockfd
				#Check for offline messages
				if messageback1[0] in private_message:
					message="You have recieved these messages offline\n"
					sockfd.send(message)
					temp=private_message[messageback1[0]]
					for message in temp:
						sockfd.send(message)
					private_message.pop(messageback1[0],None)
					print private_message
				loginTime[messageback1[0]]=[time.time(),time.time()]

				message="%s entered the room \n" % messageback1[0]
				message+="\nCommand:"
				for socket in current_Users:
					if socket != serverSocket and socket != sockfd :
						socket.send(message)

			#Block ip for 60 secs
			else:
				start=time.time()
				if blocked_Users.has_key(messageback1[0]):
					temp=blocked_Users[messageback1[0]]
					temp.append([addr,start])
					blocked_Users[messageback1[0]]=temp
				else:
					blocked_Users[messageback1[0]]=[[addr,start]]
				
				message="Too many failed attempts\n"
				sockfd.send(message)
				login(serverSocket,sockfd,addr)
		else:
			login(serverSocket,sockfd,addr)
			#sockfd.close()
	except:
		sockfd.close()

def check(serverSocket,item,sockfd,addr,messageback):

	#handle logout command
	if messageback[0]=="logout":

		current_Users.remove(item)
		username=IPUsers[item]
		IPUsers.pop(item,None)
		UsersIP.pop(username,None)	
		#loginTime.pop(username,None)
		sockfd.close()

		message="%s left the room \n" % username
		for socket in current_Users:
			if socket != serverSocket:
				socket.send(message)
		return True
	

	#how long function
	if messageback[0]=="howlong":
		if len(current_Users)==2:
			message="You are the only one logged on:\nCommand:"
			item.send(message)
			return True

		for socket in current_Users:
			if socket != serverSocket and socket != item :
				duration = time.time()-loginTime[IPUsers[socket]][0]
				duration=duration/60
				message=str(IPUsers[socket])+" has been on for "+str(duration)+" minutes\n"
				message+="Command:"
				item.send(message)

		return True

	
	if messageback[0]=="wholasthr":
		boolean2=True
		for key in loginTime:
			if key==IPUsers[item]:
				continue
			if time.time()-loginTime[key][0]<LAST_HOUR:
				if boolean2:
					message="Users that connected in the last hour are:\n"
					item.send(message)
					boolean2=False
				message1=key
				message1+="\n"
				item.send(message1)
		if boolean2:
			message="You are the only user who logged on in the last hour:\nComand:"
			item.send(message)
			return True
		message="Command:"
		item.send(message)
		return True


	if messageback[0]=="whoelse":
		if len(current_Users)==2:
			message="You are the only one logged on:\n"
			message+="Command:"
			item.send(message)
			return True
		print len(current_Users)
		message="The current connected users are:\n"
		item.send(message)
		for socket in current_Users:
			if socket != serverSocket and socket != item :
				message=str(IPUsers[socket])
				item.send(message)
		message="\nCommand:"
		item.send(message)
		return True


	# if messageback[0]=="wholasthr":
	# 	message="Users that connected in the last hour are:\n"
	# 	item.send(message)

	# 	for key in loginTime:
	# 		if time.time()-loginTime[key][0]<LAST_HOUR:
	# 			message=key
	# 			message+="\n"
	# 			item.send(message)
	# 	message="\nCommand:"
	# 	item.send(message)
	# 	return True
	
	if messageback[0]=="block":
		if len(messageback)==1:
			return False
		#name of user they want to block
		user=messageback[1]
		#username of user
		username=IPUsers[item]

		if username == user:
			message="Error! You cannot block yourself!\nCommand:"
			item.send(message)
			return True
		
		#check to see if valid username
		for users in userDictionary:
			print users
			if users == user:
				message="You have successfully blocked "+users+" from sending you messages\nCommand:"
				item.send(message)
				if username in user_block:
					user_block[username].append(users)
					print (user_block[username])
				else:
					user_block[username]=[users]
					print (user_block[username])
				return True
		message="invalid username\nCommand:"
		item.send(message)


	if messageback[0]=="unblock":
		if len(messageback)==1:
			return False
		#name of user they want to block
		user=messageback[1]
		#username of user
		username=IPUsers[item]

		print user

		if username == user:
			message="Error! You cannot unblock yourself!\nCommand:"
			item.send(message)
			return True
		
		#check to see if valid username
		for users in userDictionary:
			if users == user:

				if username in user_block:
					array=user_block[username]
					if users in array:
						message="You have successfully unblocked "+users+" from sending you messages\nCommand:"
						item.send(message)
						user_block[username].remove(users)
						return True
					else:
						message="You never blocked "+users+" from sending you messages\nCommand:"
						item.send(message)
						return True						
				else:
					message="You never blocked "+users+" from sending you messages\nCommand:"
					item.send(message)
					return True

		message="Invalid Username\nCommand:"
		item.send(message)
		return True		

	return False

def main():
	if(len(sys.argv) < 2) :
	    print 'Usage : python Server.py port'
	    sys.exit()
	
	serverSocket=setup()
	#accept socket, revise content and send back
	while 1:
		# Get the list sockets which are ready to be read through select
		incomingSockets,outgoingSockets,errorSockets = select(current_Users,[],[])
		
		for item in incomingSockets:
			#new connection	
			if item==serverSocket:
				sockfd,addr=serverSocket.accept()
				login(serverSocket,sockfd,addr)
				
			else:
				try:
					if item not in IPUsers:
						sockfd.close()
						continue
					#recieve incoming socket
					messageback=item.recv(BUFFER)
					messageback3=messageback.split()

					#update activity time
					username=IPUsers[item]
					temp=loginTime[username]
					temp[1]=time.time()
					loginTime[username]=temp


					#check to see if command is empty
					if len(messageback3)==0:	
						message="Command:"
						item.send(message)
						continue
					#check special commands that are not broadcast or message
					if check(serverSocket,item,sockfd,addr,messageback3):
						continue
				
					#Split lines to make things easier
					messageback1=messageback.split(' ')
					
					sender=username

					#Check to see if command is broadcast
					if(messageback1[0]=="broadcast"):
						#cut the command from message
						messageback=messageback[9:]
						message="\r" + str(username) + ': ' + messageback
						message+="\nCommand:"
						for socket in current_Users:
							if socket != serverSocket and socket != item:
								socket.send(message)
						message="Command:"
						item.send(message)
						continue
					#Check to see if command is broadcast
					if(messageback1[0]=="boldbroadcast"):
						#cut the command from message
						messageback=messageback[13:]
						message="\r"+'\033[1m' + str(username) + ': ' + messageback+'\033[1m' 
						message+="\n Command:"
						for socket in current_Users:
							if socket != serverSocket and socket != item:
								socket.send(message)
						message="Command:"
						item.send(message)
						continue
					
					boolean=False
					#check to see if command is message
					if(messageback1[0]=="message"):
						boolean=True
						boolean1=True

						messageback=messageback[8:]

						if messageback1[1]==IPUsers[item]:
							message="You cannot message yourself!"
							message+="\nCommand:"
							item.send(message)
							continue
						for users in userDictionary:
							if users == messageback1[1]:
								for socket in current_Users:
									if socket != serverSocket and socket != item:
										if checkBlock(sender,IPUsers[socket]):
											if not IPUsers[socket]==users:
												continue
											boolean=False
											num=len(IPUsers[socket])
											message="\r" + str(username) + ': ' + messageback[num:]
											message+="\nCommand:"
											socket.send(message)
											boolean1=False
										else:
											message="\r"+"You cannot send a message to "+str(IPUsers[socket])+". You have been blocked by the user."
								if boolean and checkBlock(sender,messageback1[1]):
									boolean1=False
									num=len(messageback1[1])
									message="\r" + '<' + str(username) + '> ' + messageback[num:]
									message+="\nCommand:"
									if messageback1[1] in private_message:
										temp=private_message[messageback1[1]]
										temp.append(message)
										private_message[messageback1[1]]=temp

									else:
										private_message[messageback1[1]]=[message]
						message="Command:"
						item.send(message)
						boolean=True
					if boolean:
						continue
					

					boolean=False
					#check to see if command is message
					if(messageback1[0]=="boldmessage"):
						boolean=True
						boolean1=True

						messageback=messageback[12:]

						if messageback1[1]==IPUsers[item]:
							message="You cannot message yourself!"
							message+="\nCommand:"
							item.send(message)
							continue
						for users in userDictionary:
							if users == messageback1[1]:
								for socket in current_Users:
									if socket != serverSocket and socket != item:
										if checkBlock(sender,IPUsers[socket]):
											if not IPUsers[socket]==users:
												continue											
											boolean=False
											num=len(IPUsers[socket])
											message="\r" +'\033[1m'+ str(username) + ': ' + messageback[num:]+'\033[0m'
											message+="\nCommand:"
											socket.send(message)
											boolean1=False
										else:
											message="\r"+"You cannot send a message to "+str(IPUsers[socket])+". You have been blocked by the user."
								if boolean and checkBlock(sender,messageback1[1]):
									boolean1=False
									num=len(messageback1[1])
									message="\r" +'\033[1m'+ '<' + str(username) + '> ' + messageback[num:]+'\033[0m'
									message+="\nCommand:"
									if messageback1[1] in private_message:
										temp=private_message[messageback1[1]]
										temp.append(message)
										private_message[messageback1[1]]=temp

									else:
										private_message[messageback1[1]]=[message]
						message="Command:"
						item.send(message)
						boolean=True
					if boolean:
						continue

						#Command did not match. Let user know
						if boolean1:	
							message="Invalid username. Try again"
							message+="\nCommand:"
							item.send(message)
						continue


					message="Invalid command. Try again"
					message+="\nCommand:"
					item.send(message)

				except:
					for socket in current_Users:
						if socket != serverSocket:
							socket.close()
						serverSocket.close()

	serverSocket.close()

if __name__ == "__main__":
	main()
