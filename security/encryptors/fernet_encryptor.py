import base64

from cryptography.fernet import Fernet

from security.enums.encryption_type import EncryptionType
from security.hashing.generic_hash import GenericHash
from security.encryptors.generic_encryptor import GenericEncryptor
from security.hashing.none_hash import NoneHash


class FernetEncryptor(GenericEncryptor):

    # https://cryptography.io/en/latest/fernet/

    def __init__(self, hash_algo: GenericHash, decryption: bool):
        super().__init__(EncryptionType.FERNET)

        if type(hash_algo) == NoneHash:
            raise ValueError('Fernet encryption requires a hash (PBKDF2/SCRYPT)')

        self.__hash_algo = hash_algo

        if decryption:
            key = self.__hash_algo.get_key_with_existing_credentials()
        else:
            key = self.__hash_algo.get_key()

        key_base64 = base64.urlsafe_b64encode(key)

        self.__fernet = Fernet(key_base64)

    @property
    def hash_type(self):
        return self.__hash_algo.hash_type

    @property
    def salt(self):
        if hasattr(self.__hash_algo, "salt"):
            return self.__hash_algo.salt
        return None

    def encrypt(self, data: bytes) -> bytes:
        encrypted_data = self.__fernet.encrypt(data)

        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        decrypted_data = self.__fernet.decrypt(data)

        return decrypted_data
