import json
import threading

from ska_tango_base.control_model import HealthState, ObsState
from tango import DevState

from ska_tmc_common.enum import DishMode, PointingState


def dev_state_2_str(value):
    if value == DevState.ON:
        return "DevState.ON"
    elif value == DevState.OFF:
        return "DevState.OFF"
    elif value == DevState.CLOSE:
        return "DevState.CLOSE"
    elif value == DevState.OPEN:
        return "DevState.OPEN"
    elif value == DevState.INSERT:
        return "DevState.INSERT"
    elif value == DevState.EXTRACT:
        return "DevState.EXTRACT"
    elif value == DevState.MOVING:
        return "DevState.MOVING"
    elif value == DevState.STANDBY:
        return "DevState.STANDBY"
    elif value == DevState.FAULT:
        return "DevState.FAULT"
    elif value == DevState.INIT:
        return "DevState.INIT"
    elif value == DevState.RUNNING:
        return "DevState.RUNNING"
    elif value == DevState.ALARM:
        return "DevState.ALARM"
    elif value == DevState.DISABLE:
        return "DevState.DISABLE"
    else:
        return "DevState.UNKNOWN"


class DeviceInfo:
    def __init__(self, dev_name: str, _unresponsive=False):
        self.dev_name = dev_name
        self.state = DevState.UNKNOWN
        self.health_state = HealthState.UNKNOWN
        self.ping = -1
        self.last_event_arrived = None
        self.exception = None
        self._unresponsive = _unresponsive
        self.lock = threading.Lock()

    def from_dev_info(self, devInfo):
        self.dev_name = devInfo.dev_name
        self.state = devInfo.state
        self.health_state = devInfo.health_state
        self.ping = devInfo.ping
        self.last_event_arrived = devInfo.last_event_arrived
        self.lock = devInfo.lock

    def update_unresponsive(self, value, exception=None):
        """
        Set device unresponsive

        :param: value unresponsive boolean
        """
        self._unresponsive = value
        self.exception = exception
        if self._unresponsive:
            self.state = DevState.UNKNOWN
            self.health_state = HealthState.UNKNOWN
            self.ping = -1

    @property
    def unresponsive(self):
        """
        Return whether this device is currently unresponsive.

        :return: whether this device is faulting
        :rtype: bool
        """
        return self._unresponsive

    def __eq__(self, other):
        if isinstance(other, DeviceInfo):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        result = {
            "dev_name": self.dev_name,
            "state": dev_state_2_str(DevState(self.state)),
            "healthState": str(HealthState(self.health_state)),
            "ping": str(self.ping),
            "last_event_arrived": str(self.last_event_arrived),
            "unresponsive": str(self.unresponsive),
            "exception": str(self.exception),
        }
        return result


class SubArrayDeviceInfo(DeviceInfo):
    def __init__(self, dev_name, _unresponsive=False):
        super(SubArrayDeviceInfo, self).__init__(dev_name, _unresponsive)
        self.id = -1
        self.resources = []
        self.obs_state = ObsState.EMPTY

    def from_dev_info(self, subarrayDevInfo):
        super().from_dev_info(subarrayDevInfo)
        if isinstance(subarrayDevInfo, SubArrayDeviceInfo):
            self.id = subarrayDevInfo.id
            self.resources = subarrayDevInfo.resources
            self.obs_state = subarrayDevInfo.obs_state

    def __eq__(self, other):
        if isinstance(other, SubArrayDeviceInfo) or isinstance(
            other, DeviceInfo
        ):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        super_dict = super().to_dict()
        result = []
        if self.resources is not None:
            for res in self.resources:
                result.append(res)
            super_dict["resources"] = result
        super_dict["resources"] = result
        super_dict["id"] = self.id
        super_dict["obsState"] = str(ObsState(self.obs_state))
        return super_dict


class SdpSubarrayDeviceInfo(SubArrayDeviceInfo):
    def __init__(self, dev_name, _unresponsive=False):
        super().__init__(dev_name, _unresponsive)
        self.receive_addresses = ""

    def from_dev_info(self, sdpSubarrayDeviceInfo):
        super().from_dev_info(sdpSubarrayDeviceInfo)
        if isinstance(sdpSubarrayDeviceInfo, SdpSubarrayDeviceInfo):
            self.receive_addresses = sdpSubarrayDeviceInfo.receive_addresses

    def __eq__(self, other):
        if isinstance(other, SdpSubarrayDeviceInfo) or isinstance(
            other, DeviceInfo
        ):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        super_dict = super().to_dict()
        super_dict["receiveAddresses"] = self.receive_addresses
        return super_dict


class DishDeviceInfo(DeviceInfo):
    def __init__(self, dev_name, _unresponsive=False):
        super().__init__(dev_name, _unresponsive)
        self.id = -1
        self.pointing_state = PointingState.NONE
        self.dish_mode = DishMode.UNKNOWN
        self.rx_capturing_data = 0
        self.achieved_pointing = []
        self.desired_pointing = []

    def from_dev_info(self, dishDeviceInfo):
        super().from_dev_info(dishDeviceInfo)
        if isinstance(dishDeviceInfo, DishDeviceInfo):
            self.id = dishDeviceInfo.id
            self.pointing_state = dishDeviceInfo.pointing_state
            self.dish_mode = dishDeviceInfo.dish_mode
            self.rx_capturing_data = dishDeviceInfo.rx_capturing_data
            self.achieved_pointing = dishDeviceInfo.achieved_pointing
            self.desired_pointing = dishDeviceInfo.desired_pointing

    def __eq__(self, other):
        if isinstance(other, DishDeviceInfo) or isinstance(other, DeviceInfo):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        super_dict = super().to_dict()
        super_dict["id"] = self.id
        super_dict["pointingState"] = str(PointingState(self.pointing_state))
        super_dict["dishMode"] = str(DishMode(self.dish_mode))
        super_dict["rxCapturingData"] = self.rx_capturing_data
        super_dict["achievedPointing"] = self.achieved_pointing
        super_dict["desiredPointing"] = self.desired_pointing
        return super_dict
