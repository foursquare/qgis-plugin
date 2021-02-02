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
from qgis._core import QgsVectorLayer

from .conftest import get_map_config
from ..core.exceptions import InvalidInputException
from ..core.processing.layer2layer_config import LayerToLayerConfig


@pytest.mark.parametrize('layer,config',
                         [('simple_harbour_points', 'harbours_config_point.json'),
                          ('lines', 'lines_config.json'),
                          ('polygons', 'polygons_config.json'),
                          ('quantile_points', 'harbours_graduated_quantile.json'),
                          ('quantize_points', 'harbours_graduated_quantize.json')
                          ])
def test__extract_layer(layer, config, request):
    layer: QgsVectorLayer = request.getfixturevalue(layer)
    alg = LayerToLayerConfig(uuid.UUID('7d193484-21a7-47f4-8cbc-497474a39b64'), layer)

    map_config = get_map_config(config)
    layer_conf = alg._extract_layer()
    assert layer_conf.to_dict() == map_config.config.config.vis_state.layers[0].to_dict()


@pytest.mark.parametrize('layer', ['simple_harbour_points_invalid_size_units', 'lines_invalid_size_units',
                                   'polygons_invalid_size_units'])
def test__extract_layer_with_invalid_size_units(layer, request):
    layer: QgsVectorLayer = request.getfixturevalue(layer)
    alg = LayerToLayerConfig(uuid.UUID('7d193484-21a7-47f4-8cbc-497474a39b64'), layer)

    with pytest.raises(InvalidInputException) as execinfo:
        alg._extract_layer()
    assert "Size unit" in str(execinfo)
