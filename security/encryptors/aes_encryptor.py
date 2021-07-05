import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from security.enums.encryption_type import EncryptionType
from security.hashing.generic_hash import GenericHash
from security.encryptors.generic_encryptor import GenericEncryptor
from security.hashing.none_hash import NoneHash


class AesEncryptor(GenericEncryptor):

    # https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/#algorithms
    NONCE_LENGTH = 16

    def __init__(self, hash_algo: GenericHash, decryption: bool, nonce: Optional[bytes] = None):
        super().__init__(EncryptionType.AES)

        if type(hash_algo) == NoneHash:
            raise ValueError('AES encryption requires a hash (PBKDF2/SCRYPT)')

        self.__hash_algo = hash_algo

        if decryption:
            key = self.__hash_algo.get_key_with_existing_credentials()

            if nonce is None:
                nonce_string = input('Please enter the nonce for AES decryption: ')
                nonce = bytes.fromhex(nonce_string)

        else:
            key = self.__hash_algo.get_key()

            if nonce is None:
                nonce = os.urandom(AesEncryptor.NONCE_LENGTH)

        self.__nonce = nonce

        self.__cipher = Cipher(algorithms.AES(key), modes.CTR(self.__nonce))

    @property
    def salt(self):
        if hasattr(self.__hash_algo, "salt"):
            return self.__hash_algo.salt
        return None

    @property
    def nonce(self):
        return self.__nonce

    def encrypt(self, data: bytes) -> bytes:

        nonce = os.urandom(AesEncryptor.NONCE_LENGTH)
        print(f'nonce: {nonce.hex()}')

        self.__cipher.mode = modes.CTR(nonce)

        encryptor = self.__cipher.encryptor()

        encrypted_data = encryptor.update(data) + encryptor.finalize()

        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:

        decryptor = self.__cipher.decryptor()

        decrypted_data = decryptor.update(data) + decryptor.finalize()

        a = decrypted_data.hex()

        return decrypted_data
