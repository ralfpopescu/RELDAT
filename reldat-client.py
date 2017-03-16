import socket
import sys

connection = [0, 0, "", 0] #{client packet num, server packet num, server IP address, connected}

def establishConnection(socket, server, port):
    global connection
    print "sent syn"

    while not connection[3]:
        try:
            socket.sendto("SYN", (server, port))
            synAck = socket.recv(4096) #message should be syn/ack

            if synAck == "BUSY":
                print "server is busy"
                return False
            if synAck == "SYNACK":
                connection = [0, 0, server, 1]
                print "received synack, sent ack"
                socket.sendto("ACK", (server, port))

        except socket.error, msg:
            print "could not connect to address or port"

    print "CONNECTED"

def sendMessage():
    global packetnumber
    packetnumber += 1

def main(argv):
    numArgs = len(argv)

    port = -1

    server = argv[1]
    host = socket.gethostbyname(socket.gethostname())
    port = int(argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    establishConnection(sock, server, port)

    sock.close()

if __name__ == '__main__': main(sys.argv)