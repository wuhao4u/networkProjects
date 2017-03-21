import os
import sys
import socket
import threading
import getopt
import SocketServer
from struct import *
from hostselector import *

ORIGIN_SERVER_IP = "54.167.4.20"
DNS_SERVER_IP = "129.10.117.186"
IP_MAPPING_CACHE = {}

###############################################################################
# DNSRequestHandler is a request handler 
# which is specific for handline DNS request
class DNSRequestHandler(SocketServer.BaseRequestHandler):
    """docstring for DNSRequestHandler"""

    # Over-write the handle function from BaseRequestHandler
    def handle(self):
        # parse incoming request
        # process data
        # send a response
        data = self.request[0].strip()
        socket = self.request[1]
        print "{} wrote:".format(self.client_address[0])
        pkt = DNSPacket()
        pkt.set(data)

        print("-----------------recv pkt----------------")
        print(pkt)

        # find the best host for this client based on the client IP
        if IP_MAPPING_CACHE.has_key(self.client_address[0]):
            pkt.answer.rdata = IP_MAPPING_CACHE[self.client_address[0]]
        else:
            try:
                pkt.answer.rdata = get_host_by_location(self.client_address[0])
                # set ip mapping cache for later use
                IP_MAPPING_CACHE[self.client_address[0]] = pkt.answer.rdata
            except Exception as e:
                print("cannot resolve address name.")
                print(e)
                # use the original server if we cannot get result by his/her IP info
                pkt.answer.rdata = ORIGIN_SERVER_IP

            # Commented out code was for using qname to get closest IP
            # try:
            #     pkt.answer.rdata = get_host_by_location(pkt.question.qname)
            #     # set ip mapping cache for later use
            #     IP_MAPPING_CACHE[pkt.question.qname] = pkt.answer.rdata
            # except Exception as e:
            #     print("cannot resolve address name, generating result by client IP.")
            #     print(e)
            #     pkt.answer.rdata = get_host_by_location(self.client_address[0])
            #     # set ip mapping cache for later use
            #     IP_MAPPING_CACHE[self.client_address[0]] = pkt.answer.rdata


        pkt.header.qr = 1
        pkt.header.rd = 1
        pkt.header.ra = 1
        pkt.header.qdcount = 1
        pkt.header.ancount = 1
        pkt.answer.name = pkt.question.qname
        res = pkt.get()
        print("---------------send pkt-----------------")
        print(pkt)
 
        socket.sendto(res, self.client_address)

###############################################################################
# DNSPacket is a packet contains a DNS Header, DNS Question, 
# and a DNS Answer object
# and get/set methods
class DNSPacket():
    """docstring for DNSPacket"""
    def __init__(self):
        # answer, authority and addtional info shares same format
        self.header = DNSHeader()
        self.question = DNSQuestion()
        self.answer = DNSResourceRecord()
    
    def __str__(self):
        return str(self.header) + str(self.question) + str(self.answer)

    def set(self, rawData):
        self.header.set(rawData[:12])
        if self.header.qdcount == 1 and self.header.qr == 0:
            self.question.set(rawData[12:])

    def get(self):
        return self.header.get() + self.question.get() + self.answer.get()

###############################################################################
# DNSHeader is a header contains all the DNS field and get/set methods
class DNSHeader():
    def __init__(self):
        self.id = 0

        self.flags = 0
        self.qr = 0
        self.opcode = 0
        self.aa = 0
        self.tc = 0
        self.rd = 0
        self.ra = 0
        self.z = 0
        self.rcode = 0

        # number of entries in the question section
        self.qdcount = 0
        # number of resources records in answer section
        self.ancount = 0
        # number of name server resource records in auth records section
        self.nscount = 0
        # number of rr in addiotional records section
        self.arcount = 0
    
    def __str__(self):
        return (
'''
-----------------------------
DNSHeader
id: {}
flags: {}
qdcount: {}
ancount: {}
nscount: {}
arcount: {}

Indie Flag:
qr: {}
opcode: {}
aa: {}
tc: {}
rd: {}
ra: {}
z: {}
rcode: {}
'''.format(self.id, self.flags, self.qdcount, self.ancount, self.nscount, self.arcount,
            self.qr, self.opcode, self.aa, self.tc, self.rd, self.ra, self.z, self.rcode))

    def set(self, rawData):
        rawHeader = unpack('!HHHHHH', rawData)
        self.id = rawHeader[0]
        self.flags = rawHeader[1]
        self.qdcount = rawHeader[2]
        self.ancount = rawHeader[3]
        self.nscount = rawHeader[4]
        self.arcount = rawHeader[5]
        self.set_flags()

    def set_flags(self):
        rawFlags = self.flags
        print("raw flags: {}".format(self.flags))
        self.rcode = rawFlags & 0x8
        self.z = (rawFlags & 0x40) >> 4
        self.ra = (rawFlags & 0x80) >> 7
        self.rd = (rawFlags & 0x100) >> 8
        self.tc = (rawFlags & 0x200) >> 9
        self.aa = (rawFlags & 0x400) >> 10
        self.opcode = (rawFlags & 0x4000) >> 11
        self.qr = (rawFlags & 0x8000) >> 15

    def get_flags(self):
        res = long(0)
        res = self.rcode + (self.z << 4) + (self.ra << 7) + (self.rd << 8) \
        + (self.tc << 9) + (self.aa << 10) + (self.opcode << 11) + (self.qr << 15)
        self.flags = res
        print("get_flags: {}".format(res))
        return res

    def get(self):
        res = pack('!HHHHHH', self.id, self.get_flags(), self.qdcount,
         self.ancount, self.nscount, self.arcount)
        return res

