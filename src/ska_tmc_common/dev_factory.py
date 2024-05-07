"""It is a factory class which provide the ability to create an object of
type DeviceProxy.
"""

import logging

import tango


class DevFactory:
    """
    This class is an easy attempt to develop the concept developed by MCCS team
    in the following confluence page:
    https://confluence.skatelescope.org/display/SE/Running+BDD+tests+in+multiple+harnesses

    It is a factory class which provide the ability to create an object of
    type DeviceProxy.

    When testing the static variable _test_context is an instance of
    the TANGO class MultiDeviceTestContext.

    More information on tango testing can be found at the following link:
    https://pytango.readthedocs.io/en/stable/testing.html

    """

    _test_context = None

    def __init__(
        self
    ) -> None:
        self.dev_proxys = {}
        self.logger = logging.getLogger(__name__)

    def get_device(self, dev_name: str) -> tango.DeviceProxy:
        """
        Create (if not done before) a DeviceProxy for the Device fqnm

        :param dev_name: Device name
        :param green_mode: tango.GreenMode (synchronous by default)

        :return: DeviceProxy
        """
        # import debugpy; debugpy.debug_this_thread()
        if DevFactory._test_context is None:
            if dev_name not in self.dev_proxys:
                self.logger.debug("Creating Proxy for %s", dev_name)
                self.dev_proxys[dev_name] = tango.DeviceProxy(
                    dev_name
                )
            return self.dev_proxys[dev_name]

        return DevFactory._test_context.get_device(dev_name)
