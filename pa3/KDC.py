import socket
import pyDes
import helper
import threading

# Known information:
EXTENDED = helper.is_extended_NS()
DES_MODE = helper.get_3DES_mode()

Alice_ID = '41193000'
Alice_key = helper.get_key('Alice')
Bob_ID = '80800000'
Bob_key = helper.get_key('Bob')

credentials = {
    Alice_ID: Alice_key,
    Bob_ID: Bob_key
}

# Location:
IP = '127.0.0.1'
PORT = 8090

def handle(conn):
    ''' Handles a single connection. '''
    # Get Alice's request
    print 'KDC: Receiving request'
    recv = helper.sock_safe_recv(conn)

    # Error checking
    size = 32 if EXTENDED else 24
    if len(recv) != size:
        helper.shutdown(conn, msg='KDC: Size mismatch')

    # Get the nonce, source, and dest
    N1s = recv[:8]
    src = recv[8:16]
    dest = recv[16:24]

    if (src not in credentials or dest not in credentials):
        helper.shutdown(conn, msg='KDC: Unrecognized source or destination')

    # Decrypt the dest's challenge (extended protocol)
    if EXTENDED:
        dest_N = recv[24:]
        dest_Ns = pyDes.triple_des(credentials[dest], DES_MODE).decrypt(dest_N)

    # Construct ticket
    Kab = helper.get_key(helper.nonce_num_to_str(helper.get_nonce(src + dest))) # Invent a shared session key
    inner_ticket = '{0}{1}{2}'.format(Kab, src, dest_Ns if EXTENDED else '')
    ticket_to_Bob = pyDes.triple_des(credentials[dest], DES_MODE).encrypt(inner_ticket)

    # Construct full response and send
    inner_send = '{0}{1}{2}{3}'.format(N1s, dest, Kab, ticket_to_Bob)
    send = pyDes.triple_des(credentials[src], DES_MODE).encrypt(inner_send)
    print 'KDC: Sending ticket'
    helper.sock_safe_send(conn, send)

    # Wrap up
    print 'KDC: Done'
    conn.close()

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
        print 'KDC: closing down'
        sock.close()
        break
