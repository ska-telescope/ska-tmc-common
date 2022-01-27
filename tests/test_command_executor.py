import pytest
from ska_tmc_common.command_executor import CommandExecutor
from tests.settings import logger
from ska_tmc_common.tmc_command import TMCCommand

class TestCommand():
    def __init__(self, logger=logger):
        self.logger = logger

    def do(self):
        self.logger.info("do method execution")
        return True


@pytest.mark.executor
def test_enqueue_command():
    executor = CommandExecutor(logger, 2)
    command = TestCommand()
    id = executor.enqueue_command(command)
    assert "TestCommand" in id

@pytest.mark.executor
def test_queue_full():
    executor = CommandExecutor(logger, 2)
    command = TestCommand()
    id = executor.enqueue_command(command)
    id = executor.enqueue_command(command)
    assert executor.queue_full == True