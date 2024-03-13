# -*- coding: utf-8 -*-
#
# This file is part of the ska-tmc-common project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
"""
This is the Tango Server Helper module of Tango Interface Layer.
This module implements a class
TangoServerHelper which helps in operations like getting and
setting attributes and properties of the Tango device.
This class is now deprecated.
"""
# pylint: disable=inconsistent-return-statements

# Tango imports
import tango
from tango import Database, DevFailed


class TangoServerHelper:
    """
    This class provides APIs to help performing role of Tango device server.
    """

    __instance = None

    def __init__(self):
        """Private constructor of the class
        :raises Exception
        """
        if TangoServerHelper.__instance is not None:
            raise Exception("This is singleton class")

        TangoServerHelper.__instance = self
        self.device = None

    @staticmethod
    def get_instance():
        """
        Return instance object of TangoServerHelper class.
        Creates one if the object does
        not exist.

        :param: None.

        return:
            object of TangoServerHelper class
        """
        if TangoServerHelper.__instance is None:
            TangoServerHelper()
        return TangoServerHelper.__instance

    def set_tango_class(self, device):
        """
        Set the Tango class object as a device

        :param device: Tango class object
        """
        if not self.device:
            self.device = device

    def read_property(self, property_name):
        """
        Returns the value of given Tango device property
        :param property_name: String. Name of the Tango device property

        :return
            List of strings containing value(s) of the device property

        :throws
            Devfailed exception in case of error
        """
        try:
            db = Database()
            device_name = self.device.get_name()
            return db.get_device_property(device_name, property_name)[
                property_name
            ]
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(
                dev_failed,
                "Failed to read property",
                str(dev_failed),
                "TangoServerHelper.read_property()",
                tango.ErrSeverity.ERR,
            )

    def write_property(self, property_name, value):
        """
        Sets the value to a given device property

        :param property_name: String. Name of the Tango device property

        :param value: Value of the property to be set

        :throws: Devfailed exception in case command failed error.
                 ValueError exception in case value error.
                 KeyError exception in case key error
        """
        try:
            db = Database()
            device_name = self.device.get_name()
            property_map = {}
            property_map[property_name] = value
            db.put_device_property(device_name, property_map)
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(
                dev_failed,
                "Failed to write property",
                str(dev_failed),
                "TangoServerHelper.write_property()",
                tango.ErrSeverity.ERR,
            )
        except KeyError as key_error:
            tango.Except.re_throw_exception(
                key_error,
                "Failed to write property",
                str(key_error),
                "TangoServerHelper.write_property()",
                tango.ErrSeverity.ERR,
            )
        except ValueError as val_error:
            tango.Except.re_throw_exception(
                val_error,
                "Failed to write property",
                str(val_error),
                "TangoServerHelper.write_property()",
                tango.ErrSeverity.ERR,
            )

    def get_status(self):
        """
        Returns value of the Status attribute of the Tango device.

        :param: None

        :return: String. The Status value of the Tango device.

        :throws: DevFailed on failure in getting device status.
        """
        try:
            return self.device.get_status()
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(
                dev_failed,
                "Failed to get status .",
                str(dev_failed),
                "TangoServerHelper.get_status()",
                tango.ErrSeverity.ERR,
            )

    def set_status(self, new_status):
        """
        Sets the Status attribute of the Tango device with given value.

        :param new_status: String. New value for Status attribute.s

        :throws: DevFailed on failure in setting device status.
        """
        try:
            self.device.set_status(new_status)
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(
                dev_failed,
                "Failed to set status .",
                str(dev_failed),
                "TangoServerHelper.set_status()",
                tango.ErrSeverity.ERR,
            )

    def get_state(self):
        """
        Returns value of the State attribute of the Tango device.

        :param: None

        :return: (DevState). The State value of the Tango device.

        :throws: DevFailed on failure in getting device state.
        """
        try:
            return self.device.get_state()
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(
                dev_failed,
                "Failed to get state .",
                str(dev_failed),
                "TangoServerHelper.get_state()",
                tango.ErrSeverity.ERR,
            )

    def set_state(self, new_state):
        """
        Sets the State attribute of the Tango device with given value.

        :param new_state: (DevState). New value for State attribute.

        :throws: DevFailed on failure in setting device state.
        """
        try:
            self.device.set_state(new_state)
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(
                dev_failed,
                "Failed to set state .",
                str(dev_failed),
                "TangoServerHelper.set_state()",
                tango.ErrSeverity.ERR,
            )

    def _generate_change_event(self, attr_name, value):
        """
        Generates an event of type CHANGE_EVENT on
        the given attribute along with the new data

        :param attr_name: String.

        Name of the attribute on which change event is to be raised.

        :param value: Changed values of the attribute.

        :throws: Devfailed exception in case of error.
        """
        try:
            self.device.push_change_event(attr_name, value)
        except DevFailed as dev_failed:
            tango.Except.re_throw_exception(
                dev_failed,
                "Failed to push change event .",
                str(dev_failed),
                "TangoServerHelper._generate_change_event()",
                tango.ErrSeverity.ERR,
            )

    def write_attr(self, attr_name, value, push_change_event=True):
        """
        Updates the value of device server's attribute

        :param attr_name: String.

        Name of the attribute which should be updated.

        :param value: New value of the attribute.

        :param push_change_event: Change event value.

        :throws: ValueError exception in case of error.
        """
        try:
            self.device.attr_map[attr_name] = value
        except ValueError as val_error:
            tango.Except.re_throw_exception(
                val_error,
                "Invalid value of tango attribute .",
                str(val_error),
                "TangoServerHelper.write_attr()",
                tango.ErrSeverity.ERR,
            )
        except KeyError as key_error:
            tango.Except.re_throw_exception(
                key_error,
                "Failed to write attribute",
                str(key_error),
                "TangoServerHelper.write_attr()",
                tango.ErrSeverity.ERR,
            )
        if push_change_event:
            self._generate_change_event(attr_name, value)

    def read_attr(self, attr_name):
        """
        Returns the value of device server's attribute

        :param attr_name: String.
                         Name of the attribute which should be updated.

        :return:
            value: Value of the attribute

        :throws: ValueEror exception in case of error.
        """
        try:
            return self.device.attr_map[attr_name]

        except ValueError as val_error:
            tango.Except.re_throw_exception(
                val_error,
                "Invalid value of tango attribute .",
                str(val_error),
                "TangoServerHelper.read_attr()",
                tango.ErrSeverity.ERR,
            )
        except KeyError as key_error:
            tango.Except.re_throw_exception(
                key_error,
                "Failed to read attribute",
                str(key_error),
                "TangoServerHelper.read_attr()",
                tango.ErrSeverity.ERR,
            )
