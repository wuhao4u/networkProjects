import sys
import socket
import struct
import errno
import random
import time
from bpPacketLib import *

#################### CONSTANTS ####################

BUFFERSIZE = 8192
URL2MB = "http://david.choffnes.com/classes/cs4700fa16/2MB.log"
URL10MB = "http://david.choffnes.com/classes/cs4700fa16/10MB.log"
URL50MB = "http://david.choffnes.com/classes/cs4700fa16/50MB.log"

#################### HELPER FUNCTIONS ####################

# CONTRACT: -> Socket.socket
# GIVEN: None
# RETURNS: a IPPROTO_RAW socket for sending packets
def create_raw_send_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        return s
    except socket.error , msg:
        print "Failed Creating Raw Socket \n{}".format(msg)
        sys.exit()

# CONTRACT: -> Socket.socket
# GIVEN: None
# RETURNS: an IPPROTO_TCP socket for receiving packets
def create_raw_recv_socket():
    try:
        # IPPROTO_IP is a dummy protocol, not usable
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        return s
    except socket.error , msg:
        print "Failed Creating Raw Socket \n{}".format(msg)
        sys.exit()

# CONTRACT: -> Tuple
# GIVEN: None
# RETURNS: a tuple with 2 strings, 1st is the ip address of the local machine,
#          2nd is an open port which the socket can use
def get_src_addr():
    # create a dummy socket to find out our ip and open port of this machine
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('google.com', 80))
    res = sock.getsockname()
    # close it for raw sockets to use later
    sock.close()
    return res

# CONTRACT: String -> String
# GIVEN: an string in format of "david.choffnes.com/"
# RETURNS: the ip address of the given address
def get_dest_ip(destAddr):
    # resolve destination address as ip
    destIP = ""
    try:
        destIP = socket.gethostbyname(destAddr)
    except socket.error, errStr:
        print("Cannot resolve host name.\n{}".format(errStr))
        sys.exit(2)

    return destIP

