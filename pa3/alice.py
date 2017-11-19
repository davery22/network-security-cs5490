import socket
import pyDes
import helper

# Known information:
EXTENDED = helper.is_extended_NS()
DES_MODE = helper.get_3DES_mode()

Alice_ID = '41193000'
Alice_key = helper.get_key('Alice')
Bob_ID = '80800000'

# Locations:
IP = '127.0.0.1'
PORT_BOB = 8080
PORT_KDC = 8090

# Connect to Bob
sock_bob = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_bob.connect((IP, PORT_BOB))

if EXTENDED:
    # 1. Send communication request to Bob
    send = 'I want to talk'
    print 'Alice: Notifying Bob'
    helper.sock_safe_send(sock_bob, send)

    # 2. Get response from Bob
    print 'Alice: Getting response from Bob'
    Kbob_Nb = helper.sock_safe_recv(sock_bob)

# Connect to KDC
sock_kdc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_kdc.connect((IP, PORT_KDC))

# 3. Forward request to KDC (N1, Alice -> Bob, [Kbob_Nb])
N1 = helper.get_nonce(Alice_key)
N1s = helper.nonce_num_to_str(N1)
send = '{0}{1}{2}{3}'.format(N1s, Alice_ID, Bob_ID, Kbob_Nb if EXTENDED else '')
print 'Alice: Requesting to KDC'
helper.sock_safe_send(sock_kdc, send, sock_bob)

# 4. Get response from KDC
print 'Alice: Getting response from KDC'
recv = helper.sock_safe_recv(sock_kdc, sock_bob)
sock_kdc.close() # Done with KDC
recv = pyDes.triple_des(Alice_key, DES_MODE).decrypt(recv)

# Error checking
size = 80 if EXTENDED else 72
if len(recv) != size:
    helper.shutdown(sock_bob, msg='Alice: KDC message size mismatch')
if recv[:8] != N1s or recv[8:16] != Bob_ID:
    helper.shutdown(sock_bob, msg='Alice: KDC validation failed')

Kab = recv[16:40]
ticket_to_Bob = recv[40:]

# 5. Send ticket to Bob
N2 = helper.get_nonce(Alice_key)
N2s = helper.nonce_num_to_str(N2)
send = '{0}{1}'.format(ticket_to_Bob, pyDes.triple_des(Kab, DES_MODE).encrypt(N2s))
print 'Alice: Sending to Bob'
helper.print_hex(send)
helper.sock_safe_send(sock_bob, send)

# 6. Get response from Bob
print 'Alice: Receiving from Bob (Kab{N2-1, N3}):'
recv = helper.sock_safe_recv(sock_bob)
helper.print_hex(recv)
recv = pyDes.triple_des(Kab, DES_MODE).decrypt(recv)

# Error checking
if len(recv) != 16:
    helper.shutdown(sock_bob, msg='Alice: Bob message size mismatch')
N2sub1s = helper.nonce_num_to_str(N2-1)
if recv[:8] != N2sub1s:
    helper.shutdown(sock_bob, msg='Alice: Bob validation failed')

N3s = recv[8:]
N3 = helper.nonce_str_to_num(N3s)
N3sub1s = helper.nonce_num_to_str(N3-1)

# 7. Send final message to Bob
send = pyDes.triple_des(Kab, DES_MODE).encrypt(N3sub1s)
print 'Alice: Sending final to Bob (Kab{N3-1}):'
helper.print_hex(send)
helper.sock_safe_send(sock_bob, send)

# Wrap up
sock_bob.close()
print 'Alice: Done'

