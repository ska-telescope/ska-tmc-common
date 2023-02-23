"""
This module implements ComponentManager class for the Csp Master Leaf Node.
"""
from typing import Tuple

from ska_tango_base.executor import TaskExecutorComponentManager, TaskStatus
from tango import DevState

from ska_tmc_common.exceptions import CommandNotAllowed


class TimeOutComponentManager(TaskExecutorComponentManager):
    """ """

    def __init__(
        self,
        logger,
        communication_state_callback=None,
        component_state_callback=None,
        max_workers=1,
    ):
        """ """
        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            max_workers=max_workers,
        )

        # self.command_object = Command(
        #     self, self.op_state_model, self._adapter_factory, logger
        # )

    def command(self, task_callback=None) -> Tuple[TaskStatus, str]:
        """Submits the command for execution.

        :rtype: tuple
        """
        task_status, response = self.submit_task(
            self.command_object.command,
            args=[self.logger],
            task_callback=task_callback,
        )
        self.logger.info("command queued for execution")
        return task_status, response

    def is_command_allowed(self, command_name: str) -> bool:
        """
        Checks whether this command is allowed.
        It checks that the device is in the right state to execute this command
        and that all the components needed for the operation are not
        unresponsive.

        :return: True if this command is allowed

        :rtype: boolean
        """

        if command_name in ["Command"]:
            if self.op_state_model.op_state in [
                DevState.FAULT,
                DevState.UNKNOWN,
            ]:
                raise CommandNotAllowed(
                    "The invocation of the {} command on this".format(
                        __class__
                    )
                    + "device is not allowed."
                    + "Reason: The current operational state is %s."
                    + "The command has NOT been executed."
                    + "This device will continue with normal operation.",
                    self.op_state_model.op_state,
                )
            return True
        return False
