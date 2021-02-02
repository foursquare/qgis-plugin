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
import math
import random
from typing import List, Tuple

from PyQt5.QtGui import QColor
from qgis.core import QgsPointXY, QgsRectangle, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from qgis.gui import QgsMapCanvas

from ..definitions.settings import Settings

UNFOLDED_CRS = QgsCoordinateReferenceSystem(Settings.crs.get())


def extract_color(color: str) -> Tuple[List[int], float]:
    """ Extract rgb and aplha values from color string """
    _color = list(map(int, color.split(",")))
    rgb_value = _color[:-1]
    alpha = _color[-1] / 255.0
    return rgb_value, alpha


def rgb_to_hex(rgb_color: List[int]) -> str:
    """ Convert rgb color value to hex """
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)


def get_canvas_center(canvas: QgsMapCanvas) -> QgsPointXY:
    """ Get canvas center in supported spatial reference system """
    extent: QgsRectangle = canvas.extent()
    center = extent.center()
    # noinspection PyArgumentList
    transformer = QgsCoordinateTransform(canvas.mapSettings().destinationCrs(), UNFOLDED_CRS, QgsProject.instance())
    return transformer.transform(center)


def generate_zoom_level(scale: float, dpi: int) -> float:
    """
    Generates zoom level from scale and dpi

    Adapted from https://gis.stackexchange.com/a/268894/123927
    """
    max_scale_per_pixel = 156543.04
    inches_per_meter = 39.37
    zoomlevel = round(math.log(((dpi * inches_per_meter * max_scale_per_pixel) / scale), 2), 759672619963176)
    return zoomlevel


def random_color() -> QColor:
    """ Generate random color. Adapted from https://stackoverflow.com/a/28999469/10068922 """
    color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    return QColor(*color)
