# -*- coding: utf-8 -*-
#
# This file is part of the ska-tmc-common project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Tango Client Code

"""
import logging

# Tango imports
import tango
from tango import DevFailed, DeviceProxy, EventType
from tango.server import attribute


class TangoClient:
    """
    Class for TangoClient API
    """

    def __init__(self, fqdn, logger=None):
        """
        The class constructor.
        :param
            fqdn: string. The fqdn of the device.

        :param
            logger: (optional) The logger object.
        """

        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.device_fqdn = fqdn
        self.deviceproxy = None
        self.deviceproxy = self._get_deviceproxy()

    def _get_deviceproxy(self):
        """
        Returns device proxy for given FQDN.
        """

        if self.deviceproxy is None:
            retry = 0
            while retry < 3:
                try:
                    self.deviceproxy = DeviceProxy(self.device_fqdn)
                    break
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
        return self.deviceproxy

    def get_device_fqdn(self):
        """
        Returns the Fully Qualified Device Name (FQDN) of the Tango device server.
        """
        return self.device_fqdn

    def send_command(self, command_name, command_data=None):
        """
        This method invokes command on the device server in synchronous mode.

        :param
            command_name: string. Name of the command

        :param
            command_data: (optional) void. Parameter with the command.

        :return
            The result of the command. The type depends on the command. It may be None.

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
        self, command_name, command_data=None, callback_method=None
    ):
        """
        This method invokes command on the device server in asynchronous mode.

        :params
            command_name: string. Name of the command

        :param
            command_data: (optional) void. Parameter with the command.

        :param
            callback_method: (optional) Callback function that should be executed after completion
            of the command execution.

        :returns
            int. Command identifier returned by the Tango device server.

        :throws
            DevFailed in case of error.
        """
        try:
            log_msg = f"Invoking {command_name} on {self.device_fqdn} asynchronously."
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

    def get_attribute(self, attribute_name):
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
                attribute + "Attribute not found",
                log_msg,
                "TangoClient.get_attribute",
                tango.ErrSeverity.ERR,
            )

    def set_attribute(self, attribute_name, value):
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
                attribute + "Attribute not found",
                log_msg,
                "TangoClient.set_attribute",
                tango.ErrSeverity.ERR,
            )

    def subscribe_attribute(self, attr_name, callback_method):
        """
        Subscribes to the change event on the given attribute.

        :params
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

    def unsubscribe_attribute(self, event_id):
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
