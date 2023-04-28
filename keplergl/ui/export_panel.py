#  Gispo Ltd., hereby disclaims all copyright interest in the program kepler.gl QGIS plugin by Foursquare
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of kepler.gl QGIS plugin by Foursquare.
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

import logging
import uuid
import webbrowser
from pathlib import Path
from typing import Optional, Tuple, List

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QComboBox, QTableWidget, QTableWidgetItem, QCheckBox
from qgis.core import QgsProject, QgsVectorLayer, QgsApplication
from qgis.gui import QgsMapCanvas
from qgis.utils import iface

from .base_panel import BasePanel
from .progress_dialog import ProgressDialog
from ..core.config_creator import ConfigCreator
from ..core.exceptions import ExportException
from ..core.layer_handler import LayerHandler
from ..core.utils import generate_zoom_level, random_color, get_canvas_center
from ..definitions.gui import Panels
from ..definitions.settings import Settings
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name, resources_path

LOGGER = logging.getLogger(plugin_name())


class ExportPanel(BasePanel):
    """
    """

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.Export
        self.progress_dialog: Optional[ProgressDialog] = None
        self.config_creator: Optional[ConfigCreator] = None

    # noinspection PyArgumentList
    def setup_panel(self):
        # Map configuration
        self.dlg.input_title.setText(QgsProject.instance().baseName())

        # Visualization state
        cb_layer_blending: QComboBox = self.dlg.cb_layer_blending
        cb_layer_blending.clear()
        cb_layer_blending.addItems(Settings.layer_blending.get_options())
        cb_layer_blending.setCurrentText(Settings.layer_blending.get())

        # Map style
        cb_basemap: QComboBox = self.dlg.cb_basemap
        cb_basemap.clear()
        cb_basemap.addItems(Settings.basemap.get_options())

        # Map interaction
        self.dlg.cb_tooltip.setChecked(True)
        self.dlg.cb_brush.setChecked(False)
        self.dlg.cb_geocoder.setChecked(False)
        self.dlg.cb_coordinate.setChecked(False)

        # "Export to Studio" button
        self.dlg.btn_export.clicked.connect(self.run)

        # "Export to kepler.gl" button
        # self.dlg.btn_export_kepler.clicked.connect(self.run)
        self.dlg.btn_export_kepler.setIcon(QIcon(resources_path('icons', 'keplergl.png')))

        # Studio button
        self.dlg.btn_open_studio.setIcon(QIcon(resources_path('icons', 'icon.png')))
        self.dlg.btn_open_studio.clicked.connect(lambda _: webbrowser.open(Settings.studio_url.get()))

        # Refresh
        self.dlg.btn_refresh.setIcon(QgsApplication.getThemeIcon('/mActionRefresh.svg'))
        self.dlg.btn_refresh.clicked.connect(self.__refreshed)

        # Setup dynamic contents
        self.__refreshed()

    def __refreshed(self):
        """ Set up dynamic contents """
        self.__setup_layers_to_export()
        current_basemap = LayerHandler.get_current_basemap_name()
        self.dlg.cb_basemap.setCurrentText(current_basemap if current_basemap else Settings.basemap.get())

    def __setup_layers_to_export(self):
        """ """
        # Vector layers
        table: QTableWidget = self.dlg.tw_layers
        table.setColumnCount(3)
        table.setRowCount(0)
        layers_with_visibility = LayerHandler.get_vector_layers_and_visibility()
        table.setRowCount(len(layers_with_visibility))
        for i, layer_with_visibility in enumerate(layers_with_visibility):
            layer, visibility = layer_with_visibility
            cb_export = QCheckBox()
            cb_export.setChecked(visibility)
            cb_is_visible = QCheckBox()
            cb_is_visible.setChecked(True)
            layer_name = QTableWidgetItem(layer.name())
            table.setItem(i, 0, layer_name)
            table.setCellWidget(i, 1, cb_export)
            table.setCellWidget(i, 2, cb_is_visible)

    def __get_layers_to_export(self) -> List[Tuple[QgsVectorLayer, bool]]:
        """

        :return: List of Tuples with (layer, is_hidden)
        """
        layers_with_visibility = []
        # noinspection PyArgumentList
        qgs_project = QgsProject.instance()
        table: QTableWidget = self.dlg.tw_layers
        for row in range(table.rowCount()):
            cb_export = table.cellWidget(row, 1)
            if cb_export.isChecked():
                layer_name = table.item(row, 0).text()
                is_visible = table.cellWidget(row, 2).isChecked()
                layers = qgs_project.mapLayersByName(layer_name)
                if len(layers) > 1:
                    raise ExportException(
                        tr('Multiple layers found with name {}.', layer_name),
                        bar_msg=bar_msg(tr('Please use unique layer names.')))
                if not layers:
                    raise ExportException(tr('No layers found with name {}!', layer_name),
                                          bar_msg=bar_msg(tr('Open the dialog again to refresh the layers')))
                layers_with_visibility.append((layers[0], is_visible))
        if not layers_with_visibility:
            raise ExportException(tr('No layers selected'),
                                  bar_msg=bar_msg(tr('Select at least on layer to continue export')))

        return layers_with_visibility

    def _run(self):
        """ Exports map to configuration """
        title = self.dlg.input_title.text()
        description = self.dlg.input_description.toPlainText()
        output_dir = Path(self.dlg.f_conf_output.filePath())
        basemap = self.dlg.cb_basemap.currentText()

        layers_with_visibility = self.__get_layers_to_export()

        # Map state
        canvas: QgsMapCanvas = iface.mapCanvas()
        center = get_canvas_center(canvas)
        # noinspection PyTypeChecker
        zoom = generate_zoom_level(canvas.scale(), iface.mainWindow().physicalDpiX())

        # Interaction
        tooltip_enabled = self.dlg.cb_tooltip.isChecked()
        brush_enabled = self.dlg.cb_brush.isChecked()
        geocoder_enabled = self.dlg.cb_geocoder.isChecked()
        coordinate_enabled = self.dlg.cb_coordinate.isChecked()

        # Vis state
        layer_blending = self.dlg.cb_layer_blending.currentText()

        self.progress_dialog = ProgressDialog(len(layers_with_visibility) * 2, self.dlg)
        self.progress_dialog.show()
        self.progress_dialog.aborted.connect(self.__aborted)

        self.config_creator = ConfigCreator(title, description, output_dir)
        self.config_creator.completed.connect(self.__completed)
        self.config_creator.canceled.connect(self.__aborted)
        self.config_creator.tasks_complete.connect(
            lambda: self.progress_dialog.status_label.setText(tr("Writing config file to the disk...")))
        self.config_creator.progress_bar_changed.connect(self.__progress_bar_changed)
        self.config_creator.set_map_style(basemap)
        self.config_creator.set_map_state(center, zoom)
        self.config_creator.set_animation_config(None, 1)
        self.config_creator.set_vis_state_values(layer_blending)
        self.config_creator.set_interaction_config_values(tooltip_enabled, brush_enabled, geocoder_enabled,
                                                          coordinate_enabled)

        for layer_info in layers_with_visibility:
            layer, is_visible = layer_info
            self.config_creator.add_layer(uuid.uuid4(), layer, random_color(), is_visible)

        self.config_creator.start_config_creation()

    def __progress_bar_changed(self, i: int, progress: int):
        if self.progress_dialog:
            self.progress_dialog.update_progress_bar(i, progress)

    def __aborted(self):
        if self.config_creator:
            self.config_creator.abort()
        if self.progress_dialog:
            self.progress_dialog.close()
        self.progress_dialog = None
        self.config_creator = None

    def __completed(self):
        if self.progress_dialog:
            self.progress_dialog.close()
        self.progress_dialog = None
        self.config_creator = None
