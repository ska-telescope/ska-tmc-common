"""
This module includes methods for common attributes.
"""

# pylint: disable=duplicate-code
import json
from typing import Any

from ska_tango_base import SKABaseDevice
from tango.server import attribute, device_property


# pylint: disable=invalid-name
class TMCBaseDevice(SKABaseDevice):
    """
    Class for common attributes.
    """

    # -----------------
    # Device Properties
    # -----------------
    SleepTime = device_property(dtype="DevFloat", default_value=1)

    # -----------------
    # Attributes
    # -----------------

    @attribute(
        dtype="DevString",
        doc="Json String representing the last device info changed in the \
            internal model.",
    )
    def lastDeviceInfoChanged(self):
        """
        Returns last device info changed in the internal model.
        :return: last device information changed
        """
        return self.last_device_info_changed

    @attribute(
        dtype="DevString",
        doc="Json String representing the entire internal model transformed \
            for better reading.",
    )
    def transformedInternalModel(self) -> str:
        """
        Returns entire internal model transformed for better reading
        :return: internal model transformed
        """
        return self.transformedInternalModel_read()

    def transformedInternalModel_read(self) -> str:
        """
        This method consists of basic  read implementation
        of transformedInternalModel and
        must be overloaded to add additional values to result dictionary.
        Returns json string with device data.
        :return: result json string with device data
        Sample Output:
        {'mccs':{'state':'DevState.UNKNOWN','healthState':
        'HealthState.UNKNOWN', 'ping':'-1','last_event_arrived':'None',
        'unresponsive':'False','exception':'None',
        'id':-1,'pointingState':'PointingState.NONE'}}
        """
        json_model = json.loads(self.component_manager.component.to_json())
        result = {}
        if (
            "TmcLeafNodeComponentManager"
            not in self.component_manager.__class__.__bases__
        ):
            for dev in json_model["devices"]:
                dev_name = dev["dev_name"]
                del dev["dev_name"]
                result[dev_name] = dev
        else:
            dev = json_model["device"]
            dev_name = dev["dev_name"]
            del dev["dev_name"]
            result[dev_name] = dev
        return json.dumps(result)

    @attribute(
        dtype="DevString",
        doc="Json String representing the entire internal model.",
    )
    def internalModel(self) -> str:
        """
        Returns entire internal model
        :return: internal model transformed
        """
        return self.internalModel_read()

    def internalModel_read(self) -> str:
        """
        This method consists of basic  read implementation of InternalModel
        and must be overloaded to add additional attribute values to internal
        model. Returns json string representing internal model with basic
        attributes only.
        :return: json string representing internal model
        with basic attributes only
        Sample Output:
        {"subarray_health_state":"HealthState.UNKNOWN",
        "devices":[{"dev_name":"mccs","state":"DevState.UNKNOWN",
        "healthState":"HealthState.UNKNOWN","ping":"-1",
        "last_event_arrived":"None","unresponsive":"False",
        "exception":"None","id":-1,"pointingState":"PointingState.NONE"}]}
        """
        return self.component_manager.component.to_json()

    def create_component_manager(self):
        """
        Create and return a component manager for this device.

        :raises NotImplementedError: for no implementation
        """
        raise NotImplementedError(
            "TMCBaseDevice is abstract; implement"
            "'create_component_manager` method in "
            "a subclass."
        )

    def push_change_archive_events(
        self, attribute_name: str, value: Any
    ) -> None:
        """Method to push change event and archive event
        of the given attribute.

        Args:
            attribute_name (str): Attribute name
            value (Any): Attribute value need to be pushed
        """
        self.push_change_event(attribute_name, value)
        self.push_archive_event(attribute_name, value)
