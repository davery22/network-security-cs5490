# SSL Handshake and Data Transfer
The handshake is launched by running programs in two separate terminals:

`python bob.py`
`python alice.py`

(Launch Bob first)
These programs rely on `mySSL.py` to do most of the dirty work - encryption/decryption, certificate generation, hashing, exception handling, etc.

## Protocol:
The handshake protocol looks roughly like the following:

Alice                        Bob

cipher, certificate
------------------------------->
K_A+{nonce_b}, certificate
<-------------------------------
K_B+{nonce_a}, {hash of (secret,messages,CLIENT)}
------------------------------->
{hash of (secret,messages,SERVER)}
<-------------------------------

Alice establishes the cipher - no negotiation. Alice and Bob authenticate each other via the certificates. They each send nonces encrypted with the other's public key. These nonces are decrypted and XOR'd to produce a secret. This secret is used to generate four more keys for later use. The secret is also incorporated in a keyed message hash that either side verifies.

## Output:
Each node outputs their current interaction in the handshake, culminating in a 'Handshake accepted' message if all goes well. We can force all to not go well by changing a global parameter in Bob (FORCE_FAIL) to True, which will result in a failed hash verification. Examples of both outputs are spliced to `good_handshake.txt` and `bad_handshake.txt`.

### Notes:
Some dpendencies... `pip install -r requirements.txt`. 
