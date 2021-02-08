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

from PyQt5.QtWidgets import QLineEdit
from qgis.gui import QgsFileWidget

from .base_panel import BasePanel
from ..definitions.gui import Panels
from ..definitions.settings import Settings
from ..qgis_plugin_tools.tools.custom_logging import get_log_level_key, LogTarget, get_log_level_name
from ..qgis_plugin_tools.tools.resources import plugin_name, plugin_path
from ..qgis_plugin_tools.tools.settings import set_setting

LOGGER = logging.getLogger(plugin_name())

LOGGING_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


# noinspection PyMethodMayBeStatic
class SettingsPanel(BasePanel):
    """
    This file is originally adapted from https://github.com/GispoCoding/qaava-qgis-plugin licensed under GPL version 2
    """

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.Settings

    # noinspection PyUnresolvedReferences
    def setup_panel(self):
        # Mapbox token
        line_edit_token: QLineEdit = self.dlg.le_mapbox_token
        line_edit_token.setText(Settings.mapbox_api_token.get())
        line_edit_token.textChanged.connect(self._mapbox_token_changed)

        # Configuration output
        f_conf_output: QgsFileWidget = self.dlg.f_conf_output
        f_conf_output.setFilePath(Settings.conf_output_dir.get())
        f_conf_output.fileChanged.connect(self._conf_output_dir_changed)

        # Logging
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

    def _conf_output_dir_changed(self, new_dir: str):
        if new_dir:
            Settings.conf_output_dir.set(new_dir)

    def _mapbox_token_changed(self, new_token: str):
        if new_token:
            Settings.mapbox_api_token.set(new_token)
