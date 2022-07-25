import threading
from concurrent import futures
from queue import Empty, Queue
from time import sleep

import tango

from ska_tmc_common.dev_factory import DevFactory


class BaseLivelinessProbe:
    """
    The BaseLivelinessProbe class has the responsibility to monitor the sub devices.

    It is inherited for basic liveliness probe functionality.

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

    def run(self):
        raise NotImplementedError("This method must be inherited")

    def device_task(self, dev_info):
        with tango.EnsureOmniThread():
            try:
                proxy = self._dev_factory.get_device(dev_info.dev_name)
                proxy.set_timeout_millis(self._proxy_timeout)
                self._component_manager.update_ping_info(
                    proxy.ping(), dev_info.dev_name
                )
            except Exception as e:
                self._logger.error(
                    "Device not working %s: %s", dev_info.dev_name, e
                )
                self._component_manager.device_failed(dev_info, e)


class MultiDeviceLivelinessProbe(BaseLivelinessProbe):
    """A class for monitoring multiple devices"""

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
        """A method to add device in the Queue for monitoring"""
        self._monitoring_devices.put(dev_name)

    def run(self):
        with futures.ThreadPoolExecutor(
            max_workers=self._max_workers
        ) as executor:
            while not self._stop:
                not_read_devices_twice = []
                try:
                    while not self._monitoring_devices.empty():
                        dev_name = self._monitoring_devices.get(block=False)
                        dev_info = self._component_manager.get_device(dev_name)
                        executor.submit(self.device_task, dev_info)
                        not_read_devices_twice.append(dev_info)
                    for dev_info in self._component_manager.devices:
                        if dev_info not in not_read_devices_twice:
                            executor.submit(self.device_task, dev_info)
                except Empty:
                    pass
                except Exception as e:
                    self._logger.warning("Exception occured: %s", e)
                sleep(self._sleep_time)


class SingleDeviceLivelinessProbe(BaseLivelinessProbe):
    """A class for monitoring a single device"""

    def __init__(
        self,
        component_manager,
        logger=None,
        proxy_timeout=500,
        sleep_time=1,
    ):
        super().__init__(component_manager, logger, proxy_timeout, sleep_time)

    def run(self):
        dev_info = self._component_manager.get_device()
        while not self._stop:
            with futures.ThreadPoolExecutor(max_workers=1) as executor:
                try:
                    executor.submit(self.device_task, dev_info)
                except Exception as e:
                    self._logger.error(
                        "Error in submitting the task for %s: %s",
                        dev_info.dev_name,
                        e,
                    )

            sleep(self._sleep_time)
