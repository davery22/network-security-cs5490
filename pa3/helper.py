import random
import struct
import pyDes

# Configuration parameters
EXTENDED_NS = False
DES3_MODE = pyDes.CBC # choices: pyDes.CBC, pyDes.ECB
CONSISTENT_NONCES = True

# Set up
if CONSISTENT_NONCES:
    random.seed(7)

def is_extended_NS():
    return EXTENDED_NS

def get_3DES_mode():
    return DES3_MODE

def print_hex(s):
    print '  ' + ':'.join('{:02x}'.format(ord(x)) for x in s)

def shutdown(sock_a, sock_b=None, msg=None):
    ''' Tries to shut down open sockets, then exits the program (with an optional error message). '''
    if sock_a:
        try:
            sock_a.close()
        except:
            pass
    if sock_b:
        try:
            sock_b.close()
        except:
            pass
    if msg:
        print msg
    exit(1)

def sock_safe_send(sock_a, msg, sock_b=None):
    ''' Tries to send to over sock_a, else shuts down. '''
    try:
        sock_a.send(msg)
    except Exception as ex:
        shutdown(sock_a, sock_b, ex)

def sock_safe_recv(sock_a, sock_b=None):
    ''' Tries to receive from sock_a, else shuts down. '''
    buffer_size = 1024
    try:
        return sock_a.recv(buffer_size)
    except Exception as ex:
        shutdown(sock_a, sock_b, ex)

def get_key(user_id):
    ''' Creates a (24-byte) 3DES key (string) for this user. '''
    h = str(hash(user_id))
    return h[:24] if len(h) >= 24 else h.rjust(24, '0')

def get_nonce(key):
    ''' Returns a nonce (as a number). '''
    s = struct.pack('=q', random.randint(0, 0xffffffff))
    h = hash(key + s)
    return h

def nonce_num_to_str(nonce):
    ''' Converts a nonce (number) to a string representation. '''
    return struct.pack('=q', nonce)

def nonce_str_to_num(nonce):
    ''' Converts a nonce (string) to a number representation. '''
    return struct.unpack('=q', nonce)[0]