#################### CLASS DEFINITIONS ####################
class Socket(object):
        """docstring for Socket"""
        def __init__(self, data, addr, portNum = 80):
            super(Socket, self).__init__()
            self.data = data
            self.destAddr = addr
            self.destPort =portNum
            self.connected = False

            self.seqNum = 0
            self.ackNum = 0

            self.srcIP, self.srcPort = get_src_addr()

            self.destIP = get_dest_ip(self.destAddr)

            self.recvPackets = []
            self.rawSendSock = create_raw_send_socket()
            self.rawRecvSock = create_raw_recv_socket()

            self.cwnd = 1

            self.outOfOrderPkts = []
            # self.ackWaitingQueue = 

        # CONTRACT: String Integer -> 
        # GIVEN: the address and port this socket wants to connect to
        # RETURNS: None
        def connect(self, addr="", port=80):
            if addr:
                self.destAddr = addr
                self.destIP = get_dest_ip(self.destAddr)
            if port != 80:
                self.destPort = port

            if self.destIP == "0.0.0.0":
                print("Invalid host name.")
                sys.exit(2)

            # build connection using 3-way handshake
            # we will attempt 5 times
            counter = 5
            while counter > 0:
                if self.three_way_handshakes():
                    self.connected = True
                    return
                counter -= 1

            raise socket.timeout

        # CONTRACT: -> Boolean
        # GIVEN: None
        # RETURNS: a boolean flag indicates wether the 3way handshake was successful or not
        def three_way_handshakes(self):
            # Client: SYN = 1, seq = x, ACK = 0
            # Server: SYN = 1, seq = y, ACK = x+1
            # Client: seq = x+1, ACK = y+1
            # SYN: The active open is performed by the client sending a SYN to the server. 
            #      The client sets the segment's sequence number to a random value A.
            # SYN-ACK: In response, the server replies with a SYN-ACK. 
            #          The acknowledgment number is set to one more than the received sequence number 
            #          i.e. A+1, and the sequence number that the server chooses for the packet is another random number, B.
            # ACK: Finally, the client sends an ACK back to the server.
            #      The sequence number is set to the received acknowledgement value 
            #      i.e. A+1, and the acknowledgement number is set to one more than the received sequence number i.e. B+1.

            # a 16 bit number
            self.seqNum = random.randint(0, 65535)

            # packet with no data
            synPkt = TCPPacket("", self.srcIP, self.srcPort, self.destIP, self.destPort)
            synPkt.seqNum = self.seqNum
            synPkt.syn = 1
            synPkt.ack = 0

            sendingMsg = synPkt.get_tcp_packet()
            # self.debug()
            self.rawSendSock.sendto(sendingMsg, (self.destIP, self.destPort))

            synackPkt = TCPPacket("", self.srcIP, self.srcPort, self.destIP, self.destPort)
            try:
                synackPkt = self.recv_packet()
            except socket.error as e:
                raise e

            if synackPkt.ackNum == (self.seqNum+1) and synackPkt.syn == 1 and synackPkt.ack == 1:
                self.seqNum += 1
                self.ackNum = synackPkt.seqNum + 1

                ackPkt = TCPPacket("", self.srcIP, self.srcPort, self.destIP, self.destPort)
                ackPkt.seqNum = self.seqNum
                ackPkt.ackNum = self.ackNum
                ackPkt.ack = 1
                ackPkt.syn = 0
                # print("3-way: received SYN+ACK.")

                sendingMsg = ackPkt.get_tcp_packet()
                self.rawSendSock.sendto(sendingMsg, (self.destIP, self.destPort))
                return True
            else:
                print("Cannot connected to the server. 3-way handshakes failed.")
                return False

        # CONTRACT: String -> Boolean
        # GIVEN: a http get request as string
        # RETURNS: a flag indicates whethere the request being sent successfully in the TCP level
        def send(self, httpGetReq):
            if self.connected:
                sendPkt = TCPPacket(httpGetReq, self.srcIP, self.srcPort, self.destIP, self.destPort)
                sendPkt.seqNum = self.seqNum
                sendPkt.ackNum = self.ackNum
                sendPkt.ack = 1
                sendPkt.psh = 1

                sendingMsg = sendPkt.get_tcp_packet()
                self.rawSendSock.sendto(sendingMsg, (self.destIP, self.destPort))
                self.cwnd += 1

                # get the ack from server
                startTime = time.time()
                while (time.time() - startTime) < 60:
                    ackPkt = self.recv_packet()
                    if ackPkt.ackNum == (sendPkt.seqNum + len(httpGetReq)):
                        self.seqNum = ackPkt.ackNum
                        self.ackNum = ackPkt.seqNum + len(ackPkt.data)
                        self.cwnd -= 1
                        return True

                # retrasmit
                self.rawSendSock.sendto(sendingMsg, (self.destIP, self.destPort))
                return False
            else:
                raise socket.error("Socket is not connected.")

        def inOutOfOrderQueue(self, newPkt):
            for p in self.outOfOrderPkts:
                if newPkt.seqNum == p.seqNum:
                    return True

        # CONTRACT: None -> String
        # GIVEN: None
        # RETURNS: a string contains the accumulation of the packets that arrived in sequence
        def recv(self):
            res = ""
            while 1:
                try:
                    recvPkt = self.recv_packet()
                except socket.error as errStr:
                    self.cwnd = 1
                    self.disconnect()
                    return res

                # packet arrived in order
                if self.ackNum == recvPkt.seqNum:
                    self.cwnd -= 1
                    self.ackNum = recvPkt.seqNum + len(recvPkt.data)
                    # self.seqNum = recvPkt.ackNum 
                    res += recvPkt.data
                else:
                    print("out of order packets number: {}".format(len(self.outOfOrderPkts)))
                    if not self.inOutOfOrderQueue(recvPkt):
                        self.outOfOrderPkts.append(recvPkt)

                # server wants to finish
                if recvPkt.fin == 1:
                    if recvPkt.seqNum == self.ackNum:
                        #send fin ack
                        clientFinPkt = TCPPacket("", self.srcIP, self.srcPort, self.destIP, self.destPort)
                        clientFinPkt.seqNum = self.seqNum
                        clientFinPkt.ackNum = self.ackNum
                        clientFinPkt.fin = 1
                        clientFinPkt.ack = 1

                        sendingMsg = clientFinPkt.get_tcp_packet()

                        self.rawSendSock.sendto(sendingMsg, (self.destIP, self.destPort))
                        self.connected = False
                    return res
                elif recvPkt.rst == 1:
                    # server reset the connection, no need to send fin
                    self.connected = False
                    return res
                else:
                    # send ack pakcet
                    ackPkt = TCPPacket("", self.srcIP, self.srcPort, self.destIP, self.destPort)
                    ackPkt.seqNum = self.seqNum
                    ackPkt.ackNum = self.ackNum
                    ackPkt.ack = 1
                    sendingMsg = ackPkt.get_tcp_packet()
                    # print("ackPkt TCP header:")
                    # print(ackPkt)
                    # print("ackPkt IP header:")
                    # print(ackPkt.ipHeader)

                    if self.cwnd < 1000:
                        self.cwnd += 1 
                        self.rawSendSock.sendto(sendingMsg, (self.destIP, self.destPort))


        # CONTRACT: None
        # GIVEN: None
        # RETURNS: a received TCP Packet.
        def recv_packet(self):
            startTime = time.time()

            # 3 second is enough for a packet transfer to India/China...
            while (time.time() - startTime) < 60:
                recvTCPPkt = TCPPacket('','', 0, '', 0)
                rawRecvPkt = self.rawRecvSock.recv(BUFFERSIZE)

                ########## IP header unpacking ##########
                rawIPHeader = rawRecvPkt[0:20]
                rawIPHeaderUnpacked = struct.unpack('!BBHHHBBH4s4s', rawIPHeader)

                recvTCPPkt.ipHeader.headerLenVersion = rawIPHeaderUnpacked[0]
                recvTCPPkt.ipHeader.version = recvTCPPkt.ipHeader.headerLenVersion >> 4
                recvTCPPkt.ipHeader.headerLen = recvTCPPkt.ipHeader.headerLenVersion & 0xF

                ipHeaderLen = recvTCPPkt.ipHeader.headerLen * 4

                recvTCPPkt.ipHeader.serviceType = rawIPHeaderUnpacked[1]
                recvTCPPkt.ipHeader.pktLen = rawIPHeaderUnpacked[2]
                recvTCPPkt.ipHeader.id = rawIPHeaderUnpacked[3]
                recvTCPPkt.ipHeader.fragOffset = rawIPHeaderUnpacked[4]
                recvTCPPkt.ipHeader.ttl = rawIPHeaderUnpacked[5]
                recvTCPPkt.ipHeader.protocol = rawIPHeaderUnpacked[6]
                recvTCPPkt.ipHeader.checksum = rawIPHeaderUnpacked[7]
                recvTCPPkt.ipHeader.srcIP = socket.inet_ntoa(rawIPHeaderUnpacked[8])
                recvTCPPkt.ipHeader.destIP = socket.inet_ntoa(rawIPHeaderUnpacked[9])

                # ip checksum only checks its header's integrity
                if get_checksum(rawIPHeader) != 0:
                    raise socket.error("Received packet IP checksum error")

                # check if the recevied packet is sending to this ip
                if (recvTCPPkt.ipHeader.srcIP == self.destIP and 
                    recvTCPPkt.ipHeader.destIP == self.srcIP and
                    recvTCPPkt.ipHeader.protocol == socket.IPPROTO_TCP):
                    # ip packet to us

                    ########## TCP header unpacking ##########
                    rawTCPHeader = rawRecvPkt[ipHeaderLen:ipHeaderLen + 20]
                    rawTCPHeaderUnpacked = struct.unpack('!HHLLBBHHH', rawTCPHeader)
                
                    recvTCPPkt.srcPort = rawTCPHeaderUnpacked[0]
                    recvTCPPkt.destPort = rawTCPHeaderUnpacked[1]
                    
                    # check if the recevied packet is sending to this port
                    if recvTCPPkt.destPort == self.srcPort:
                        recvTCPPkt.seqNum = rawTCPHeaderUnpacked[2]
                        recvTCPPkt.ackNum = rawTCPHeaderUnpacked[3]
                        recvTCPPkt.dataOffset = rawTCPHeaderUnpacked[4] >> 4

                        tcpHeaderLenBit = recvTCPPkt.dataOffset * 4

                        recvTCPPkt.srcIP = socket.inet_ntoa(rawIPHeaderUnpacked[8])
                        recvTCPPkt.destIP = socket.inet_ntoa(rawIPHeaderUnpacked[9])
                        headerSize = ipHeaderLen + tcpHeaderLenBit
                        recvTCPPkt.data = rawRecvPkt[headerSize:]

                        tcpFlags = rawTCPHeaderUnpacked[5]

                        recvTCPPkt.fin = tcpFlags & 0x01
                        recvTCPPkt.syn = (tcpFlags & 0x02) >> 1
                        recvTCPPkt.rst = (tcpFlags & 0x04) >> 2
                        recvTCPPkt.psh = (tcpFlags & 0x08) >> 3
                        recvTCPPkt.ack = (tcpFlags & 0x10) >> 4
                        recvTCPPkt.urg = (tcpFlags & 0x20) >> 5

                        recvTCPPkt.windowSize = rawTCPHeaderUnpacked[6]
                        recvTCPPkt.checksum = rawTCPHeaderUnpacked[7]
                        recvTCPPkt.urgentPtr = rawTCPHeaderUnpacked[8]

                        # TCP checksum verify
                        ipPseudoHeader = struct.pack('!4s4sBBH',
                                                    socket.inet_aton(recvTCPPkt.srcIP),
                                                    socket.inet_aton(recvTCPPkt.destIP),
                                                    0,
                                                    socket.IPPROTO_TCP,
                                                    recvTCPPkt.dataOffset * 4 + len(recvTCPPkt.data))

                        if get_checksum(ipPseudoHeader + rawRecvPkt[ipHeaderLen:]) != 0:
                            print("ph 1: {}\nph 2: {}".format(ipPseudoHeader, recvTCPPkt.get_pseudo_header()))
                            raise socket.error("Received packet TCP checksum error")

                        return recvTCPPkt
            raise socket.error("Timeout, not able to receive packet")

        # CONTRACT: ->
        # Purpose Statement: proactively disconnect
        # GIVEN: None
        # RETURNS: None
        def disconnect(self):
            # Client: FIN = 1, seq = x, ACK = 0
            # Server: FIN = 1, seq = y, ack = x+1
            # Client: seq = x+1, ack = y+1

            if self.connected:
                clientFinPkt = TCPPacket("", self.srcIP, self.srcPort, self.destIP, self.destPort)
                clientFinPkt.seqNum = self.seqNum
                clientFinPkt.fin = 1
                clientFinPkt.ack = 1

                sendingMsg = clientFinPkt.get_tcp_packet()
                self.rawSendSock.sendto(sendingMsg, (self.destIP, self.destPort))
                self.connected = False

                serverFinPkt = TCPPacket("", self.srcIP, self.srcPort, self.destIP, self.destPort)

                startTime = time.time()
                while (time.time() - startTime) < 10:
                    try:
                        serverFinPkt = self.recv_packet()
                    except socket.error as e:
                        return

                    if serverFinPkt.ackNum == (self.seqNum+1) and serverFinPkt.fin == 1:
                        self.seqNum += 1
                        self.ackNum = serverFinPkt.seqNum + 1
                        if serverFinPkt.psh:
                            self.ackNum += len(serverFinPkt.data)

                        # send the final message
                        ackPkt = TCPPacket("", self.srcIP, self.srcPort, self.destIP, self.destPort)
                        ackPkt.seqNum = self.seqNum
                        ackPkt.ackNum = self.ackNum
                        sendingMsg = ackPkt.get_tcp_packet()
                        self.rawSendSock.sendto(sendingMsg, (self.destIP, self.destPort))
                        self.connected = False
                    elif serverFinPkt.rst == 1:
                        self.connected = False                        
                else:
                    print("Disconnection failed.")