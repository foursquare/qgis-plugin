#  Gispo Ltd., hereby disclaims all copyright interest in the program Foursquare
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of Foursquare .
#
#  kepler.gl QGIS plugin by Foursquare is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  kepler.gl QGIS plugin by Foursquare is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with kepler.gl QGIS plugin by Foursquare.  If not, see <https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html>.
from ..qgis_plugin_tools.tools.exceptions import QgsPluginException


class ProcessInterruptedException(QgsPluginException):
    pass


class InvalidInputException(QgsPluginException):
    pass


class MapboxTokenMissing(QgsPluginException):
    pass


class ExportException(QgsPluginException):
    pass
