"""
This module assigns the enum values to PointingState,
DishMode, Number of devices LivelinessProbeType, TimeoutState
"""
from enum import IntEnum, unique


@unique
class PointingState(IntEnum):
    """
    This is an enumerator class that contains PointingState values.
    """

    READY = 0
    SLEW = 1
    TRACK = 2
    SCAN = 3
    UNKNOWN = 4
    NONE = 5


@unique
class DishMode(IntEnum):
    """
    This class assigns the enum value to DishMode.
    """

    # ska-mid-dish-manager is having dependency conflicts with ska-tmc-common
    # So redefined DishMode enum, which reflects the ska-mid-dish-manager
    # DishMode enum.
    # We will work out on this separately once dish manager is sorted.
    STARTUP = 0
    SHUTDOWN = 1
    STANDBY_LP = 2
    STANDBY_FP = 3
    MAINTENANCE = 4
    STOW = 5
    CONFIG = 6
    OPERATE = 7
    UNKNOWN = 8


@unique
class LivelinessProbeType(IntEnum):
    """
    This class assigns the enum value to single or multiple devices.
    """

    NONE = 0
    SINGLE_DEVICE = 1
    MULTI_DEVICE = 2


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


@unique
class FaultType(IntEnum):
    """Enum class for raising various exceptions from helper devices."""

    NONE = 0
    COMMAND_NOT_ALLOWED = 1
    FAILED_RESULT = 2
    LONG_RUNNING_EXCEPTION = 3
    STUCK_IN_INTERMEDIATE_STATE = 4
    # UNRESPONSIVE = 5
    # COMMAND_REJECTED = 6
    STUCK_IN_OBSTATE = 5
