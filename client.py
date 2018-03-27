import threading
import Crypto
import time
import socket
from Crypto.Cipher import Salsa20
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from os import urandom

s = socket.socket()
s.connect(("localhost", 12345))

class writeproc(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def run(self):
        global recieved
        global salsakey
        global salsanonce
        while True:
            x = recieved
            message = input()
            messagelen = str("%020d"%len(message))
            salsaenc = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
            salsadec = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
            self.server.send(salsaenc.encrypt(bytes((messagelen + message), "utf_8")))
            lock.acquire()
            recieved += 1
            lock.release()
            if message == "BYE!":
                final.set()
                break
            print("---------------", recieved)

class readproc(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

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
            mlen = int(str(salsadec.decrypt(self.server.recv(20)), 'utf_8'))
            response = str(salsadec.decrypt(self.server.recv(mlen)), 'utf_8')
            lock.acquire()
            recieved += 1
            lock.release()
            print(response)
            print("---------------", recieved)

rsa = RSA.generate(1024)
pubkey = rsa.publickey()
prikey = rsa
s.send(pubkey.exportKey())

skeydec = PKCS1_OAEP.new(prikey)

salsakey = skeydec.decrypt(s.recv(2048))
time.sleep(0.5)
salsanonce = skeydec.decrypt(s.recv(2048))

recieved = 0
print("convo starts -------------------------------------------")

final = threading.Event()
lock = threading.Lock()
cwrite = writeproc(s)
cread = readproc(s)
cwrite.start()
cread.setDaemon(True)
cread.start()
cwrite.join()
s.close()
