from enum import Enum


class EncryptionType(Enum):

    NONE = 0
    FERNET = 1
    AES = 2
    RSA = 3
