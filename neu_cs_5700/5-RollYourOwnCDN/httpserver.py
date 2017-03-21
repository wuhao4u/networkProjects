import BaseHTTPServer
import SocketServer
import httplib
import sys
import getopt
import os

# The default value of origin address and port
# PAGE_CACHE = LRUCache.LRUCache(60)
ORIGIN_ADDRESS = "54.167.4.20"
ORIGIN_PORT = 8080

def main(argv):
    # The default value of port number of server
    portNum = 44445
    originAddress = ''
 
    # Check the format of command line
    try:
        options, args = getopt.getopt(argv, "p:o:")
    except getopt.GetoptError:
        print("./httpserver -p <port> -o <origin>")
        sys.exit(2)

    print("options:{}, args: {}".format(options, args))

    # This for loop handles command options with parameters
    gotPort = False
    gotOrigin = False
    for o, a in options:
        print("o: {}, a:{}".format(o,a))
        if o == "-p":
            try:
                portNum = long(a)
                gotPort = True
            except ValueError, errMsg:
                print "Invalid port number. \n{}".format(errMsg)
        elif o == "-o":
            originAddress = str(a)
            gotOrigin = True
        else:
            print("Invalid command option.{}, {}".format(o, a))
            print("./httpserver -p <port> -o <option>")
            sys.exit(2)
    # print portNum
    # print originAddress

    # If port number of server and address of origin acknowleged
    if gotPort and gotOrigin:
        # Run the server
        httpd = BaseHTTPServer.HTTPServer(("",portNum), CdnHTTPRequestHandler)
        httpd.serve_forever()

# search_cache_folder : String -> Boolean
def search_cache_folder(filename):
    for f in os.listdir("./cache"):
        if filename in f:
            # print f
            return True
    return False

# CdnHTTPRequestHandler is a subclass of BaseHTTPReuqestHandler
class CdnHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        # Get the requested filename
        filename = str(self.path)
        filename = filename.replace("/","_")

        # If file is in cache, send it to client
        if search_cache_folder(filename):
            print("page in disk")
            # print(self.path)

            self.send_response(200)
            self.end_headers()
            with open("./cache/"+filename) as cacheFile:
                for line in cacheFile:
                    self.wfile.write(line)
        # If file is not in cache, fetch from origin
        else:
            print("page fetched from origin")

            client = httplib.HTTPConnection(ORIGIN_ADDRESS,ORIGIN_PORT)
            client.request("GET",self.path)
            res = client.getresponse()

            # print(self.path)
            # print(res.status, res.reason)

            self.send_response(res.status)
            self.end_headers()
            data=res.read()
            self.wfile.write(data)

if __name__ == "__main__":
    main(sys.argv[1:])
