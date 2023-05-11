#  Gispo Ltd., hereby disclaims all copyright interest in the program Foursquare
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of Foursquare.
#
#  kepler QGIS plugin by Foursquare is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  kepler QGIS plugin by Foursquare is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with kepler QGIS plugin by Foursquare.  If not, see <https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html>.

import os

from .qgis_plugin_tools.infrastructure.debugging import setup_pydevd

if os.environ.get('QGIS_PLUGIN_USE_DEBUGGER') == 'pydevd':
    if os.environ.get('IN_TESTS', "0") != "1" and os.environ.get('QGIS_PLUGIN_IN_CI', "0") != "1":
        setup_pydevd()


def classFactory(iface):
    from .plugin import Plugin
    return Plugin(iface)
