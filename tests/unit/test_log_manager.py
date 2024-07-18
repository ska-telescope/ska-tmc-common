import time

from ska_tmc_common.log_manager import LogManager


def test_is_logging_allowed_within_waiting_time():
    """Tests that is_logging_allowed returns False if logged recently."""
    log_manager = LogManager(max_waiting_time=2)
    log_manager.log_type_to_last_logged_time["log_type"] = time.time()
    assert log_manager.is_logging_allowed("log_type") is False

    time.sleep(2)

    assert log_manager.is_logging_allowed("log_type") is True


def test_is_logging_allowed_exceeded_waiting_time():
    """Tests that is_logging_allowed returns True if enough time passed"""
    log_manager = LogManager(max_waiting_time=2)  # Set lower wait time
    initial_last_logged_time = time.time()
    log_manager.log_type_to_last_logged_time[
        "Dev_error"
    ] = initial_last_logged_time

    # Assert initial state (before waiting time)
    assert log_manager.is_logging_allowed("Dev_error") is False
    assert (
        log_manager.last_log_type_time("Dev_error") == initial_last_logged_time
    )

    time.sleep(3)  # Wait for more than the waiting time

    # Assert after waiting time
    assert log_manager.is_logging_allowed("Dev_error") is True
    # Verify last_log_type_time is updated to the most recent log time
    assert (
        log_manager.last_log_type_time("Dev_error") > initial_last_logged_time
    )
