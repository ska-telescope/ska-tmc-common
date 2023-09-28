"""Tests for the utilities in Dish Helper"""
import pytest

from ska_tmc_common import DishHelper


@pytest.mark.parametrize(
    "dd, expected_dms",
    [
        pytest.param(30.7129252, "30:42:46.5307"),
        pytest.param(-30.7129252, "-30:42:46.5307"),
        pytest.param(2.4871655, "2:29:13.7958"),
    ],
)
def test_dd_to_dms(dd: float, expected_dms: str):
    """Test the degree decimal to DMS conversion."""
    dish_helper = DishHelper()
    dms = dish_helper.dd_to_dms(dd)
    assert dms == expected_dms


@pytest.mark.parametrize(
    "dms, expected_dd",
    [
        pytest.param("30:42:46.5307", "30.7129252"),
        pytest.param("-30:42:46.5307", "-30.7129252"),
        pytest.param("2:29:13.7958", "2.4871655"),
    ],
)
def test_dms_to_dd(dms: str, expected_dd: str):
    """Test the DMS to degree decimal conversion."""
    dish_helper = DishHelper()
    dd = dish_helper.dms_to_dd(dms)
    dd = str(round(float(dd), 7))
    assert dd == expected_dd




@pytest.mark.parametrize(
    "dd, expected_hms",
    [
        pytest.param(37.96199884, "2:31:50.88"),
        pytest.param(247.35191667,"16:29:24.46"),
        pytest.param(342.717625, "22:50:52.23")
    ],
)
def test_dms_to_dd(dd: float, expected_hms: str):
    """Test the DMS to degree decimal conversion."""
    dish_helper = DishHelper()
    hms = dish_helper.dd_to_hms(dd)
    assert hms == expected_hms
