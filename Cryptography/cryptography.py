from Crypto.Cipher import AES, DES3, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA, SHA224, SHA256, SHA384, SHA512
from Crypto import Random
from enum import Enum

crypto_random = Random.new()
digest_methods = {
    "SHA-1": SHA,
    "SHA-2-224": SHA224,
    "SHA-2-256": SHA256,
    "SHA-2-384": SHA384,
    "SHA-2-512": SHA512
}

class Algorithm(Enum):
    AES = 0
    DES3 = 1
    RSA = 2

class Method:
    def __init__(self, algorithm, key_size, mode=None):
        self.algorithm = algorithm
        self.key_size = key_size
        self.mode = mode 

class Crypter:
    def __init__(self, method, key=None, initial_vector=None):
        self.method = method
        self.key = key
        self.initial_vector = initial_vector
        self.create_crypter()

    def create_crypter(self):
        # AES
        if self.method.algorithm == Algorithm.AES:
            if not self.key and not self.initial_vector:
                self.key = crypto_random.read(self.method.key_size)
                self.initial_vector = crypto_random.read(AES.block_size)
            self.cipher = AES.new(self.key, self.method.mode, self.initial_vector)
        # 3DES
        elif self.method.algorithm == Algorithm.DES3:
            if not self.key and not self.initial_vector:
                self.key = crypto_random.read(self.method.key_size)
                self.initial_vector = crypto_random.read(DES3.block_size)
            self.cipher = DES3.new(self.key, self.method.mode, self.initial_vector)
        # RSA
        elif self.method.algorithm == Algorithm.RSA:
            self.key = RSA.generate(self.method.key_size, Random.new().read)
            public_key = self.key.publickey()
            self.cipher = PKCS1_OAEP.new(public_key)

    def encrypt(self, plaintext):
        plaintext = bytes(plaintext, encoding='utf-8') if type(plaintext) == str else plaintext
        return self.cipher.encrypt(plaintext)
    
    def decrypt(self, ciphertext):
        ciphertext = bytes(ciphertext, encoding='utf-8') if type(ciphertext) == str else ciphertext
        if self.method.algorithm == Algorithm.RSA:
            decryptor = PKCS1_OAEP.new(self.key)  
            return decryptor.decrypt(ciphertext)
        else:
            return self.cipher.decrypt(ciphertext).decode('utf-8')
        
    def sign(self, plaintext, digest_method):
        # print(f"Public key: (n={hex(self.key.n)}, e={hex(self.key.e)})")
        # print(f"Private key: (n={hex(self.key.n)}, d={hex(self.key.d)})")
        plaintext = str(plaintext) if type(plaintext) == tuple else plaintext
        plaintext = bytes(plaintext, encoding='utf-8') if type(plaintext) == str else plaintext
        hash = int.from_bytes(digest_method.new(plaintext).digest(), byteorder='big')
        signature = pow(hash, self.key.d, self.key.n)
        print("Signature:", end=" "); print(signature)

        # proof it works - check signature
        hash = int.from_bytes(digest_method.new(plaintext).digest(), byteorder='big')
        hashFromSignature = pow(signature, self.key.e, self.key.n)
        print("Signature valid:", hash == hashFromSignature, end="\n\n")


def pad(plaintext, method):
    if method.algorithm == Algorithm.AES:
        padding_max_length = 16  
    elif method.algorithm == Algorithm.DES3:
        padding_max_length = 8
    padding_length = padding_max_length - len(plaintext) % padding_max_length
    return plaintext + padding_length*"0"

def unpad(plaintext):
    padding = 0
    for char in plaintext[::-1]:
        if char != "0": break
        padding += 1
    return plaintext[:len(plaintext)-padding]

def digital_envelope(plaintext, symmetric_method, asymmetric_method):
    print("--- DIGITAL ENVELOPE ---")
    plaintext = pad(plaintext, symmetric_method)

    # encrypt plaintext
    print("Plaintext: ", unpad(plaintext))
    encrypter = Crypter(symmetric_method)
    symmetric_key = encrypter.key
    ciphertext = encrypter.encrypt(plaintext)
    print("Ciphertext:", ciphertext)

    # proof it works - decryption
    decrypter = Crypter(symmetric_method, encrypter.key, encrypter.initial_vector)
    print("Decrypted: ", unpad(decrypter.decrypt(ciphertext)), end="\n\n")

    # encrypt symmetric key
    print("Plain key:    ", end=" "); print(symmetric_key)
    encrypter = Crypter(asymmetric_method)
    key_cipher = encrypter.encrypt(symmetric_key)
    print("Cipher key:   ", end=" "); print(key_cipher)

    # proof it works - decryption
    print("Decrypted key:", end=" "); print(encrypter.decrypt(key_cipher), end="\n\n")

    return (ciphertext, key_cipher)

def digital_signature(plaintext, method, digest_method):
    print("--- DIGITAL SIGNATURE ---")
    crypter = Crypter(method)
    signature = crypter.sign(plaintext, digest_method)
    return (plaintext, signature)

def digital_seal(plaintext, symmetric_method, asymmetric_method, digest_method):
    print("\n--- DIGITAL SEAL ---\n")
    plaintext = pad(plaintext, symmetric_method)
    envelope = digital_envelope(plaintext, symmetric_method, asymmetric_method)
    seal = digital_signature(envelope, asymmetric_method, digest_method)
    return seal

if __name__ == '__main__':
    plaintext = "Message for testing."

    # DEMO 1
    symmetric_method = Method(Algorithm.AES, 32, AES.MODE_CBC)
    asymmetric_method = Method(Algorithm.RSA, 1024)
    envelope = digital_envelope(plaintext, symmetric_method, asymmetric_method)

    # DEMO 3
    symmetric_method = Method(Algorithm.DES3, 24, AES.MODE_OFB)
    asymmetric_method = Method(Algorithm.RSA, 1024)
    envelope = digital_envelope(plaintext, symmetric_method, asymmetric_method)

    # DEMO 3
    asymmetric_method = Method(Algorithm.RSA, 1024)
    digest_method = digest_methods["SHA-2-256"]
    signature = digital_signature(plaintext, asymmetric_method, digest_method)

    # DEMO 4
    asymmetric_method = Method(Algorithm.RSA, 1024)
    digest_method = digest_methods["SHA-2-512"]
    signature = digital_signature(plaintext, asymmetric_method, digest_method)

    # DEMO 5
    symmetric_method = Method(Algorithm.AES, 32, AES.MODE_CBC)
    asymmetric_method = Method(Algorithm.RSA, 1024)
    digest_method = digest_methods["SHA-2-256"]
    seal = digital_seal(plaintext, symmetric_method, asymmetric_method, digest_method)

    # DEMO 6
    symmetric_method = Method(Algorithm.AES, 32, AES.MODE_CBC)
    asymmetric_method = Method(Algorithm.RSA, 1024)
    digest_method = digest_methods["SHA-2-512"]
    seal = digital_seal(plaintext, symmetric_method, asymmetric_method, digest_method)
