import sys
import socket
import random
import hashlib
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
                    if mes == "SYNACK" and addr == connection[2]:
                        ackreceived = True
        except socket.error, msg:
            print "could not connect to address or port"

    print "CONNECTED"


def resendRequest(filereceiving, host, port, sock):

    print "creating resend request"
    resendString = "RESENDREQUEST_"

    for i in range (0, len(filereceiving), 1):
        if filereceiving[i] == 0:
            print "missing packet: " + str(i)
            resendString = resendString + "_" + str(i)

    if resendString == "RESENDREQUEST_":
        return True

    print len(resendString.split("_"))

    sock.sendto(resendString, (host, port))

    return False



def main(argv):

    global connection

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
    m = hashlib.md5() #checksummer

    filename = "none" #declare outside of scope
    filesize = 0
    transferringFile = False #make sure old FINTRANSFERS don't stop new transfers

    print "Server started listening at %s port %d" % (host,port) #we need beginning and end file indicators
    while True:

        print counter
        counter += 1
        #recieve message and address from client
        mes, addr = sock.recvfrom(1200)

        # if connection[3] and addr is not connection[2]: #maintain connection with only one address
        #     sock.sendto("BUSY", addr)

        mes = mes.split('_')
        checksum = mes[-1]
        fullmes = mes[:]
        fullmes = "_".join(fullmes[:-1]) #just in case there are other underscores in the message


        if(mes[0] == "INITFILETRANSFER") and not transferringFile:
            print "initializing file transfer of " + mes[1]
            transferringFile = True
            filename = mes[1].split(".") #takes off .txt ending
            filesize = mes[2]
            out_file = open(filename[0] + "-received.txt", "wb")
            filereceiving = [0] * int(mes[2]) # we initialize an array of zeroes representing each packet indexed by sequence number

        elif(mes[0] == "FINTRANSFER") and transferringFile:
            print "all packets attempted transfer"
            allReceived = False
            while not allReceived:
                allReceived = resendRequest(filereceiving, host, port, sock)

            send_sock.sendto("TRANSFERCOMPLETE",addr)

            for piece in filereceiving:
                #print piece
                out_file.write(piece)
            transferringFile = False
            connection = [0, 0, "", 0]
            waitforconnection(sock)

        elif mes[0] == "SYN" or mes[0] == "SYNACK":
            print "picked up old syn packet"

        else:
            m.update(fullmes)
            calculatedChecksum = m.hexdigest()

            if checksum == calculatedChecksum:
                print "checksum matches"
                send_sock.sendto("ACK_"+mes[0]+"_Got "+mes[1],addr)
                print "ACK'ed " + str(mes[0])
                filereceiving[int(mes[0])] = fullmes
            else:
                print "bad packet"
                send_sock.sendto("RESENDREQUEST_" + str(mes[0]), addr)


if __name__ == '__main__': print(main(sys.argv))