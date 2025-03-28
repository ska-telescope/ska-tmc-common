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


class Band(IntEnum):
    """
    This is an enumerator class that contains Dish Band values.
    """

    NONE = 0
    B1 = 1
    B2 = 2
    B3 = 3
    B4 = 4
    B5a = 5  # pylint: disable=invalid-name
    B5b = 6  # pylint: disable=invalid-name
    UNKNOWN = 7


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
    COMMAND_NOT_ALLOWED_BEFORE_QUEUING = 1
    FAILED_RESULT = 2
    LONG_RUNNING_EXCEPTION = 3
    STUCK_IN_INTERMEDIATE_STATE = 4
    STUCK_IN_OBSTATE = 5
    COMMAND_NOT_ALLOWED_AFTER_QUEUING = 6
    COMMAND_NOT_ALLOWED_EXCEPTION_AFTER_QUEUING = 7
    GPM_JSON_ERROR = 8
    GPM_URI_ERROR = 9
    GPM_URI_NOT_REACHABLE = 10
    GPM_ERROR_REPORTED_BY_DISH = 11
    SDP_FAULT = 12
    SDP_BACK_TO_INITIAL_STATE = 13


@unique
class TrackTableLoadMode(IntEnum):
    """Class for track table load mode enums."""

    NEW = 0
    APPEND = 1
