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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QProgressBar, QLabel

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
        self.progress_per_tasks = [0] * number_of_tasks
        self.progress_bar: QProgressBar = self.progress_bar
        self.status_label: QLabel = self.status_label

    def closeEvent(self, evt) -> None:
        LOGGER.debug('Closing progress dialog')
        # noinspection PyUnresolvedReferences
        self.aborted.emit()

    def update_progress_bar(self, task_number: int, progress: int):
        """ Update progress bar with progress of a task """
        self.progress_per_tasks[task_number] = progress
        self._update_progress_bar()

    def _update_progress_bar(self):
        self.progress_bar.setValue(min(97, int(sum(self.progress_per_tasks) / len(self.progress_per_tasks))))

    def __aborted(self):
        LOGGER.warning(tr("Export aborted"), extra=bar_msg(tr("Export aborted by user")))
        self.status_label.setText(tr("Aborting..."))
        # noinspection PyUnresolvedReferences
        self.aborted.emit()
