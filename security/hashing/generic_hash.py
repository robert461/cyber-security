from abc import ABC, abstractmethod

from security.enums.hash_type import HashType


class GenericHash(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_key(self) -> bytes:
        pass

    @abstractmethod
    def get_key_with_existing_credentials(self) -> bytes:
        pass
