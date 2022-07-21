from enum import Enum, IntEnum, unique

from ska_tmc_common.liveliness_probe import (
    MultiDeviceLivelinessProbe,
    SingleDeviceLivelinessProbe,
)


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
class LP(Enum):
    OFF = False
    SINGLE_DEVICE = SingleDeviceLivelinessProbe
    MULTI_DEVICE = MultiDeviceLivelinessProbe
