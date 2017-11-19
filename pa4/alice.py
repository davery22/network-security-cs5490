import mySSL
import socket

# Known information:
alice_key = mySSL.get_RSA_key()
cipher_to_use = 'RSA'

# Bob's location:
IP_BOB = '127.0.0.1'
PORT_BOB = 8080

# Connect to Bob
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP_BOB, PORT_BOB))

''' HANDSHAKE '''

messages = ''

# 1. Send (cipher, certificate)
cert = mySSL.create_certificate('Alice', alice_key)
send = ''.join((cipher_to_use, cert))
messages += send

print 'Alice: Sending certificate'
mySSL.sock_safe_send(sock, send)

# 2. Receive (alice encrypted nonce, certificate)
recv = mySSL.sock_safe_recv(sock)
print 'Alice: Received certificate'

messages += recv
idx = recv.index('-----BEGIN CERTIFICATE-----')
nonce_b_enc = recv[:idx]
cert = recv[idx:]

# Verify the certificate and extract Bob's public (encryption) key
mySSL.verify_certificate(cert, sock)
bob_pubkey = mySSL.pubkey_from_cert(cert)

# Decrypt Bob's nonce with Alice's private key
nonce_b_dec = mySSL.decrypt_nonce(alice_key, nonce_b_enc)

# 3. Send (bob encrypted nonce, {keyed hash of handshake msgs - CLIENT})
nonce_a_dec = mySSL.get_nonce()
nonce_a_enc = mySSL.get_encrypted_nonce(bob_pubkey, nonce_a_dec)

secret = mySSL.xor(nonce_a_dec, nonce_b_dec)

keyed_hash = mySSL.keyed_hash(secret + messages + 'CLIENT')
send = '----- SPLIT -----'.join((nonce_a_enc, keyed_hash))
messages += send

print 'Alice: Sending secret and message hash'
mySSL.sock_safe_send(sock, send)

# 4. Receive ({keyed hash of handshake msgs - SERVER})
recv = mySSL.sock_safe_recv(sock)
print 'Alice: Received message hash'

keyed_hash = mySSL.keyed_hash(secret + messages + 'SERVER')
mySSL.verify_hash(keyed_hash, recv, sock)

# Create four keys from secret
keys = mySSL.get_keys(secret)

print 'Alice: Handshake accepted'

''' FILE TRANSFER '''
'''
recv = mySSL.sock_safe_recv(sock)
recv = mySSL.decrypt_nonce(alice_key, recv)

with open('56kB.txt', 'r') as exfile:
    exfile = exfile.read()

if exfile == recv:
    print 'match'
else:
    print 'fail'
'''
sock.close()
