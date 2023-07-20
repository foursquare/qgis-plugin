#  Gispo Ltd., hereby disclaims all copyright interest in the program kepler QGIS plugin by Foursquare
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of kepler QGIS plugin by Foursquare.
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

import logging

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox, QDesktopWidget

from .about_panel import AboutPanel
from .export_panel import ExportPanel
from .settings_panel import SettingsPanel
from ..core.utils import set_project_crs
from ..definitions.gui import Panels
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import load_ui, plugin_name, resources_path

FORM_CLASS = load_ui('kepler_dialog.ui')
LOGGER = logging.getLogger(plugin_name())


class Dialog(QDialog, FORM_CLASS):
    """
    The structure and idea of the UI is adapted https://github.com/GispoCoding/qaava-qgis-plugin and originally
    from https://github.com/3liz/QuickOSM. Both projects are licenced under GPL version 2
    """

    def __init__(self, parent=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(resources_path('icons', 'icon.png')))
        self.is_running = False

        self._set_window_location()

        self.panels = {
            Panels.Export: ExportPanel(self),
            Panels.Settings: SettingsPanel(self),
            Panels.About: AboutPanel(self)
        }

        self.responsive_elements = {
            Panels.Export: [self.btn_export, self.gb_, self.gb_1, self.gb_2, self.gb_3],
            Panels.Settings: [],
            Panels.About: []
        }

        for i, panel in enumerate(self.panels):
            item = self.menu_widget.item(i)
            item.setIcon(panel.icon)
            self.panels[panel].panel = panel

        # Change panel as menu item is changed
        self.menu_widget.currentRowChanged['int'].connect(
            self.stacked_widget.setCurrentIndex)

        try:
            for panel in self.panels.values():
                panel.setup_panel()
        except Exception as e:
            LOGGER.exception(tr(u'Unhandled exception occurred during UI initialization.'), bar_msg(e))

        # The first panel is shown initially
        self.menu_widget.setCurrentRow(0)

        # Change crs if needed
        set_project_crs()

    def _set_window_location(self):
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        widget = self.geometry()
        x = (ag.width() - widget.width()) / 1.5
        y = 2 * ag.height() - sg.height() - 1.2 * widget.height()
        self.move(x, y)

    def ask_confirmation(self, title: str, msg: str) -> bool:
        """
        Ask confirmation via QMessageBox question
        :param title: title of the window
        :param msg: message of the window
        :return: Whether user wants to continue
        """
        res = QMessageBox.information(self, title, msg, QMessageBox.Ok, QMessageBox.Cancel)
        return res == QMessageBox.Ok

    def display_window(self, title: str, msg: str) -> None:
        """
        Display window to user
        :param title: title of the window
        :param msg: message of the window
        :return:
        """
        res = QMessageBox.information(self, title, msg, QMessageBox.Ok)

    def closeEvent(self, evt: QtGui.QCloseEvent) -> None:
        LOGGER.debug('Closing dialog')
        try:
            for panel in self.panels.values():
                panel.teardown_panel()
        except Exception as e:
            LOGGER.exception(tr(u'Unhandled exception occurred during UI closing.'), bar_msg(e))
