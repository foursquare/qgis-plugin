#  Gispo Ltd., hereby disclaims all copyright interest in the program Unfolded QGIS plugin
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of Unfolded QGIS plugin.
#
#  Unfolded QGIS plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  Unfolded QGIS plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Unfolded QGIS plugin.  If not, see <https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html>.

import logging

from .base_panel import BasePanel
from ..definitions.gui import Panels
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name
from ..qgis_plugin_tools.tools.version import version

LOGGER = logging.getLogger(plugin_name())


class AboutPanel(BasePanel):
    """
    This file is taken from https://github.com/GispoCoding/qaava-qgis-plugin licensed under GPL version 2
    """

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.About

    def setup_panel(self):
        v = version()
        LOGGER.info(tr(u"Plugin version is {}", v))
        self.dlg.label_version.setText(v)
