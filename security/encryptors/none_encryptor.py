from security.encryptors.generic_encryptor import GenericEncryptor
from security.hashing.generic_hash import GenericHash


class NoneEncryptor(GenericEncryptor):

    # https://cryptography.io/en/latest/fernet/

    def __init__(self):
        super().__init__()

    def encrypt(self, data: bytes) -> bytes:
        return data

    def decrypt(self, data: bytes) -> bytes:
        return data
