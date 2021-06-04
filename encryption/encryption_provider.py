from encryption.aes_encryptor import AesEncryptor
from encryption.encryption_type import EncryptionType
from encryption.fernet_encryptor import FernetEncryptor
from encryption.generic_encryptor import GenericEncryptor
from encryption.rsa_encryptor import RsaEncryptor


class EncryptionProvider:

    def __init__(self):
        pass

    @staticmethod
    def get_encryptor(encryption_type: EncryptionType) -> GenericEncryptor:
        if encryption_type == EncryptionType.NONE:
            return None

        if encryption_type == EncryptionType.FERNET:
            return FernetEncryptor()

        if encryption_type == EncryptionType.AES:
            return AesEncryptor()

        if encryption_type == EncryptionType.RSA:
            return RsaEncryptor()

        raise ValueError('EncryptionType unkown')
