"""Tests for the utilities in Dish Helper"""

import pytest

from ska_tmc_common import (
    AntennaLocation,
    AntennaParams,
    ConversionError,
    DishHelper,
)


@pytest.mark.parametrize(
    "dd, expected_dms",
    [
        pytest.param(30.7129252, "30:42:46.5307"),
        pytest.param(-30.7129252, "-30:42:46.5307"),
        pytest.param(2.4871655, "2:29:13.7958"),
        pytest.param(
            "2.4871655",
            "Error while converting 2.4871655 to Degree:Minutes:Seconds",
        ),
    ],
)
def test_degree_to_degree_minute_seconds(dd: float, expected_dms: str):
    """Test the degree decimal to Degrees:Minutes:Seconds conversion."""
    dish_helper = DishHelper()
    if isinstance(dd, float):
        dms = dish_helper.degree_to_degree_minute_seconds(dd)
        assert dms == expected_dms
    else:
        with pytest.raises(ConversionError) as conversion_error:
            dms = dish_helper.degree_to_degree_minute_seconds(dd)
        assert expected_dms in str(conversion_error)


@pytest.mark.parametrize(
    "dms, expected_dd",
    [
        pytest.param("30:42:46.5307", "30.7129252"),
        pytest.param("-30:42:46.5307", "-30.7129252"),
        pytest.param("2:29:13.7958", "2.4871655"),
        pytest.param("12", "Error while converting 12 to Degree Decimals"),
    ],
)
def test_degree_minute_seconds_to_degree(dms: str, expected_dd: str):
    """Test the Degrees:Minutes:Seconds to degree decimal conversion."""
    dish_helper = DishHelper()
    if len(dms) >= 11:
        dd = dish_helper.degree_minute_seconds_to_degree(dms)
        dd = str(round(float(dd), 7))
        assert dd == expected_dd
    else:
        with pytest.raises(ConversionError) as conversion_error:
            dd = dish_helper.degree_minute_seconds_to_degree(dms)
        assert expected_dd in str(conversion_error)


@pytest.mark.parametrize(
    "dd, expected_hms",
    [
        pytest.param(37.96199884, "2:31:50.88"),
        pytest.param(247.35191667, "16:29:24.46"),
        pytest.param(342.717625, "22:50:52.23"),
        pytest.param(
            "342.717625",
            "Error while converting 342.717625 to Hours:Minutes:Seconds",
        ),
    ],
)
def test_degree_to_hour_minute_seconds(dd: float, expected_hms: str):
    """Test the Hours:Minutes:Seconds to degree decimal conversion."""
    dish_helper = DishHelper()
    if isinstance(dd, float):
        hms = dish_helper.degree_to_hour_minute_seconds(dd)
        assert hms == expected_hms
    else:
        with pytest.raises(ConversionError) as conversion_error:
            hms = dish_helper.degree_to_hour_minute_seconds(dd)
        assert expected_hms in str(conversion_error)


def test_get_antenna_params():
    dish_helper = DishHelper()
    sample_location = {
        "diameter": 15.0,
        "location": {
            "geodetic": {
                "lat": -30.71292499,
                "lon": 21.44380263,
                "h": 1095.967,
            },
        },
        "station_label": "AC",
        "station_id": 0,
    }
    antenna_params = dish_helper.get_antenna_params(sample_location)
    assert antenna_params.dish_diameter == 15.0
    assert antenna_params.antenna_station_name == "AC"


def test_classes_defined_for_dish_helpers():
    """Test for AntennaLocation and AntennaParams"""
    antenna_params = AntennaParams()
    assert antenna_params.antenna_station_name == ""
    assert antenna_params.dish_diameter == 0.0
    assert isinstance(antenna_params.antenna_location, AntennaLocation)

    antenna_location = AntennaLocation()
    assert antenna_location.height == 0.0
    assert antenna_location.latitude == 0.0
    assert antenna_location.longitude == 0.0


def test_get_dish_antennas_list():
    dish_helper = DishHelper()
    antennas_list = dish_helper.get_dish_antennas_list()
    assert isinstance(antennas_list, list)
