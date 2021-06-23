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
import csv
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Optional, List, Tuple

from PyQt5.QtCore import QVariant
from qgis.core import (QgsVectorLayer, QgsField, QgsVectorFileWriter, QgsCoordinateReferenceSystem,
                       QgsProject)

from .base_config_creator_task import BaseConfigCreatorTask
from .csv_field_value_converter import CsvFieldValueConverter
from ..exceptions import ProcessInterruptedException
from ..utils import set_csv_field_size_limit
from ...definitions.settings import Settings
from ...model.map_config import OldDataset, Data, Field, UnfoldedDataset
from ...qgis_plugin_tools.tools.custom_logging import bar_msg
from ...qgis_plugin_tools.tools.exceptions import QgsPluginNotImplementedException
from ...qgis_plugin_tools.tools.i18n import tr
from ...qgis_plugin_tools.tools.layers import LayerType
from ...qgis_plugin_tools.tools.resources import plugin_name, resources_path

# This logger is safe to use inside the task
LOGGER = logging.getLogger(f'{plugin_name()}_task')

# Main thread logger meant to be used in finished method
LOGGER_MAIN = logging.getLogger(plugin_name())


class LayerToDatasets(BaseConfigCreatorTask):

    def __init__(self, layer_uuid: uuid.UUID, layer: QgsVectorLayer, color: Tuple[int, int, int],
                 output_directory: Optional[Path] = None):
        super().__init__('LayerToDatasets')
        self.layer_uuid = layer_uuid
        self.layer = layer
        self.color = color
        self.output_directory = output_directory
        self.result_dataset: Optional[OldDataset] = None

    def run(self) -> bool:
        try:
            self._check_if_canceled()
            self.result_dataset = self._convert_to_dataset()
            self.setProgress(100)
            return True
        except Exception as e:
            self.exception = e
            return False

    def _convert_to_dataset(self) -> OldDataset:
        self._add_geom_to_fields()
        try:
            self.setProgress(20)
            self._check_if_canceled()

            fields = self._extract_fields()

            self.setProgress(40)
            self._check_if_canceled()

            source, all_data = self._extract_all_data()
            self.setProgress(60)
            self._check_if_canceled()

            if self.output_directory:
                dataset = UnfoldedDataset(self.layer_uuid, self.layer.name(), list(self.color), source, fields)
            else:
                data = Data(self.layer_uuid, self.layer.name(), list(self.color), all_data, fields)
                dataset = OldDataset(data)

            self.setProgress(80)
            return dataset
        finally:
            self._remove_geom_from_fields()

    def _add_geom_to_fields(self) -> None:
        """ Adds geometry to the layer as virtual field(s) """

        LOGGER.info(tr('Adding layer geometry to fields'))

        crs: QgsCoordinateReferenceSystem = self.layer.crs().authid()
        dest_crs = Settings.crs.get()
        do_transform = crs != dest_crs
        layer_type = LayerType.from_layer(self.layer)
        if layer_type == LayerType.Point:
            LOGGER.debug('Point layer')
            if not do_transform:
                self.layer.addExpressionField('$x', QgsField('longitude', QVariant.Double))
                self.layer.addExpressionField('$y', QgsField('latitude', QVariant.Double))
            else:
                self.layer.addExpressionField(f"x(transform($geometry, '{crs}', '{dest_crs}'))",
                                              QgsField('longitude', QVariant.Double))
                self.layer.addExpressionField(f"y(transform($geometry, '{crs}', '{dest_crs}'))",
                                              QgsField('latitude', QVariant.Double))
            # TODO: z coord
        elif layer_type in (LayerType.Polygon, LayerType.Line):
            LOGGER.debug('Polygon or line layer')
            expression = ('geom_to_wkt($geometry)' if not do_transform
                          else f"geom_to_wkt(transform($geometry, '{crs}', '{dest_crs}'))")

            self.layer.addExpressionField(expression, QgsField(self.GEOM_FIELD, QVariant.String))
        else:
            raise QgsPluginNotImplementedException(
                bar_msg=bar_msg(tr('Unsupported layer wkb type: {}', self.layer.wkbType())))

    def _remove_geom_from_fields(self):
        """ Removes virtual geometry field(s) from the layer """

        LOGGER.info(tr('Removing layer geometry fields'))

        layer_type = LayerType.from_layer(self.layer)
        field_count = len(self.layer.fields().toList())
        if layer_type == LayerType.Point:
            self.layer.removeExpressionField(field_count - 1)
            self.layer.removeExpressionField(field_count - 2)
        elif layer_type in (LayerType.Polygon, LayerType.Line):
            self.layer.removeExpressionField(field_count - 1)
        else:
            raise QgsPluginNotImplementedException(
                bar_msg=bar_msg(tr('Unsupported layer wkb type: {}', self.layer.wkbType())))

    def _extract_fields(self) -> List[Field]:
        """ Extract field information from layer """
        fields: List[Field] = []
        field: QgsField
        LOGGER.info(tr('Extracting fields'))

        for field in self.layer.fields():
            fields.append(self._qgis_field_to_unfolded_field(field))
        return fields

    def _extract_all_data(self) -> Tuple[Optional[str], Optional[List]]:
        """ Extract data either as csv file or list representing csv
        :returns csv file source if exists, data list if output directory for the file is not set
        """

        LOGGER.info(tr('Extracting layer data'))

        all_data, source = [None] * 2
        if self.output_directory:
            output_file = self._save_layer_to_file(self.layer, self.output_directory)
            source = output_file.name
        else:
            all_data = []
            field_types = [field.type() for field in self.layer.fields()]
            conversion_functions = {}
            for i, field_type in enumerate(field_types):
                if field_types[i] in [QVariant.Int, QVariant.UInt, QVariant.LongLong,
                                      QVariant.ULongLong]:
                    conversion_functions[i] = lambda x: int(x) if x else None
                elif field_types[i] == QVariant.Double:
                    conversion_functions[i] = lambda x: float(x) if x else None
                elif field_types[i] == QVariant.Bool:
                    conversion_functions[i] = lambda x: None if x == "" else x == "true"
                else:
                    conversion_functions[i] = lambda x: x.rstrip().strip('"')

            with tempfile.TemporaryDirectory(dir=resources_path()) as tmpdirname:
                output_file = self._save_layer_to_file(self.layer, Path(tmpdirname))
                with open(output_file, newline='', encoding="utf-8") as f:
                    set_csv_field_size_limit()
                    data_reader = csv.reader(f, delimiter=',')
                    # Skipping header
                    next(data_reader)
                    for row in data_reader:
                        data = []
                        for i, value in enumerate(row):
                            data.append(conversion_functions[i](value))
                        all_data.append(data)

        return source, all_data

    # noinspection PyArgumentList
    @staticmethod
    def _save_layer_to_file(layer: QgsVectorLayer, output_path: Path) -> Path:
        """ Save layer to file"""
        output_file = output_path / f'{layer.name().replace(" ", "")}.csv'
        LOGGER.debug(f'Saving layer to a file {output_file.name}')

        converter = CsvFieldValueConverter(layer)

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "csv"
        options.fileEncoding = "utf-8"
        options.layerOptions = ["SEPARATOR=COMMA"]
        options.fieldValueConverter = converter

        if hasattr(QgsVectorFileWriter, "writeAsVectorFormatV3"):
            # noinspection PyCallByClass
            writer_, msg, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(layer, str(output_file),
                                                                           QgsProject.instance().transformContext(),
                                                                           options)
        else:
            writer_, msg = QgsVectorFileWriter.writeAsVectorFormatV2(layer, str(output_file),
                                                                     QgsProject.instance().transformContext(), options)
        if msg:
            raise ProcessInterruptedException(tr('Process ended'),
                                              bar_msg=bar_msg(tr('Exception occurred during data extraction: {}', msg)))
        return output_file
