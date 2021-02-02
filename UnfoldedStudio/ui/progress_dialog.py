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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
from pydev_ipython.qt import QtGui

from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import load_ui, plugin_name

FORM_CLASS = load_ui('progress_dialog.ui')
LOGGER = logging.getLogger(plugin_name())


class ProgressDialog(QDialog, FORM_CLASS):
    aborted = pyqtSignal()

    def __init__(self, number_of_tasks: int, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.progress_bars = [QProgressBar() for _ in range(number_of_tasks)]
        self.pb_vlayout: QVBoxLayout = self.pb_vlayout
        self.status_label: QLabel = self.status_label
        self.__initialize_ui()

    def closeEvent(self, evt: QtGui.QCloseEvent) -> None:
        LOGGER.debug('Closing progress dialog')
        # noinspection PyUnresolvedReferences
        self.aborted.emit()

    def __initialize_ui(self):
        for i, pb in enumerate(self.progress_bars):
            pb.setValue(0)
            self.pb_vlayout.addWidget(pb, i)
        self.btn_abort.clicked.connect(self.__aborted)

    def __aborted(self):
        LOGGER.warning(tr("Export aborted"), extra=bar_msg(tr("Export aborted by user")))
        self.status_label.setText(tr("Aborting..."))
        # noinspection PyUnresolvedReferences
        self.aborted.emit()
