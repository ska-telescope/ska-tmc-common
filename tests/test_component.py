from ska_tmc_common import TmcComponent


class TestTMCComponent(TmcComponent):
    def get_device(self, device_name):
        for device_info in self._devices:
            if device_name in device_info.dev_name:
                return device_info

    def update_device(self, dev_info):
        """
        Base method for update_device method for different nodes
        """

        self._devices.append(dev_info)

    def update_device_exception(self, device_info, exception):
        """
        Base method for update_device_exception method for different nodes
        """
        self.logger.error("error %s %s", device_info, exception)
        device_info.update_unresponsive(True, exception)

    def to_dict(self):
        """
        Base method for to_dict method for different nodes

        """
        self.logger.info("to dict")
