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
from ska_tmc_common.enum import ExceptionState, TimeoutState
from ska_tmc_common.lrcr_callback import LRCRCallback
from ska_tmc_common.op_state_model import TMCOpStateModel
from ska_tmc_common.timeout_callback import TimeoutCallback
from ska_tmc_common.tmc_component_manager import BaseTmcComponentManager


class BaseTMCCommand:
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
            except Exception as e:
                self.logger.error(
                    "Unexpected error occured while creating the adapter: %s",
                    e,
                )
                raise

    def do(self, argin=None) -> NotImplementedError:
        raise NotImplementedError(
            "This method must be implemented by command class"
        )

    def update_task_status(
        self, result: ResultCode, message: str = ""
    ) -> NotImplementedError:
        raise NotImplementedError(
            "This method must be implemented by command class"
        )

    def start_tracker_thread(
        self,
        state_function: Callable,
        expected_state: IntEnum,
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
                    as a callable functions to call when longRunningCommandResult
                    event is recieved.
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
        expected_state: IntEnum,
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
                    as a callable functions to call in the event of timeout.
        """
        with EnsureOmniThread():
            while not self._stop:
                try:
                    if state_function() == expected_state:
                        self.logger.info(
                            "State change has occured, command succeded"
                        )
                        self.update_task_status(result=ResultCode.OK)
                        self.stop_tracker_thread()

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
                            self.stop_tracker_thread()

                    if command_id:
                        if lrcr_callback.assert_against_call(
                            command_id, ExceptionState.EXCEPTION_OCCURED
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
                            self.stop_tracker_thread()
                except Exception as e:
                    self.logger.error(
                        "Exception occured in Tracker thread: %s", e
                    )

                time.sleep(0.1)

    def stop_tracker_thread(self) -> None:
        """External stop method for stopping the timer thread as well as the
        tracker thread."""
        if self.tracker_thread.is_alive():
            self.logger.info("Stopping tracker thread")
            self._stop = True
            self.component_manager.stop_timer()


class TMCCommand(BaseTMCCommand):
    def init_adapters(self):
        raise NotImplementedError("This method must be inherited!")

    def init_adapters_mid(self):
        raise NotImplementedError("This method must be inherited!")

    def init_adapters_low(self):
        raise NotImplementedError("This method must be inherited!")

    def do_mid(self, argin=None):
        raise NotImplementedError("This method must be inherited!")

    def do_low(self, argin=None):
        raise NotImplementedError("This method must be inherited!")


class TmcLeafNodeCommand(BaseTMCCommand):
    def init_adapter(self):
        raise NotImplementedError("This method must be inherited!")

    def do_mid(self, argin=None):
        raise NotImplementedError("This method must be inherited!")

    def do_low(self, argin=None):
        raise NotImplementedError("This method must be inherited!")

    def init_adapter_mid(self):
        raise NotImplementedError("This method must be inherited!")

    def init_adapter_low(self):
        raise NotImplementedError("This method must be inherited!")

    def call_adapter_method(
        self, device: str, adapter, command_name: str, argin=None
    ) -> Tuple[ResultCode, str]:
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

        except Exception as e:
            self.logger.exception("Command invocation failed: %s", e)
            return (
                ResultCode.FAILED,
                f"The invocation of the {command_name} command is failed on "
                + f"{device} device {adapter.dev_name}.\n"
                + f"Reason: Followin exception occured - {e}.\n"
                + "The command has NOT been executed.\n"
                + "This device will continue with normal operation.",
            )
        self.logger.info(
            f"{command_name} command successfully invoked on:{adapter.dev_name}"
        )
        return ResultCode.OK, ""
