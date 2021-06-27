from cryptography.fernet import Fernet

from security.utils.encryption_utils import EncryptionUtils
from security.encryptors.generic_encryptor import GenericEncryptor


class FernetEncryptor(GenericEncryptor):

    # https://cryptography.io/en/latest/fernet/

    def __init__(self):
        super().__init__()

        key = EncryptionUtils.get_base64_key_from_user_input()

        self.__fernet = Fernet(key)

        key = Fernet.generate_key()

        self.__fernet = Fernet(key)

    def encrypt(self, data: bytes) -> bytes:
        encrypted_data = self.__fernet.encrypt(data)

        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        decrypted_data = self.__fernet.decrypt(data)

        return decrypted_data