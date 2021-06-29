from abc import ABC, abstractmethod

from security.enums.encryption_type import EncryptionType


class GenericEncryptor(ABC):

    def __init__(self, encryption_type: EncryptionType):
        self.encryption_type: EncryptionType = encryption_type

    @abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, data: bytes) -> bytes:
        pass
