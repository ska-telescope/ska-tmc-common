"""
A module defining a list of fixtures that are shared across all ska.base tests.
"""
"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
import importlib
import mock
import pytest
from tango import DeviceProxy
from tango.test_context import DeviceTestContext


@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    module = importlib.import_module("src/tmc/common")
    klass = getattr(module, "TangoClient")
    tango_context = DeviceTestContext(klass, properties=properties)
    tango_context.start()
    klass.get_name = mock.Mock(side_effect=tango_context.get_device_access)
    yield tango_context
    tango_context.stop()
