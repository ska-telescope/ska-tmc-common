import threading
from concurrent import futures
from time import sleep

import tango

from ska_tmc_common.dev_factory import DevFactory


class EventReceiver:
    """
    Simple event receiver to subsribe to state change event for timeout testing
    """

    def __init__(
        self,
        component_manager,
        logger=None,
        max_workers=1,
        proxy_timeout=500,
        sleep_time=1,
    ):
        self._thread = threading.Thread(target=self.run)
        self._stop = False
        self.logger = logger
        self._thread.setDaemon(True)
        self.component_manager = component_manager
        self._proxy_timeout = proxy_timeout
        self._sleep_time = sleep_time
        self._max_workers = max_workers
        self._dev_factory = DevFactory()

    def start(self):
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self):
        self._stop = True
        # self._thread.join()

    def run(self):
        with tango.EnsureOmniThread() and futures.ThreadPoolExecutor(
            max_workers=self._max_workers
        ) as executor:
            while not self._stop:
                try:
                    for dev_info in self.component_manager.devices:
                        if dev_info.last_event_arrived is None:
                            executor.submit(self.subscribe_events, dev_info)
                except Exception as e:
                    self.logger.warning("Exception occured: %s", e)
                sleep(self._sleep_time)

    def subscribe_events(self, dev_info):
        try:
            # import debugpy; debugpy.debug_this_thread()
            proxy = self._dev_factory.get_device(dev_info.dev_name)
            proxy.subscribe_event(
                "State",
                tango.EventType.CHANGE_EVENT,
                self.handle_state_event,
                stateless=True,
            )
        except Exception as e:
            self.logger.debug(
                "event not working for device %s/%s", proxy.dev_name, e
            )

    def handle_state_event(self, evt):
        # import debugpy; debugpy.debug_this_thread()
        if evt.err:
            error = evt.errors[0]
            self.logger.error("%s %s", error.reason, error.desc)
            self.component_manager.update_event_failure(evt.device.dev_name())
            return

        new_value = evt.attr_value.value
        self.component_manager.update_device_state(
            evt.device.dev_name(), new_value
        )
