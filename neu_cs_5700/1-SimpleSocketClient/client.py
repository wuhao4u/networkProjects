#!/usr/bin/env python
import os
import sys
import socket
import ssl
import getopt

BUFFERSIZE = 256
HOSTNAME = "cs5700f16.ccs.neu.edu"
PORTNUM_NON_SSL = 27993
PORTNUM_SSL = 27994
NUID = str(001606723)

def calculate(msgList):
    x = int(msgList[2])
    symbol = chr(ord(msgList[3]))
    y = int(msgList[4])
    if(symbol == '+'):
        return x+y
    elif(symbol == '-'):
        return x-y
    elif(symbol == '*'):
        return x*y
    elif(symbol == '/'):
        return x/y
    else:
        raise ValueError("Unexpected symbol %s", symbol)


def connect(hostName, portNum, nuid, sslOpt):
    msgHead = "cs5700fall2016 "
    try:
        host = socket.gethostbyname(hostName)
    except socket.error, errStr:
        print "problem resolving the hostname: {}, {}".format(hostName, errStr)

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.settimeout(5)

    try:
        clientSocket.connect((host, portNum))
    except Exception, errStr:
        print "problem connecting: {}".format(errStr)
        sys.exit(1)
    # SSL option enabled
    try:
        if sslOpt == True: 
            clientSocket = ssl.wrap_socket(clientSocket, ciphers = "ALL")
    except ssl.SSLError, errMsg:
        print "ssl cannot establish. {}".format(errMsg)

    # 1st message afetr commection established
    helloMsg = "cs5700fall2016 HELLO {}\n".format(nuid)
    clientSocket.send(helloMsg)

    msg = ""
    try:
        msg = (clientSocket.recv(BUFFERSIZE))
    except Exception, e:
        print "Did not receive from server correctly, error: ", e
        sys.exit(1)

    sol = 0
    while len(msg) > 0 and msg != 0:
        try:
            msg = msg.strip().split()
        except:
            print "Unexpected return value, check your calculation."
            clientSocket.shutdown(1)
            clientSocket.close()
            sys.exit(1)

        if msg[1] == "STATUS":
            sol = calculate(msg)
            clientSocket.send(msgHead + str(sol) + '\n')
            msg = (clientSocket.recv(BUFFERSIZE))
        elif msg[-1] == "BYE":
            print msg[1]
            break
    else:
        print("problem with the solution %d, connection broke.", sol)

    clientSocket.shutdown(1)
    clientSocket.close()

def main(argv):
    try:
        options, nonParamOptions = getopt.getopt(argv, "p:s")
    except getopt.GetoptError:
        print("./client <-p port> <-s> [hostname] [NEU ID]")
        sys.exit(2)

    hostName = HOSTNAME
    portNum = PORTNUM_NON_SSL
    nuid = NUID
    sslOpt = False
    portNumSpecified = False
    # This for loop handles command options with parameters
    for o, a in options:
        if o == "-p":
            try:
                portNum = long(a)
                portNumSpecified = True
            except ValueError, errMsg:
                print "Invalid port number. \n{}".format(errMsg)
        elif o == "-s":
            sslOpt = True
            if portNumSpecified == False:
                portNum = PORTNUM_SSL 

    if len(nonParamOptions) != 2:
        print("./client <-p port> <-s> [hostname] [NEU ID]")
        sys.exit(2)
    else:
        hostName = nonParamOptions[0]
        nuid = str(nonParamOptions[1])

    connect(hostName, portNum, nuid, sslOpt)

if __name__ == '__main__':
    main(sys.argv[1:])
