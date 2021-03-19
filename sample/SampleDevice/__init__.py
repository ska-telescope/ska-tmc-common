# -*- coding: utf-8 -*-
#
# This file is part of the SampleDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SampleServer

"""

from . import release
from .SampleDevice import SampleDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
