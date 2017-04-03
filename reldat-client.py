import socket
import sys
import hashlib
import os
import struct


connection = [0, 0, "", 0] #{client packet num, server packet num, server IP address, connected}


def establishConnection(sock, server, port): #need to make reliable
    global connection
    print "sent syn"

    while not connection[3]:
        try:
            sock.sendto("SYN", (server, port))
            synAck = sock.recv(4096) #message should be syn/ack

            if synAck == "BUSY":
                print "server is busy"
                return False
            if synAck == "SYNACK":
                connection = [0, 0, server, 1]
                print "received synack, sent ack"
                sock.sendto("SYNACK", (server, port))

        except socket.error, msg:
            print "could not connect to address or port"

    print "CONNECTED"


def initfiletransfer(sock, numofpackets, filename, host, port):
    print "initializing file transfer"
    sock.sendto("INITFILETRANSFER_" + filename + "_" + str(numofpackets), (host, port)) #need to make reliable

def resolveResendRequest(fullmes, packets, host, port, sock):
    missingPackets = fullmes.split("_")
    print missingPackets
    try:
        for i in range(1, missingPackets - 1, 1):
            print "resent packet " + str(i)
            sock.sendto(str(i)+"_"+packets[i], (host, port))
    except:
         print "resend error"


def resendAllinAir(inAir, sock, host, port):
    for packet in inAir:
        seqNum = packet[0]
        message = packet[1]
        sock.sendto(str(seqNum)+"_"+message, (host, port))


def main(argv):

    args = len(argv)
    if args < 3:
        return "Input port number and window size"
    host_port = argv[1].split(':')
    host = host_port[0]
    port = int(host_port[1])
    window = int(argv[2])
    server = host_port[0]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packets = []
    print "Connecting to "+str(host)+":"+str(port)
    sock.bind((socket.gethostbyname(socket.gethostname()), port))

    packetsize = 1024
    filename = sys.argv[3]
    f = open(argv[3], "rb")
    f.seek(0,2)
    filesize = f.tell() #get file size
    f.seek(0,0) #reset file position

    print "Filesize: " + str(filesize)

    m = hashlib.md5() #checksummer

    numofpackets = (filesize / packetsize) + 1
    print "NUM OF PACKETS: " + str(numofpackets)

    establishConnection(sock, server, port)
    # while True:
    lastSent = 0;
    lastRec = 0

    l = f.read(packetsize)

    while (l):
        packets.append(l)
        l = f.read(packetsize)

    acked = [0] * numofpackets
    inAir = []
    numberAcked = 0

    initfiletransfer(sock, numofpackets, filename, host, port)

    transferComplete = False

    while not transferComplete:
        print lastRec
        try:
            sock.settimeout(2)
            print lastSent - lastRec
            while lastSent < len(packets) and len(inAir) < window: #len(inAir) used to be lastSent - lastRec
                m.update(str(lastSent)+"_" + packets[lastSent])
                checksum = m.hexdigest()
                print "CHECKSUM: " + str(checksum)
                sendString = str(lastSent)+"_"+packets[lastSent] + "_" + checksum
                print sendString
                sock.sendto(sendString, (host, port))
                inAir.append((lastSent, packets[lastSent]))
                lastSent+=1
            print "WAITING"

            if lastSent >= len(packets):
                sock.sendto("FINTRANSFER", (host, port))

            fullmes = sock.recv(4096)
            mes = fullmes.split('_')

            if "ACK" in mes:
                numberAcked += 1 #keep track of how many things have been acked

                recNum = int(mes[1]) #number
                acked[recNum] = 1 #confirm acked in array
                if recNum - numberAcked > window/2: #we assume we lost half of sent packets, resend
                    "Lost ACK limit reached"
                    resendAllinAir(inAir, sock, host, port)
                inAir.remove((recNum, packets[recNum]))

            if mes[0] == "RESENDREQUEST":
                resolveResendRequest(fullmes, packets, host, port, sock) #fullmes includes missing packet info

            if mes[0] == "TRANSFERCOMPLETE":
                transferComplete = True

        except socket.timeout:
            resendAllinAir(inAir, sock, host, port)
            print "The server has not answered in the last two seconds.\nretrying..."
        except socket.error:
            print "could not connect to address or port"

    #sock.sendto("FINTRANSFER", (host, port))

    print mes
    sock.close()

if __name__ == '__main__': main(sys.argv)
