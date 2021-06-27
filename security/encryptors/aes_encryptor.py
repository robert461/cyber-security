import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from security.hashing.generic_hash import GenericHash
from security.utils.encryption_utils import EncryptionUtils
from security.encryptors.generic_encryptor import GenericEncryptor


class AesEncryptor(GenericEncryptor):

    def __init__(self, hash_algo: GenericHash):
        super().__init__()

        self.__hash_algo = hash_algo

        key = self.__hash_algo.get_key()

        nonce = os.urandom(16)

        self.__cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))

    def encrypt(self, data: bytes) -> bytes:

        nonce = os.urandom(16)
        self.__cipher.mode = modes.CTR(nonce)

        encryptor = self.__cipher.encryptor()

        encrypted_data = encryptor.update(data) + encryptor.finalize()

        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:

        decryptor = self.__cipher.decryptor()

        decrypted_data = decryptor.update(data) + decryptor.finalize()

        return decrypted_data
