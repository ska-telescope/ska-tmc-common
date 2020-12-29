# -*- coding: utf-8 -*-
#
# This file is part of the ska-tmc-common project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

"""
ska-tmc-common
"""

from . import release
from .tango_client import TangoClient
from .tango_group_client import TangoGroupClient
from .tango_server_helper import TangoServerHelper

__all__ = ["release", "TangoClient", "TangoGroupClient", "TangoServerHelper"]

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author