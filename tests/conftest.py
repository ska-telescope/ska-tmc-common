import importlib
import logging

import mock
import pytest
import tango
from tango.test_context import DeviceTestContext, MultiDeviceTestContext

from ska_tmc_common.dev_factory import DevFactory

"""
A module defining a list of fixtures that are shared across all ska.base tests.
"""


def pytest_sessionstart(session):
    """
    Pytest hook; prints info about tango version.
    :param session: a pytest Session object
    :type session: :py:class:`pytest.Session`
    """
    print(tango.utils.info())


@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and Yields a TANGO DeviceTestContext object.

    :param request: _pytest.fixtures.SubRequest.

    A request object gives access to the requesting test context.
    """
    module = importlib.import_module("src/tmc/common")
    klass = getattr(module, "TangoClient")
    properties = request
    tango_context = DeviceTestContext(klass, properties=properties)
    tango_context.start()
    klass.get_name = mock.Mock(side_effect=tango_context.get_device_access)
    yield tango_context
    tango_context.stop()


def pytest_addoption(parser):
    """
    Pytest hook; implemented to add the `--true-context` option, used to
    indicate that a true Tango subsystem is available, so there is no
    need for a :py:class:`tango.test_context.MultiDeviceTestContext`.
    :param parser: the command line options parser
    :type parser: :py:class:`argparse.ArgumentParser`
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


@pytest.fixture(scope="module")
def tango_context_multitest(devices_to_load, request):
    true_context = request.config.getoption("--true-context")
    logging.info("true context: %s", true_context)
    if not true_context:
        with MultiDeviceTestContext(devices_to_load, process=False) as context:
            DevFactory._test_context = context
            logging.info("test context set")
            yield context
    else:
        yield None
