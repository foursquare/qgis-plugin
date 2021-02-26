#  Gispo Ltd., hereby disclaims all copyright interest in the program Unfolded Map Exporter
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of Unfolded Map Exporter.
#
#  Unfolded Map Exporter is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  Unfolded Map Exporter is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Unfolded Map Exporter.  If not, see <https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html>.
import logging
from typing import Optional

from PyQt5.QtCore import QVariant
from qgis.core import (QgsTask, QgsField)

from ..exceptions import ProcessInterruptedException
from ...model.map_config import Field
from ...qgis_plugin_tools.tools.custom_logging import bar_msg
from ...qgis_plugin_tools.tools.exceptions import QgsPluginException, QgsPluginNotImplementedException
from ...qgis_plugin_tools.tools.i18n import tr
from ...qgis_plugin_tools.tools.resources import plugin_name

# This logger is safe to use inside the task
LOGGER = logging.getLogger(f'{plugin_name()}_task')

# Main thread logger meant to be used in finished method
LOGGER_MAIN = logging.getLogger(plugin_name())


class BaseConfigCreatorTask(QgsTask):
    GEOM_FIELD = 'geometry'

    def __init__(self, description: str):
        super().__init__(description, QgsTask.CanCancel)
        self.exception: Optional[Exception] = None

    def _qgis_field_to_unfolded_field(self, field: QgsField) -> Field:
        """
        Analyze information about the field
        :param field: QGIS field
        :return: Unfolded field
        """
        field_name = field.name()
        field_type = field.type()
        format_ = ''
        if field_type in [QVariant.Int, QVariant.UInt, QVariant.LongLong, QVariant.ULongLong]:
            type_, analyzer_type = 'integer', 'INT'
        elif field_type == QVariant.Double:
            type_, analyzer_type = 'real', 'FLOAT'
        elif field_type == QVariant.String:
            if field_name == self.GEOM_FIELD:
                type_, analyzer_type = 'geojson', 'PAIR_GEOMETRY_FROM_STRING'
            else:
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
            raise QgsPluginNotImplementedException(tr('Field type "{}" not implemented yet', field_type))

        return Field(field_name, type_, format_, analyzer_type)

    def _check_if_canceled(self) -> None:
        """ Check if the task has been canceled """
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
                    LOGGER_MAIN.exception(str(e), extra=e.bar_msg)
                except Exception as e:
                    LOGGER_MAIN.exception(tr('Unhandled exception occurred'), extra=bar_msg(e))
