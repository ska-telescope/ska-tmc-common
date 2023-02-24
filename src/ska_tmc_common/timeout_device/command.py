from typing import Optional, Tuple
import logging
import time
from tango import DeviceProxy
from ska_tmc_common.timeout_callback import TimeoutCallback
from ska_tmc_common.tmc_command import BaseTMCCommand

from ska_tango_base.commands import ResultCode
from ska_tango_base.executor import TaskStatus

class Command(BaseTMCCommand):
    """A simple command class."""

    def __init__(self, component_manager, logger: Optional[logging.Logger] = None, *args, **kwargs):
        super().__init__(component_manager, logger, *args, **kwargs)
        self.id = f"{time.time()}_{__class__.__name__}"
        self.timeout_callback = TimeoutCallback(id=self.id)


    def invoke_command(self, task_callback, abort_event):
        """Invokes the do method for command class, setting the task callback
        to appropriate value."""

        task_callback(status=TaskStatus.IN_PROGRESS)

        self.component_manager.start_timer(
            self.id,
            self.component_manager.timeout,
            self.timeout_callback,
        )
        result, message = self.do()

        if result == ResultCode.FAILED:
            self.logger.error("Invocation of Command failed with message : %s", message)
            task_callback(
                status=TaskStatus.COMPLETED,
                result=ResultCode.FAILED,
                exception=message,
            )
            self.component_manager.stop_timer()
        else:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=result,
            )


    def track_state(self):
        """Simple method to track the state change to expected value after
        invocation of the command."""


    def do(self, argin=None) -> Tuple[ResultCode, str]:
        """Simple do method to invoke command on lower device."""
        proxy = DeviceProxy("")
        result, message = proxy.On()
        return result, message
