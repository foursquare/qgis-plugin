#  Gispo Ltd., hereby disclaims all copyright interest in the program Unfolded Studio QGIS plugin
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of Unfolded Studio QGIS plugin.
#
#  Unfolded Studio QGIS plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  Unfolded Studio QGIS plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Unfolded Studio QGIS plugin.  If not, see <https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html>.

import logging
import webbrowser

from .base_panel import BasePanel
from ..definitions.gui import Panels
from ..qgis_plugin_tools.tools.custom_logging import get_log_level_key, LogTarget, get_log_level_name
from ..qgis_plugin_tools.tools.resources import plugin_name, plugin_path
from ..qgis_plugin_tools.tools.settings import set_setting

LOGGER = logging.getLogger(plugin_name())

LOGGING_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class SettingsPanel(BasePanel):
    """
    This file is adapted from https://github.com/GispoCoding/qaava-qgis-plugin licensed under GPL version 2
    """

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.Settings

    def setup_panel(self):
        self.dlg.combo_box_log_level_file.clear()
        self.dlg.combo_box_log_level_console.clear()

        self.dlg.combo_box_log_level_file.addItems(LOGGING_LEVELS)
        self.dlg.combo_box_log_level_console.addItems(LOGGING_LEVELS)
        self.dlg.combo_box_log_level_file.setCurrentText(get_log_level_name(LogTarget.FILE))
        self.dlg.combo_box_log_level_console.setCurrentText(get_log_level_name(LogTarget.STREAM))

        self.dlg.combo_box_log_level_file.currentTextChanged.connect(
            lambda level: set_setting(get_log_level_key(LogTarget.FILE), level))

        self.dlg.combo_box_log_level_console.currentTextChanged.connect(
            lambda level: set_setting(get_log_level_key(LogTarget.STREAM), level))

        self.dlg.btn_open_log.clicked.connect(lambda _: webbrowser.open(plugin_path("logs", f"{plugin_name()}.log")))
