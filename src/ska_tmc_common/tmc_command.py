"""
This module manages all the base classes and methods
required for TMC commands
"""
# pylint: disable=unused-argument

import threading
import time
from enum import IntEnum
from logging import Logger
from operator import methodcaller
from typing import Callable, List, Optional, Tuple, Union

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus
from tango import ConnectionFailed, DevFailed, EnsureOmniThread

from ska_tmc_common.adapters import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    CspMasterAdapter,
    CspSubarrayAdapter,
    DishAdapter,
    MCCSMasterLeafNodeAdapter,
    SdpSubArrayAdapter,
    SubArrayAdapter,
)
from ska_tmc_common.enum import TimeoutState
from ska_tmc_common.lrcr_callback import LRCRCallback
from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.timeout_callback import TimeoutCallback
from ska_tmc_common.tmc_component_manager import BaseTmcComponentManager


class BaseTMCCommand:
    """
    Base class for managing all TMC commands.
    """

    def __init__(
        self,
        component_manager: BaseTmcComponentManager,
        logger: Logger,
        *args,
        **kwargs,
    ):
        self.adapter_factory = AdapterFactory()
        self.op_state_model = TMCOpStateModel(logger, callback=None)
        self.component_manager = component_manager
        self.logger = logger
        self.tracker_thread: Optional[threading.Thread] = None
        self._stop: bool = False
        self.index: int = 0

    def set_command_id(self, command_name: str):
        """Sets the command id for error propagation."""
        command_id = f"{time.time()}-{command_name}"
        self.logger.info(
            "Setting command id as %s for command: %s",
            command_id,
            command_name,
        )
        self.component_manager.command_id = command_id

    # pylint: disable=inconsistent-return-statements
    def adapter_creation_retry(
        self,
        device_name: str,
        adapter_type: AdapterType,
        start_time: float,
        timeout: int,
    ) -> Optional[
        Union[
            DishAdapter,
            SubArrayAdapter,
            CspMasterAdapter,
            CspSubarrayAdapter,
            MCCSMasterLeafNodeAdapter,
            BaseAdapter,
            SdpSubArrayAdapter,
        ]
    ]:
        """
        Method to create adapters for device.
        """
        elapsed_time = 0

        while elapsed_time <= timeout:
            try:
                adapter = self.adapter_factory.get_or_create_adapter(
                    device_name,
                    adapter_type,
                )
                return adapter

            except ConnectionFailed:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    raise
            except DevFailed:
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    raise
            except Exception as exp_msg:
                self.logger.error(
                    "Unexpected error occurred while creating the adapter: %s",
                    exp_msg,
                )
                raise

    # pylint: enable=inconsistent-return-statements
    def do(self, argin=None) -> NotImplementedError:
        """
        Base method for do method for different nodes
        """
        raise NotImplementedError(
            "This method must be implemented by command class"
        )

    def update_task_status(
        self,
        **kwargs,
    ) -> NotImplementedError:
        """Method to update the task status for command."""
        raise NotImplementedError(
            "This method must be implemented by command class"
        )

    def start_tracker_thread(
        self,
        state_function: Callable,
        expected_state: List[IntEnum],
        abort_event: threading.Event,
        timeout_id: Optional[str] = None,
        timeout_callback: Optional[TimeoutCallback] = None,
        command_id: Optional[str] = None,
        lrcr_callback: Optional[LRCRCallback] = None,
    ) -> None:
        """Creates and starts a thread that will keep track of the State/
        obsState change to be monitored (For confirming command completion.
        Currently only supports obsState change.), the timeout callback to
        monitor the timeout and the longRunningCommandResult callback to keep
        track of LRCR events.

        :param expected_state: Expected state of the device in case of
                    successful command execution.

        :param abort_event: threading.Event class object that is used to check
                    if the command has been aborted.

        :param timeout_id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.

        :param command_id: Id for LRCRCallback class object.

        :param lrcr_callback: An instance of LRCRCallback class that acts
                    as a callable functions to call when
                    longRunningCommandResult event is received.
        """
        self.tracker_thread = threading.Thread(
            target=self.track_and_update_command_status,
            args=[
                state_function,
                expected_state,
                abort_event,
                timeout_id,
                timeout_callback,
                command_id,
                lrcr_callback,
            ],
        )
        self._stop = False
        self.logger.info("Starting tracker thread")
        self.tracker_thread.start()

    def track_and_update_command_status(
        self,
        state_function: Callable,
        expected_state: List[IntEnum],
        abort_event: threading.Event,
        timeout_id: Optional[str] = None,
        timeout_callback: Optional[TimeoutCallback] = None,
        command_id: Optional[str] = None,
        lrcr_callback: Optional[LRCRCallback] = None,
    ) -> None:
        """Keeps track of the obsState change and the timeout callback to
        determine whether timeout has occurred or the command completed
        successfully. Logs the result for now.

        :param expected_state: Expected state of the device in case of
                    successful command execution.

        :param abort_event: threading.Event class object that is used to check
                    if the command has been aborted.

        :param timeout_id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable function to call in the event of timeout.

        :param command_id: Id for LRCRCallback class object.

        :param lrcr_callback: An instance of LRCRCallback class that acts
                    as a callable function to call when an event from the
                    attribute longRunningCommandResult arrives.
        """
        with EnsureOmniThread():
            self.index = 0
            while not self._stop:
                state_to_achieve = expected_state[self.index]
                try:
                    if self.check_abort_event(abort_event):
                        self.update_task_status(status=TaskStatus.ABORTED)
                        self.stop_tracker_thread(timeout_id)

                    if self.check_command_timeout(
                        timeout_id, timeout_callback
                    ):
                        self.update_task_status(
                            result=ResultCode.FAILED,
                            message="Timeout has occurred, command failed",
                        )
                        self.stop_tracker_thread(timeout_id)

                    if self.check_final_obsstate(
                        state_function, state_to_achieve, expected_state
                    ):
                        self.update_task_status(result=ResultCode.OK)
                        self.stop_tracker_thread(timeout_id)

                    if self.check_command_exception(command_id, lrcr_callback):
                        self.update_task_status(
                            result=ResultCode.FAILED,
                            message=lrcr_callback.command_data[command_id][
                                "exception_message"
                            ],
                        )
                        self.stop_tracker_thread(timeout_id)

                except Exception as e:
                    self.logger.error(
                        "Exception occurred in Tracker thread: %s", e
                    )
                    self.update_task_status(
                        result=ResultCode.FAILED,
                        message="Exception occured in track transitions "
                        + f"thread: {e}",
                    )
                    self.stop_tracker_thread(timeout_id)
                time.sleep(0.1)

            if command_id:
                lrcr_callback.remove_data(command_id)

    def check_abort_event(self, abort_event) -> bool:
        """Checks for abort event. If abort event detected, sets TaskStatus
        to ABORTED and stops the tracker thread.
        :param abort_event: threading.Event class object that is used to check
        if the command has been aborted.
        """
        if abort_event.is_set():
            self.logger.error(
                "Command has been Aborted, " + "Setting TaskStatus to aborted"
            )
            return True
        return False

    def check_command_timeout(self, timeout_id, timeout_callback) -> bool:
        """Checks for command timeout. On timeout, it sets ResultCode
        to FAILED and stops the tracker thread.

        :param timeout_id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable function to call in the event of timeout.
        """
        if timeout_id:
            if timeout_callback.assert_against_call(
                timeout_id, TimeoutState.OCCURED
            ):
                self.logger.error("Timeout has occurred, command failed")
                return True
        return False

    def check_final_obsstate(
        self,
        state_function,
        state_to_achieve,
        expected_state,
    ) -> bool:
        """Waits for expected final obsState with or without
        transitional obsState. On expected obsState occurrence,
        it sets ResultCode to OK and stops the tracker thread

        :param state_function: a callable provides current state of
                                the device.

        :param state_to_achieve: A particular state to needs to be
                                achieved for command completion.

        :param expected_state: Expected state of the device in case of
                    successful command execution. It's a list contains
                    transitional obsState if exists for a command.
        """
        if state_function() == state_to_achieve:
            self.logger.info(
                "State change has occurred, current state is %s",
                state_to_achieve,
            )
            if len(expected_state) > self.index + 1:
                self.index += 1
                state_to_achieve = expected_state[self.index]
            else:
                self.logger.info(
                    "State change has occurred, command successful"
                )
                return True
        return False

    def check_command_exception(self, command_id, lrcr_callback) -> bool:
        """Checks if command has been failed with an exception.
        On exception, it sets ResultCode to FAILED and stops
        the tracker thread.

        :param command_id: Id for LRCRCallback class object.

        :param lrcr_callback: An instance of LRCRCallback class that acts
                    as a callable function to call when an event from the
                    attribute longRunningCommandResult arrives.
        """
        if command_id and lrcr_callback.assert_against_call(
            command_id, ResultCode.FAILED
        ):
            self.logger.error("Exception has occurred, command failed")
            return True
        return False

    def stop_tracker_thread(self, timeout_id) -> None:
        """External stop method for stopping the timer thread as well as the
        tracker thread."""
        if self.tracker_thread.is_alive():
            self.logger.info("Stopping tracker thread")
            self._stop = True
        if timeout_id:
            # The if else block is to keep backwards compatibility. Once all
            # repositories start using the TimeKeeper class, the block can be
            # replaced with the if part.
            if hasattr(self.component_manager, "timekeeper"):
                self.component_manager.timekeeper.stop_timer()
            else:
                self.component_manager.stop_timer()


