import threading
import socket
import time
import sys

ss = socket.socket()
ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ss.bind(("localhost", 12345))
ss.listen(10)

sock, addr = ss.accept()

class writeproc(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        while True:
            if final.is_set():
                break
            message = input()
            messagelen = str("%020d"%len(message))
            self.client.send((messagelen + message).encode('utf_8'))

class readproc(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        while True:
            mlen = int(self.client.recv(20).decode('utf_8'))
            response = self.client.recv(mlen).decode('utf_8')
            if not response == "BYE!":
                print(response)
            if response == "BYE!":
                final.set()
                break

final = threading.Event()
ssread = readproc(sock)
sswrite = writeproc(sock)
sswrite.setDaemon(True)
sswrite.start()
ssread.start()
ssread.join()
sock.close()
ss.close()
