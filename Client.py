from socket import *
from select import *
import sys
import threading

TIME_OUT=30*60

def newline() :
    sys.stdout.flush()

def prompt() :
    sys.stdout.flush()

def logout(sock):
    message="logout"
    sock.send(message)

#main function
if __name__ == "__main__":
     
    if(len(sys.argv) < 3) :
        print 'Usage : python Client.py hostname port'
        sys.exit()
     
    servername = sys.argv[1]
    portnum = int(sys.argv[2])
     
    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.settimeout(2)
     
    # connect to remote host
    clientSock.connect((servername, portnum))

    newline()
    boolean=False
     
    while 1:
        try:
            socket_list = [sys.stdin, clientSock]
            read_sockets, write_sockets, error_sockets =select(socket_list , [], [])
             
            for sock in read_sockets:
                if sock == clientSock:
                    data = sock.recv(1026)
                    if "Welcome to simple chat server!" in data:
                        if not boolean:
                            boolean=True
                            logouttime=threading.Timer(TIME_OUT,logout,[clientSock])
                            logouttime.start()

                    if not data :
                        print '\nDisconnected from chat server'
                        sys.exit()
                    else:
                        if not boolean:
                            #print data
                            sys.stdout.write(data)
                            substring='\n'
                            if substring in data:
                                newline()
                            sys.stdout.flush()
                        else:
                            #print data
                            sys.stdout.write(data)
                            substring='\n'
                            if substring in data:
                                prompt()
                            sys.stdout.flush()
                     
                    
                #user entered a message
                else :
                    if not boolean:
                        newline()
                        msg = sys.stdin.readline()
                        clientSock.send(msg)
                    else:
                        newline()
                        msg = sys.stdin.readline()
                        clientSock.send(msg)
                        logouttime.cancel()
                        logouttime=threading.Timer(TIME_OUT,logout,[clientSock])
                        logouttime.start()


        except KeyboardInterrupt:
            logout(clientSock)
            if boolean:
                logouttime.cancel()
            sys.exit()


              