class TMCCommand(BaseTMCCommand):
    """
    Class to add device adapters
    """

    def init_adapters(self):
        """
        Base method for init_adapters method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")

    def init_adapters_mid(self):
        """
        Base method for init_adapters_mid method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")

    def init_adapters_low(self):
        """
        Base method for init_adapters_low method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")

    def do_mid(self, argin=None):
        """
        Base method for do_mid method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")

    def do_low(self, argin=None):
        """
        Base method for do_low method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")


class TmcLeafNodeCommand(BaseTMCCommand):
    """
    Class to add adapters for LeafNode devices
    """

    def init_adapter(self):
        """
        Base method for init_adapter method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")

    def do_mid(self, argin=None):
        """
        Base method for do_mid method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")

    def do_low(self, argin=None):
        """
        Base method for do_low method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")

    def init_adapter_mid(self):
        """
        Base method for init_adapter_mid method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")

    def init_adapter_low(self):
        """
        Base method for init_adapter_low method for different nodes
        """
        raise NotImplementedError("This method must be inherited!")

    def call_adapter_method(
        self, device: str, adapter, command_name: str, argin=None
    ) -> Tuple[List[ResultCode], List[str]]:
        """
        Method to invoke commands on device adapters.
        """
        if adapter is None:
            return (
                [ResultCode.FAILED],
                [f"The proxy is missing for {device}"],
            )

        self.logger.info(
            f"Invoking {command_name} command on: {adapter.dev_name}"
        )
        try:
            if argin is not None:
                func = methodcaller(command_name, argin)
                result_code, message = func(adapter)
            else:
                func = methodcaller(command_name)
                result_code, message = func(adapter)
            return result_code, message

        except Exception as exp_msg:
            self.logger.exception("Command invocation failed: %s", exp_msg)
            return (
                [ResultCode.FAILED],
                [
                    f"The invocation of the {command_name} command is failed "
                    + f"on {device} device {adapter.dev_name}.\n"
                    + f"The following exception occurred - {exp_msg}."
                ],
            )
