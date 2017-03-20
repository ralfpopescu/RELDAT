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



    # args = len(argv)
    # if args < 3:
    #     return "Input port number and window size"
    # host_port = argv[1].split(':')
    # host = host_port[0]
    # port = int(host_port[1])
    # window = int(argv[2])
    # message = "hello"
    # host = socket.gethostbyname(socket.gethostname())
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # packets = "Hello my name is joe and i live in a button factory i have a mom house and a family".split(' ')
    # print "Connecting to "+str(host)+":"+str(port)
    # # while True:
    # lastSent = 0;
    # lastRec = 0
    # while lastRec < len(packets):
    #     try:
    #         #send text
    #         sock.settimeout(2)
    #         print lastSent - lastRec
    #         while lastSent < len(packets) and lastSent - lastRec < window:
    #             print packets[lastSent]
    #             sock.sendto(str(lastSent)+"_"+packets[lastSent], (host, port))
    #             lastSent+=1
    #         print "WAITING"
    #         mes = sock.recv(4096).split('_')
    #         print mes
    #         lastRec = int(mes[0])
    #     except socket.timeout:
    #         print "The server has not answered in the last two seconds.\nretrying..."
    #     except socket.error:
    #         print "could not connect to address or port"
    #
    #
    # print mes
    # sock.close()

if __name__ == '__main__': main(sys.argv)