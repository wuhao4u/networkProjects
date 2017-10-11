import socket
import random
import struct

# CONTRACT: String -> Integer
# GIVEN: a string
# RETURNS: a unique integer checksum calculated based on the given message
# pseudo code from
# https://tools.ietf.org/html/rfc1071#section-4
def get_checksum(msg):
    # add tailing 0 if there is odd number of chars in this msg
    if len(msg) % 2 == 1:
        msg += '\0'

    s = 0
    for i in range(0, len(msg), 2):
        # process by pair of char, one's complement
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w

    s = (s>>16) + (s & 0xffff)
    s = s + (s >> 16)

    return ~s & 0xffff

class TCPPacket(object):
    """docstring for TCPPacket"""
    def __init__(self, data, srcIP, srcPort, destIP, destPort=80):
        super(TCPPacket, self).__init__()
        # self.init_tcp_header_fields()
        self.data = data

        self.srcIP = srcIP
        self.srcPort = srcPort
        self.destIP = destIP
        self.destPort = destPort

        self.ipHeader = IPHeader(self.data, self.srcIP, self.destIP)

        self.seqNum = 0
        self.ackNum = 0
        self.dataOffset = 5
        self.offsetInByte = self.dataOffset << 4
        self.fin = 0
        self.syn = 0
        self.rst = 0
        self.psh = 0
        self.ack = 0
        self.urg = 0
        self.flagsInByte = 0
        self.windowSize = 8192
        self.checksum = 0
        self.urgentPtr = 0

        # self.packetStatus = 0

    def __str__(self):
        return (
'''----------TCP Packet----------
srcIP:{}
srcPort:{}
destIP:{}
destPort:{}
seq#:{}
ack#:{}
dataOffset:{}
fin:{}
syn:{}
rst:{}
psh:{}
ack:{}
urg:{}
winSize:{}
checksum:{}
urgPrt:{}
'''.format(self.srcIP, self.srcPort, self.destIP, self.destPort, 
            self.seqNum, self.ackNum, self.dataOffset,
            self.fin,self.syn,self.rst,self.psh,self.ack,self.urg,
            self.windowSize,self.checksum,self.urgentPtr))

    # CONTRACT: String -> String
    # GIVEN: the tcp header without checksum
    # RETURNS: a string with pseudo ip header
    def get_pseudo_header(self):
        srcIPBin = socket.inet_aton(self.srcIP)
        destIPBin = socket.inet_aton(self.destIP)
        tcpLen = len(self.get_tcp_header_no_checksum()) + len(self.data)
        res = struct.pack('!4s4sBBH' , srcIPBin , destIPBin , 0 , socket.IPPROTO_TCP , tcpLen);
        return res

    # CONTRACT: String Integer -> String
    # GIVEN: the data offset and flags shifted into byte
    # RETURNS: a header string without real checksum
    def get_tcp_header_no_checksum(self):
        self.offsetInByte = (self.dataOffset << 4) + 0
        self.flagsInByte = self.fin + (self.syn << 1) + (self.rst << 2) + (self.psh <<3) + (self.ack << 4) + (self.urg << 5)

        res = struct.pack('!HHLLBBHHH',
            self.srcPort,self.destPort,
            self.seqNum,self.ackNum,
            self.offsetInByte,self.flagsInByte,
            self.windowSize,self.checksum, self.urgentPtr)
        return res

    # CONTRACT: None -> String
    # GIVEN: None
    # RETURNS: the TCP header as string
    def get_tcp_header(self):
        tcpHeaderNoChecksum = self.get_tcp_header_no_checksum()
        pseudoHeader = self.get_pseudo_header()
        self.checksum = get_checksum(pseudoHeader + tcpHeaderNoChecksum + self.data)

        header = struct.pack('!HHLLBBH',
         self.srcPort, self.destPort, 
         self.seqNum, self.ackNum, 
         self.offsetInByte, self.flagsInByte, self.windowSize) + \
        struct.pack('H',self.checksum) + \
        struct.pack('!H' , self.urgentPtr)

        return header

    # CONTRACT: -> String
    # GIVEN: None
    # RETURNS: a string contains ip header, tcp header, and data
    def get_tcp_packet(self):
        res = self.ipHeader.get_ip_header() + self.get_tcp_header() + self.data
        return res


class IPHeader(object):
    """docstring for IPHeader"""
    def __init__(self, data, srcIP, destIP):
        super(IPHeader, self).__init__()

        self.srcIP = srcIP
        self.destIP = destIP
        self.data = data
        self.version = 4
        self.headerLen = 5
        self.serviceType = 0
        self.pktLen = 0
        self.id = 12345
        self.fragOffset = 0
        self.ttl = 180
        self.protocol = socket.IPPROTO_TCP
        self.checksum = 0
        self.headerLenVersion = (self.version << 4) + self.headerLen

    def __str__(self):
        return ('''
----------IP Header----------
srcIP:{}
destIP:{}
version:{}
headerLen:{}
serviceType:{}
pktLen:{}
id:{}
fragOffset:{}
ttl:{}
protocol:{}
checksum:{}
headerLenVersion:{}
'''.format(self.srcIP, self.destIP, self.version, self.headerLen, 
            self.serviceType, self.pktLen, self.id, self.fragOffset,
        self.ttl, self.protocol, self.checksum, self.headerLenVersion))

    # CONTRACT: None -> String
    # GIVEN: the tcp header without checksum
    # RETURNS: a string with pseudo ip header
    def get_ip_pseudo_header(self):
        ipPseudoHeader = struct.pack('!BBHHHBBH4s4s', self.headerLenVersion, self.serviceType, 
                    self.pktLen, self.id, self.fragOffset, self.ttl, self.protocol,
                    self.checksum, self.srcIPBinary, self.destIPBinary)
        return ipPseudoHeader

    # CONTRACT: None -> String
    # GIVEN: None
    # RETURNS: the IP header as string
    def get_ip_header(self):

        self.srcIPBinary = socket.inet_aton(self.srcIP)
        self.destIPBinary = socket.inet_aton(self.destIP)
        self.id = random.randint(0, 65535)
        self.pktLen = self.headerLen * 4 + len(self.data)

        ipPseudoHeader = self.get_ip_pseudo_header()
        self.checksum = get_checksum(ipPseudoHeader)

        header = struct.pack('!BBHHHBBH4s4s', self.headerLenVersion, self.serviceType, 
                    self.pktLen, self.id, self.fragOffset, self.ttl, self.protocol,
                    self.checksum, self.srcIPBinary, self.destIPBinary)

        return header