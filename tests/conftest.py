# pylint: disable=unused-argument
import logging

import pytest
import tango
from ska_tango_testing.mock import MockCallable
from tango.test_context import MultiDeviceTestContext

from ska_tmc_common import DevFactory, DummyTmcDevice

"""
A module defining a list of fixtures that are shared across all ska_tmc_common tests.
"""


def pytest_sessionstart(session):
    """
    Pytest hook; prints info about tango version.
    :param session: a pytest Session object
    :type session: class:`pytest.Session`
    """
    print(tango.utils.info())


def pytest_addoption(parser):
    """
    Pytest hook; implemented to add the `--true-context` option, used to
    indicate that a true Tango subsystem is available, so there is no
    need for a class:`tango.test_context.MultiDeviceTestContext`.
    :param parser: the command line options parser
    :type parser: class:`argparse.ArgumentParser`
    """
    parser.addoption(
        "--true-context",
        action="store_true",
        default=False,
        help=(
            "Tell pytest that you have a true Tango context and don't "
            "need to spin up a Tango test context"
        ),
    )


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": DummyTmcDevice,
            "devices": [
                {"name": "src/tmc/common"},
            ],
        },
    )


@pytest.fixture(scope="module")
def tango_context(devices_to_load, request):
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with MultiDeviceTestContext(devices_to_load, process=False) as context:
            DevFactory._test_context = context
            logging.info("test context set")
            yield context
    else:
        yield None


@pytest.fixture
def task_callback() -> MockCallable:
    """Creates a mock callable for asynchronous testing

    :rtype: MockCallable
    """
    task_callback = MockCallable(5)
    return task_callback
