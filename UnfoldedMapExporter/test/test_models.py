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
import json

from ..model.map_config import MapConfig
from ..qgis_plugin_tools.tools.resources import plugin_test_data_path


def test_map_config_model_points():
    with open(plugin_test_data_path('config', 'harbours_config_point.json')) as f:
        map_config_dict = json.load(f)
    map_config = MapConfig.from_dict(map_config_dict)
    assert map_config.datasets[0].version == 'v1'
    assert map_config.to_dict() == map_config_dict


def test_map_config_model_polygon_points():
    with open(plugin_test_data_path('config', 'harbours_config.json')) as f:
        map_config_dict = json.load(f)
    map_config = MapConfig.from_dict(map_config_dict)
    assert map_config.to_dict() == map_config_dict


def test_map_config_model_polygon_points_2():
    with open(plugin_test_data_path('config', 'harbours_config2.json')) as f:
        map_config_dict = json.load(f)
    map_config = MapConfig.from_dict(map_config_dict)
    assert map_config.to_dict() == map_config_dict


def test_map_config_model_polygon_points_3():
    with open(plugin_test_data_path('config', 'harbours_config3.json')) as f:
        map_config_dict = json.load(f)
    map_config = MapConfig.from_dict(map_config_dict)
    assert map_config.to_dict() == map_config_dict


def test_map_config_model_polygon_lines():
    with open(plugin_test_data_path('config', 'lines_config.json')) as f:
        map_config_dict = json.load(f)
    map_config = MapConfig.from_dict(map_config_dict)
    assert map_config.to_dict() == map_config_dict


def test_map_config_model_polygon_polygons():
    with open(plugin_test_data_path('config', 'lines_config.json')) as f:
        map_config_dict = json.load(f)
    map_config = MapConfig.from_dict(map_config_dict)
    assert map_config.to_dict() == map_config_dict


def test_unfolded_config_format():
    with open(plugin_test_data_path('config', 'harbours_config_with_unfolded_datasets.json')) as f:
        map_config_dict = json.load(f)
    map_config = MapConfig.from_dict(map_config_dict)
    assert map_config.to_dict() == map_config_dict
