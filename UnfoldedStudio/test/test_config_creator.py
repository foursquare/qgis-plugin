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
import uuid

import pytest
from PyQt5.QtGui import QColor
from qgis._core import QgsPointXY

from .conftest import get_map_config, get_loaded_map_config
from ..core.config_creator import ConfigCreator


@pytest.fixture
def config_creator(tmpdir_pth) -> ConfigCreator:
    map_config = get_map_config('harbours_config_point.json')
    creator = ConfigCreator("keplergl_nabzfz", "", tmpdir_pth)
    creator.set_map_state(QgsPointXY(23.383588699716316, 60.556795942038995), 6.759672619963176)
    creator.set_map_style("dark")
    creator.set_animation_config(None, 1)
    creator.set_interaction_config_values(True, False, False, False)
    vis_state = map_config.config.config.vis_state
    creator.set_vis_state_values(vis_state.layer_blending, vis_state.filters,
                                 vis_state.split_maps, vis_state.metrics, vis_state.geo_keys, vis_state.group_bys,
                                 vis_state.joins)
    return creator


def test_map_config_creation_w_simple_points(config_creator, simple_harbour_points):
    excpected_map_config = get_map_config('harbours_config_point.json')

    config_creator.add_layer(uuid.UUID('7d193484-21a7-47f4-8cbc-497474a39b64'), simple_harbour_points,
                             QColor.fromRgb(0, 92, 255))
    config_creator._start_config_creation()

    map_config = get_loaded_map_config(config_creator.created_configuration_path)

    assert map_config.to_dict() == excpected_map_config.to_dict()
