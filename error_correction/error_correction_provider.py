from error_correction.error_correction_type import ErrorCorrectionType
from error_correction.generic_error_correction import GenericErrorCorrection
from error_correction.hamming_error_correction import HammingErrorCorrection
from error_correction.none_error_correction import NoneErrorCorrection
from error_correction.reed_solomon_error_correction import ReedSolomonErrorCorrection


class ErrorCorrectionProvider:

    def __init__(self):
        pass

    @staticmethod
    def get_error_correction(
            error_correction_type: ErrorCorrectionType
    ) -> GenericErrorCorrection:
        """Return error correction"""

        if not error_correction_type or error_correction_type == ErrorCorrectionType.NONE:
            return NoneErrorCorrection()

        if error_correction_type == ErrorCorrectionType.HAMMING:
            return HammingErrorCorrection()

        if error_correction_type == ErrorCorrectionType.REED_SOLOMON:
            return ReedSolomonErrorCorrection()

        raise ValueError('Could not get Error Correction')
