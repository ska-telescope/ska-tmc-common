"""
Run this Python3 script on your local machine like this:
python3 test_device.py test -v4 -nodb -port 45678 -dlist test/device/1

Then connect to the Device from the same machine like this in iTango:
dp = tango.DeviceProxy('tango://127.0.0.1:45678/test/device/1#dbase=no')
"""
# pylint: disable=broad-exception-caught
from tango import DevDouble, DevState, DevVoid
from tango.server import Device, attribute, command, run

from ska_tmc_common.test_helpers.helper_cm_and_event_receiver import LOGGER


class TestDevice(Device):
    """Test device for testing event channel failure"""

    def __init__(self, cl, name):
        super().__init__(cl, name)
        self.__my_ro_attribute_value = 1.2345
        self.__my_rw_attribute_value = 5.4321

    def init_device(self):
        super().init_device()
        self.__my_ro_attribute_value = 1.2345
        self.__my_rw_attribute_value = 5.4321
        self.set_change_event("State", True, False)
        self.set_change_event("my_ro_attribute", True, False)
        self.set_change_event("my_rw_attribute", True, False)
        self.set_state(DevState.ON)

    @attribute(dtype=DevDouble, rel_change=0.1)
    def my_ro_attribute(self) -> DevDouble:
        """Simple read only attribute"""
        return self.__my_ro_attribute_value

    @command(dtype_in=DevDouble, dtype_out=DevVoid)
    def modify_ro_attribute_value(self, new_value: DevDouble) -> DevVoid:
        """Simple commmand to modify read only attribute"""
        self.__my_ro_attribute_value = new_value
        LOGGER.info("Pushing event for my_ro_attribute: %s", new_value)
        try:
            self.push_change_event("my_ro_attribute", new_value)
        except Exception as exception:
            LOGGER.exception(
                "Exception occured while trying to push the event: %s",
                exception,
            )
        else:
            LOGGER.info("No exception")

    @attribute(dtype=DevDouble, rel_change=0.1)
    def my_rw_attribute(self) -> DevDouble:
        """Simple read write attribute"""
        return self.__my_rw_attribute_value

    @my_rw_attribute.write
    def my_rw_attribute(self, value: DevDouble = None) -> DevVoid:
        """Write method for attribute"""
        self.__my_rw_attribute_value = value
        LOGGER.info("Pushing event for my_rw_attribute: %s", value)
        try:
            self.push_change_event("my_rw_attribute", value)
        except Exception as exception:
            LOGGER.exception(
                "Exception occured while trying to push the event: %s",
                exception,
            )
        else:
            LOGGER.info("No exception")


def main(args=None, **kwargs):
    """Main function"""
    return run((TestDevice,), *args, **kwargs)


if __name__ == "__main__":
    main()
