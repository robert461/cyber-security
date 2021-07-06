from enum import Enum


class EvalReportChoice(str, Enum):

    FIRST = 'First'
    SECOND = 'Second'
    BOTH = 'Both'
    NONE = 'None'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
