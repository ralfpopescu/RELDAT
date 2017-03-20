import sys
import socket
import time

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
    port = -1
    #host = socket.gethostbyname(socket.gethostname())
    host = "127.0.0.1"

    if numArgs == 1:
        return "port number and spam words file required"
    elif numArgs == 2:
        return "missing either port number or spam words file"
    else:
        port = int(argv[1])
        windowSize = argv[2]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    print host
    print port

    waitforconnection(sock)

    print "Server started listening at %s port %d" % (host,port)
    while True:

        #recieve message and address from client
        mes, addr = sock.recvfrom(1024)

        if connection[3] and addr is not connection[2]: #maintain connection with only one address
            sock.sendto("BUSY", addr)

        # time.sleep(10)
        mes = mes[:-1]
        mes = mes.lower()


        #reply to client
        sock.sendto("reply", addr)



if __name__ == '__main__': print(main(sys.argv))