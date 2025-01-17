"""
This module implements the Helper devices for CSP subarray nodes for testing
an integrated TMC
"""

from ska_tango_base.control_model import AdminMode
from tango.server import run

from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)


class HelperCSPSubarrayDevice(HelperSubArrayDevice):
    """
    A device exposing commands and attributes of the CSP Subarray Device.
    """

    def init_device(self):
        super().init_device()
        self._admin_mode: AdminMode = AdminMode.OFFLINE


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Runs the HelperSubArrayDevice Tango device.
    :param args: Arguments internal to TANGO
    :param kwargs: Arguments internal to TANGO
    :return: integer. Exit code of the run method.
    """
    return run((HelperCSPSubarrayDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
