"""
Sample SKA Tango device
"""
# -*- coding: utf-8 -*-
#
# This file is part of the Sample project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PyTango imports
import tango
from tango import DebugIt, AttrWriteType, ApiUtil
from tango.server import run, attribute, command, device_property

# Additional import
from ska.base.commands import ResultCode
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState

from tmc.common.tango_server_helper import TangoServerHelper

__all__ = [
    "SKASampleDevice",
    "main",
    "AttributeAccess",
    "PropertyAccess",
    "DeviceData"
]

class SKASampleDevice(SKABaseDevice):
    """
    Sample device for SKA
    """

    # -----------------
    # Device Properties
    # -----------------
    TestProperty = device_property(
        dtype='str',
    )

    # ----------
    # Attributes
    # ----------
    DoubleAttrib = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
    )

    StrAttrib = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    # ---------------
    # General methods
    # ---------------
    class InitCommand(SKABaseDevice.InitCommand):
        """
        Class to handle device initialization as per SKA lmc base classes implementation
        """

        def do(self):
            super().do()
            device = self.target

            ## Dictionary to maintain mapping of attributes and their values
            this_server.attribute_map = {}

            # ------------------
            # Instantiate object of TangoServerHelper class
            # ------------------
            this_server = TangoServerHelper.get_instance()
            this_server.device = device



            self.logger.info("Initialization successful")
            return (ResultCode.OK, const.STR_CSPSALN_INIT_SUCCESS)

    def always_executed_hook(self):
        pass

    def delete_device(self):
        pass

    # ------------------
    # Attributes methods
    # ------------------
    def read_DoubleAttrib(self):
        return self.attribute_map["DoubleAttrib"]

    def write_DoubleAttrib(self, value):
        self.attribute_map["DoubleAttrib"] = value

    def read_StrAttrib(self):
        return self.attribute_map["StrAttrib"]

    def write_StrAttrib(self, value):
        self.attribute_map["StrAttrib"] = value

    # --------
    # Commands
    # --------
    def is_AttributeAccess_allowed(self):
        handler = self.get_command_object("AttributeAccess")
        return handler.check_allowed()

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def AttributeAccess(self, argin):
        handler = self.get_command_object("AttributeAccess")
        handler(argin)

    def is_PropertyAccess_allowed(self):
        handler = self.get_command_object("PropertyAccess")
        return handler.check_allowed()

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def PropertyAccess(self, argin):
        handler = self.get_command_object("AttributeAccess")
        handler(argin)

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()
        device_data = DeviceData.get_instance()
        args = (device_data, self.state_model, self.logger)

        self.register_command_object("AttributeAccess", AttributeAccessCommand(*args))
        self.register_command_object("PropertyAccess", PropertyAccessCommand(*args))


# ---------------------------------------------
# Command classes that implement business logic
# ---------------------------------------------
class AttributeAccessCommand():
    def is_AttributeAccessCommand_allowed(self):
        return True

    def do(argin):
        this_tango_device = TangoServerHelper.get_instance()
        device_data = DeviceData.get_instance()

        # read attribute value
        double_data = this_device.read_attribute("DoubleAttrib")
        log_message = f"double_data read: {double_data}"
        self.logger.info(log_message)

        string_data = this_device.read_attribute("StrAttrib")
        log_message = f"string_data read: {string_data}"
        self.logger.info(log_message)

        ## perform business operations
        double_data += device_data.double_common_data
        log_message = f"double_data new value: {double_data}"
        self.logger.info(log_message)

        # write attribute value
        this_tango_device.write_attribute("DoubleAttrib", double_data)
        this_tango_device.write_attribute("StrAttrib", argin)

class PropertyAccessCommand():
    def is_PropertyAccessCommand_allowed(self):
        return True

    def do():
        this_tango_device = TangoServerHelper.get_instance()
        device_data = DeviceData.get_instance()

        # read property value
        property_value = this_device.read_property("TestProperty")

        # perform business operations
        new_property_value = property_value + device_data.string_common_data

        # write property value
        this_tango_device.write_property("TestProperty", property_value)

class DeviceData:
    """
    This class contains the data common across multiple functionalities. This 
    is a singleton class.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class"""
        if DeviceData.__instance is not None:
            raise Exception("This is singletone class")
        else:
            DeviceData.__instance = self

        self.string_common_data = "default value"
        self.double_common_data = 5

    @staticmethod
    def get_instance():
        if DeviceData.__instance is None:
            DeviceData()
        return DeviceData.__instance

# ----------
# Run server
# ----------
def main(args=None, **kwargs):
    return run((CspSubarrayLeafNode,), args=args, **kwargs)

if __name__ == "__main__":
    main()
