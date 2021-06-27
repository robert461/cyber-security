from security.encryptors.aes_encryptor import AesEncryptor
from security.enums.encryption_type import EncryptionType
from security.encryptors.fernet_encryptor import FernetEncryptor
from security.encryptors.generic_encryptor import GenericEncryptor
from security.encryptors.none_encryptor import NoneEncryptor
from security.encryptors.rsa_encryptor import RsaEncryptor
from security.enums.hashing_type import HashingType
from security.hashing_provider import HashingProvider


class EncryptionProvider:

    def __init__(self):
        pass

    @staticmethod
    def get_encryptor(encryption_type: EncryptionType, hashing_type: HashingType) -> GenericEncryptor:

        hash_algo = HashingProvider.get_hash(hashing_type)

        if not encryption_type or encryption_type == EncryptionType.NONE:
            return NoneEncryptor(hash_algo)

        if encryption_type == EncryptionType.FERNET:
            return FernetEncryptor(hash_algo)

        if encryption_type == EncryptionType.AES:
            return AesEncryptor(hash_algo)

        if encryption_type == EncryptionType.RSA:
            return RsaEncryptor()

        raise ValueError('Could not get Encryptor')
