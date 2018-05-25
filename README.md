# Python Sockets - Full Duplex communication - Client Server

---

This is an implementation of a communications suite that uses python sockets. It aims at replicating some features of `netcat`. Full duplex communication allows for simultaneous read and write (exchange of messages) for both the client as well as server, just as in netcat. The addition is the encryption mechanism. `RSA key exchange` is used for exchanging key and `Salsa20 stream cipher` for encryption of the messages. The same can also transfer file contents securely using a particular command line argument. 

For message exchange, the length of a message is automatically prepended to the message. The receiver side therefore reads the message length and then reads that many bytes to receive the message. The bound on number of messages is for a session is equal to the number which can fit in 7 digits (in decimal as the nonce is set to increment for every message and is of 8 bytes). The maximum length of messages can be of size that fits in 20 decimal digits but this is only according to the code. The practical size that can be sent is equal to the 20 decimal digits but the receiving side only receives a particular amount which is set by the kernel of the receiving side operating system as the max socket buffer.

For the file content exchange, the maximum size to send is as much as the socket send buffer can handle. And the receive is unlimited.

Only client can exit the connection for messaging interface (holding on to the stereotype for the server to reply to each request by the client until it disconnects) by sending a message "BYE!". 

`appt.py` is the standalone file which has both the server and client implementaions to simulate experience of `netcat` and upon required arguments as described in the next section, it can send files as well as communicate. The sending file option is one that just sends the contents of a file and then exits. The messaging interface is kept separate due to threading of read and write for full duplex communication. 

## Run the code

1. To run on localhost i.e., listen and connect on local machine, simply clone and run the python file on separate terminals.
2. To run between two separate systems, give the appropriate IP address and port as arguments and deploy on the machines (run on terminal).
3. The **--------\<number\>** is a part of the nonce being printed which is commented out. 
```python
print("---------------", recieved)
```
4. For running, just **python3 appt.py -l 1233** to listen on the current machine on port 1233 and **python3 appt.py 192.168.56.4 1233** to connect to a machine listeing on port 1233.
5. For dile transfer, two actions can be done by both the client and the server machine which are to send the contents of a file or to receive the contents of a file and write to a file.
6. The file sharing requires two more arguments on the command line at the exact position as mentioned - 
```bash
python3 appt.py -l <port> -fr <filename>    # server to receive and write into a file <filename>
python3 appt.py -l <port> -fs <filename>    # server to send a file <filename>
python3 appt.py <ip> <port> -fr <filename>    # client to receive from a machine <ip> listening on <port> and write into a file <filename>
python3 appt.py <ip> <port> -fs <filename>    # client to send a file <filename> to a machine <ip> listening on <port> 
```

---

##### Note
The above was tested and written in Python 3.5.2. It should also work with most other versions, however socket implementation is different on 2.7 and few others (specifically byte type behaviour as well as RSA module and Salsa20 module behaviour) are also slightly different in implementation. Therefore, the code may or may not work as intended, however, you are free to test it out. Recommended Python3.
