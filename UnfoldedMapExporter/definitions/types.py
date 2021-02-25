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
import enum


@enum.unique
class UnfoldedLayerType(enum.Enum):
    Point = 'point'
    Geojson = 'geojson'


"""
Following classes are applied from the QGIS plugin Spatial Data Package Export created by Gispo Ltd.
https://github.com/cividi/spatial-data-package-export/blob/master/SpatialDataPackageExport/definitions/symbols.py
Licensed by GPLv3
"""


@enum.unique
class SymbolType(enum.Enum):
    categorizedSymbol = 'categorizedSymbol'
    graduatedSymbol = 'graduatedSymbol'
    singleSymbol = 'singleSymbol'


@enum.unique
class SymbolLayerType(enum.Enum):
    SimpleMarker = 'SimpleMarker'
    SimpleLine = 'SimpleLine'
    CentroidFill = 'CentroidFill'
    SimpleFill = 'SimpleFill'