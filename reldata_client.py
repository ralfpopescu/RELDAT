import socket
import sys
import time
import Queue as queue


def main(argv):
    args = len(argv)
    if args < 3:
        return "Input port number and window size"
    host_port = argv[1].split(':')
    host = host_port[0]
    port = int(host_port[1])
    window = int(argv[2])
    sentQueue = queue.Queue(maxsize = window)
    connectionEstablish = ['0_1_0_', '1_0_1_',]
    count = 2
    messageQueue = queue.Queue()
    host = socket.gethostbyname(socket.gethostname())
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packets = "Hello my name is joe and i live in a button factory i have a mom house and a family".split(' ')
    print "Connecting to "+str(host)+":"+str(port)
    for pack in packets:
        messageQueue.put(str(count%window)+"_0_0_"+pack)
        count += 1
    while not messageQueue.empty():
        print messageQueue.get()
    lastSent = 0;
    lastRec = 0
    while lastRec < len(packets):
        try:
            #send text
            sock.settimeout(2)
            print lastSent - lastRec
            while lastSent < len(packets) and lastSent - lastRec < window:
                print packets[lastSent]
                sock.sendto(str(lastSent)+"_"+packets[lastSent], (host, port))
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
