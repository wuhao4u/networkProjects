# This fiel inludes two functions: send_get and send_get_with_cookie
import re
import socket

# BUFFESIZE is the size of memory assigned to socket().recv for msgs 
BUFFERSIZE = 8192

#####################################################################
#
# This function send a GET request and returns the html page
#
# Contract of the function:
# sent_get : Sockt, String -> String
# 
# Purpose Statement:
# GIVEN: a Socket named clientSocket and a String url which is the 
#        the page we want to get
# RETURNS: the page as a string
#
# Function definition:
def send_get(clientSocket, url):

    # get_req contains all the specifications of the GET request
    get_req = """
GET {} HTTP/1.0
Host: cs5700f16.ccs.neu.edu
Connection: Keep-Alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
DNT: 1
Referer: http://cs5700f16.ccs.neu.edu/
Accept-Encoding: deflate, sdch
Accept-Language: en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2

""".format(url)
    # Send the request
    clientSocket.send(get_req)

    # The response is stored in get_res, initially set to none
    get_res = ""

    # Try to receive the response 
    try:
        get_res = (clientSocket.recv(BUFFERSIZE))
    except socket.error, errStr:
        print "Sending simple GET request failed: ", errStr
        clientSocket.shutdown(1)
        clientSocket.close()
        sys.exit(1)

    return get_res

#####################################################################
#
# This function sends a GET request with a cookie
#
# Contract of the function:
# send_get_with_cookie : Socket, String, String -> String
#
# Purpose Statement:
# GIVEN: a Socket, a string as the url of the requested page
# and the cookie
# RETURNS: the requested page as a string
#
# Function definition:
def send_get_with_cookie(clientSocket, url, cookie):

    # getReq contains all the specifications for the GET requset
    getReq =  """
GET {} HTTP/1.0
Host: cs5700f16.ccs.neu.edu
Connection: Keep-Alive
Upgrade-Insecure-Requests: 1
User-Agent: HTTPTool
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
DNT: 1
Accept-Encoding: deflate
Accept-Language: en-US,en
Cookie: csrftoken={}; sessionid={}


""".format(url, cookie.get_csrftoken(), cookie.get_sessionid())
    
    # Send the request
    clientSocket.send(getReq)

    # getRes is used to store the received msg from sever
    # initially set to none
    getRes = ""
    try:
        getRes = (clientSocket.recv(BUFFERSIZE))
    except socket.error, errStr:
        print "Sending GET request with cookie failed: ", errStr
        clientSocket.shutdown(1)
        clientSocket.close()
        sys.exit(1)

    return getRes
