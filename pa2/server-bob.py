import EXPO
import socket

S_B = 12067
g = 1907
p = 784313

IP = '127.0.0.1'
PORT = 8080
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT))
s.listen(1)

conn, addr = s.accept()
Alice = int(conn.recv(BUFFER_SIZE))
print 'Bob: Got from Alice:', Alice
Bob = EXPO.expMod(g, S_B, p)
print 'Bob: Sending:', Bob
conn.send(str(Bob))
conn.close()

shared = EXPO.expMod(Alice, S_B, p)
print 'Bob: Shared key:', shared
