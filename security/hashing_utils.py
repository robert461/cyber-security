from getpass import getpass


class HashingUtils:

    @staticmethod
    def get_password_from_user() -> bytes:

        password = getpass('Please enter the password you want to use: ')

        password_bytes = bytes(password, 'utf-8')

        return password_bytes

    @staticmethod
    def get_salt_from_user() -> bytes:
        salt_string = input('Please enter the salt: ')

        salt = bytes.fromhex(salt_string)

        return salt
