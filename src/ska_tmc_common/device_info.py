"""
This module provdevice_id es us the information about the devices
"""

import json
import threading
from typing import Any

from ska_tango_base.control_model import AdminMode, HealthState, ObsState
from tango import DevState

from ska_tmc_common.enum import (
    Band,
    DishMode,
    PointingState,
    TrackTableLoadMode,
)


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
        self._state: DevState = DevState.UNKNOWN
        self._health_state: HealthState = HealthState.UNKNOWN
        self._device_availability = False
        self._ping: int = -1
        self.last_event_arrived = None
        self.exception = None
        self._unresponsive = _unresponsive
        self.lock = threading.Lock()
        self._source_dish_vcc_config = ""
        self._dish_vcc_config = ""
        self._admin_mode = None

    @property
    def state(self) -> DevState:
        """State property"""
        return self._state

    @state.setter
    def state(self, value: DevState):
        """State property setter.

        :param value: Value to be set
        :type value: `DevState`
        """
        with self.lock:
            self._state = value

    @property
    def admin_mode(self) -> DevState:
        """State property"""
        return self._admin_mode

    @admin_mode.setter
    def admin_mode(self, value: AdminMode):
        """State property setter.

        :param value: Value to be set
        :type value: `AdminMode`
        """
        with self.lock:
            self._admin_mode = value

    @property
    def health_state(self) -> HealthState:
        """HealthState property"""
        return self._health_state

    @health_state.setter
    def health_state(self, value: HealthState):
        """HealthState property setter.

        :param value: Value to be set
        :type value: `HealthState`
        """
        with self.lock:
            self._health_state = value

    @property
    def device_availability(self) -> bool:
        """DeviceAvailability property"""
        return self._device_availability

    @device_availability.setter
    def device_availability(self, value: bool):
        """DeviceAvailability property setter.

        :param value: Value to be set
        :type value: `bool`
        """
        with self.lock:
            self._device_availability = value

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
        self._obs_state = ObsState.EMPTY

    @property
    def obs_state(self) -> ObsState:
        """ObsState property"""
        return self._obs_state

    @obs_state.setter
    def obs_state(self, value: ObsState):
        """ObsState property setter.

        :param value: Value to be set
        :type value: `ObsState`
        """
        with self.lock:
            self._obs_state = value

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
        self._pointing_state = PointingState.NONE
        self._dish_mode = DishMode.UNKNOWN
        self.configured_band = Band.NONE
        self.rx_capturing_data = 0
        self.achieved_pointing = []
        self.program_track_table = []
        self._track_table_load_mode = TrackTableLoadMode.APPEND
        self._kvalue = 0
        self.scan_id = ""

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
    def pointing_state(self) -> PointingState:
        """PointingState property"""
        return self._pointing_state

    @pointing_state.setter
    def pointing_state(self, value: PointingState):
        """PointingState property setter.

        :param value: Value to be set
        :type value: `PointingState`
        """
        with self.lock:
            self._pointing_state = value

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
        with self.lock:
            self._dish_mode = value

    @property
    def track_table_load_mode(self) -> TrackTableLoadMode:
        """
        Returns the track table load mode value for Dish master device
        :return: track table load mode for Dish Master
        """
        return self._track_table_load_mode

    @track_table_load_mode.setter
    def track_table_load_mode(self, value: TrackTableLoadMode) -> None:
        """
        Sets the value of dish mode for Dish master device
        :param value: TrackTableLoadMode (NEW or APPEND)
        :value dtype: TrackTableLoadMode
        :rtype: None
        """
        with self.lock:
            self._track_table_load_mode = value

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
            self.track_table_load_mode = dev_info.track_table_load_mode

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
        super_dict["track_table_load_mode"] = self.track_table_load_mode
        return super_dict


class SdpQueueConnectorDeviceInfo:
    """
    This class gives SdpQueueConnector device info
    """

    def __init__(self) -> None:
        self._dev_name: str = ""
        self._device_availability = False
        self._ping: int = -1
        self._event_id: int = 0
        self._exception = None
        self._pointing_data: list = [0.0, 0.0, 0.0]
        self._subscribed_to_attribute = False
        self._unresponsive = False
        self._attribute_name: str = ""

    @property
    def dev_name(self) -> str:
        """Device name property"""
        return self._dev_name

    @dev_name.setter
    def dev_name(self, dev_name: str) -> None:
        """dev_name property setter.

        :param dev_name: device name to be set
        :type dev_name: `str`
        """
        self._dev_name = dev_name

    @property
    def event_id(self) -> int:
        """Event ID property"""
        return self._event_id

    @event_id.setter
    def event_id(self, event_id: int) -> None:
        """Event ID property setter.

        :param event_id:  event id to be set
        :type event_id: `int`
        """
        self._event_id = event_id

    @property
    def pointing_data(self) -> list:
        """Pointing data property"""
        return self._pointing_data

    @pointing_data.setter
    def pointing_data(self, pointing_data: list) -> None:
        """Pointing data property setter.

        :param pointing_data:  pointing data to be set
        :type pointing_data: `list`
        """
        self._pointing_data = pointing_data

    @property
    def subscribed_to_attribute(self) -> bool:
        """Subscribed to attribute property"""
        return self._subscribed_to_attribute

    @subscribed_to_attribute.setter
    def subscribed_to_attribute(self, flag: bool) -> None:
        """subscribed_to_attribute setter.

        :param flag:  flag to check subscribed to attribute or not
        :type flag: `bool`
        """
        self._subscribed_to_attribute = flag

    @property
    def attribute_name(self) -> str:
        """Attribute name property"""
        return self._attribute_name

    @attribute_name.setter
    def attribute_name(self, attribute_name: str) -> None:
        """Attribute name setter.

        :param attribute_name:  attribute_name to check
         subscribed to attribute or not
        :type attribute_name: `str`
        """
        self._attribute_name = attribute_name
