import sys
import errno
import socket
import time
from urlparse import urlparse

import bpHTTPLib
import bpSocketLib

################### NOTICE: WE ARE ONLY USING THIS FUNCTION FOR TESTING PURPOSES
def download_using_stream_socket(urlObject, fileObject):
    request = bpHTTPLib.get_requst_string(urlObject)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((urlObject.netloc, 80))
    s.settimeout(180)
    s.send(request)

    result = s.recv(bpUtil.BUFFERSIZE)
    writeFlag = False
    while (len(result) > 0):
        fileObject.write(result)

        if result.find("</HTML>") != -1:
            writeFlag = False
            break

        try:
            result = s.recv(bpUtil.BUFFERSIZE)
        except socket.error, e:
            if e.errno != errno.ECONNRESET:
                print "Sending simple GET request failed: ", errStr
            else:
                print "Connection Closed"
            s.close()
            fileObject.close()
            return

    s.shutdown(1)
    s.close()

# get_requst_string : UrlParse File -> None
# GIVEN:a String url object which is the page we want to get, and the opened file name
# RETURNS: None
def download_using_raw_socket(urlObject, fileObject):
    httpGetReq = bpHTTPLib.get_requst_string(urlObject)

    # 1. create tcp socket
    reqSocket = bpSocketLib.Socket(httpGetReq, urlObject.netloc, 80)

    # 2. connect tcp socket
    try:
        reqSocket.connect()
    except socket.error as errStr:
        reqSocket.disconnect()
        print("Connection Failed. {}".format(errStr))
        sys.exit(2)

    # 3. send tcp socket
    if reqSocket.send(httpGetReq):
        res = ""
        try:
            # 4. receive packets
            res = reqSocket.recv()
        except socket.error as errStr:
            print("Receive error: {}".format(errStr))

        # print("------------------------------All recved packets")
        # print(len(res))

        httpHeader = bpHTTPLib.seperate_http(res)[0]
        httpBody = bpHTTPLib.seperate_http(res)[1:]
        if bpHTTPLib.search_status(httpHeader) == "200 OK":
            # 5. write to response file
            httpBody = bpHTTPLib.seperate_http(res)[1]
            fileObject.write(httpBody)
        else:
            print("Return unexpected status code: {}".format(res))
    else:
        print("Get request sent failed")

# get_file_name : UrlParse -> None
# GIVEN:a String url object which is the page we want to get
# RETURNS: A file name which the program will write to
def get_file_name(urlObj):
    if not urlObj.path or urlObj.path == '':
        return "index.html"
    elif urlObj.path == '/':
        return "index.html"
    else:
        fname = urlObj.geturl().split('/')[-1]
        return fname

def main(argv):
    if len(argv) != 2:
        print("./rawhttpget [URL]")
        sys.exit(2)

    urlObj = urlparse(argv[1])
    fname = get_file_name(urlObj)
    outputFile = open(fname, 'w')
    download_using_raw_socket(urlObj, outputFile)
    outputFile.close()


if __name__ == '__main__':
    # start_time = time.time()
    main(sys.argv)
    # print "--- %s seconds ---" % (time.time() - start_time)
