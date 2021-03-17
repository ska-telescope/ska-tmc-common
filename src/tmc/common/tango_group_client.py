# -*- coding: utf-8 -*-
#
# This file is part of the ska-tmc-common project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Tango Group Client Code

"""
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run,attribute, command, device_property
import logging

class TangoGroupClient:
    """
    Class for TangoGroupClient API
    """
    def __init__(self, group_name, logger):
        if logger == None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        self.group_name = group_name
        self.tango_group = self.get_tango_group(group_name)
    
    def get_tango_group(self, group_name):
        """
        Creates a Tango Group with given name
        """
        self.tango_group = tango.Group(group_name)
        return self.tango_group

    def add_device(self, device_to_add):
        """
        Add device element in the Group.

        :param:
            device_to_add: string. Device FQDN to add in the group
        
        :return: None

        :throws: DevFailed in case of error.
        """
        try:
            log_msg = f"Adding in group: {device_to_add}."
            self.logger.debug(log_msg)
            self.tango_group.add(device_to_add)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to add device")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to add device",
                str(dev_failed),
                "TangoGroupClient.add_device()")  

    def remove_device(self, device_to_remove):
        """
        Removes all elements from the Group.

        :param:
            device_to_remove: string. FQDN of the device to be removed from group.
        
        :return: None

        :throws: DevFailed in case of error.
        """
        try:
            log_msg = f"Removing from group: {device_to_remove}."
            self.logger.debug(log_msg)
            self.tango_group.remove(device_to_remove)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to remove device")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to remove device",
                str(dev_failed),
                "TangoGroupClient.remove_device()")

    def delete_group(self, group_to_delete):
        """
        Deletes the Group.
        """
        try:
            log_msg = f"Deleting group: {group_to_delete}."
            self.logger.debug(log_msg)
            self.tango_group.delete(group_to_delete)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to delete group")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to remove device",
                str(dev_failed),
                "TangoGroupClient.delete_group()")

    def get_group_device_list(self, forward=True):
        """
        Returns the list of devices in the group

        :params: None

        :return: list. The list of devices

        :throws:
            DevFailed on failure in getting group device list.

        """
        try:
            return self.tango_group.get_device_list()
        except DevFailed as dev_failed:
            self.logger.exception("Failed to get group device list")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to get group device list",
                str(dev_failed),
                "TangoGroupClient.get_group_device_list()")  
        
    def remove_all_device(self):
        """
        Removes all the devices from the group.
        """
        self.logger.debug("Removing all devices from the group.")
        self.tango_group.remove_all()

    def send_command(self, command_name, command_data = None):
        """
        Invokes command on the Tango group synchronously.

        :param:
            command_name: string. Name of the command to be invoked

            command_data: (optional) Void. The arguments with the command.
        
        :returns: int. Request id returned by tango group. Pass this id to `get_command_reply`
        to retrieve the reply of the command.

        :throws:
            DevFailed on failure in executing the command.
        """
        try:
            log_msg = f"Invoking {command_name} on {self.group_name} synchronously."
            self.logger.debug(log_msg)
            return self.tango_group.command_inout(command_name, command_data)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to execute command .")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to execute command.",
                str(dev_failed),
                "TangoGroupClient.send_command()")

    def send_command_async(self, command_name, command_data = None, callback_method = None):
        """
        Invokes command on the Tango group asynchronously.

        :param:
            command_name: string. Name of the command to be invoked

            command_data: (optional) Void. The arguments with the command.

            callback_method: The callback method that should be executed upon execution

        :returns: int. Request id returned by tango group. Pass this id to `get_command_reply`
        to retrieve the reply of the command.

        :throws:
            DevFailed on failure in executing the command.
        """
        try:
            log_msg = f"Invoking {command_name} on {self.group_name} asynchronously."
            self.logger.debug(log_msg)
            return self.tango_group.command_inout_asynch(command_name, command_data, callback_method)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to execute command .")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to execute command.",
                str(dev_failed),
                "TangoGroupClient.send_command_async()")
    
    def get_command_reply(self, command_id, timeout = 0):
        """
        Retrieves the response of the command

        :params:
            command_id: int. Id of the command

            timeout: (optional) int. Timeout in milliseconds. If no timeout is mentioned, 
            the API waits indefinitely.

        :returns:
            The results of an asynchronous command

        :throws:
            DevFailed on failure in executing the command.
        """
        try:
            log_msg = f"Retrieving response for command id: {command_id}."
            self.logger.debug(log_msg)
            return self.tango_group.command_inout_reply(command_id, timeout)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to execute command .")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to retrieve response.",
                str(dev_failed),
                "TangoGroupClient.get_command_reply()")
