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
from qgis.core import QgsLayerTree

from .conftest import QGIS_INSTANCE
from ..core.layer_handler import LayerHandler


def test_add_unfolded_basemaps(initialize_settings):
    layers = LayerHandler.add_unfolded_basemaps()
    assert len(layers) == 7
    assert all([layer.isValid() for layer in layers])


def test_get_all_visible_vector_layers(new_project, harbour_points, harbour_points_3067, lines):
    root: QgsLayerTree = QGIS_INSTANCE.layerTreeRoot()
    group1 = root.addGroup("test1")
    group1.addLayer(harbour_points)
    group2 = group1.addGroup("test2")
    group2.addLayer(lines)
    group2.setItemVisibilityCheckedRecursive(False)
    group2.setItemVisibilityChecked(True)
    group2.addLayer(harbour_points_3067)

    layers = LayerHandler.get_all_visible_vector_layers()
    assert layers == [harbour_points, harbour_points_3067]


def test_get_layers_from_node(new_project, harbour_points, harbour_points_3067, lines, polygons):
    root: QgsLayerTree = QGIS_INSTANCE.layerTreeRoot()
    group1 = root.addGroup("test1")
    group1.addLayer(harbour_points)
    group2 = group1.addGroup("test2")
    group2.addLayer(lines)
    group2.setItemVisibilityCheckedRecursive(False)
    group2.setItemVisibilityChecked(True)
    group2.addLayer(harbour_points_3067)
    group3 = root.addGroup("test3")
    group3.addLayer(polygons)
    group3.setItemVisibilityChecked(False)

    layers = LayerHandler.get_visible_layers_from_node(root, root)
    assert layers == [harbour_points, harbour_points_3067]
