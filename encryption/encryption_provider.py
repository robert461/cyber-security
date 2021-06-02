from encryption.encryption_type import EncryptionType
from encryption.fernet_encryptor import FernetEncryptor
from encryption.generic_encryptor import GenericEncryptor


class EncryptionProvider:

    def __init__(self):
        pass

    @staticmethod
    def get_encryptor(encryption_type: EncryptionType) -> GenericEncryptor:
        if encryption_type == EncryptionType.FERNET:
            return FernetEncryptor()

    @staticmethod
    def encode(data: bytes, password: str, encryption_type: EncryptionType):

        if encryption_type == EncryptionType.FERNET:
            token = FernetEncryptor.encrypt(data, password)

            return token

        return data
