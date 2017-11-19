from OpenSSL import crypto, SSL
import os
import struct
import hashlib
import cryptography.hazmat.primitives.asymmetric.padding as padding

store = crypto.X509Store()

def shutdown(sock, msg=None):
    ''' Closes the socket with an optional error message. '''
    try:
        sock.close()
    except:
        pass
    if msg:
        print msg
    exit(1)

def sock_safe_send(sock, send):
    ''' Tries to send a message, else shuts down. '''
    try:
        sock.send(send)
    except Exception as ex:
        shutdown(sock, msg=ex)

def sock_safe_recv(sock):
    ''' Tries to receive a message, else shuts down. '''
    buffer_size = 1000000
    try:
        return sock.recv(buffer_size)
    except Exception as ex:
        shutdown(sock, msg=ex)

def get_RSA_key():
    ''' Creates a new SSL key (for signing certificates). '''
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)
    return k

def create_certificate(name, ssl_key):
    ''' Creates a self-signed certificate. '''
    cert = crypto.X509()
    
    cert.get_subject().CN = name
    cert.get_subject().C = "US"
    cert.get_subject().ST = "Utah"
    cert.get_subject().L = "Salt Lake City"
    cert.get_subject().O = "University of Utah"
    cert.get_subject().OU = "Students"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)

    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(ssl_key)
    cert.sign(ssl_key, 'sha1')

    global store
    store.add_cert(cert)

    dump = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
    return dump

def verify_certificate(cert, sock):
    ''' Verifies a self-signed certificate. '''
    return
    try:
        global store
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
        context = crypto.X509StoreContext(store, cert)
        context.verify_certificate()
    except:
        shutdown(sock, msg='Certificate verification error')

def pubkey_from_cert(cert):
    ''' Extracts the public key from a certificate. '''
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    return cert.get_pubkey()

def get_nonce():
    ''' Generates a nonce. '''
    return os.urandom(8)

def get_encrypted_nonce(key, nonce):
    ''' Encrypts an existing nonce with the key. '''
    pad = padding.PKCS1v15()
    enc = key.to_cryptography_key().encrypt(nonce, pad)
    return enc

def decrypt_nonce(key, nonce):
    ''' Decrypts a nonce with the key. '''
    pad = padding.PKCS1v15()
    dec = key.to_cryptography_key().decrypt(nonce, pad)
    return dec

def xor(nonce_a, nonce_b):
    ''' Combines two string nonces into a new nonce via bitwise xor. '''
    a = struct.unpack('=q', nonce_a)[0]
    b = struct.unpack('=q', nonce_b)[0]
    x = a ^ b
    return struct.pack('=q', x)

def keyed_hash(msg):
    ''' Constructs a SHA1 hash. '''
    return hashlib.sha1(msg).hexdigest()

def verify_hash(hash_msg, expected, sock):
    ''' Checks that the hashed message equals the expected bytes. '''
    if hash_msg != expected:
        shutdown(sock, msg='Message hash verification failed')

def get_keys(secret):
    ''' Converts a secret into four keys. '''
    secret = struct.unpack('=q', secret)[0]
    keys = []
    secret = (secret + 1) << 1
    keys.append(secret)
    secret = (secret + 1) << 1
    keys.append(secret)
    secret = (secret + 1) << 1
    keys.append(secret)
    secret = (secret + 1) << 1
    keys.append(secret)
    
    return keys
