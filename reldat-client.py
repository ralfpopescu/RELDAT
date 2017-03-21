import socket
import sys
import os


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


def initfiletransfer():
    print "initializing file transfer"

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
    packets = "Hello my name is joe and i live in a button factory i have a mom house and a family".split(' ')
    print "Connecting to "+str(host)+":"+str(port)
    sock.bind((socket.gethostbyname(socket.gethostname()), port))

    packetsize = 1000
    f = open(argv[3], "rb")
    f.seek(0,2)
    filesize = f.tell()
    f.seek(0,0) #reset file

    print filesize

    numofpackets = (filesize / packetsize) + 1
    print "NUM OF PACKETS: " + str(numofpackets)

    # packets = []
    # with open(argv[3], "rb") as in_file:
    #     while True:
    #         piece = in_file.read(packetsize)
    #
    #         if piece == "":
    #             break # end of file
    #
    #         packets.append(piece)



    establishConnection(sock, server, port)
    # while True:
    lastSent = 0;
    lastRec = 0

    packets = []
    l = f.read(packetsize)
    while (l):
        packets.append(l)
        l = f.read(packetsize)


    while lastRec < numofpackets: #we need to detect duplicate and lost packets
        try:
            #send text
            sock.settimeout(2)
            print lastSent - lastRec
            while lastSent < len(packets) and lastSent - lastRec < window:
                sock.sendto(packets[lastSent], (host, port))
                lastSent+=1
            print "WAITING"
            mes = sock.recv(4096).split('_')
            print mes
            lastRec = int(mes[0])
        except socket.timeout:
            print "The server has not answered in the last two seconds.\nretrying..."
        except socket.error:
            print "could not connect to address or port"


    print mes
    sock.close()

if __name__ == '__main__': main(sys.argv)