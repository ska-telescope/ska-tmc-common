"""
This module implements ComponentManager class for the Csp Master Leaf Node.
"""
from typing import Tuple

from ska_tango_base.executor import TaskExecutorComponentManager, TaskStatus

from ska_tmc_common.timeout_device.event_receiver import EventReceiver
from ska_tmc_common.timeout_device.command import Command
from ska_tmc_common.timeout_callback import TimeoutCallback, TimeoutState
class TimeOutComponentManager(TaskExecutorComponentManager):
    """ """

    def __init__(
        self,
        logger,
        _event_receiver,
        max_workers=1,
    ):
        """ """
        super().__init__(
            logger,
            communication_state_callback=None,
            component_state_callback=None,
            max_workers=max_workers,
        )

        self.command_object = Command(
            self, logger
        )
        self.event_receiver = _event_receiver
        self.max_workers = max_workers

        if self.event_receiver:
            self.event_receiver_object = EventReceiver(
                self,
                logger=self.logger,
                proxy_timeout=100,
                sleep_time=5,
            )

    def start_timer(
        self, id: str, timeout: int, timeout_callback: TimeoutCallback
    ):
        """
        Starts a timer for the command execution which will run for
        <self.timeout> seconds. After the timer runs out, it will execute the
        task failed method.

        :param id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.
        """
        self.timer_object = threading.Timer(
            timeout,
            self.task_failed,
            args=[id, timeout_callback],
        )
        self.logger.info(f"Starting timer for id : {id}")
        self.timer_object.start()

    def task_failed(self, id: str, timeout_callback: TimeoutCallback):
        """
        Updates the timeout callback to reflect timeout failure.

        :param id: Id for TimeoutCallback class object.

        :param timeout_callback: An instance of TimeoutCallback class that acts
                    as a callable functions to call in the event of timeout.
        """
        self.logger.info(f"Timeout occured for id : {id}")
        timeout_callback(id=id, state=TimeoutState.OCCURED)

    def stop_timer(self):
        """Stops the timer for command execution"""
        self.logger.info("Stopping timer")
        self.timer_object.cancel()
        
    def start_event_receiver(self):
        """Starts the Event Receiver for given device"""
        if self.event_receiver:
            self.event_receiver_object.start()

    def stop_event_receiver(self):
        """Stops the Event Receiver"""
        if self.event_receiver:
            self.event_receiver_object.stop()

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

    def is_command_allowed(self) -> bool:
        """
        Checks whether this command is allowed.
        It checks that the device is in the right state to execute this command
        and that all the components needed for the operation are not
        unresponsive.

        :return: True if this command is allowed

        :rtype: boolean
        """

        return True
