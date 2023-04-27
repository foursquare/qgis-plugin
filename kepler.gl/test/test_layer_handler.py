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
import pytest
from qgis.core import QgsLayerTree

from .conftest import QGIS_INSTANCE
from ..core.layer_handler import LayerHandler
from ..qgis_plugin_tools.testing.utilities import is_running_inside_ci


@pytest.mark.skipif(is_running_inside_ci(), reason='In CI')
def test_add_unfolded_basemaps(new_project, initialize_settings):
    layers = LayerHandler.add_unfolded_basemaps()
    assert len(layers) == 7
    assert all([layer.isValid() for layer in layers])
    newly_created = LayerHandler.add_unfolded_basemaps()
    assert newly_created == []


@pytest.mark.skipif(is_running_inside_ci(), reason='In CI')
def test_get_current_basemap_name(new_project, initialize_settings):
    LayerHandler.add_unfolded_basemaps()
    layer_name = LayerHandler.get_current_basemap_name()
    assert layer_name == 'dark'


def test_get_current_basemap_name_without_basemaps(new_project):
    layer_name = LayerHandler.get_current_basemap_name()
    assert layer_name is None


def test_get_all_visible_vector_layers(new_project, harbour_points, harbour_points_3067, lines):
    root: QgsLayerTree = QGIS_INSTANCE.layerTreeRoot()
    group1 = root.addGroup("test1")
    group1.addLayer(harbour_points)
    group2 = group1.addGroup("test2")
    group2.addLayer(lines)
    group2.setItemVisibilityCheckedRecursive(False)
    group2.setItemVisibilityChecked(True)
    group2.addLayer(harbour_points_3067)

    layers = LayerHandler.get_vector_layers_and_visibility()
    visible_layers = [layer[0] for layer in layers if layer[1]]
    assert visible_layers == [harbour_points, harbour_points_3067]


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

    layers = LayerHandler.get_layers_and_visibility_from_node(root, root)
    visible_layers = [layer[0] for layer in layers if layer[1]]
    assert visible_layers == [harbour_points, harbour_points_3067]
