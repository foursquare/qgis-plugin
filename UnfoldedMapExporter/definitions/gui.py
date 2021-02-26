#  Gispo Ltd., hereby disclaims all copyright interest in the program Unfolded Map Exporter
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of Unfolded Map Exporter.
#
#  Unfolded Map Exporter is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  Unfolded Map Exporter is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Unfolded Map Exporter.  If not, see <https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html>.
import enum

from PyQt5.QtGui import QIcon
from qgis._core import QgsApplication

from ..qgis_plugin_tools.tools.resources import resources_path


class Panels(enum.Enum):
    """
    Panels in the Dialog

    This class is adapted from https://github.com/GispoCoding/qaava-qgis-plugin licensed under GPL version 2
    """
    Export = {'icon': '/mActionSharingExport.svg'}
    Settings = {'icon': '/mActionMapSettings.svg'}
    About = {'icon': '/mActionHelpContents.svg'}

    # noinspection PyCallByClass,PyArgumentList
    @property
    def icon(self) -> QIcon:
        _icon: str = self.value['icon']

        # QGIS icons
        # https://github.com/qgis/QGIS/tree/master/images/themes/default
        if _icon.startswith("/"):
            return QgsApplication.getThemeIcon(_icon)
        else:
            # Internal icons
            return QIcon(resources_path('icons', _icon))
