import mySSL
import OpenSSL
import socket
import struct
import threading

# Known information:
FORCE_FAIL = False
bob_key = mySSL.get_RSA_key()

# Location:
IP = '127.0.0.1'
PORT = 8080

def connect(conn):
    try:
        messages = ''

        ''' HANDSHAKE '''

        # 1. Receive (cipher, certificate)
        recv = mySSL.sock_safe_recv(conn)
        print 'Bob: Received certificate'

        messages += recv
        cert = recv[3:]

        # Verify the certificate and extract Alice's public (encryption) key
        mySSL.verify_certificate(cert, conn)
        alice_pubkey = mySSL.pubkey_from_cert(cert)

        # 2. Send (alice encrypted nonce, certificate)
        nonce_b_dec = mySSL.get_nonce()
        nonce_b_enc = mySSL.get_encrypted_nonce(alice_pubkey, nonce_b_dec)
        cert = mySSL.create_certificate('Bob', bob_key)
        send = ''.join((nonce_b_enc, cert))
        messages += send

        print 'Bob: Sending certificate'
        mySSL.sock_safe_send(conn, send)

        # 3. Receive (bob encrypted nonce, {keyed hash of handshake messages - CLIENT})
        recv = mySSL.sock_safe_recv(conn)
        print 'Bob: Received message hash and secret'

        splitter = '----- SPLIT -----'
        idx = recv.index(splitter)
        nonce_a_enc = recv[:idx]
        idx = idx + len(splitter) + (1 if FORCE_FAIL else 0)
        recv_hash = recv[idx:]

        # Compute the key, verify the hash
        nonce_a_dec = mySSL.decrypt_nonce(bob_key, nonce_a_enc)
        secret = mySSL.xor(nonce_a_dec, nonce_b_dec)
        keyed_hash = mySSL.keyed_hash(secret + messages + 'CLIENT')
        mySSL.verify_hash(keyed_hash, recv_hash, conn)
        messages += recv

        # 4. Send ({keyed hash of handshake messages - SERVER})
        keyed_hash = mySSL.keyed_hash(secret + messages + 'SERVER')

        print 'Bob: Sending message hash'
        mySSL.sock_safe_send(conn, keyed_hash)

        # Create four keys from secret
        keys = mySSL.get_keys(secret)

        print 'Bob: Handshake accepted'
        
        ''' FILE TRANSFER '''
        '''
        with open('56kB.txt', 'r') as exfile:
            exfile = exfile.read()

        send = mySSL.get_encrypted_nonce(alice_pubkey, exfile)
        mySSL.sock_safe_send(conn, send)'''

    except Exception as ex:
        print ex

    conn.close()

def transfer_file(conn):
    pass

# Listen at our location
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((IP, PORT))
sock.listen(1)

while True:
    try:
        conn, addr = sock.accept()
        t = threading.Thread(target=lambda: connect(conn))
        t.start()
    except KeyboardInterrupt:
        print 'Bob: closing down'
        sock.close()
        break
