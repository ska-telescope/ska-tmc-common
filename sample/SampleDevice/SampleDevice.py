""" 
Sample Tango device
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import device_property
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import

__all__ = ["SampleDevice", "main", "AttributeAccessCommand", "PropertyAccessCommand"]


class SKASampleDevice(Device):
    """
    """
    __metaclass__ = DeviceMeta

    # -----------------
    # Device Properties
    # -----------------

    TestProperty = device_property(
        dtype='str',
    )

    # ----------
    # Attributes
    # ----------

    DoubleAttrib = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
    )

    StrAttrib = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        this_server = TangoServerHelper.get_instance()

    def always_executed_hook(self):
        pass

    def delete_device(self):
        pass

    # ------------------
    # Attributes methods
    # ------------------

    def read_DoubleAttrib(self):
        return self.attribute_map["DoubleAttrib"]

    def write_DoubleAttrib(self, value):
        self.attribute_map["DoubleAttrib"] = value

    def read_StrAttrib(self):
        return self.attribute_map["StrAttrib"]

    def write_StrAttrib(self, value):
        self.attribute_map["StrAttrib"] = value


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def AttributeAccess(self, argin):
        command_object = AttributeAccessCommand(self)

    @command(
    dtype_in='str', 
    )
    @DebugIt()
    def PropertyAccess(self, argin):
        pass

# ----------
# Run server
# ----------
def main(args=None, **kwargs):
    return run((SampleDevice,), args=args, **kwargs)

if __name__ == '__main__':
    main()

# ---------------------------------------------
# Command classes that implement business logic
# ---------------------------------------------
class AttributeAccessCommand():
    def __init__(tango_class_object):
        self.this_device = tango_class_object

    def do():
        pass

class AttributeAccessCommand():
    def __init__(tango_class_object):
        self.this_device = tango_class_object

    def do():
        pass