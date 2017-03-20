import socket
import sys


def main(argv):
    args = len(argv)
    if args < 3:
        return "Input port number and window size"
    port = int(argv[1])
    window = argv[2]
    host = socket.gethostbyname(socket.gethostname())
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rec_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    send_sock.bind((host, port))
    print "listening for connection on "+str(host)+":"+str(port)
    while True:

        #recieve message and address from client
        mes, addr = send_sock.recvfrom(1024)
        # time.sleep(10)
        mes = mes.split('_')
        send_sock.sendto(mes[0]+"_Got "+mes[1],addr)
if __name__ == '__main__': main(sys.argv)
