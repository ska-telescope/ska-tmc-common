from enum import IntEnum, unique


@unique
class PointingState(IntEnum):
    NONE = 0
    READY = 1
    SLEW = 2
    TRACK = 3
    SCAN = 4
    UNKNOWN = 5


@unique
class DishMode(IntEnum):
    UNKNOWN = 0
    OFF = 1
    STARTUP = 2
    SHUTDOWN = 3
    STANDBY_LP = 4
    STANDBY_FP = 5
    STOW = 6
    CONFIG = 7
    OPERATE = 8
    MAINTENANCE = 9
    FORBIDDEN = 10
    ERROR = 11


@unique
class TimeoutState(IntEnum):
    """Enum class for keeping track of timeout state.
    Has 2 values according to the state of timer.

    :NOT_OCCURED: Specifics timer is either running or has been canceled.
    :OCCURED: Specifies the timeout has occured and corresponding method was
        called.
    """

    NOT_OCCURED = 0
    OCCURED = 1
