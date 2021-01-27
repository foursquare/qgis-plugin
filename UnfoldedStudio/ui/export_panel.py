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
import uuid
from pathlib import Path

from PyQt5.QtWidgets import QComboBox
from qgis._core import QgsProject
from qgis.gui import QgsMapCanvas

from .base_panel import BasePanel
from ..core.config_creator import ConfigCreator
from ..core.layer_handler import LayerHandler
from ..core.utils import generate_zoom_level, random_color, get_canvas_center
from ..definitions.gui import Panels
from ..definitions.settings import Settings
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class ExportPanel(BasePanel):
    """
    """

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.Export

    def setup_panel(self):
        # Map configuration
        # noinspection PyArgumentList
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
        cb_basemap.setCurrentText(Settings.basemap.get())

        # Map interaction
        self.dlg.cb_tooltip.setChecked(True)
        self.dlg.cb_brush.setChecked(False)
        self.dlg.cb_geocoder.setChecked(False)
        self.dlg.cb_coordinate.setChecked(False)

        # Export button
        self.dlg.btn_export.clicked.connect(self.run)

    def _run(self):
        """ Exports map to configuration """
        title = self.dlg.input_title.text()
        description = self.dlg.input_description.toPlainText()
        output_dir = Path(self.dlg.f_conf_output.filePath())
        basemap = self.dlg.cb_basemap.currentText()

        # Map state
        canvas: QgsMapCanvas = self.dlg.iface.mapCanvas()
        center = get_canvas_center(canvas)
        # noinspection PyTypeChecker
        zoom = generate_zoom_level(canvas.scale(), self.dlg.iface.mainWindow().physicalDpiX())

        # Interaction
        tooltip_enabled = self.dlg.cb_tooltip.isChecked()
        brush_enabled = self.dlg.cb_brush.isChecked()
        geocoder_enabled = self.dlg.cb_geocoder.isChecked()
        coordinate_enabled = self.dlg.cb_coordinate.isChecked()

        # Vis state
        layer_blending = self.dlg.cb_layer_blending.currentText()

        # Vector layers
        layers = LayerHandler.get_all_visible_vector_layers()

        config_creator = ConfigCreator(title, description, output_dir)
        config_creator.set_map_style(basemap)
        config_creator.set_map_state(center, zoom)
        config_creator.set_animation_config(None, 1)
        config_creator.set_vis_state_values(layer_blending)
        config_creator.set_interaction_config_values(tooltip_enabled, brush_enabled, geocoder_enabled,
                                                     coordinate_enabled)
        for layer in layers:
            config_creator.add_layer(uuid.uuid4(), layer, random_color())

        config_creator._start_config_creation()
