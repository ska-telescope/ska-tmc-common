import threading
import time
from concurrent import futures
from typing import Optional

import tango
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import HealthState
from tango import DevState
from tango.server import command

from ska_tmc_common.event_receiver import EventReceiver
from ska_tmc_common.exceptions import TimeoutOccured


class EmptyComponentManager(BaseComponentManager):
    def __init__(
        self,
        event_receiver: bool = False,
        logger=None,
        max_workers: Optional[int] = None,
        *args,
        **kwargs
    ):
        super().__init__(
            logger=logger, max_workers=max_workers, *args, **kwargs
        )
        self.devices = []
        self._stop = False
        self.timeout = 5
        self.timer_thread = threading.Thread(
            target=self.run_timer, kwargs={"timeout": self.timeout}
        )
        self.event_receiver = event_receiver
        if self.event_receiver:
            self.event_receiver_object = EventReceiver(
                self, logger=self.logger
            )
            self.start_event_receiver()

    def start_event_receiver(self):
        """Starts the Event Receiver for given device"""
        print("Starting event receiver")
        if self.event_receiver:
            self.event_receiver_object.start()

    def stop_event_receiver(self):
        """Stops the Event Receiver"""
        if self.event_receiver:
            self.event_receiver_object.stop()

    def start_timer(self) -> Optional[str]:
        """Starts the timer thread to keep track of timeout during command
        execution."""
        if not self.timer_thread.is_alive():
            self.logger.info("Starting timer thread")
            self.timer_thread.start()

    def stop_timer(self) -> None:
        """Stop method for stopping the timer thread"""
        if self.timer_thread.is_alive():
            self._stop = True
            self.logger.info("The stop flag is set to true")
            self.timer_thread.join()

    def run_timer(self, timeout: int) -> Optional[TimeoutOccured]:
        """Runs the timer thread"""
        with tango.EnsureOmniThread():
            try:
                for _ in range(timeout):
                    time.sleep(1)
                    self.logger.info("Counting ....")
                    if self._stop:
                        self.logger.info("Stopping timer thread")
                        break
                if not self._stop:
                    self.logger.warning("Raising an exception")
                    raise TimeoutOccured()
            except Exception as e:
                self.logger.warning("Exception Occured : %s", e)

    def start_communicating(self):
        """This method is not used by TMC."""
        self.logger.info("Start communicating method called")
        pass

    def stop_communicating(self):
        """This method is not used by TMC."""
        self.logger.info("Stop communicating method called")
        pass


class HelperCspMasterDevice(SKABaseDevice):
    """A helper device for triggering state changes with a command on CspMaster."""

    def init_device(self):
        super().init_device()
        self._health_state = HealthState.OK

    class InitCommand(SKABaseDevice.InitCommand):
        def do(self):
            super().do()
            self._device.set_change_event("State", True, False)
            self._device.set_change_event("healthState", True, False)
            return (ResultCode.OK, "")

    def create_component_manager(self):
        cm = EmptyComponentManager(
            logger=self.logger,
            max_workers=None,
            communication_state_callback=None,
            component_state_callback=None,
        )
        return cm

    @command(
        dtype_in="DevState",
        doc_in="state to assign",
    )
    def SetDirectState(self, argin):
        """
        Trigger a DevState change
        """
        # import debugpy; debugpy.debug_this_thread()
        if self.dev_state() != argin:
            self.set_state(argin)
            self.push_change_event("State", self.dev_state())

    @command(
        dtype_in=int,
        doc_in="state to assign",
    )
    def SetDirectHealthState(self, argin):
        """
        Trigger a HealthState change
        """
        # import debugpy; debugpy.debug_this_thread()
        value = HealthState(argin)
        if self._health_state != value:
            self._health_state = HealthState(argin)
            self.push_change_event("healthState", self._health_state)

    def is_On_allowed(self):
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def On(self, argin):
        self.logger.info("Processing On command")
        if self.dev_state() != DevState.ON:
            self.set_state(DevState.ON)
            self.push_change_event("State", self.dev_state())
        return [[ResultCode.OK], [""]]

    def is_Off_allowed(self):
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Off(self, argin):
        self.logger.info("Processing Off command")
        if self.dev_state() != DevState.OFF:
            self.set_state(DevState.OFF)
            self.push_change_event("State", self.dev_state())
        return [[ResultCode.OK], [""]]

    def is_Standby_allowed(self):
        return True

    @command(
        dtype_in="DevVarStringArray",
        doc_in="Input argument as an empty list",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    def Standby(self, argin):
        self.logger.info("Processing Standby command")
        if self.dev_state() != DevState.STANDBY:
            self.set_state(DevState.STANDBY)
            self.push_change_event("State", self.dev_state())
        return [[ResultCode.OK], [""]]
