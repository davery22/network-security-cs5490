# Part a
`gcc rc4.c`
The minor bug seems to have been a missing modulo in the rc4step() function, allowing an index to go out of bounds. So I added a modulo.
The key "mnbvc" is hard-coded, as is the message string. Running the program prints out the encrypted message, as space-delimited hex octets (Can change to ascii by adjusting the printf() to use "%c" instead of "%02 ").
The file `rc4.output` is simply the aforementioned output piped to a file.

# Part b
`gcc crypto.c`
The rc4 algorithms were reused in generating the substitution tables for encryption/decryption.
The key/password "password" is hard-coded, while the message is passed via command line argument (just do it wrong and it will print usage).
Running the program prints the ascii output at each round of encryption and decryption. Rounds are denoted.
The file `crypto.output` contains the aforementioned output, for two bit patterns/inputs/messages: 'dathouse' and 'eathouse', which are one bit apart. A couple labels were added manually.
