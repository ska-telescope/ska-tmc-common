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
    # ska-mid-dish-manager is having dependency conflicts with ska-tmc-common
    # So redefined DishMode enum, which reflects the ska-mid-dish-manager DishMode enum.
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
class ExceptionState(IntEnum):
    """Enum class for keeping track of exception state.
    Has 3 values according to occurance of exceptions.

    :COMMAND_IN_PROGRESS: Specifics the command still being in progress.
    :COMMAND_COMPLETE: Specifies that command has completed execution without
        raising any exceptions.
    :EXCEPTION_OCCURED: Specifies that an exception has occured during command
        run.
    """

    COMMAND_IN_PROGRESS = 0
    COMMAND_COMPLETE = 1
    EXCEPTION_OCCURED = 2
