README.txt

a) A brief description of my code:
My code runs as it should. When a user connects to a server, they will be 
prompted for a username. They will get reprompted over and over again until
they input a valid username. Then they will have three attempts to type 
the correct password. The rest of the program runs as described in the code.
I set it up so that after a certain while, an idle user will get logged out
and free up the username. 

b) Details about development environment
The environment I used was python and the method on multithreading and 
handling multiple users was from the python Documentation page. I imported
the socket library, select library, and standard library.

c) Instructions on running the code
Since this code is in Python, there is no need for a makefile. To run the
server, simply type "python Server.py <portnumber>. The IP address of the
server is now set to localhost but that can easily be changed later. The
client is run the similarly by typing "python Client.py <ServerIP> <portnumber>
where the servip matches the IP Address of the Server and the port number is
the same one as the one the Server is using. 

d) Sample code to run code:

Server Side
python Server.py 4119      

Client side

python Client.py localhost 4119

#Implementation of login:

>Username: columbia
>Username: Columbia
>Password: 116bwa
>Password: 116bways
>Password: 114broadway
>Too many failed attempts
>Username: SEAS
>Password: winterbreakisover
>Welcome to simple chat server!
>whoelse
>The current connected users are:
facebook
>wholasthr
>Users that connected in the last hour are:
facebook
Google
>block facebook
You have successfully blocked facebook from sending you messages
>unblock facebook
You have successfully unblocked facebook from sending you messages
>broadcast HI facebook!
>message facebook Hey man you there?
logout

e) Additional functionalities

The private messaging implementation makes it so that it can infinitely keep
track of all the messages that people send. So five different users can send
10 messages to an offline user and he will recieve all of them when he logs
back in

additional commands:

howlong:
I created a "howlong" function that works very similarly to who else
but instead tells you how long a user had been online for (ever since 
log in).

boldmessage:
This works exactly the same way as message but it will bold the whole messag
for you. NOTE THIS ONLY WORKS IN TERMINAL

boldbroadcast:
This works exactly the same as broadcast but it will bold the whole message
for you. NOTE THIS ONLY WORKS IN TERMINAL



