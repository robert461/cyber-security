from security.hashing.generic_hash import GenericHash
from security.utils.hash_utils import HashUtils


class NoneHash(GenericHash):

    # Not hashing at all

    def __init__(self):
        super().__init__()

    def get_key(self) -> bytes:
        password_bytes = HashUtils.get_password_from_user()

        return password_bytes

    def get_key_with_existing_credentials(self) -> bytes:
        password_bytes = HashUtils.get_password_from_user()

        return password_bytes