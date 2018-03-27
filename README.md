# Python Sockets - Full Duplex communication - Client Server

---

This is an implementation of client server architecture that uses sockets for communication. It tries to replicate the working of `netcat` to some extent. Full duplex communication allows for simultaneous read and write (exchange of messages) for both the client as well as server. The addition is the encryption mechanism. RSA key exchange is used for exchanging key and 1 byte of nonce for Salsa20 stream cipher.

No bound on length of messages (technically, the bound is the length for which the value can fit in 20 digits). The length is automatically prepended to the message. The receiver therefore reads the message length and then reads that many bytes to receive the message. The bound on number of messages is however about the number which can fit in 7 digits (in decimal).

Only client can exit the connection (stereotypical for the server to reply to each request by until it disconnects) by sending a message "BYE!". 

## Run the code

1. To run on localhost i.e., listen and connect on local machine, simply clone and run the two python files on separate terminals.
2. To run between two separate systems, give the appropriate IP address and port as arguments and deploy on the machines (run on terminal).
3. The **--------\<number\>** is a part of the nonce being printed which is commented out. 
```python
print("---------------", recieved)
```

---

###### Note
The above was tested and written in Python 3.5.2. Should also work with most other versions, however socket implementation is different on 2.7 and few others (specifically byte type behaviour as well as RSA module and Salsa20 module behaviour, so may or may not work as intended, you are free to test it out). Recommended Python3.
