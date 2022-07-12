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

    def device_task(self, dev_info, proxy):
        with tango.EnsureOmniThread():
            try:
                proxy.set_timeout_millis(self._proxy_timeout)
                new_dev_info = type(dev_info)(dev_info.dev_name)
                new_dev_info.ping = proxy.ping()
                self._component_manager.update_ping_info(
                    new_dev_info.ping, new_dev_info.dev_name
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

                    for dev_info in self._component_manager.devices:
                        if dev_info not in not_read_devices_twice:
                            proxy = self._dev_factory.get_device(
                                dev_info.dev_name
                            )
                            executor.submit(self.device_task, dev_info, proxy)
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
                    dev_info = self._monitoring_device
                    proxy = self._dev_factory.get_device(dev_info.dev_name)
                    executor.submit(self.device_task, dev_info, proxy)
                except Exception as e:
                    self._logger.error(
                        "Error in submitting the task for %s: %s",
                        dev_info.dev_name,
                        e,
                    )

            sleep(self._sleep_time)
