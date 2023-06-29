"""
This module monitors sub devices.
Inherited from liveliness probe functionality
"""
import threading
from concurrent import futures
from logging import Logger
from queue import Empty, Queue
from time import sleep

import tango

from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.device_info import DeviceInfo


class BaseLivelinessProbe:
    """
    The BaseLivelinessProbe class has the responsibility to monitor the sub devices.

    It is inherited for basic liveliness probe functionality.

    TBD: what about scalability? what if we have 1000 devices?
    """

    def __init__(
        self,
        component_manager,
        logger: Logger,
        proxy_timeout: int = 500,
        sleep_time: int = 1,
    ):
        self._thread = threading.Thread(target=self.run)
        self._stop = False
        self._logger = logger
        self._thread.daemon = True
        self._component_manager = component_manager
        self._proxy_timeout = proxy_timeout
        self._sleep_time = sleep_time
        self._dev_factory = DevFactory()
        self._logger.info(
            f"self._component_manager in BaseLivelinessProbe ...... {self._component_manager}"
        )

    def start(self) -> None:
        """
        Starts the sub devices
        """
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        """
        Stops the sub devices
        """
        self._stop = True

    def run(self) -> NotImplementedError:
        """
        Runs the sub devices
        """
        raise NotImplementedError("This method must be inherited")

    def device_task(self, dev_info: DeviceInfo) -> None:
        """
        Checks device status and logs error messages on state change
        """
        try:
            proxy = self._dev_factory.get_device(dev_info.dev_name)
            proxy.set_timeout_millis(self._proxy_timeout)
            self._component_manager.update_ping_info(
                proxy.ping(), dev_info.dev_name
            )
        except Exception as err:
            self._logger.exception(f"Error on {dev_info.dev_name}: {err} ")
            self._component_manager.device_failed(
                dev_info, f"Unable to ping device {dev_info.dev_name}"
            )


class MultiDeviceLivelinessProbe(BaseLivelinessProbe):
    """A class for monitoring multiple devices"""

    def __init__(
        self,
        component_manager,
        logger: Logger,
        max_workers: int = 5,
        proxy_timeout: int = 500,
        sleep_time: int = 1,
    ):
        super().__init__(component_manager, logger, proxy_timeout, sleep_time)
        self._max_workers = max_workers
        self._monitoring_devices = Queue(0)

    def add_device(self, dev_name: str) -> None:
        """A method to add device in the Queue for monitoring"""
        self._monitoring_devices.put(dev_name)

    def run(self) -> None:
        """A method to run device in the queue for monitoring"""
        with tango.EnsureOmniThread() and futures.ThreadPoolExecutor(
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
                except Exception as exp_msg:
                    self._logger.warning("Exception occured: %s", exp_msg)
                sleep(self._sleep_time)


class SingleDeviceLivelinessProbe(BaseLivelinessProbe):
    """A class for monitoring a single device"""

    def run(self) -> None:
        """A method to run single device in the Queue for monitoring"""
        with tango.EnsureOmniThread() and futures.ThreadPoolExecutor(
            max_workers=1
        ) as executor:
            while not self._stop:
                try:
                    self._logger.info(
                        f"self._component_manager ...... {self._component_manager}"
                    )
                    dev_info = self._component_manager.get_device()
                except Exception as exp_msg:
                    self._logger.error(
                        "Exception occured while getting device info: %s",
                        exp_msg,
                    )
                else:
                    try:
                        if dev_info is None:
                            continue
                        executor.submit(self.device_task, dev_info)
                    except Exception as exp_msg:
                        self._logger.error(
                            "Error in submitting the task for %s: %s",
                            dev_info.dev_name,
                            exp_msg,
                        )
                sleep(self._sleep_time)
