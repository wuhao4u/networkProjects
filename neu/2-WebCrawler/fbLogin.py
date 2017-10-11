import socket
import fbCommunicator
import fbSearcher

BUFFERSIZE = 8192

# fbLogin : Socket, String, String, FBCookie -> String
# Given: A connected socket and username & password to send login request.
# A cookie for storing and passing csrf token and session id for later uses.
# Return: The http response string from the login page.
# Design Strategy: combine simpler functions
def fb_login(clientSocket, username, password, cookie):
    # GET /fakebook/
    get_response = fbCommunicator.send_get(clientSocket, "/accounts/login/?next=/fakebook/")
    # parse GET response header the first Cookie info

    cookie.set_csrftoken(fbSearcher.search_csrftoken(get_response))
    cookie.set_sessionid(fbSearcher.search_sessionid(get_response))

    # print "cookie from login GET: " + str(cookie)

    # POST /accounts/login/
    # use the Cookie from previous GET for the POST request
    post_body = "username={}&password={}&csrfmiddlewaretoken={}&next=%2Ffakebook%2F".format(username, password, cookie.csrftoken)

    login_post = """
POST /accounts/login/ HTTP/1.0
Host: cs5700f16.ccs.neu.edu
Connection: keep-alive
Content-Length: {}
Origin: http://cs5700f16.ccs.neu.edu
Upgrade-Insecure-Requests: 1
User-Agent: HTTPTool/1.0
Content-Type: application/x-www-form-urlencoded
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
DNT: 1
Referer: http://cs5700f16.ccs.neu.edu/accounts/login/?next=%2Ffakebook%2F
Accept-Encoding: deflate
Accept-Language: en-US,en
Cookie: csrftoken={}; sessionid={}

{}

""".format(str(len(post_body)), cookie.csrftoken, cookie.sessionid, post_body)

    clientSocket.send(login_post)

    post_res = ""
    try:
        post_res = (clientSocket.recv(BUFFERSIZE))
    except socket.error, errStr:
        print "Login failed, did not receive from server correctly, error: ", errStr
        clientSocket.shutdown(1)
        clientSocket.close()
        sys.exit(1)

    # looking for cookie from the post response
    if fbSearcher.search_csrftoken(post_res):
        cookie.set_csrftoken(fbSearcher.search_csrftoken(post_res))

    if fbSearcher.search_sessionid(post_res):
        cookie.set_sessionid(fbSearcher.search_sessionid(post_res))

    return post_res
