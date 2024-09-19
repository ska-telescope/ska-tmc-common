"""Test for the Aggregators class"""

import pytest

from ska_tmc_common import Aggregator
from tests.conftest import logger


def cm():
    """A dummy component manager to test aggregators"""


def test_aggregator():
    """A test for aggregator class"""
    aggregator = Aggregator(cm, logger)
    with pytest.raises(NotImplementedError):
        aggregator.aggregate()
