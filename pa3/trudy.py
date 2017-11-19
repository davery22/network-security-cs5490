import socket
import pyDes
import helper

# Known information:
DES_MODE = helper.get_3DES_mode()

eavesdropped_msg = ''.join(chr(int(x, 16)) for x in '96:47:5e:f3:32:02:01:7f:b0:3c:49:6d:c3:76:df:68:59:2f:50:4f:89:88:59:67:47:c5:53:7c:27:4a:0c:dd:d5:06:44:b1:73:ec:b7:c5'.split(':'))

# Locations:
IP = '127.0.0.1'
PORT_BOB = 8080

# Connect to Bob
sock_bob1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_bob1.connect((IP, PORT_BOB))

# 5. Send eavesdropped message (ticket, Kab{N2}) to Bob
print 'Trudy: Sending to Bob on conn.1'
helper.sock_safe_send(sock_bob1, eavesdropped_msg)

# 6. Get response from Bob
print 'Trudy: Receiving from Bob on conn.1'
recv = helper.sock_safe_recv(sock_bob1)

# Error checking
if len(recv) != 16:
    helper.shutdown(sock_bob1, msg='Trudy: Bob message size mismatch, conn.1')

Kab_N3s = recv[8:] # works because ECB separately encrypts nonces

# Connect to Bob _again_
print 'Trudy: Opening new connection'
sock_bob2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_bob2.connect((IP, PORT_BOB))

# 5-2. Send spliced-together ticket + Bob's challenge
send = eavesdropped_msg[:32] + Kab_N3s
print 'Trudy: Sending to Bob on conn.2'
helper.sock_safe_send(sock_bob2, send)

# 6-2. Get response from Bob
print 'Trudy: Receiving from Bob on conn.2'
recv = helper.sock_safe_recv(sock_bob2)

# Error checking
if len(recv) != 16:
    helper.shutdown(sock_bob1, sock_bob2, msg='Trudy: Bob message size mismatch, conn.2')

# Splice the part we need and close the extraneous connection
Kab_N3sub1s = recv[:8] # again, works because ECB separately ecrypts nonces
sock_bob2.close()

# 7. Send final message to Bob
print 'Trudy: Sending final to Bob on conn.1'
helper.sock_safe_send(sock_bob1, Kab_N3sub1s)

# Wrap up
sock_bob1.close()
print 'Trudy: Done'

