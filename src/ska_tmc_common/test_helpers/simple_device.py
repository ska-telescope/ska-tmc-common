"""
Run this Python3 script on your local machine like this:
python3 simple_device.py test -v4 -nodb -port 45679 -dlist simple/device/1

Then connect to the Device from the same machine like this in iTango:
dp = tango.DeviceProxy('tango://127.0.0.1:45678/simple/device/1#dbase=no')
"""
# pylint: disable=broad-exception-caught
from tango import DevState
from tango.server import Device, run

from ska_tmc_common.test_helpers.helper_cm_and_event_receiver import (
    LOGGER,
    SimpleComponentManager,
)


class SimpleDevice(Device):
    """Test device for testing event channel failure"""

    def __init__(self, cl, name):
        super().__init__(cl, name)
        self.component_manager = self.create_component_manager()

    def init_device(self):
        super().init_device()
        self.set_state(DevState.ON)

    def create_component_manager(self) -> SimpleComponentManager:
        """Simple create method."""
        component_manager = SimpleComponentManager("test/device/1", True)
        LOGGER.info(
            "Created component manager for devices: %s",
            component_manager.devices,
        )
        return component_manager


def main(args=None, **kwargs):
    """Main function"""
    return run((SimpleDevice,), *args, **kwargs)


if __name__ == "__main__":
    main()
