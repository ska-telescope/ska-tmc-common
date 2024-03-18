"""
This module provdevice_id es us the information about the devices
"""
import json
import threading
from typing import Any

from ska_tango_base.control_model import HealthState, ObsState
from tango import DevState

from ska_tmc_common.enum import Band, DishMode, PointingState


def dev_state_2_str(value: DevState) -> str:
    """
    Converts device state to string datatype.
    :return: DevState
    """
    if value == DevState.ON:
        return "DevState.ON"
    if value == DevState.OFF:
        return "DevState.OFF"
    if value == DevState.CLOSE:
        return "DevState.CLOSE"
    if value == DevState.OPEN:
        return "DevState.OPEN"
    if value == DevState.INSERT:
        return "DevState.INSERT"
    if value == DevState.EXTRACT:
        return "DevState.EXTRACT"
    if value == DevState.MOVING:
        return "DevState.MOVING"
    if value == DevState.STANDBY:
        return "DevState.STANDBY"
    if value == DevState.FAULT:
        return "DevState.FAULT"
    if value == DevState.INIT:
        return "DevState.INIT"
    if value == DevState.RUNNING:
        return "DevState.RUNNING"
    if value == DevState.ALARM:
        return "DevState.ALARM"
    if value == DevState.DISABLE:
        return "DevState.DISABLE"
    return "DevState.UNKNOWN"


# pylint: disable=too-many-instance-attributes
class DeviceInfo:
    """
    Provides different information about the device.
    Such as HealthState, DevState, availability
    """

    def __init__(self, dev_name: str, _unresponsive: bool = False) -> None:
        self.dev_name = dev_name
        self.state: DevState = DevState.UNKNOWN
        self.health_state: HealthState = HealthState.UNKNOWN
        self.device_availability = False
        self._ping: int = -1
        self.last_event_arrived = None
        self.exception = None
        self._unresponsive = _unresponsive
        self.lock = threading.Lock()
        self._source_dish_vcc_config = ""
        self._dish_vcc_config = ""

    def from_dev_info(self, dev_info) -> None:
        """
        This method makes a copy of DeviceInfo object
        from another DeviceInfo object.
        """
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
            self.device_availability = False
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
    def source_dish_vcc_config(self) -> str:
        """
        Returns the source_dish_vcc_config value for Dish master device
        :return: source_dish_vcc_config value
        """
        return self._source_dish_vcc_config

    @source_dish_vcc_config.setter
    def source_dish_vcc_config(self, value: str):
        """Sets the value of source_dish_vcc_config  for Dish master device"""
        if self._source_dish_vcc_config != value:
            self._source_dish_vcc_config = value

    @property
    def dish_vcc_config(self) -> str:
        """
        Returns the dish_vcc_config  value for Dish master device
        :return: dish_vcc_config value
        """
        return self._dish_vcc_config

    @dish_vcc_config.setter
    def dish_vcc_config(self, value: str):
        """Sets the value of dish_vcc_config attribute value
        for Dish master device"""
        if self._dish_vcc_config != value:
            self._dish_vcc_config = value

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
        return False

    def to_json(self) -> str:
        """
        This method returns the json encoded string.
        :return: json encoded string
        :rtype:str
        """
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        """
        Converts input to dictionary.
        :return: result- device information
        :rtype:dict
        """
        result = {
            "dev_name": self.dev_name,
            "state": dev_state_2_str(DevState(self.state)),
            "healthState": str(HealthState(self.health_state)),
            "ping": str(self.ping),
            "last_event_arrived": str(self.last_event_arrived),
            "unresponsive": str(self.unresponsive),
            "exception": str(self.exception),
            "isSubarrayAvailable": self.device_availability,
        }
        return result


class SubArrayDeviceInfo(DeviceInfo):
    """
    Gives subarray devices information
    """

    def __init__(self, dev_name: str, _unresponsive: bool = False) -> None:
        super().__init__(dev_name, _unresponsive)
        self.device_id = -1
        self.resources = []
        self.obs_state = ObsState.EMPTY

    def from_dev_info(self, dev_info) -> None:
        super().from_dev_info(dev_info)
        if isinstance(dev_info, SubArrayDeviceInfo):
            self.device_id = dev_info.device_id
            self.resources = dev_info.resources
            self.obs_state = dev_info.obs_state

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, (DeviceInfo, SubArrayDeviceInfo)):
            return self.dev_name == other.dev_name
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
        super_dict["device_id "] = self.device_id
        super_dict["obsState"] = str(ObsState(self.obs_state))
        return super_dict


class SdpSubarrayDeviceInfo(SubArrayDeviceInfo):
    """
    Gives SDP subarray device information
    """

    def __init__(self, dev_name: str, _unresponsive: bool = False) -> None:
        super().__init__(dev_name, _unresponsive)
        self.receive_addresses = ""

    def from_dev_info(self, dev_info) -> None:
        super().from_dev_info(dev_info)
        if isinstance(dev_info, SdpSubarrayDeviceInfo):
            self.receive_addresses = dev_info.receive_addresses

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, (DeviceInfo, SdpSubarrayDeviceInfo)):
            return self.dev_name == other.dev_name
        return False

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        super_dict = super().to_dict()
        super_dict["receiveAddresses"] = self.receive_addresses
        return super_dict


class DishDeviceInfo(DeviceInfo):
    """
    Gives Dishes device information
    """

    def __init__(self, dev_name: str, _unresponsive: bool = False) -> None:
        super().__init__(dev_name, _unresponsive)
        self.device_id = -1
        self.pointing_state = PointingState.NONE
        self._dish_mode = DishMode.UNKNOWN
        self.configured_band = Band.NONE
        self.rx_capturing_data = 0
        self.achieved_pointing = []
        self.program_track_table = []
        self._kvalue = 0

    @property
    def kvalue(self) -> int:
        """
        Returns the k value for Dish master device
        :return: kvalue for Dish Master
        """
        return self._kvalue

    @kvalue.setter
    def kvalue(self, value: int):
        """Sets the value of k value for Dish master device"""
        if self._kvalue != value:
            self._kvalue = value

    @property
    def dish_mode(self) -> DishMode:
        """
        Returns the dish mode value for Dish master device
        :return: dish mode for Dish Master
        """
        return self._dish_mode

    @dish_mode.setter
    def dish_mode(self, value: DishMode) -> None:
        """Sets the value of dish mode for Dish master device"""
        if self._dish_mode != value:
            self._dish_mode = value

    # pylint: disable=protected-access
    def from_dev_info(self, dev_info) -> None:
        super().from_dev_info(dev_info)
        if isinstance(dev_info, DishDeviceInfo):
            self.device_id = dev_info.device_id
            self.pointing_state = dev_info.pointing_state
            self.dish_mode = dev_info._dish_mode
            self.configured_band = dev_info.configured_band
            self.rx_capturing_data = dev_info.rx_capturing_data
            self.achieved_pointing = dev_info.achieved_pointing
            self.program_track_table = dev_info.program_track_table

    # pylint: enable=protected-access

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, (DishDeviceInfo, DeviceInfo)):
            return self.dev_name == other.dev_name
        return False

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict:
        super_dict = super().to_dict()
        super_dict["device_id"] = self.device_id
        super_dict["pointingState"] = str(PointingState(self.pointing_state))
        super_dict["dishMode"] = str(DishMode(self.dish_mode))
        super_dict["configuredBand"] = str(Band(self.configured_band))
        super_dict["rxCapturingData"] = self.rx_capturing_data
        super_dict["achievedPointing"] = self.achieved_pointing
        super_dict["program_track_table"] = self.program_track_table
        return super_dict
