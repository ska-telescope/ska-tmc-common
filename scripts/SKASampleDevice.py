"""
Sample SKA Tango device
"""
# -*- coding: utf-8 -*-
#
# This file is part of the ska-tmc-common project
# This code is as a sample of design pattern of a SKA device.
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

# PyTango imports
import tango
from tango import DebugIt, AttrWriteType, ApiUtil
from tango.server import run, attribute, command, device_property

# Additional import
from ska.base.commands import ResultCode, BaseCommand
from ska.base import SKABaseDevice
from ska.base.control_model import HealthState, ObsState

from tmc.common.tango_server_helper import TangoServerHelper

__all__ = ["SKASampleDevice", "main", "AttributeAccess", "PropertyAccess", "DeviceData"]


class SKASampleDevice(SKABaseDevice):
    """
    Sample device for SKA
    """

    # -----------------
    # Device Properties
    # -----------------
    TestProperty = device_property(
        dtype="str",
    )

    # ----------
    # Attributes
    # ----------
    DoubleAttrib = attribute(
        dtype="double",
        access=AttrWriteType.READ_WRITE,
    )

    StrAttrib = attribute(
        dtype="str",
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

            # ------------------
            # Instantiate object of TangoServerHelper class
            # ------------------
            this_server = TangoServerHelper.get_instance()

            # Set tango class object as a target for TangoServerHelper class object.
            # This is to be done only once in the code.
            this_server.set_tango_class(device)

            ## Dictionary to maintain mapping of attributes and their values
            this_server._device.attr_map = {}
            this_server._device.attr_map["DoubleAttrib"] = 10
            this_server._device.attr_map["StrAttrib"] = "Default value"

            self.logger.info("Initialization successful")
            return (ResultCode.OK, "Device initialization successful.")

    def always_executed_hook(self):
        pass

    def delete_device(self):
        pass

    # ------------------
    # Attributes methods
    # ------------------
    def read_DoubleAttrib(self):
        return self.attr_map["DoubleAttrib"]

    def write_DoubleAttrib(self, value):
        self.attr_map["DoubleAttrib"] = value

    def read_StrAttrib(self):
        return self.attr_map["StrAttrib"]

    def write_StrAttrib(self, value):
        self.attr_map["StrAttrib"] = value

    # --------
    # Commands
    # --------
    def is_AttributeAccess_allowed(self):
        handler = self.get_command_object("AttributeAccess")
        return handler.check_allowed()

    @command(
        dtype_in="str",
    )
    @DebugIt()
    def AttributeAccess(self, argin):
        handler = self.get_command_object("AttributeAccess")
        handler(argin)

    def is_PropertyAccess_allowed(self):
        handler = self.get_command_object("PropertyAccess")
        return handler.check_allowed()

    @command(
        dtype_in="str",
    )
    @DebugIt()
    def PropertyAccess(self, argin):
        handler = self.get_command_object("PropertyAccess")
        handler(argin)

    def init_command_objects(self):
        """
        Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()

        # Instantiate the class object which contains common data members or methods
        # in the code.
        device_data = DeviceData.get_instance()
        args = (device_data, self.state_model, self.logger)

        self.register_command_object("AttributeAccess", AttributeAccessCommand(*args))
        self.register_command_object("PropertyAccess", PropertyAccessCommand(*args))


# ---------------------------------------------
# Command classes that implement business logic
# ---------------------------------------------
class AttributeAccessCommand(BaseCommand):
    def check_allowed(self):
        return True

    def do(self, argin):
        this_tango_device = TangoServerHelper.get_instance()
        device_data = DeviceData.get_instance()

        # read attribute value
        double_data = this_tango_device.read_attr("DoubleAttrib")
        log_message = f"double_data read: {double_data}"
        self.logger.info(log_message)

        string_data = this_tango_device.read_attr("StrAttrib")
        log_message = f"string_data read: {string_data}"
        self.logger.info(log_message)

        ## perform business operations
        double_data += device_data.double_common_data
        log_message = f"double_data new value: {double_data}"
        self.logger.info(log_message)

        # write attribute value
        this_tango_device.write_attr("DoubleAttrib", double_data)
        this_tango_device.write_attr("StrAttrib", argin)


class PropertyAccessCommand(BaseCommand):
    def check_allowed(self):
        return True

    def do(self, argin):
        this_tango_device = TangoServerHelper.get_instance()
        device_data = DeviceData.get_instance()

        # read property value
        property_value = this_tango_device.read_property("TestProperty")
        log_message = f"property_value: {property_value}"
        self.logger.info(log_message)

        # # perform business operations
        new_value = device_data.string_common_data + " " + argin

        # # write property value
        this_tango_device.write_property("TestProperty", new_value)

        # # read property value
        property_value = this_tango_device.read_property("TestProperty")
        log_message = f"property_value: {property_value}"
        self.logger.info(log_message)


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

        self.string_common_data = "value from business class"
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
    return run((SKASampleDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
