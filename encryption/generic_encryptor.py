from abc import ABC, abstractmethod


class GenericEncryptor(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def configure(self):
        pass

    @abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, data: bytes):
        pass

    @staticmethod
    def ask_user_if_existing_credentials_should_be_used():

        user_input = input('Do you want to enter existing credentials? (yes/no): ')

        if user_input == 'yes':
            return True
        if user_input == 'no':
            return False
