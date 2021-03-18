# -*- coding: utf-8 -*-
#
# This file is part of the SampleServer project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SampleDevice

Code for Tango interface layer sample.
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango import AttrWriteType
# Additional import
from tmc.common.tango_server_helper import TangoServerHelper

__all__ = ["SampleDevice", "main"]


class SampleDevice(Device):
    """
    Code for Tango interface layer sample.
    """
    __metaclass__ = DeviceMeta

    # ---------------
    # General methods
    # ---------------
       
    def always_executed_hook(self):
        pass
        

    def delete_device(self):
        pass
        
    # ------------------
    # Attributes methods
    # ------------------

    def read_testattr(self):
        return self._testattr
       
    def write_testattr(self, value):
        self._testattr = testattr
       

    def init_device(self):
        Device.init_device(self)
        self._testattr = 0
        self.set_state()

    # ----------
    # Run server
    # ----------


def main(args=None, **kwargs):

    return run((SampleDevice,), args=args, **kwargs)


if __name__ == '__main__':
    main()

# --------
# Commands
# --------

@command(
    dtype_in='str',
    )

class TestCommand(self):
    """
    Code for TestCommand command execution .
    """
    # ----------
    # Attributes
    # ----------

    test_attr = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
    )

    test_property = device_property(
        dtype='str')

    #Returns instance object of TangoServerHelper class. 
    #Creates one if the object does not exist.
    sample_server = TangoServerHelper.get_instance()
 

    def read_testattr(self):
        return self.attr_map[test_attr]
 
    def write_activityMessage(self, value):
       self.sample_server.attr_map[attribute] = value

    def do():

        #Returns the value of given device property in string type
        sample_server.get_property(test_property)

        #Sets the value to a given device property
        sample_server.set_property(test_property, "sys/tg_test/1")

        #Returns value of the status attribute of the Tango device.
        sample_server.get_status()

        #Sets the status attribute of the Tango device with given value.
        sample_server.set_status("test_attr is ON")

        #Returns value of the state attribute of the Tango device.
        sample_server.get_state()

        #Sets the state attribute of the Tango device with given value.
        sample_server.set_state(DevState.ON)
