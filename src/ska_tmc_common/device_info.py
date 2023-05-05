import json
import threading
from typing import Any

from ska_tango_base.control_model import HealthState, ObsState
from tango import DevState

from ska_tmc_common.enum import DishMode, PointingState


def dev_state_2_str(value: DevState) -> str:
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
    def __init__(self, dev_name: str, _unresponsive: bool = False) -> None:
        self.dev_name = dev_name
        self.state: DevState = DevState.UNKNOWN
        self.health_state: HealthState = HealthState.UNKNOWN
        self._ping: int = -1
        self.last_event_arrived = None
        self.exception = None
        self._unresponsive = _unresponsive
        self.lock = threading.Lock()

    def from_dev_info(self, dev_info) -> None:
        self.dev_name = dev_info.dev_name
        self.state = dev_info.state
        self.health_state = dev_info.health_state
        self.ping = dev_info.ping
        self.last_event_arrived = dev_info.last_event_arrived
        self.lock = dev_info.lock

    def update_unresponsive(self, value: bool, exception: str = "") -> None:
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
    def ping(self) -> int:
        """Return the ping value for current device

        :return: ping value for device
        :rtype: int
        """
        return self._ping

    @ping.setter
    def ping(self, value: int) -> None:
        """Updates the ping value for current device

        :param value: updated ping value for device
        :type value: int
        """
        self._ping = value

    @property
    def unresponsive(self) -> bool:
        """
        Return whether this device is currently unresponsive.

        :return: whether this device is faulting
        :rtype: bool
        """
        return self._unresponsive

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DeviceInfo):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
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
    def __init__(self, dev_name: str, _unresponsive: bool = False) -> None:
        super(SubArrayDeviceInfo, self).__init__(dev_name, _unresponsive)
        self.id = -1
        self.resources = []
        self.obs_state = ObsState.EMPTY

    def from_dev_info(self, subarray_device_info) -> None:
        super().from_dev_info(subarray_device_info)
        if isinstance(subarray_device_info, SubArrayDeviceInfo):
            self.id = subarray_device_info.id
            self.resources = subarray_device_info.resources
            self.obs_state = subarray_device_info.obs_state

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SubArrayDeviceInfo) or isinstance(
            other, DeviceInfo
        ):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
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
    def __init__(self, dev_name: str, _unresponsive: bool = False) -> None:
        super().__init__(dev_name, _unresponsive)
        self.receive_addresses = ""

    def from_dev_info(self, sdp_subarray_device_info) -> None:
        super().from_dev_info(sdp_subarray_device_info)
        if isinstance(sdp_subarray_device_info, SdpSubarrayDeviceInfo):
            self.receive_addresses = sdp_subarray_device_info.receive_addresses

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SdpSubarrayDeviceInfo) or isinstance(
            other, DeviceInfo
        ):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        super_dict = super().to_dict()
        super_dict["receiveAddresses"] = self.receive_addresses
        return super_dict


class DishDeviceInfo(DeviceInfo):
    def __init__(self, dev_name: str, _unresponsive: bool = False) -> None:
        super().__init__(dev_name, _unresponsive)
        self.id = -1
        self.pointing_state = PointingState.NONE
        self._dish_mode = DishMode.UNKNOWN
        self.rx_capturing_data = 0
        self.achieved_pointing = []
        self.desired_pointing = []

    @property
    def dish_mode(self) -> DishMode:
        """Returns the dish mode value for Dish master device"""
        return self._dish_mode

    @dish_mode.setter
    def dish_mode(self, value: DishMode) -> None:
        """Sets the value of dish mode for Dish master device"""
        if self._dish_mode != value:
            self._dish_mode = value

    def from_dev_info(self, dish_device_info) -> None:
        super().from_dev_info(dish_device_info)
        if isinstance(dish_device_info, DishDeviceInfo):
            self.id = dish_device_info.id
            self.pointing_state = dish_device_info.pointing_state
            self.dishMode = dish_device_info._dish_mode
            self.rx_capturing_data = dish_device_info.rx_capturing_data
            self.achieved_pointing = dish_device_info.achieved_pointing
            self.desired_pointing = dish_device_info.desired_pointing

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DishDeviceInfo) or isinstance(other, DeviceInfo):
            return self.dev_name == other.dev_name
        else:
            return False

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        super_dict = super().to_dict()
        super_dict["id"] = self.id
        super_dict["pointingState"] = str(PointingState(self.pointing_state))
        super_dict["dishMode"] = str(DishMode(self.dishMode))
        super_dict["rxCapturingData"] = self.rx_capturing_data
        super_dict["achievedPointing"] = self.achieved_pointing
        super_dict["desiredPointing"] = self.desired_pointing
        return super_dict
