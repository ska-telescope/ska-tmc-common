# -*- coding: utf-8 -*-
#
# This file is part of the ska-tmc-common project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" 
This is the Tango Server Helper module of Tango Interface Layer. This module implements a class
TangoServerHelper which helps in operations like getting and setting attributes and properties of
the Tango device.
"""
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType, Database
from tango.server import run,attribute, command, device_property
import logging

class TangoServerHelper:
    """
    This class provides APIs to help performing role of Tango device server.
    """
    __instance = None

    def __init__(self):
        """Private constructor of the class""" 
        if TangoServerHelper.__instance is not None:
            raise Exception("This is singletone class")
        else:
            TangoServerHelper.__instance = self
        self.device = None
        self.database = Database()
    
    @staticmethod
    def get_instance():
        """
        Returns instance object of TangoServerHelper class. Creates one if the object does 
        not exist.

        :param: None.

        :return: object of TangoServerHelper class
        """
        if TangoServerHelper.__instance is None:
            TangoServerHelper()
        return TangoServerHelper.__instance

    def read_property(self, property_name):
        """
        Returns the value of given Tango device property

        :param:
            property_name: String. Name of the Tango device property

        :return: Value of the device property

        :throws: Devfailed exception in case of error
        """
        try:
            device_name = self.device.get_name()
            return self.database.get_device_property(device_name, property_name)
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(dev_failed,
                "Failed to read property",
                str(dev_failed),
                "TangoServerHelper.read_property()",
                tango.ErrSeverity.ERR)
    
    def write_property(self, property_name, value):
        """
        Sets the value to a given device property

        :param: 
            property_name: String. Name of the Tango device property

            value: Value of the property to be set

        :return:None
    
        :throws: KeyError
                 ValueError 
        """
        try:
            device_name = self.device.get_name()
            property_map = {}
            property_map[property_name] = value
            self.database.put_device_property(device_name, property_map)  
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(dev_failed,
                "Failed to write property",
                str(dev_failed),
                "TangoServerHelper.write_property()",
                tango.ErrSeverity.ERR)      
        except KeyError as key_error:
            tango.Except.re_throw_exception(key_error,
                "Failed to write property",
                str(key_error),
                "TangoServerHelper.write_property()",
                tango.ErrSeverity.ERR)     
        except ValueError as val_error:
            tango.Except.re_throw_exception(val_error,
                "Failed to write property",
                str(val_error),
                "TangoServerHelper.write_property()",
                tango.ErrSeverity.ERR)  

    def get_status(self):
        """
        Returns value of the Status attribute of the Tango device.

        :param: None

        :return: String. The Status value of the Tango device.

        :throws: Devfailed exception in case of error.
        """
        try:
            return self.device.get_status()
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(dev_failed,
                "Failed to get status .",
                str(dev_failed),
                "TangoServerHelper.get_status()",
                tango.ErrSeverity.ERR)      

    def set_status(self, new_status):
        """
        Sets the Status attribute of the Tango device with given value.

        :param:
            new_status: String. New value for Status attribute.

        :return: None.

        :throws: Devfailed exception in case of error.
        """
        try:
            self.device.set_status(new_status)
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(dev_failed,
                "Failed to set status .",
                str(dev_failed),
                "TangoServerHelper.set_status()",
                tango.ErrSeverity.ERR)      

    def get_state(self):
        """
        Returns value of the State attribute of the Tango device.

        :param: None

        :return: String. The State value of the Tango device.

        :throws: Devfailed exception in case of error.
        """
        try:
            return self.device.get_state()
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(dev_failed,
                "Failed to get state .",
                str(dev_failed),
                "TangoServerHelper.get_state()",
                tango.ErrSeverity.ERR)      

    def set_state(self, new_state):
        """
        Sets the State attribute of the Tango device with given value.

        :param:
            new_state: DevEnum. New value for State attribute.

        :return: None.

        :throws: Devfailed exception in case of error.
        """
        try:
            self.device.set_state(new_state)
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(dev_failed,
                "Failed to set state .",
                str(dev_failed),
                "TangoServerHelper.set_state()",
                tango.ErrSeverity.ERR)      

