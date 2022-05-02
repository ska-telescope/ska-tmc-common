import threading
from concurrent import futures
from queue import Empty, Queue
from time import sleep

import numpy as np
import tango

from ska_tmc_common.dev_factory import DevFactory
from ska_tmc_common.device_info import DeviceInfo, SubArrayDeviceInfo


class MonitoringLoop:
    """
    The MonitoringLoop class has the responsibility to monitor
    the sub devices.

    It is an infinite loop which ping, get the state, the obsState,
    the healthState and device information of the monitored SKA devices

    TBD: what about scalability? what if we have 1000 devices?

    """

    def __init__(
        self,
        component_manager,
        logger=None,
        max_workers=5,
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
        self._max_workers = max_workers
        self._dev_factory = DevFactory()
        self._priority_devices = Queue(0)

    def start(self):
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self):
        self._stop = True
        # self._thread.join()

    def add_priority_devices(self, dev_name):
        self._priority_devices.put(dev_name)

    def run(self):
        while not self._stop:
            with futures.ThreadPoolExecutor(
                max_workers=self._max_workers
            ) as executor:
                not_read_devices_twice = []
                try:
                    while not self._priority_devices.empty():
                        dev_name = self._priority_devices.get(block=False)
                        dev_info = self._component_manager.get_device(dev_name)
                        executor.submit(self.device_task, dev_info)
                        not_read_devices_twice.append(dev_info)
                except Empty:
                    pass

                for dev_info in self._component_manager.devices:
                    if dev_info not in not_read_devices_twice:
                        executor.submit(self.device_task, dev_info)

            sleep(self._sleep_time)

    def device_task(self, dev_info):
        with tango.EnsureOmniThread():
            try:
                # import debugpy; debugpy.debug_this_thread()
                proxy = self._dev_factory.get_device(dev_info.dev_name)
                proxy.set_timeout_millis(self._proxy_timeout)
                new_dev_info = None
                if "subarray" in dev_info.dev_name.lower():
                    new_dev_info = SubArrayDeviceInfo(dev_info.dev_name)
                    new_dev_info.from_dev_info(dev_info)
                    assigned_res = proxy.assignedResources
                    if assigned_res is not None:
                        new_dev_info.resources = np.asarray(
                            proxy.assignedResources
                        )
                    else:
                        new_dev_info.resources = []
                    new_dev_info.obs_state = proxy.obsState
                    for s in dev_info.dev_name:
                        if s.isdigit():
                            new_dev_info.id = int(s)
                else:
                    new_dev_info = DeviceInfo(dev_info.dev_name)
                    new_dev_info.from_dev_info(dev_info)

                new_dev_info.ping = proxy.ping()
                new_dev_info.state = proxy.State()
                new_dev_info.health_state = proxy.HealthState
                new_dev_info.dev_info = proxy.info()
                self._component_manager.update_device_info(new_dev_info)
            except Exception as e:
                self._logger.error(
                    "Device not working %s: %s", dev_info.dev_name, e
                )
                self._component_manager.device_failed(dev_info, e)
