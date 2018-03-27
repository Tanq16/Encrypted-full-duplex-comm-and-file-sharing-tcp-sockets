import threading
import Crypto
import time
import socket
from Crypto.Cipher import Salsa20
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from os import urandom
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
        global recieved
        global salsakey
        global salsanonce
        while True:
            x = recieved
            if final.is_set():
                break
            salsaenc = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
            salsadec = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
            message = input()
            messagelen = str("%020d"%len(message))
            self.client.send(salsaenc.encrypt(bytes((messagelen + message), 'utf_8')))
            lock.acquire()
            recieved += 1
            lock.release()
            print("---------------", recieved)

class readproc(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client

    def run(self):
        global recieved
        global salsakey
        global salsanonce
        while True:
            x = recieved
            salsaenc = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
            salsadec = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
            mlen = int(str(salsadec.decrypt(self.client.recv(20)), 'utf_8'))
            response = str(salsadec.decrypt(self.client.recv(mlen)), 'utf_8')
            lock.acquire()
            recieved += 1
            lock.release()
            if not response == "BYE!":
                print(response)
            if response == "BYE!":
                final.set()
                break
            print("---------------", recieved)

clientpubkey = RSA.import_key(sock.recv(2048))

salsakey = urandom(32)
salsanonce = urandom(1)

skeyenc = PKCS1_OAEP.new(clientpubkey)
sock.send(skeyenc.encrypt(salsakey))
time.sleep(1)
sock.send(skeyenc.encrypt(salsanonce))

recieved = 0
print("convo starts -------------------------------------------")

final = threading.Event()
lock = threading.Lock()
ssread = readproc(sock)
sswrite = writeproc(sock)
sswrite.setDaemon(True)
sswrite.start()
ssread.start()
ssread.join()
sock.close()
ss.close()
