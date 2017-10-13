import EXPO
import socket

S_A = 160011
g = 1907
p = 784313

IP = '127.0.0.1'
PORT = 8080
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
Alice = EXPO.expMod(g, S_A, p)
print 'Alice: Sending:', Alice
s.send(str(Alice))
Bob = int(s.recv(BUFFER_SIZE))
print 'Alice: Got from Bob:', Bob
s.close()

shared = EXPO.expMod(Bob, S_A, p)
print 'Alice: Shared key:', shared
