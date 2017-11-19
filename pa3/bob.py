import socket
import pyDes
import helper
import threading

# Known information:
EXTENDED = helper.is_extended_NS()
DES_MODE = helper.get_3DES_mode()

Bob_ID = '80800000'
Bob_key = helper.get_key('Bob')

known_clients = {'41193000'} # Alice's ID is known to Bob

# Location:
IP = '127.0.0.1'
PORT = 8080

def handle(conn):
    ''' Handles a single connection. '''
    if EXTENDED:
        # Get request from Alice (do nothing with it)
        print 'Bob: Receiving request'
        recv = helper.sock_safe_recv(conn)

        # Send encrypted nonce to Alice
        Nb = helper.get_nonce(Bob_key)
        Nbs = helper.nonce_num_to_str(Nb)
        Kbob_Nb = pyDes.triple_des(Bob_key, DES_MODE).encrypt(Nbs)
        print 'Bob: Sending encryption'
        helper.sock_safe_send(conn, Kbob_Nb)

    # Get ticket from Alice and extract
    print 'Bob: Getting ticket'
    recv = helper.sock_safe_recv(conn)

    # Error checking
    size = 48 if EXTENDED else 40
    if len(recv) != size:
        helper.shutdown(conn, msg='Bob: Client message size mismatch')
    ticket = recv[:size-8]
    inner_ticket = pyDes.triple_des(Bob_key, DES_MODE).decrypt(ticket)
    if (inner_ticket[24:32] not in known_clients) or (EXTENDED and inner_ticket[32:40] != Nbs):
        helper.shutdown(conn, msg='Bob: Client validation failed')

    Kab = inner_ticket[:24]

    # Decrypt Alice's challenge with the extracted shared key, decrement the challenge
    N2s = pyDes.triple_des(Kab, DES_MODE).decrypt(recv[size-8:])
    N2 = helper.nonce_str_to_num(N2s)
    N2sub1s = helper.nonce_num_to_str(N2-1)

    N3 = helper.get_nonce(Bob_key)
    N3s = helper.nonce_num_to_str(N3)

    # Send proof of decryption and new challenge
    send = pyDes.triple_des(Kab, DES_MODE).encrypt(N2sub1s + N3s)
    print 'Bob: Sending validation to client'
    helper.sock_safe_send(conn, send)

    # Validate last challenge
    N3sub1s = helper.nonce_num_to_str(N3-1)

    print 'Bob: Getting last validation'
    recv = helper.sock_safe_recv(conn)
    recv = pyDes.triple_des(Kab, DES_MODE).decrypt(recv)

    if recv != N3sub1s:
        helper.shutdown(conn, msg='Bob: Client validation failed')

    # Wrap up
    conn.close()
    print 'Bob: Done'

# Listen (for Alice) at this location
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((IP, PORT))
sock.listen(1)

while True:
    try:
        conn, addr = sock.accept()
        t = threading.Thread(target=lambda: handle(conn))
        t.start()
    except KeyboardInterrupt:
        print 'Bob: closing down'
        sock.close()
        break

