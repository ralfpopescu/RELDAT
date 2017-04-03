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
            mes, addr = sock.recvfrom(1200)
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
def send(sock, addr, packets, window, m):
    lastSent = 0
    lastRec = 0
    highestAck = 0
    transferComplete = False
    dup = 0

    while not transferComplete:
        print "highest ack"+str(highestAck)
        try:
            print lastSent - highestAck
            while lastSent < len(packets) and lastSent - highestAck < window: #len(inAir) used to be lastSent - lastRec
                m = hashlib.md5()
                m.update(str(lastSent)+"_" + packets[lastSent])
                checksum = m.hexdigest()
                print "CHECKSUM: " + str(checksum)
                sendString = str(lastSent)+"_"+packets[lastSent] + "_" + checksum
                print sendString
                sock.sendto(sendString, addr)
                lastSent+=1
            sock.settimeout(2)
            print "WAITING"

            if highestAck >= len(packets) - 1:
                sock.sendto("FINTRANSFER", addr)

            fullmes = sock.recv(4096)
            mes = fullmes.split('_')

            if mes[0] == 'ACK':
                print "WAITING FOR " + mes[1]
                if highestAck == int(mes[1]):
                    dup += 1
                if dup == 3:
                    lastSent = highestAck
                highestAck = int(mes[1])
                recNum = int(mes[1]) #number
                # acked[recNum] = 1 #confirm acked in array
                # if recNum - numberAcked > window/2: #we assume we lost half of sent packets, resend
                #     "Lost ACK limit reached"
                #     resendAllinAir(inAir, sock, host, port)
                # inAir.remove((recNum, packets[recNum]))

            if mes[0] == "RESENDREQUEST":
                resolveResendRequest(fullmes, packets, host, port, sock) #fullmes includes missing packet info

            if mes[0] == "TRANSFERCOMPLETE":
                transferComplete = True

        except socket.timeout:
            # resendAllinAir(inAir, sock, host, port)
            lastSent = highestAck
            print "The server has not answered in the last two seconds.\nretrying..."
        except socket.error:
            print "could not connect to address or port"



def main(argv):

    global connection

    numArgs = len(argv)
    port = int(argv[1])
    window = argv[2]
    host = socket.gethostbyname(socket.gethostname())
    # host = "127.0.0.1"
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

    acks = []
    filereceiving = []
    m = hashlib.md5() #checksummer

    filename = "none" #declare outside of scope
    filesize = 0
    transferringFile = False #make sure old FINTRANSFERS don't stop new transfers
    fileID = 0 #simple counter that prevents old packets from interfering

    print "Server started listening at %s port %d" % (host,port) #we need beginning and end file indicators
    ind = 0
    while True:
        try:
            print counter
            counter += 1
            #recieve message and address from client
            sock.settimeout(10)
            mes, addr = sock.recvfrom(1200)

            # if connection[3] and addr is not connection[2]: #maintain connection with only one address
            #     sock.sendto("BUSY", addr)

            mes = mes.split('_')
            checksum = str(mes[-1])
            fullmes = mes[:-1]
            fullmes = "_".join(fullmes) #just in case there are other underscores in the message
            # print "FULL CHECKSUM CALC:"+fullmes
            m.update(fullmes)
            print "CHECKSUM:" + str(m.hexdigest())
            print "packet sum: " + str(checksum)

            if(mes[0] == "INITFILETRANSFER") and not transferringFile:
                print "initializing file transfer of " + mes[1]
                transferringFile = True
                filename = mes[1].split(".") #takes off .txt ending
                filesize = mes[2]
                filereceiving = [0] * int(mes[2]) # we initialize an array of zeroes representing each packet indexed by sequence number
                acks = [0] * int(mes[2])
                sock.sendto('ACK', addr)

            elif(mes[0] == "FINTRANSFER") and transferringFile:
                print "all packets attempted transfer"
                allReceived = False
                transferringFile = False

                send_sock.sendto("TRANSFERCOMPLETE",addr)
                # print filereceiving
                newPackets = [x.upper() for x in filereceiving]
                final = ''.join(filereceiving)
                # for pack in newPackets:
                #     print pack
                send(sock, addr, newPackets, window, m)
                # for piece in filereceiving:
                # print final
                # with open(filename[0]+"-recieved.txt",'w') as out_file:
                #     out_file.write(final)
                #     out_file.close()
                #reset server for new file
                connection = [0, 0, "", 0]
                filereceiving = []
                print "finished transfer"
                # waitforconnection(sock)
                counter = 0
                mes = None

            elif mes[0] == "SYN" or mes[0] == "SYNACK" or (mes[0] == "FINTRANSFER" and not transferringFile) or (mes[0] == "INITFILETRANSFER" and transferringFile):
                print "picked up garbage packet"

            else:
                # print fullmes
                m = hashlib.md5()
                m.update(fullmes)
                calculatedChecksum = m.hexdigest()
                checksum = mes[-1]

                print checksum
                print calculatedChecksum


                if checksum == calculatedChecksum:
                    print "checksum matches"
                    # print mes
                    print "len file recieving:" +str(len(filereceiving))
                    filereceiving[int(mes[0])] = fullmes
                    while ind < len(filereceiving) and filereceiving[ind] != 0:
                        # print filereceiving[ind]
                        ind += 1
                    send_sock.sendto("ACK_"+str(ind)+"_Got "+mes[1],addr)
                    print "ACK'ed " + str(mes[0])
                else:
                    print "corrupted packet"
                    send_sock.sendto("ACK_"+str(ind)+"_Got" + str(mes[0]), addr)
        except:
            print "Retrying connection"


if __name__ == '__main__': print(main(sys.argv))
