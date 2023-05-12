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
from typing import Callable, Optional, Tuple, Union

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
    SubArrayAdapter,
)
from ska_tmc_common.enum import TimeoutState
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
        ]
    ]:
        """
        Method to create adaptors for device.
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

    def update_task_status(self, result: ResultCode) -> NotImplementedError:
        """
        Base method for update_task_status method for different nodes
        """
        raise NotImplementedError(
            "This method must be implemented by command class"
        )

    def start_tracker_thread(
        self,
        state_function: Callable,
        expected_state: IntEnum,
        timeout_id: str,
        timeout_callback: TimeoutCallback,
    ) -> None:
        """Creates and starts a thread that will keep track of the State/
        obsState change to be monitored (For confirming command completion.
        Currently only supports obsState change.) and the timeout callback to
        montior the timeout.

        :param expected_state: Expected state of the device in case of
                    successful command execution.

        :param timeout_id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.
        """
        self.tracker_thread = threading.Thread(
            target=self.track_timeout_and_transition,
            args=[
                state_function,
                expected_state,
                timeout_id,
                timeout_callback,
            ],
        )
        self._stop = False
        self.logger.info("Starting tracker thread")
        self.tracker_thread.start()

    def track_timeout_and_transition(
        self,
        state_function: Callable,
        expected_state: IntEnum,
        timeout_id: str,
        timeout_callback: TimeoutCallback,
    ) -> None:
        """Keeps track of the obsState change and the timeout callback to
        determine whether timeout has occured or the command completed
        successfully. Logs the result for now.

        :param expected_state: Expected state of the device in case of
                    successful command execution.

        :param timeout_id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.
        """
        with EnsureOmniThread():
            while not self._stop:
                if state_function() == expected_state:
                    self.logger.info(
                        "State change has occured, command succeded"
                    )
                    self.update_task_status(result=ResultCode.OK)
                    self.stop_tracker_thread()

                elif timeout_callback.assert_against_call(
                    timeout_id, TimeoutState.OCCURED
                ):
                    self.logger.error("Timeout has occured, command failed")
                    self.update_task_status(result=ResultCode.FAILED)
                    self.stop_tracker_thread()
                time.sleep(0.1)

    def stop_tracker_thread(self) -> None:
        """External stop method for stopping the timer thread as well as the
        tracker thread."""
        if self.tracker_thread.is_alive():
            self.logger.info("Stopping tracker thread")
            self._stop = True
            self.component_manager.stop_timer()


class TMCCommand(BaseTMCCommand):
    """
    Class to add device adaptors
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
    Class to add adaptors for LeafNode devices
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
        Method to invoke commands on device adaptors.
        """
        if adapter is None:
            return ResultCode.FAILED, f"The proxy is missing for {device}"

        self.logger.info(
            f"Invoking {command_name} command on: {adapter.dev_name}"
        )
        try:
            if argin is not None:
                func = methodcaller(command_name, argin)
                func(adapter)
            else:
                func = methodcaller(command_name)
                func(adapter)

        except Exception as exp_msg:
            self.logger.exception("Command invocation failed: %s", exp_msg)
            return (
                ResultCode.FAILED,
                f"The invocation of the {command_name} command is failed on "
                + f"{device} device {adapter.dev_name}.\n"
                + f"Reason: Following exception occured - {exp_msg}.\n"
                + "The command has NOT been executed.\n"
                + "This device will continue with normal operation.",
            )
        self.logger.info(
            f"{command_name} command successfully invoked on:{adapter.dev_name}"
        )
        return ResultCode.OK, ""
