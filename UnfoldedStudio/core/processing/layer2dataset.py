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
import tempfile
import uuid
from pathlib import Path
from typing import Optional, List, Tuple

from PyQt5.QtCore import QVariant
from qgis.core import (QgsTask, QgsVectorLayer, QgsField, QgsVectorFileWriter, QgsCoordinateReferenceSystem,
                       QgsProject)

from ..exceptions import ProcessInterruptedException
from ...definitions.settings import Settings
from ...model.map_config import Dataset, Data, Field
from ...qgis_plugin_tools.tools.custom_logging import bar_msg
from ...qgis_plugin_tools.tools.exceptions import QgsPluginException, QgsPluginNotImplementedException
from ...qgis_plugin_tools.tools.i18n import tr
from ...qgis_plugin_tools.tools.layers import LayerType
from ...qgis_plugin_tools.tools.resources import plugin_name, resources_path

# This logger is safe to use inside the task
LOGGER = logging.getLogger(f'{plugin_name()}_task')

# Main thread logger meant to be used in finished method
LOGGER_MAIN = logging.getLogger(plugin_name())


class LayerToDatasets(QgsTask):

    def __init__(self, layer_uuid: uuid.UUID, layer: QgsVectorLayer, color: Tuple[int, int, int],
                 output_directory: Optional[Path] = None):
        super().__init__('LayerToDatasets', QgsTask.CanCancel)
        self.layer_uuid = layer_uuid
        self.layer = layer
        self.color = color
        self.output_directory = output_directory
        self.result_dataset: Optional[Dataset] = None
        self.exception: Optional[Exception] = None

    def run(self) -> bool:
        try:
            self.__check_if_canceled()
            self.result_dataset = self._convert_to_dataset()
            self.setProgress(100)
            return True
        except Exception as e:
            self.exception = e
            return False

    def _convert_to_dataset(self) -> Dataset:
        self._add_geom_to_fields()
        try:
            self.setProgress(20)
            self.__check_if_canceled()

            all_data = self._extract_all_data()
            self.setProgress(40)
            self.__check_if_canceled()

            fields = self._extract_fields()
            self.setProgress(60)
            self.__check_if_canceled()

            data = Data(self.layer_uuid, self.layer.name(), list(self.color), all_data, fields)
            self.setProgress(80)
            return Dataset(data)
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
            LOGGER.info('Point layer')
            if not do_transform:
                self.layer.addExpressionField('$x', QgsField('longitude', QVariant.Double))
                self.layer.addExpressionField('$y', QgsField('latitude', QVariant.Double))
            else:
                self.layer.addExpressionField(f"x(transform($geometry, '{crs}', '{dest_crs}'))",
                                              QgsField('longitude', QVariant.Double))
                self.layer.addExpressionField(f"y(transform($geometry, '{crs}', '{dest_crs}'))",
                                              QgsField('latitude', QVariant.Double))
            # TODO: z coord
        else:
            raise QgsPluginNotImplementedException()

    def _remove_geom_from_fields(self):
        """ Removes virtual geometry field(s) from the layer """

        LOGGER.info(tr('Removing layer geometry fields'))

        layer_type = LayerType.from_layer(self.layer)
        if layer_type == LayerType.Point:
            field_count = len(self.layer.fields().toList())
            self.layer.removeExpressionField(field_count - 1)
            self.layer.removeExpressionField(field_count - 2)

    def _extract_fields(self) -> List[Field]:
        """ Extract field information from layer """
        fields: List[Field] = []
        field: QgsField
        LOGGER.info(tr('Extracting fields'))

        for field in self.layer.fields():
            field_type = field.type()
            format_ = ''
            if field_type in [QVariant.Int, QVariant.UInt, QVariant.LongLong, QVariant.ULongLong]:
                type_, analyzer_type = 'integer', 'INT'
            elif field_type == QVariant.Double:
                type_, analyzer_type = 'real', 'FLOAT'
            elif field_type == QVariant.String:
                type_, analyzer_type = 'string', 'STRING'
            elif field_type == QVariant.Bool:
                type_, analyzer_type = ('boolean', 'BOOLEAN')
            # TODO: check date time formats
            elif field_type == QVariant.Date:
                type_, analyzer_type = ('date', 'DATE')
                format_ = 'YYYY/M/D'
            elif field_type == QVariant.DateTime:
                type_, analyzer_type = ('timestamp', 'DATETIME')
                format_ = 'YYYY/M/D H:m:s'
            elif field_type == QVariant.Time:
                type_, analyzer_type = ('timestamp', 'INT')
                format_ = 'H:m:s'
            # elif field_type == QVariant.ByteArray:
            #     type, analyzer_type = ('integer', 'INT')
            else:
                raise QgsPluginNotImplementedException('Field type not implemented yet')

            fields.append(Field(field.name(), type_, format_, analyzer_type))

        return fields

    def _extract_all_data(self) -> List:
        """ Extract data either as csv, json or as file """

        LOGGER.info(tr('Extracting layer data'))

        if self.output_directory:
            raise QgsPluginNotImplementedException()
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
                    # There is a possible bug in QGIS csv export that exports booleans as '1', '0' or ''
                    conversion_functions[i] = lambda x: bool(int(x)) if x else None
                else:
                    conversion_functions[i] = lambda x: x

            with tempfile.TemporaryDirectory(dir=resources_path()) as tmpdirname:
                output_file = self._save_layer_to_file(self.layer, Path(tmpdirname))
                with open(output_file) as f:
                    for line_nro, line in enumerate(f):
                        if line_nro > 0:
                            data = []
                            for i, value in enumerate(line.split(',')):
                                data.append(conversion_functions[i](value))
                            all_data.append(data)
            return all_data

    # noinspection PyArgumentList
    @staticmethod
    def _save_layer_to_file(layer: QgsVectorLayer, output_path: Path) -> Path:
        """ Save layer to file"""
        output_file = output_path / f'{layer.name()}.csv'

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "csv"
        options.fileEncoding = "utf-8"
        options.layerOptions = ["SEPARATOR=COMMA", "STRING_QUOTING=IF_NEEDED"]

        # noinspection PyCallByClass
        writer_, msg = QgsVectorFileWriter.writeAsVectorFormatV2(layer, str(output_file),
                                                                 QgsProject.instance().transformContext(), options)

        if msg:
            raise ProcessInterruptedException(tr('Exception occurred during data extraction: {}', msg))
        return output_file

    def __check_if_canceled(self) -> None:
        if self.isCanceled():
            raise ProcessInterruptedException()

    def finished(self, result: bool) -> None:
        """
        This function is automatically called when the task has completed (successfully or not).

        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.

        :param result: the return value from self.run
        """
        if result:
            pass
        else:
            if self.exception is None:
                LOGGER_MAIN.warning(tr('Task was not successful'),
                                    extra=bar_msg(tr('Task was probably cancelled by user')))
            else:
                try:
                    raise self.exception
                except QgsPluginException as e:
                    LOGGER.exception(str(e), extra=e.bar_msg)
                except Exception as e:
                    LOGGER.exception(tr('Unhandled exception occurred'), extra=bar_msg(e))
