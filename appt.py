import threading
import Crypto
import time
import socket
from Crypto.Cipher import Salsa20
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from os import urandom
import sys
import os

what = "server"
filetransfer = False
filewrite = False
if len(sys.argv) == 3:
    if(sys.argv[1] == '-l'):
        port = int(sys.argv[2])
    else:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        what = "client"
elif len(sys.argv) == 5:
    if(sys.argv[3] == "-fr" and sys.argv[1] == "-l"):
        filetransfer = True
        filewrite = True
        port = int(sys.argv[2])
        filename = sys.argv[4]
    elif(sys.argv[3] == "-fs" and sys.argv[1] == "-l"):
        filetransfer = True
        port = int(sys.argv[2])
        filename = sys.argv[4]
    elif(sys.argv[3] == "-fr" and sys.argv[1] != "-l"):
        filetransfer = True
        filewrite = True
        what = "client"
        ip = sys.argv[1]
        port = int(sys.argv[2])
        filename = sys.argv[4]
    elif(sys.argv[3] == "-fs" and sys.argv[1] != "-l"):
        filetransfer = True
        what = "client"
        ip = sys.argv[1]
        port = int(sys.argv[2])
        filename = sys.argv[4]
else:
    print("Usage for server: python3 appt.py -l <port>\nUsage for client: python3 appt.py <ip> <port>")
    print("\nFile transfer usage:")
    print("Usage for server: python3 appt.py -l <port> [-fr|-fs] <filename>\nUsage for client: python3 appt.py <ip> <port> [-fr|-fs] <filename>")
    print("-fr : receive file\n-fs : send file")
    sys.exit()

print("-"*80)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if what == "server" and filetransfer == False:
    ss = socket.socket()
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ss.bind(("localhost", port))
    ss.listen(10)

    print("-"*80)

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
                # print("---------------", recieved)

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
                # print("---------------", recieved)

    clientpubkey = RSA.import_key(sock.recv(2048))

    salsakey = urandom(32)
    salsanonce = urandom(1)

    skeyenc = PKCS1_OAEP.new(clientpubkey)
    sock.send(skeyenc.encrypt(salsakey))
    time.sleep(1)
    sock.send(skeyenc.encrypt(salsanonce))

    recieved = 0
    for i in range(5):
        time.sleep(0.1)
    print()
    os.system('clear')
    print("%s connected."%addr[0])
    print("-"*80)

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

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

elif what == "client" and filetransfer == False:
    s = socket.socket()
    s.connect((ip, port))

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
                # print("---------------", recieved)

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
                # print("---------------", recieved)

    rsa = RSA.generate(1024)
    pubkey = rsa.publickey()
    prikey = rsa
    s.send(pubkey.exportKey())

    skeydec = PKCS1_OAEP.new(prikey)

    salsakey = skeydec.decrypt(s.recv(2048))
    time.sleep(0.5)
    salsanonce = skeydec.decrypt(s.recv(2048))

    recieved = 0
    for i in range(5):
        time.sleep(0.1)
    print()
    os.system('clear')
    print("CONNECTED TO %s"%ip)
    print("Type 'BYE!' to end connection\n" + "-"*80)

    final = threading.Event()
    lock = threading.Lock()
    cwrite = writeproc(s)
    cread = readproc(s)
    cwrite.start()
    cread.setDaemon(True)
    cread.start()
    cwrite.join()
    s.close()

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

elif what == "client" and filetransfer == True:
    s = socket.socket()
    s.connect((ip, port))

    rsa = RSA.generate(1024)
    pubkey = rsa.publickey()
    prikey = rsa
    s.send(pubkey.exportKey())
    skeydec = PKCS1_OAEP.new(prikey)
    salsakey = skeydec.decrypt(s.recv(2048))
    time.sleep(0.5)
    salsanonce = skeydec.decrypt(s.recv(2048))

    x = 123456
    print()

    if(filewrite == True):
        salsaenc = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
        salsadec = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
        z = b''
        while True:
            y = s.recv(1024)
            if not y: break
            z += y
        response = str(salsadec.decrypt(z), 'utf_8')
        with open (filename, 'w') as myfile:
            myfile.write(response)
        s.close()

    else:
        with open (filename, "r") as myfile:
            message = myfile.read()
        salsaenc = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
        salsadec = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
        s.send(salsaenc.encrypt(bytes(message, "utf_8")))
        s.close()

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

elif what == "server" and filetransfer == True:
    ss = socket.socket()
    ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ss.bind(("localhost", port))
    ss.listen()
    sock, addr = ss.accept()

    clientpubkey = RSA.import_key(sock.recv(2048))
    salsakey = urandom(32)
    salsanonce = urandom(1)
    skeyenc = PKCS1_OAEP.new(clientpubkey)
    sock.send(skeyenc.encrypt(salsakey))
    time.sleep(1)
    sock.send(skeyenc.encrypt(salsanonce))

    x = 123456
    print()

    if(filewrite == True):
        salsaenc = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
        salsadec = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
        z = b''
        while True:
            y = sock.recv(1024)
            if not y: break
            z += y
        response = str(salsadec.decrypt(z), 'utf_8')
        with open (filename, 'w') as myfile:
            myfile.write(response)
        sock.close()
        ss.close()

    else:
        with open (filename, "r") as myfile:
            message = myfile.read()
        salsaenc = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
        salsadec = Salsa20.new(salsakey, nonce=(salsanonce + bytes(str("%07d"%x), "utf_8")))
        sock.send(salsaenc.encrypt(bytes(message, "utf_8")))
        sock.close()
        ss.close()
