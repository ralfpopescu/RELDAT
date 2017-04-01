import socket
import sys
import os
import struct


connection = [0, 0, "", 0] #{client packet num, server packet num, server IP address, connected}


def establishConnection(sock, server, port):
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
                sock.sendto("ACK", (server, port))

        except socket.error, msg:
            print "could not connect to address or port"

    print "CONNECTED"


def packetize(array, packetsize):
    packets = []
    for i in range(0, len(array), packetsize):
        packets.append(array[i:i + packetsize])
    return packets


def initfiletransfer(sock, numofpackets, filename, host, port):
    print "initializing file transfer"
    sock.sendto("INITFILETRANSFER_" + filename + "_" + str(numofpackets), (host, port))

def resolveResendRequest(fullmes, packets, host, port, sock):
    missingPackets = fullmes.split("_")
    try:
        for i in range(1, missingPackets - 1, 1):
            sock.sendto(str(i)+"_"+packets[i], (host, port))
    except:
         print "resend error"


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

    packetsize = 1000
    filename = sys.argv[3]
    f = open(argv[3], "rb")
    f.seek(0,2)
    filesize = f.tell()
    f.seek(0,0) #reset file

    print filesize

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

    acked = []
    inAir = []

    initfiletransfer(sock, numofpackets, filename, host, port)

    allPacketsReceived = False

    while lastRec < numofpackets: #we need to detect duplicate and lost packets
        try:
            #send text
            sock.settimeout(2)
            print lastSent - lastRec
            while lastSent < len(packets) and len(inAir) < window: #len(inAir) used to be lastSent - lastRec
                sock.sendto(str(lastSent)+"_"+packets[lastSent], (host, port))
                inAir.append((lastSent, packets[lastSent]))
                lastSent+=1
            print "WAITING"
            fullmes = sock.recv(4096)
            mes = fullmes.split('_')
            print mes

            if mes[0] == "ACK":
                lastRec = int(mes[1])
                inAir.remove((lastRec, packets[lastRec]))

            if mes[0] == "RESENDREQUEST":
                resolveResendRequest(fullmes, packets, host, port, sock)

        except socket.timeout:
            print "The server has not answered in the last two seconds.\nretrying..."
        except socket.error:
            print "could not connect to address or port"

    sock.sendto("FINTRANSFER", (host, port))
    print mes
    sock.close()

if __name__ == '__main__': main(sys.argv)