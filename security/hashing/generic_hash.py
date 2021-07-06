from abc import ABC, abstractmethod

from security.enums.hash_type import HashType


class GenericHash(ABC):
    HASH_TYPE = HashType.NONE

    def __init__(self):
        pass

    @property
    def hash_type(self):
        return self.HASH_TYPE

    @abstractmethod
    def get_key(self) -> bytes:
        pass

    @abstractmethod
    def get_key_with_existing_credentials(self) -> bytes:
        pass
