"""Test aggregator classs"""

import pytest
from ska_control_model import ObsState

from ska_tmc_common.v1.aggregators import StateAggregator


class MockRule:
    """Mock rule for testing"""

    def __init__(self, should_match: bool):
        """Init method for mock rules."""
        self.should_match = should_match

    def matches(self, event_data: dict) -> bool:
        """return boolean values."""
        return self.should_match


def test_aggregator_returns_correct_obsstate():
    """Test aggregator for obsstate."""
    state_rules = {
        "IDLE": [MockRule(False)],
        "READY": [MockRule(True)],
    }

    aggregator = StateAggregator(ObsState, state_rules)
    result = aggregator.aggregate({"obs_state_data": {"mock": "data"}})

    assert result == ObsState.READY


def test_aggregator_raises_for_no_match():
    """Test aggregator when no match."""
    state_rules = {
        "IDLE": [MockRule(False)],
        "READY": [MockRule(False)],
    }

    aggregator = StateAggregator(ObsState, state_rules)

    with pytest.raises(ValueError, match="No matching state found"):
        aggregator.aggregate({"obs_state_data": {}})
