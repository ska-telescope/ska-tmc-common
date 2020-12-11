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

    def set_attribute(self):
        """
        """
        pass

def main(args=None, **kwargs):
    """
    Main function of the TangoServer module.

    :param args: None
    :param kwargs:
    """
    return run((TangoServer,), args=args, **kwargs)


if __name__ == '__main__':
    main()
        