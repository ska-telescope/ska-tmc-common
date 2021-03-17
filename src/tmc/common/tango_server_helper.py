# -*- coding: utf-8 -*-
#
# This file is part of the ska-tmc-common project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Tango Server

"""
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType, Database
from tango.server import run,attribute, command, device_property
import logging

class TangoServerHelper:
    """
    Helper class for TangoServer API
    """
    __instance = None

    def __init__(self):
        """Private constructor of the class""" 
        if TangoServerHelper.__instance is not None:
            raise Exception("This is singletone class")
        else:
            TangoServerHelper.__instance = self
        self.device = None
        # self.prop_map = {}
        self.database = Database()
    
    @staticmethod
    def get_instance():
        """
        Returns instance of TangoServerHelper class
        """
        if TangoServerHelper.__instance is None:
            TangoServerHelper()
        return TangoServerHelper.__instance

    def read_property(self, prop_name):
        """
        Returns the value of given Tango device property

        :param:
            prop_name: String. Name of the Tango device property

        :return: Value of the device property.

        """
        try:
            # return self.device.prop_map[prop]
            devname = self.device.get_name()
            return self.database.get_device_property(devname, prop_name)
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(dev_failed,
                "Failed to read propert .",
                str(dev_failed),
                "TangoServerHelper.read_property()",
                tango.ErrSeverity.ERR)
    
    def write_property(self, prop_name, value):
        """
        Sets the value to a given device property

        :param: 
            prop_name: String. Name of the Tango device property

            value: Value of the property to be set.
        """
        try:
            devname = self.device.get_name()
            prop = {}
            prop[prop_name] = value
            self.database.put_device_property(devname, prop)        
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(dev_failed,
                "Failed to write propert .",
                str(dev_failed),
                "TangoServerHelper.write_property()",
                tango.ErrSeverity.ERR)  

    def get_status(self):
        """
        Get status of Tango device server
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
        Set device status.
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
        Get a COPY of the device state.
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
        Set device state.
        """
        try:
            self.device.set_state(new_state)
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(dev_failed,
                "Failed to set state .",
                str(dev_failed),
                "TangoServerHelper.set_state()",
                tango.ErrSeverity.ERR)      

