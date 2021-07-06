from enum import Enum


class EvalReportResult(str, Enum):

    TRUE = 'True'
    FALSE = 'False'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
