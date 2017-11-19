# Needham-Schroeder Mediated Authentication
## Standard authentication runs
The NS authentication can be performed by launching the relevant programs in three terminals:

`python KDC.py`
`python bob.py`
`python alice.py`

Be sure to launch the first two (servers) first, as Alice will immediately try to establish a connection with them.

These progams rely on `helper.py`, which defines error-handling socket sending/receiving methods, as well as nonce and key generation methods. It also specifies a few important parameters:
- EXTENDED_NS: if `True` the authentication will use the extended Needham-Schroeder authentication; otherwise will revert to the original Needham-Schroeder.
- DES3_MODE: specifies the key encryption/decryption algorithm to use (either Cipher Block Chaining or Electronic Code Book).
- CONSISTENT_NONCES: if `True` the random number generator will be seeded so that nonces are generated in the same sequence between runs; else no such guarantee.

To run the extended NS authentication, set `EXTENDED_NS = True`
To run the original NS authentication, set `EXTENDED_NS = False`

Example printouts from the different nodes are spliced together in `extended_exchange.txt`, `cbc_exchange.txt`, and `ecb_exchange.txt`, where the latter two use the original NS scheme. You can replicate these results by setting the parameters accordingly, including setting `CONSISTENT_NONCES = True`.

## Reflection attack
The reflection attack is possible when original Needham-Schroeder is used and the 3DES mode is ECB.

To try this out, set `EXTENDED_NS = False, DES3_MODE = pyDes.ECB` 

Then run

`python bob.py`
`python trudy.py`

An example of the printouts from both nodes is spliced together in `reflection_attack.txt`.

### Notes
- Code is dependent on pyDes --- `pip install pydes`
- Programs must be restarted before a change to the configuration parameters in `helper.py` can take effect.
- Each program outputs its interactions in the exchanges. To prevent clutter, the interactions do not include a printout of the messages (except for Alice's last two interactions, which are printed in hex).
- `bob.py` and `KDC.py` are long-running servers, so they are viable for multiple client authentications. Use Ctrl-C to exit from either of them.
- Where applicable the code uses (8-byte) hard-coded IDs in place of client names.
- Somewhat stated earlier, keys (24-byte) and nonces (8-byte) are generated rather than hard-coded. That said, keys are derived directly from ID's, whereas nonces have a random component (so use CONSISTENT_NONCES for a consistent sequence between runs).

