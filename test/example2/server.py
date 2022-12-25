import socket
import select
from threading import Thread


class ClientThread(Thread):
    def __init__(self,ip,port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print (port)


def run(self):
    while True:
        data = conn.recv(2048)
        if not data: break
        print (data)
        conn.send("<Server> Got your data. Send some more\n")

TCP_IP = '127.0.0.1'
TCP_PORT = 62
BUFFER_SIZE = 1024  # Normally 1024
threads = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("127.0.0.1", 5000))
server_socket.listen(10)

read_sockets, write_sockets, error_sockets = select.select([server_socket], [], [])

while True:
    print ("Waiting for incoming connections...")
    for sock in read_sockets:
        (conn, (ip,port)) = server_socket.accept()
        newthread = ClientThread(ip,port)
        newthread.start()
        threads.append(newthread)

for t in threads:
    t.join()
