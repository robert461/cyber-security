from security.hashing.generic_hash import GenericHash
from security.hashing_utils import HashingUtils


class NoneHash(GenericHash):

    # Not hashing at all

    def __init__(self):
        super().__init__()

    def get_key(self) -> bytes:
        password_bytes = HashingUtils.get_password_from_user()

        return password_bytes

    def get_key_with_existing_credentials(self) -> bytes:
        password_bytes = HashingUtils.get_password_from_user()

        return password_bytes
