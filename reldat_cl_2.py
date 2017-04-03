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


def terminateConnection(sock, server, port):
    global connection
    print "terminating connection"

    while connection[3]:
        try:
            sock.sendto("TERMINATECONNECTION", (server, port))
            finAck = sock.recv(4096) #message should be syn/ack

            if synAck == "FINACK":
                connection = [0, 0, "", 0]
                print "received finack, sent ack"
                sock.sendto("FINACK", (server, port))

        except socket.error, msg:
            print "could not connect to address or port"

    print "DISCONNECTED"

def initfiletransfer(sock, numofpackets, filename, host, port):
    wait = 0
    while wait == 0:
        try:
            print "initializing file transfer"
            sock.sendto("INITFILETRANSFER_" + filename + "_" + str(numofpackets), (host, port)) #need to make reliable
            wait = sock.recv(4096)
        except:
            print "trying again"

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

def send(sock, host, port, packets, window, m):
    lastSent = 0
    lastRec = 0
    highestAck = 0
    transferComplete = False
    dup = 0

    while not transferComplete:
        print highestAck
        try:
            print lastSent - highestAck
            while lastSent < len(packets) and lastSent - highestAck < window: #len(inAir) used to be lastSent - lastRec
                fullmes = str(lastSent)+"_" + packets[lastSent]
                # print "FULL CHECKSUM CALC"+fullmes
                m = hashlib.md5()
                m.update(fullmes)
                checksum = m.hexdigest()
                print "CHECKSUM: " + str(checksum)
                m = hashlib.md5()
                m.update(fullmes)
                checksum = m.hexdigest()
                print "CHECKSUM: " + str(checksum)
                sendString = str(lastSent)+"_" + packets[lastSent] + "_" + str(checksum)
                print sendString
                sock.sendto(sendString, (host, port))
                lastSent+=1
            sock.settimeout(2)
            print "WAITING"

            if highestAck >= len(packets) - 1:
                sock.sendto("FINTRANSFER", (host, port))

            fullmes = sock.recv(4096)
            mes = fullmes.split('_')

            if mes[0] == 'ACK':
                print "WAITING FOR " + mes[1]
                if highestAck == int(mes[1]):
                    dup += 1
                if dup == 3:
                    lastSent = highestAck
                highestAck = int(mes[1])
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

def recieve(sock,host,m,packets):
    filereceiving = [0]*len(packets)
    ind = 0
    while True:
        #recieve message and address from client
        mes, addr = sock.recvfrom(1200)

        # if connection[3] and addr is not connection[2]: #maintain connection with only one address
        #     sock.sendto("BUSY", addr)

        mes = mes.split('_')
        checksum = mes[-1]
        fullmes = mes[:]
        fullmes = "_".join(fullmes[:-1]) #just in case there are other underscores in the message
        if(mes[0] == "FINTRANSFER"):

            final = ''.join(filereceiving)
            sock.sendto('TRANSFERCOMPLETE', addr)
            return final

        else:
            m = hashlib.md5()
            m.update(fullmes)
            calculatedChecksum = m.hexdigest()
            checksum = mes[-1]
            print checksum
            print calculatedChecksum

            if checksum == calculatedChecksum:
                print "checksum matches"
                print int(mes[0])
                filereceiving[int(mes[0])] = fullmes
                while ind < len(filereceiving) and filereceiving[ind] != 0:
                    # print filereceiving[ind]
                    ind += 1
                sock.sendto("ACK_"+str(ind)+"_Got "+mes[1],addr)
                print "ACK'ed " + str(mes[0])
            else:
                print "corrupted packet"
                sock.sendto("ACK_"+str(ind)+"_Got" + str(mes[0]), addr)
def main(argv):
    # Connection Setup information
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
    # sock.bind((socket.gethostbyname(socket.gethostname()), port))
    establishConnection(sock, server, port)




    #command loop
    disconnect = False
    while not disconnect:
        command = raw_input("Please enter a command, 'transform <filename>' or 'disconnect': ")
        command = command.split(' ')

        #if transform file
        if len(command) == 2:

            # Begin Read File information #
            packetsize = 1000
            filename = command[1]
            f = open(filename, "rb")
            f.seek(0,2)
            filesize = f.tell() #get file size
            f.seek(0,0) #reset file position
            print "Filesize: " + str(filesize)
            m = hashlib.md5() #checksummer
            numofpackets = (filesize / packetsize) + 1
            print "NUM OF PACKETS: " + str(numofpackets)
            # while True:
            l = f.read(packetsize)
            while (l):
                packets.append(l)
                l = f.read(packetsize)

            # End read file information #

            # acked = [0] * numofpackets

            initfiletransfer(sock, numofpackets, filename, host, port)
            send(sock, host, port, packets, window, m)
            transformed = recieve(sock, host, m,packets)
            with open(filename+"_transformed.txt",'w') as open_file:
                open_file.write(transformed)
                open_file.close()
        #else disconnect
        elif command[0] == 'disconnect':
            disconnect = True
            terminateConnection(sock, server, port)
            #TODO Connection Breakdown

        #sock.sendto("FINTRANSFER", (host, port))

    sock.close()

if __name__ == '__main__': main(sys.argv)
