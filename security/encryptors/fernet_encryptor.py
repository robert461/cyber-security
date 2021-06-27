import base64

from cryptography.fernet import Fernet

from security.hashing.generic_hash import GenericHash
from security.encryptors.generic_encryptor import GenericEncryptor


class FernetEncryptor(GenericEncryptor):

    # https://cryptography.io/en/latest/fernet/

    def __init__(self, hash_algo: GenericHash):
        super().__init__()

        self.__hash_algo = hash_algo

        key = self.__hash_algo.get_key()

        key_base64 = base64.urlsafe_b64encode(key)

        self.__fernet = Fernet(key_base64)

    def encrypt(self, data: bytes) -> bytes:
        encrypted_data = self.__fernet.encrypt(data)

        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        decrypted_data = self.__fernet.decrypt(data)

        return decrypted_data
