# -*- coding: utf-8 -*-
#
# This file is part of the DishLeafNode project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.
""" The purpose of this module is to provide classes and
methods used in dish related calculations.
"""
# Standard Python imports

import logging
import math
import re

import katpoint
from ska_telmodel.data import TMData

from ska_tmc_common.exceptions import ConversionError

LAYOUT_PATH = "instrument/ska1_mid/layout/mid-layout.json"
GITLAB_MAIN_PATH = "gitlab://gitlab.com/ska-telescope/"
GITLAB_SUB_PATH = "ska-telmodel-data?main#tmdata"
logger = logging.getLogger(__name__)


class AntennaLocation:
    """class to init antenna location parameters"""

    def __init__(self) -> None:
        "Class constructor"
        self.latitude = 0.0
        self.longitude = 0.0
        self.height = 0.0


class AntennaParams:
    """Class to define antenna parameters"""

    def __init__(self) -> None:
        """AntennaParams Constructor"""
        self.antenna_station_name = ""
        self.antenna_location = AntennaLocation()
        self.dish_diameter = 0.0


class DishHelper:
    """Class to provide support for dish related calculations."""

    def get_antenna_params(self, antenna_params):
        """Method to return object of class AntennaParams"""
        antenna_location = AntennaLocation()
        antenna_param = AntennaParams()

        antenna_location.latitude = float(
            antenna_params["location"]["geodetic"]["lat"]
        )
        antenna_location.longitude = float(
            antenna_params["location"]["geodetic"]["lon"]
        )
        antenna_location.height = float(
            antenna_params["location"]["geodetic"]["h"]
        )
        antenna_param.antenna_location = antenna_location
        antenna_param.dish_diameter = antenna_params["diameter"]
        antenna_param.antenna_station_name = antenna_params["station_label"]
        return antenna_param

    def degree_to_degree_minute_seconds(self, argin: float) -> str:
        """
        Converts a number in degree decimal to Deg:Min:Sec.

        :param argin: A number in decimal degrees.
            Example: 30.7129252
        :return: Number in deg:min:sec format.
            Example: 30:42:46.5307 is returned value for input 30.7129252.
        """
        dms_str = ""  # degree:minutes:seconds
        try:
            sign = 1
            if argin < 0:
                sign = -1
            fraction_min, degrees = math.modf(abs(argin))
            fraction_sec, minutes = math.modf(fraction_min * 60)
            seconds = fraction_sec * 60
            dms_str = (
                f"{int(degrees * sign)}:{int(minutes)}:{round(seconds, 4)}"
            )
        except Exception as error:
            logger.error(
                "Error while converting decimal degree to deg:min:sec -> %s",
                error,
            )
            raise ConversionError(
                f"Error while converting {argin} to Degree:Minutes:Seconds"
            ) from error
        return str(dms_str)

    def degree_minute_seconds_to_degree(self, argin: str) -> str:
        """This method converts the give angle in Degrees:Minutes:Seconds to
        decimal degrees.

        :param argin: Input angle in D:M:S
        :dtype: str, example -> 30:42:46.5307

        :return: Angle in degree decimals.
        :rtype: str, example -> 30.7129252.

        :raises: ConversionError if the conversion fails.
        """
        try:
            dms_list = re.split(":", argin)
            if float(dms_list[0]) < 0:
                degree_decimals = (
                    float(dms_list[0])
                    - float(dms_list[1]) / 60
                    - float(dms_list[2]) / 3600
                )
            else:
                degree_decimals = (
                    float(dms_list[0])
                    + float(dms_list[1]) / 60
                    + float(dms_list[2]) / 3600
                )
        except Exception as error:
            logger.error(
                "Error occured while converting %s to Degree decimals : %s",
                argin,
                error,
            )
            raise ConversionError(
                f"Error while converting {argin} to Degree Decimals"
            ) from error
        return str(degree_decimals)

    def degree_to_hour_minute_seconds(self, argin: float) -> str:
        """
        Converts a number in degree decimal to Hours:Minutes:Seconds

        :param argin: A number in decimal degrees.
            Example: 37.96199884
        :return: Number in Hours:Minutes:Seconds format.
            Example: 2:31:50.88 is returned value for input 37.96199884.
        """
        try:
            fractions, ra_hours = math.modf(argin / 15.0)
            fractions, ra_minutes = math.modf(fractions * 60)
            ra_seconds = fractions * 60
            hours_minutes_seconds = (
                f"{int(ra_hours)}:{int(ra_minutes)}:{round(ra_seconds,2)}"
            )
        except Exception as error:
            logger.error(
                "Error while converting decimal degree to HH:MM:SS -> %s",
                error,
            )
            raise ConversionError(
                f"Error while converting {argin} to Hours:Minutes:Seconds"
            ) from error
        return hours_minutes_seconds

    def get_dish_antennas_list(self):
        """This method returns the antennas list.It gets the
        information from TelModel library.Each antenna in the list
        represents an antenna and have information station name, latitude,
        longitude, dish diameter, height.
        """
        antennas = []
        try:
            sources = [GITLAB_MAIN_PATH + GITLAB_SUB_PATH]
            antenna_params = TMData(sources)[LAYOUT_PATH].get_dict()

            for receptor in range(len(antenna_params["receptors"])):
                receptor_params = self.get_antenna_params(
                    antenna_params["receptors"][receptor]
                )

                input_to_antenna = f"{receptor_params.antenna_station_name},\
                        {self.degree_to_degree_minute_seconds(receptor_params.antenna_location.latitude)},\
                            {self.degree_to_degree_minute_seconds(receptor_params.antenna_location.longitude)},\
                                {receptor_params.antenna_location.height},\
                                    {receptor_params.dish_diameter}"
                antennas.append(katpoint.Antenna(input_to_antenna))

        except OSError as err:
            logger.exception(err)
            raise

        except ValueError as verr:
            logger.exception(verr)
            raise

        return antennas
