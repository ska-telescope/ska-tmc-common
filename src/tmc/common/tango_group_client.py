# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Tango Group Client

"""
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run,attribute, command, device_property

import logging

class TangoGroupClient:
    """
    
    """

    def __init__(self, group_name):
        self.tango_group = tango.Group(group_name)
    
    def get_tango_group(self, group_name):
        """
        Create Tango Group Command
        """
        return tango.Group(group_name)

    def add_device(self, devices_to_add):
        for device in devices_to_add:
            self.tango_group.add(device)

    def remove_device(self, devices_to_remove):
        for device in devices_to_add:   
            self.tango_group.remove(device)

    def delete_device(self, devices_to_delete)
        for device in devices_to_add:
            self.tango_group.delete(device)

    def send_command(self, command_name, input_arg = None):
        try:
            self.tango_group.command_inout(command_name, input_arg)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to execute command .")
            tango.Except.throw_exception(dev_failed,
                "Failed to execute command .",
                str(dev_failed),
                "TangoGroupClient.send_command()",
                tango.ErrSeverity.ERR)    

def main(args=None, **kwargs):
    """
    Main function of the TangoGroupClient module.

    :param args: None
    :param kwargs:
    """
    return run((TangoGroupClient,), args=args, **kwargs)


if __name__ == '__main__':
    main()