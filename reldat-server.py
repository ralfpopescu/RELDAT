import sys
import socket
import time
from struct import *

connection = [0, 0, "", 0] #{client packet num, server packet num, client IP address, connected}

def waitforconnection(sock):
    global connection
    while not connection[3]:
        try:
            print "trying to connect"
            mes, addr = sock.recvfrom(1024)
            print mes
            if mes == "SYN":
                print "waiting for syn"
                connection = [0, 0, addr, 1]
                sock.sendto("SYNACK", connection[2])
                ackreceived = False
                while not ackreceived:
                    mes, addr = sock.recvfrom(1024)
                    if mes == "ACK" and addr == connection[2]:
                        ackreceived = True
        except socket.error, msg:
            print "could not connect to address or port"

    print "CONNECTED"

def checksum():
    print "ay"


def resendRequest(filereceiving, host, port, sock):
    resendString = "RESENDREQUEST_"

    for i in range (0, len(filereceiving) - 1, 1):
        if filereceiving[i] == 0:
            resendString = resendString + "_" + str(i)

    if len(resendString.split("_")) == 1:
        return True

    sock.sendto(resendString, (host, port))

    return False



def main(argv):

    numArgs = len(argv)
    port = int(argv[1])
    window = argv[2]
    #host = socket.gethostbyname(socket.gethostname())
    host = "127.0.0.1"
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rec_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print host
    print port

    if numArgs == 1:
        return "port number and spam words file required"
    elif numArgs == 2:
        return "missing either port number or spam words file"
    else:
        port = int(argv[1])
        windowSize = argv[2]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    waitforconnection(sock)

    counter = 0

    filereceiving = []

    filename = "none" #declare outside of scope
    filesize = 0

    print "Server started listening at %s port %d" % (host,port) #we need beginning and end file indicators
    while True:

        print counter
        counter += 1
        #recieve message and address from client
        mes, addr = sock.recvfrom(1024)

        # if connection[3] and addr is not connection[2]: #maintain connection with only one address
        #     sock.sendto("BUSY", addr)

        mes = mes.split('_')

        if(mes[0] == "INITFILETRANSFER"):
            print "initializing file transfer of " + mes[1]
            filename = mes[1].split(".") #takes off .txt ending
            filesize = mes[2]
            out_file = open(filename[0] + "-received.txt", "wb")
            filereceiving = [0] * int(mes[2]) # we initialize an array of zeroes representing each packet indexed by sequence number

        elif(mes[0] == "FINTRANSFER"):
            print "all packets attempted transfer"
            for piece in filereceiving:
                out_file.write(piece)

        else:
            send_sock.sendto("ACK_"+mes[0]+"_Got "+mes[1],addr)
            print "ACK'ed " + str(mes[0])
            filereceiving[int(mes[0])] = mes[1]









if __name__ == '__main__': print(main(sys.argv))