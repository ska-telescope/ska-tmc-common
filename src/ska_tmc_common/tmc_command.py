import threading
import time
from enum import IntEnum
from operator import methodcaller
from typing import Callable, Optional

from ska_tango_base.commands import BaseCommand, ResultCode
from tango import EnsureOmniThread

from ska_tmc_common.enum import TimeoutState
from ska_tmc_common.lrcr_callback import LRCRCallback
from ska_tmc_common.timeout_callback import TimeoutCallback


class CommandNotAllowed(Exception):
    """Raised when a command is not allowed."""


class TMCCommand(BaseCommand):
    def __init__(self, target, *args, logger=None, **kwargs):
        super().__init__(target, args, logger, kwargs)

    def generate_command_result(self, result_code, message):
        if result_code == ResultCode.FAILED:
            self.logger.error(message)
        self.logger.info(message)
        return (result_code, message)

    def adapter_error_message_result(self, dev_name, e):
        message = f"Error in creating adapter for {dev_name}: {e}"
        self.logger.error(message)
        return ResultCode.FAILED, message

    def check_allowed(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapters(self):
        raise NotImplementedError("This class must be inherited!")

    def do(self, argin=None):
        raise NotImplementedError("This class must be inherited!")

    def check_allowed_mid(self):
        raise NotImplementedError("This class must be inherited!")

    def check_allowed_low(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapters_mid(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapters_low(self):
        raise NotImplementedError("This class must be inherited!")

    def do_mid(self, argin=None):
        raise NotImplementedError("This class must be inherited!")

    def do_low(self, argin=None):
        raise NotImplementedError("This class must be inherited!")


class TmcLeafNodeCommand(BaseCommand):
    def __init__(self, target, *args, logger=None, **kwargs):
        super().__init__(target, *args, logger=logger, **kwargs)

    def generate_command_result(self, result_code, message):
        if result_code == ResultCode.FAILED:
            self.logger.error(message)
        self.logger.info(message)
        return (result_code, message)

    def adapter_error_message_result(self, dev_name, e):
        message = f"Error in creating adapter for {dev_name}: {e}"
        self.logger.error(message)
        return ResultCode.FAILED, message

    def call_adapter_method(self, device, adapter, command_name, *args):
        argin = None
        for value in args:
            argin = value

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
            return self.generate_command_result(
                ResultCode.FAILED,
                f"The invocation of the {command_name} command is failed on "
                f"{device} device {adapter.dev_name}.\n"
                f"Reason: Error in calling the {command_name} command on {device}.\n"
                "The command has NOT been executed.\n"
                "This device will continue with normal operation.",
            )
        self.logger.info(
            f"{command_name} command successfully invoked on:{adapter.dev_name}"
        )
        return (ResultCode.OK, "")

    def check_allowed(self):
        raise NotImplementedError("This class must be inherited!")

    def init_adapter(self):
        raise NotImplementedError("This class must be inherited!")

    def do(self, argin=None):
        raise NotImplementedError("This class must be inherited!")

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
                    as a callable function to call in the event of timeout.

        :param command_id: Id for LRCRCallback class object.

        :param lrcr_callback: An instance of LRCRCallback class that acts
                    as a callable function to call when an event from the
                    attribute longRunningCommandResult arrives.
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
                            self.stop_tracker_thread()
                except Exception as e:
                    self.logger.error(
                        "Exception occured in Tracker thread: %s", e
                    )
                time.sleep(0.1)

            if command_id:
                lrcr_callback.remove_data(command_id)

    def stop_tracker_thread(self) -> None:
        """External stop method for stopping the timer thread as well as the
        tracker thread."""
        if self.tracker_thread.is_alive():
            self.logger.info("Stopping tracker thread")
            self._stop = True
            self.component_manager.stop_timer()
