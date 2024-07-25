import time

import pytest

from ska_tmc_common.log_manager import LogManager


@pytest.mark.ska5
def test_is_logging_allowed_within_waiting_time():
    """Tests that is_logging_allowed returns False if logged recently."""
    log_manager = LogManager(max_waiting_time=5)
    # log_manager.log_type_to_last_logged_time["log_type"] = time.time()
    assert log_manager.is_logging_allowed("log_type") is True

    time.sleep(2)

    assert log_manager.is_logging_allowed("log_type") is False

    time.sleep(6)

    assert log_manager.is_logging_allowed("log_type") is True


@pytest.mark.ska5
def test_is_logging_allowed_exceeded_waiting_time():
    """Tests that is_logging_allowed returns True if enough time passed"""
    log_manager = LogManager(max_waiting_time=2)  # Set lower wait time
    initial_last_logged_time = time.time()
    log_manager.log_type_to_last_logged_time[
        "Dev_error"
    ] = initial_last_logged_time

    # Assert initial state (before waiting time)
    assert log_manager.is_logging_allowed("Dev_error") is False

    time.sleep(3)  # Wait for more than the waiting time

    # Assert after waiting time
    assert log_manager.is_logging_allowed("Dev_error") is True
    # Verify last_log_type_time is updated to the most recent log time