###############################################################################
# DNSQuestion is a section part in DNS request
class DNSQuestion():
    def __init__(self):
        self.qname = 'cs5700cdn.example.com'
        self.rawQName = ''
        # 2 octet code specifies the type of the query
        self.qtype = 0
        # 2 octet code that specifies the class of the query
        self.qclass = 0

    def __str__(self):
        return (
'''
-----------------------------
DNS Question
qname: {}
qtype: {}
qclass: {}
'''.format(self.qname, self.qtype, self.qclass))

    # parsing raw byte code to fields in DNSQuestion
    def set(self, rawData):
        # parse qname. qtype, qclass
        self.rawQName = rawData[:-4]
        print("raw QNAME: {}".format(self.rawQName))

        self.set_qname(self.rawQName)

        # unpack qtype and qclass
        rawDataTail = unpack('!HH', rawData[-4:])
        self.qtype = rawDataTail[0]
        self.qclass = rawDataTail[1]

    # unpck qname bytecode to a regular string
    def set_qname(self, rawQName):
        # qname example, "9cs5700cdn7example3com"
        if not rawQName:
            rawQName = self.rawQName

        res = ''
        chPtr = 0

        # read the 1st address segment length
        segLen = unpack('!B', rawQName[chPtr])[0]
        chPtr += 1

        while segLen != 0:
            # innter loop count
            counter = 0
            while counter < segLen and chPtr < len(rawQName):
                ch = unpack('!c', rawQName[chPtr])[0]
                res += ch
                counter += 1
                chPtr += 1
            res += '.'
            # after finish reading a segment of IPv4 Address, unpack next segment length
            segLen = unpack('!B', rawQName[chPtr])[0]
            chPtr += 1

        # remove the extra '.' from the result string
        self.qname = res[:-1]

    # pack current fields into byte code
    def get(self):
        # we don't need to change qname field in respond packet
        res = self.rawQName + pack('!HH', self.qtype, self.qclass)
        return res

###############################################################################
# DNSResourceRecord is a RR contains all the DNS fields for
# answer, authority and addtional info and get/set methods
class DNSResourceRecord():
    def __init__(self):
        self.name = 'cs5700cdn.example.com'
        self.type = 1
        self.rclass = 1
        self.ttl = 300
        self.rdata = ORIGIN_SERVER_IP
        self.rdlength = len(socket.inet_aton(self.rdata))
    
    def __str__(self):
        return (
'''
-----------------------------
DNS Resource Record
Name: {}
Type: {}
Class: {}
TTL: {}
RDLENGTH: {}
DATA: {}
'''.format(self.name, self.type, self.rclass, 
    self.ttl, self.rdlength, self.rdata))

    # we are not implenting the reading DNS answer part in this project
    # since we will fill in our own DNS Answer
    def set(self, rawData):
        pass

    # packing our answer IP (best server IP for the client) into bytes
    def get_name_in_bin(self):
       res = ''
       if self.name:
            splitedIP = self.name.split('.')
            for seg in splitedIP:
                res += pack('!B', len(seg))
                for c in seg:
                    res += pack('!c', c)
       res += '\x00'
       return res

    # packing the DNS Answer
    def get(self):
        res =  self.get_name_in_bin() + pack(
            '!HHLH4s', self.type, self.rclass, self.ttl, 
            self.rdlength, socket.inet_aton(self.rdata))
        return res

# main : ListOfStrings -> None
# Purpose Statement: verfify arguments, starts the DNS server
def main(argv):
    if len(argv) != 4:
         print("./dnsserver -p <port> -n <name>")
       
    portNum = 0
    name = ''

    try:
        options, args = getopt.getopt(argv, "p:n:")
    except getopt.GetoptError:
        print("./dnsserver -p <port> -n <name>")
        sys.exit(2)

    # This for loop handles command options with parameters
    gotPort = False
    gotName = False
    for o, a in options:
        if o == "-p":
            try:
                portNum = long(a)
                gotPort = True
            except ValueError, errMsg:
                print "Invalid port number. \n{}".format(errMsg)
        elif o == "-n":
            name = str(a)
            gotName = True
        else:
            print("Invalid command option.{}, {}".format(o, a))
            print("./dnsserver -p <port> -n <name>")
            sys.exit(2)

    # we have the port and name, now we can start the DNS server
    if gotPort and gotName:
        address = ('', portNum)
        server = SocketServer.UDPServer(address, DNSRequestHandler)

        server.serve_forever()

        # We were going to implement multi-threading for dns server
        # mainThread = threading.Thread(target=server.serve_forever)
        # mainThread.setDaemon(True)
        # mainThread.start()


if __name__ == '__main__':
    main(sys.argv[1:])
