"""Constants
"""

import json

ON = "On"
OFF = "Off"
STAND_BY = "Standby"
ASSIGN_RESOURCES = "AssignResources"
CONFIGURE = "Configure"
CONFIGURE_BAND_2 = "ConfigureBand2"
CONFIGURE_BAND_1 = "ConfigureBand1"
RELEASE_RESOURCES = "ReleaseResources"
ABORT = "Abort"
APPLY_POINTING_MODEL = "ApplyPointingModel"
RESTART = "Restart"
RESTARTSUBARRAY = "RestartSubarray"
END = "End"
OBS_RESET = "ObsReset"
SCAN = "Scan"
END_SCAN = "EndScan"
RELEASE_ALL_RESOURCES = "ReleaseAllResources"
GO_TO_IDLE = "GoToIdle"
SLEW = "Slew"
RESET = "Reset"
CSP_SUBARRAY_DEVICE_LOW = "low-csp/subarray/01"
CSP_SUBARRAY_DEVICE_MID = "mid-csp/subarray/01"
ALLOCATE = "Allocate"
RELEASE = "Release"
SETADMINMODE = "SetAdminMode"
TRACK = "Track"
TRACK_STOP = "TrackStop"
ABORT_COMMANDS = "AbortCommands"
SET_STANDBY_FP_MODE = "SetStandbyFPMode"
SET_STANDBY_LP_MODE = "SetStandbyLPMode"
SET_STOW_MODE = "SetStowMode"
SET_OPERATE_MODE = "SetOperateMode"
SKA_EPOCH = "1999-12-31T23:59:28Z"
RECEIVE_ADDRESSES_LOW = json.dumps(
    {
        "science_A": {
            "vis0": {
                "function": "visibilities",
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.2"]],
                "port": [[0, 9000, 1], [2000, 9000, 1]],
            }
        },
        "target:a": {
            "vis0": {
                "function": "visibilities",
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.2"]],
                "port": [[0, 9000, 1], [20, 9001, 1]],
            }
        },
        "calibration:b": {
            "vis0": {
                "function": "visibilities",
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.2"]],
                "port": [[0, 9000, 1], [20, 9001, 1]],
            }
        },
    }
)

RECEIVE_ADDRESSES_MID = json.dumps(
    {
        "science_A": {
            "vis0": {
                "function": "visibilities",
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.2"]],
                "port": [[0, 9000], [20, 9001]],
            }
        },
        "target:a": {
            "vis0": {
                "function": "visibilities",
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.2"]],
                "port": [[0, 9000], [20, 9001]],
            }
        },
        "calibration:b": {
            "vis0": {
                "function": "visibilities",
                "host": [[0, "192.168.0.1"], [2000, "192.168.0.2"]],
                "port": [[0, 9000], [20, 9001]],
            }
        },
    }
)
