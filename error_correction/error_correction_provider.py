from error_correction.error_correction_type import ErrorCorrectionType
from error_correction.generic_error_correction import GenericErrorCorrection


class ErrorCorrectionProvider:

    def __init__(self):
        pass

    @staticmethod
    def get_error_correction(
            encryption_type: ErrorCorrectionType
    ) -> GenericErrorCorrection:
        """Return error correction"""

        if encryption_type == ErrorCorrectionType.HAMMING:
            return FernetEncryptor(hash_algo, decryption)

        if encryption_type == ErrorCorrectionType.REED_SOLOMON:
            return AesEncryptor(hash_algo, nonce)

        if encryption_type == EncryptionType.RSA:
            return RsaEncryptor(decryption, is_test)

        raise ValueError('Could not get Error Correction')
