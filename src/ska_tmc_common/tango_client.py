# -*- coding: utf-8 -*-
#
# This file is part of the ska-tmc-common project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
""" Tango Client Code"""

import logging
from logging import Logger
from typing import Callable, Optional

# Tango imports
import tango
from tango import DevFailed, DeviceProxy, EventType


class TangoClient:
    """
    Class for TangoClient API
    """

    def __init__(self, fqdn: str, logger: Optional[Logger] = None):
        """
        The class constructor.
        :param fqdn: string.

        The fqdn of the device.

        :param
            logger: (optional) The logger object.
        """
        self.logger = logger or logging.getLogger(__name__)

        self.device_fqdn = fqdn
        self.deviceproxy = self._get_deviceproxy()

    def _get_deviceproxy(self) -> DeviceProxy:
        """
        Returns device proxy for given FQDN.
        """
        retry = 0
        while retry < 3:
            try:
                return DeviceProxy(self.device_fqdn)
            except DevFailed as df:
                if retry >= 2:
                    tango.Except.re_throw_exception(
                        df,
                        "Retries exhausted while creating device proxy.",
                        "Failed to create DeviceProxy of "
                        + str(self.device_fqdn),
                        "SubarrayNode.get_deviceproxy()",
                        tango.ErrSeverity.ERR,
                    )
                retry += 1
                continue

    def get_device_fqdn(self) -> str:
        """
        Returns the Fully Qualified Device Name

        (FQDN) of the Tango device server.
        """
        return self.device_fqdn

    def send_command(self, command_name: str, command_data=None):
        """
        This method invokes command on the device server in synchronous mode.

        :param
            command_name: string. Name of the command

        :param
            command_data: (optional) void. Parameter with the command.

        :return
            Returns the command Result.

        :throws
            DevFailed in case of error.
        """
        try:
            log_msg = (
                f"Invoking {command_name} on {self.device_fqdn} synchronously."
            )
            self.logger.debug(log_msg)
            return self.deviceproxy.command_inout(command_name, command_data)
        except DevFailed as dev_failed:
            log_msg = (
                "Error in invoking command " + command_name + str(dev_failed)
            )
            self.logger.debug(log_msg)
            tango.Except.throw_exception(
                "Error in invoking command " + command_name,
                log_msg,
                "TangoClient.send_command",
                tango.ErrSeverity.ERR,
            )

    def send_command_async(
        self, command_name: str, command_data=None, callback_method=None
    ):
        """
        This method invokes command on the device server in asynchronous mode.

        :param
            command_name: string. Name of the command

        :param
            command_data: (optional) void. Parameter with the command.

        :param
            callback_method: (optional) Callback function

            that should be executed after completion

            of the command execution.

        :returns
            int.

            Command identifier returned by

            the Tango device server.

        :throws
            DevFailed in case of error.
        """
        try:
            log_msg = (
                f"Invoking {command_name}on{self.device_fqdn}asynchronously"
            )

            self.logger.debug(log_msg)
            return self.deviceproxy.command_inout_asynch(
                command_name, command_data, callback_method
            )
        except DevFailed as dev_failed:
            log_msg = (
                "Error in invoking command " + command_name + str(dev_failed)
            )
            self.logger.debug(log_msg)
            tango.Except.throw_exception(
                "Error in invoking command " + command_name,
                log_msg,
                "TangoClient.send_command_async",
                tango.ErrSeverity.ERR,
            )

    def get_attribute(self, attribute_name: str):
        """
        This method reads the value of the given attribute.

        :param
            attribute_name: string. Name of the attribute

        :return
            Returns the DeviceAttribute object with several fields.
            The attribute value is present in the value field of the object.
            value: Normal scalar value or NumPy array of values.

        :throws
            AttributeError in case of error.
        """
        try:
            log_msg = f"Reading attribute {attribute_name}."
            self.logger.debug(log_msg)
            return self.deviceproxy.read_attribute(attribute_name)
        except AttributeError as attribute_error:
            log_msg = (
                attribute_name + "Attribute not found" + str(attribute_error)
            )
            self.logger.debug(log_msg)
            tango.Except.throw_exception(
                f"{attribute_name} attribute not found",
                log_msg,
                "TangoClient.get_attribute",
                tango.ErrSeverity.ERR,
            )

    def set_attribute(self, attribute_name: str, value):
        """
        This method writes the value to the given attribute.

        :param
            attribute_name: string. Name of the attribute

        :param
            value: The value to be set. For non SCALAR attributes,
            it may be any sequence of sequences.

        :return
            None

        :throw
            AttributeError in case of error.
        """
        try:
            log_msg = f"Setting attribute {attribute_name}: {value}."
            self.logger.debug(log_msg)
            self.deviceproxy.write_attribute(attribute_name, value)
        except AttributeError as attribute_error:
            log_msg = (
                attribute_name + "Attribute not found" + str(attribute_error)
            )
            tango.Except.throw_exception(
                f"{attribute_name} attribute not found",
                log_msg,
                "TangoClient.set_attribute",
                tango.ErrSeverity.ERR,
            )

    def subscribe_attribute(self, attr_name: str, callback_method: Callable):
        """
        Subscribes to the change event on the given attribute.

        :param
            attr_name: string. Name of the attribute to subscribe change event.

        :param
            callback_method: Name of callback method.

        :return
            int. event_id returned by the Tango device server.
        """
        try:
            log_msg = f"Subscribing attribute {attr_name}."
            self.logger.debug(log_msg)
            return self.deviceproxy.subscribe_event(
                attr_name,
                EventType.CHANGE_EVENT,
                callback_method,
                stateless=True,
            )
        except DevFailed as dev_failed:
            log_msg = f"Failed to subscribe attribute {attr_name}."
            self.logger.debug(log_msg)
            tango.Except.throw_exception(
                "Error is subscribing event",
                dev_failed,
                "TangoClient.subscribe_attribute",
                tango.ErrSeverity.ERR,
            )

    def unsubscribe_attribute(self, event_id: int):
        """
        Unsubscribes a client from receiving the event specified by event_id.

        :param
            event_id: int. Event id of the subscription

        :return
            None.
        """
        try:
            log_msg = f"Unsubscribing attribute event {event_id}."
            self.logger.debug(log_msg)
            self.deviceproxy.unsubscribe_event(event_id)
        except DevFailed as dev_failed:
            log_message = "Failed to unsubscribe event {}.".format(dev_failed)
            self.logger.error(log_message)
            tango.Except.re_throw_exception(
                dev_failed,
                "Event unsubscription error",
                "Error in unsubscribing the event."
                "TangoClient.subscribe_attribute()",
            )
