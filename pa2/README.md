# Client-Server key exchange
Start by running `python server-bob.py` in a terminal. In another terminal, run `python client-alice.py`. Alice and Bob will perform a Diffie Hellman key exchange. Each side prints out the number they send, the number they receive, and the shared key after (and then the programs terminate).
All modular exponentiation is performed using the function in `EXPO.py`.
A sample of the outputs (with minor labeling added) is recorded in `exchange.txt`.
