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
from PyQt5.QtCore import QVariant
from qgis.core import (QgsVectorFileWriter, QgsVectorLayer, QgsField)


class CsvFieldValueConverter(QgsVectorFileWriter.FieldValueConverter):
    """
    Converts boolean fields to string fields containing true, false or empty string.
    """

    def __init__(self, layer: QgsVectorLayer):
        QgsVectorFileWriter.FieldValueConverter.__init__(self)
        self.layer = layer
        field_types = [field.type() for field in self.layer.fields()]
        self.bool_field_idxs = [i for i, field_type in enumerate(field_types) if field_type == QVariant.Bool]
        self.date_field_idxs = [i for i, field_type in enumerate(field_types) if field_type == QVariant.Date]
        self.datetime_field_idxs = [i for i, field_type in enumerate(field_types) if field_type == QVariant.DateTime]

    def convert(self, field_idx, value):
        if field_idx in self.bool_field_idxs:
            if value is None:
                return ""
            return "true" if value else "false"
        elif field_idx in self.date_field_idxs:
            return value.toPyDate().strftime("%Y/%m/%d")
        elif field_idx in self.datetime_field_idxs:
            return value.toPyDateTime().strftime("%Y/%m/%d %H:%M:%S")
        return value

    def fieldDefinition(self, field):
        idx = self.layer.fields().indexFromName(field.name())

        if idx in self.bool_field_idxs:
            return QgsField(field.name(), QVariant.String)
        return self.layer.fields()[idx]
