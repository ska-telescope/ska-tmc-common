import threading
from concurrent import futures
from queue import Empty, Queue
from time import sleep

import tango

from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.device_info import (
    DeviceInfo,
    DishDeviceInfo,
    SdpSubarrayDeviceInfo,
    SubArrayDeviceInfo,
)


class BaseLivelinessProbe:
    """
    The LivelinessProbe class has the responsibility to monitor
    the sub devices.

    It is an infinite loop which pings the monitored SKA devices.

    TBD: what about scalability? what if we have 1000 devices?

    """

    def __init__(
        self,
        component_manager,
        logger=None,
        proxy_timeout=500,
        sleep_time=1,
    ):
        self._thread = threading.Thread(target=self.run)
        self._stop = False
        self._logger = logger
        self._thread.setDaemon(True)
        self._component_manager = component_manager
        self._proxy_timeout = proxy_timeout
        self._sleep_time = sleep_time
        self._dev_factory = DevFactory()

    def start(self):
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self):
        self._stop = True
        # self._thread.join()

    def run(self):
        raise NotImplementedError("This method must be inherited")

    def device_task(self, dev_info, proxy):
        with tango.EnsureOmniThread():
            try:
                # import debugpy; debugpy.debug_this_thread()
                proxy.set_timeout_millis(self._proxy_timeout)
                new_dev_info = None
                if (
                    "low-mccs" in dev_info.dev_name.lower()
                    or "mid-csp" in dev_info.dev_name.lower()
                ):
                    new_dev_info = SubArrayDeviceInfo(dev_info.dev_name)
                    new_dev_info.from_dev_info(dev_info)
                elif "mid-d" in dev_info.dev_name.lower():
                    new_dev_info = DishDeviceInfo(dev_info.dev_name)
                    new_dev_info.from_dev_info(dev_info)
                elif "mid-sdp" in dev_info.dev_name.lower():
                    new_dev_info = SdpSubarrayDeviceInfo(dev_info.dev_name)
                    new_dev_info.from_dev_info(dev_info)
                else:
                    new_dev_info = DeviceInfo(dev_info.dev_name)
                    new_dev_info.from_dev_info(dev_info)

                new_dev_info.ping = proxy.ping()
                self._component_manager.update_device_info(new_dev_info)
            except Exception as e:
                self._logger.error(
                    "Device not working %s: %s", dev_info.dev_name, e
                )
                self._component_manager.device_failed(dev_info, e)


class MultiDeviceLivelinessProbe(BaseLivelinessProbe):
    def __init__(
        self,
        component_manager,
        logger=None,
        max_workers=5,
        proxy_timeout=500,
        sleep_time=1,
    ):
        self._max_workers = max_workers
        self._monitoring_devices = Queue(0)

        super().__init__(component_manager, logger, proxy_timeout, sleep_time)

    def add_device(self, dev_name):
        self._monitoring_devices.put(dev_name)

    def run(self):
        while not self._stop:
            with futures.ThreadPoolExecutor(
                max_workers=self._max_workers
            ) as executor:
                not_read_devices_twice = []
                try:
                    while not self._monitoring_devices.empty():
                        dev_name = self._monitoring_devices.get(block=False)
                        dev_info = self._component_manager.get_device(dev_name)
                        proxy = self._dev_factory.get_device(dev_info.dev_name)
                        executor.submit(self.device_task, dev_info, proxy)
                        not_read_devices_twice.append(dev_info)
                except Empty:
                    pass

                for dev_info in self._component_manager.devices:
                    if dev_info not in not_read_devices_twice:
                        executor.submit(self.device_task, dev_info)

            sleep(self._sleep_time)


class SingleDeviceLivelinessProbe(BaseLivelinessProbe):
    def __init__(
        self,
        component_manager,
        monitoring_device,
        logger=None,
        proxy_timeout=500,
        sleep_time=1,
    ):
        self._monitoring_device = monitoring_device
        super().__init__(component_manager, logger, proxy_timeout, sleep_time)

    def run(self):
        while not self._stop:
            with futures.ThreadPoolExecutor(max_workers=1) as executor:
                try:
                    while not self._monitoring_device.empty():
                        dev_info = self._component_manager.get_device()
                        proxy = self._dev_factory.get_device(dev_info.dev_name)
                        executor.submit(self.device_task, dev_info, proxy)
                except Empty:
                    pass

            sleep(self._sleep_time)
