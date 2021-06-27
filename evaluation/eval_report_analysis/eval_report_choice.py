from enum import Enum


class EvalReportChoice(str, Enum):

    TRUE = '1'
    FALSE = '2'
    BOTH = 'b'
    NONE = 'n'
