"""
This module implements the Helper Mccs subarray device
"""
import json

# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
import time

from ska_tango_base.commands import ResultCode

from ska_tmc_common.test_helpers.helper_subarray_device import (
    HelperSubArrayDevice,
)


class HelperMccsSubarrayDevice(HelperSubArrayDevice):
    """
    A device exposing commands and attributes of the Mccs Subarray Device.
    """

    def push_command_result(
        self, result: ResultCode, command_name: str, message: str
    ) -> None:
        """Push long running command result event for given command.
        :param result: The result code to be pushed as an event
        :type: ResultCode
        :param command_name: The command name for which event is being pushed
        :type: str
        """
        command_id = f"{time.time()}-{command_name}"
        self.logger.info(
            "The command_id is %s and the ResultCode is %s", command_id, result
        )
        command_result = command_id, json.dumps((result, message))
        self.logger.info(
            "Pushing longRunningCommandResult Event with data: %s",
            command_result,
        )
        self.push_change_event("longRunningCommandResult", command_result)
