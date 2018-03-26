import threading
import socket
import time

s = socket.socket()
s.connect(("localhost", 12345))

class writeproc(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def run(self):
        while True:
            message = input()
            messagelen = str("%020d"%len(message))
            self.server.send((messagelen + message).encode('utf_8'))
            if message == "BYE!":
                final.set()
                break

class readproc(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def run(self):
        while True:
            if final.is_set():
                break
            mlen = int(self.server.recv(20).decode('utf_8'))
            response = self.server.recv(mlen).decode('utf_8')
            print(response)

final = threading.Event()
cwrite = writeproc(s)
cread = readproc(s)
cwrite.start()
cread.setDaemon(True)
cread.start()
cwrite.join()
s.close()
