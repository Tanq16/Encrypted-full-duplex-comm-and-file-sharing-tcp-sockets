import threading
import socket
import time

ss = socket.socket()
ss.bind(("localhost", 12345))
ss.listen(10)

sock, addr = ss.accept()  # NOTE: Comment for multithreaded

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
                self.client.send((str("%020d"%len("CONNECTION RESET")) + "CONNECTION RESET").encode('utf_8'))
                print("client now offline -- press enter to exit")
                break

# class serverproc(threading.Thread):
#     final = threading.Event()
#
#     def __init__(self, server):
#         threading.Thread.__init__(self)
#         self.server = server
#
#     def run(self):
#         while True:
#             sock, add = self.server.accept()
#             ssread = readproc(sock)
#             sswrite = writeproc(sock)
#             sswrite.start()
#             ssread.start()
#             sswrite.join()
#             ssread.join()
#             sock.close()
#             ss.close()

final = threading.Event()
ssread = readproc(sock)
sswrite = writeproc(sock)
sswrite.start()
ssread.start()
sswrite.join()
ssread.join()
sock.close()
ss.close()
# serverhandler = serverproc(ss)
# serverhandler.start()
# serverhandler.join()
