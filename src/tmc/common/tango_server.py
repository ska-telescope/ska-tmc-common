# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

""" Tango Server

"""
# Tango imports
import tango
from tango import AttrWriteType, DevFailed, DeviceProxy, EventType
from tango.server import run,attribute, command, device_property
import logging

class TangoServer:
    """
    
    """
    __instance = None

    def __init__(self):
        """Private constructor of the class""" 
        if TangoServer.__instance != None:
            raise Exception("This is singletone class")
        else:
            TangoServer.__instance = self
        self.device = None

    @staticmethod
    def get_instance():
        if TangoServer.__instance == None:
            TangoServer()
        return TangoServer.__instance

    
    def get_attribute(self):
        """
        """
        pass

    def set_attribute(self, value):
        """
        """
        pass

    def get_property(self):
        """
        """
        pass

    def set_property(self, value):
        """
        """
        pass
    
    def get_status(self):
        """
        """
        try:
            self.device.get_status()
        except DevFailed as dev_failed:
            self.logger.exception("Failed to get status.")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to get status .",
                str(dev_failed),
                "TangoGroupClient.get_status()",
                tango.ErrSeverity.ERR)      
        return self.device.get_status()

    def set_status(self, new_status):
        """
        Set device status.
        """
        try:
            self.device.set_status(new_status)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to set status.")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to set status .",
                str(dev_failed),
                "TangoGroupClient.set_status()",
                tango.ErrSeverity.ERR)      

    def get_state(self):
        """
        Get a COPY of the device state.
        """
        try:
            self.device.get_state()
        except DevFailed as dev_failed:
            self.logger.exception("Failed to get state.")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to get state .",
                str(dev_failed),
                "TangoGroupClient.get_state()",
                tango.ErrSeverity.ERR)      
        return self.device.get_state()

    def set_state(self, new_state):
        """
        Set device state.
        """
        try:
            self.device.set_state(new_state)
        except DevFailed as dev_failed:
            self.logger.exception("Failed to set state.")
            tango.Except.re_throw_exception(dev_failed,
                "Failed to set state .",
                str(dev_failed),
                "TangoGroupClient.set_state()",
                tango.ErrSeverity.ERR)      

def main(args=None, **kwargs):
    """
    Main function of the TangoServer module.

    :param args: None
    :param kwargs:
    """
    return run((TangoServer,), args=args, **kwargs)


if __name__ == '__main__':
    main()
        