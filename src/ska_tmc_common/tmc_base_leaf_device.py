"""
This module includes methods for common attributes.
"""

# pylint: disable=duplicate-code
from typing import Any

from ska_tango_base import SKABaseDevice


class TMCBaseLeafDevice(SKABaseDevice):
    """
    Class for common methods of leaf devices.
    """

    def create_component_manager(self):
        """
        Create and return a component manager for this device.

        :raises NotImplementedError: for no implementation
        """
        raise NotImplementedError(
            "TMCBaseLeafDevice is abstract; implement"
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
