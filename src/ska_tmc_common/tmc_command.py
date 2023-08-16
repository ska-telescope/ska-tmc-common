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
from tango import ConnectionFailed, DevFailed, EnsureOmniThread

from ska_tmc_common.adapters import (
    AdapterFactory,
    AdapterType,
    BaseAdapter,
    CspMasterAdapter,
    CspSubarrayAdapter,
    DishAdapter,
    MCCSAdapter,
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
        self.tracker_thread: threading.Thread
        self._stop: bool

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
            MCCSAdapter,
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
        self, result: ResultCode, message: str = ""
    ) -> NotImplementedError:
        """Method to update the task status for command."""
        raise NotImplementedError(
            "This method must be implemented by command class"
        )

    def start_tracker_thread(
        self,
        state_function: Callable,
        expected_state: List[IntEnum],
        timeout_id: Optional[str] = None,
        timeout_callback: Optional[TimeoutCallback] = None,
        command_id: Optional[str] = None,
        lrcr_callback: Optional[LRCRCallback] = None,
    ) -> None:
        """Creates and starts a thread that will keep track of the State/
        obsState change to be monitored (For confirming command completion.
        Currently only supports obsState change.), the timeout callback to
        montior the timeout and the longRunningCommandResult callback to keep
        track of LRCR events.

        :param expected_state: Expected state of the device in case of
                    successful command execution.

        :param timeout_id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.

        :param command_id: Id for LRCRCallback class object.

        :param lrcr_callback: An instance of LRCRCallback class that acts
                    as a callable functions to call when
                    longRunningCommandResult event is recieved.
        """
        self.tracker_thread = threading.Thread(
            target=self.track_transitions,
            args=[
                state_function,
                expected_state,
                timeout_id,
                timeout_callback,
                command_id,
                lrcr_callback,
            ],
        )
        self._stop = False
        self.logger.info("Starting tracker thread")
        self.tracker_thread.start()

    def track_transitions(
        self,
        state_function: Callable,
        expected_state: List[IntEnum],
        timeout_id: Optional[str] = None,
        timeout_callback: Optional[TimeoutCallback] = None,
        command_id: Optional[str] = None,
        lrcr_callback: Optional[LRCRCallback] = None,
    ) -> None:
        """Keeps track of the obsState change and the timeout callback to
        determine whether timeout has occured or the command completed
        successfully. Logs the result for now.

        :param expected_state: Expected state of the device in case of
                    successful command execution.

        :param timeout_id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable function to call in the event of timeout.

        :param command_id: Id for LRCRCallback class object.

        :param lrcr_callback: An instance of LRCRCallback class that acts
                    as a callable function to call when an event from the
                    attribute longRunningCommandResult arrives.
        """
        with EnsureOmniThread():
            index = 0
            self.logger.info(f"expected states:{expected_state}")
            state_to_achieve = expected_state[index]
            self.logger.info(f"state to acheve:{state_to_achieve}")
            while not self._stop:
                try:
                    self.logger.info(f"state functions:{state_function()}")
                    self.logger.info(
                        f"state to acheve inside try:{state_to_achieve}"
                    )
                    if state_function() == state_to_achieve:
                        self.logger.info(
                            "State change has occured, current state is %s",
                            state_to_achieve,
                        )
                        self.logger.info(
                            f"length of expected state:{len(expected_state)}"
                        )
                    else:
                        self.logger.info(
                            "Outside if condition,condition failed."
                        )
                    if len(expected_state) > index + 1:
                        self.logger.info("inside 2nd if condition")
                        index += 1
                        state_to_achieve = expected_state[index]
                    else:
                        self.logger.info(
                            "State change has occured, command successful"
                        )
                        self.update_task_status(result=ResultCode.OK)
                        self.stop_tracker_thread(timeout_id)

                    if timeout_id:
                        if timeout_callback.assert_against_call(
                            timeout_id, TimeoutState.OCCURED
                        ):
                            self.logger.error(
                                "Timeout has occured, command failed"
                            )
                            self.update_task_status(
                                result=ResultCode.FAILED,
                                message="Timeout has occured, command failed",
                            )
                            self.stop_tracker_thread(timeout_id)

                    if command_id:
                        if lrcr_callback.assert_against_call(
                            command_id, ResultCode.FAILED
                        ):
                            self.logger.error(
                                "Exception has occured, command failed"
                            )
                            self.update_task_status(
                                result=ResultCode.FAILED,
                                message=lrcr_callback.command_data[command_id][
                                    "exception_message"
                                ],
                            )
                            self.stop_tracker_thread(timeout_id)
                except Exception as e:
                    self.update_task_status(
                        result=ResultCode.FAILED,
                        message=lrcr_callback.command_data[command_id][e],
                    )
                    self.stop_tracker_thread(timeout_id)
                    self.logger.error(
                        "Exception occured in Tracker thread: %s", e
                    )
                time.sleep(0.1)

            if command_id:
                lrcr_callback.remove_data(command_id)

    def stop_tracker_thread(self, timeout_id) -> None:
        """External stop method for stopping the timer thread as well as the
        tracker thread."""
        if self.tracker_thread.is_alive():
            self.logger.info("Stopping tracker thread")
            self._stop = True
            if timeout_id:
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
    ) -> Tuple[ResultCode, str]:
        """
        Method to invoke commands on device adapters.
        """
        if adapter is None:
            return ResultCode.FAILED, f"The proxy is missing for {device}"

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
                ResultCode.FAILED,
                f"The invocation of the {command_name} command is failed on "
                + f"{device} device {adapter.dev_name}.\n"
                + f"The following exception occurred - {exp_msg}.",
            )
