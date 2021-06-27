from security.encryptors.aes_encryptor import AesEncryptor
from security.enums.encryption_type import EncryptionType
from security.encryptors.fernet_encryptor import FernetEncryptor
from security.encryptors.generic_encryptor import GenericEncryptor
from security.encryptors.none_encryptor import NoneEncryptor
from security.encryptors.rsa_encryptor import RsaEncryptor
from security.enums.hash_type import HashType
from security.hash_provider import HashProvider


class EncryptionProvider:

    def __init__(self):
        pass

    @staticmethod
    def get_encryptor(encryption_type: EncryptionType, hash_type: HashType, decryption: bool) -> GenericEncryptor:

        hash_algo = HashProvider.get_hash(hash_type)

        if not encryption_type or encryption_type == EncryptionType.NONE:
            return NoneEncryptor()

        if encryption_type == EncryptionType.FERNET:
            return FernetEncryptor(hash_algo, decryption)

        if encryption_type == EncryptionType.AES:
            return AesEncryptor(hash_algo, decryption)

        if encryption_type == EncryptionType.RSA:
            return RsaEncryptor()

        raise ValueError('Could not get Encryptor')
