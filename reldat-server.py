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

        if(mes[0] == "INIT_FILETRANSFER"):
            print "initializing file transfer of" + mes[1]
            filename = mes[1].split(".") #takes off txt
            filesize = mes[2]
            out_file = open(filename[0] + "-received.txt", "wb")
            filereceiving = [0] * mes[2] # we initialize an array of zeroes indexed by sequence number

        if(mes[0] == "FIN_TRANSFER"):
            for piece in filereceiving:
                out_file.write(mes[1])


        else:
            send_sock.sendto("ACK_"+mes[0]+"_Got "+mes[1],addr)
            filereceiving[mes[0]] = mes[1]









if __name__ == '__main__': print(main(sys.argv))