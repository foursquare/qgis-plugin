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
from PyQt5.QtCore import QVariant
from qgis.core import QgsVectorLayer

from .conftest import get_map_config
from ..core.processing.layer2dataset import LayerToDatasets


@pytest.fixture
def alg(simple_harbour_points) -> LayerToDatasets:
    return LayerToDatasets(uuid.UUID('7d193484-21a7-47f4-8cbc-497474a39b64'), simple_harbour_points, (0, 92, 255))


@pytest.mark.parametrize('layer', ['simple_harbour_points', 'simple_harbour_points_3067'])
def test__add_geom_to_fields_w_points(alg, layer, request):
    layer = request.getfixturevalue(layer)
    original_fields = layer.fields().toList()
    alg.layer = layer
    alg._add_geom_to_fields()
    fields = layer.fields().toList()

    assert len(fields) == len(original_fields) + 2
    assert fields[-1].name() == 'latitude'
    assert fields[-1].type() == QVariant.Double
    assert fields[-2].name() == 'longitude'
    assert fields[-2].type() == QVariant.Double


@pytest.mark.parametrize('layer', ['simple_harbour_points', 'simple_harbour_points_3067'])
def test__remove_geom_from_fields_w_points(alg, layer, request):
    layer = request.getfixturevalue(layer)
    original_fields = layer.fields().toList()
    alg.layer = layer
    alg._add_geom_to_fields()
    alg._remove_geom_from_fields()
    fields = layer.fields().toList()

    assert fields == original_fields


def test__extract_fields(alg, simple_harbour_points):
    map_config = get_map_config('harbours_config_point.json')

    alg._add_geom_to_fields()
    fields = alg._extract_fields()
    fields = [field.to_dict() for field in fields]
    assert fields == map_config.datasets[0].data.to_dict()['fields']


@pytest.mark.parametrize('layer', ['simple_harbour_points', 'simple_harbour_points_3067'])
def test__extract_all_data(alg, layer, request):
    layer = request.getfixturevalue(layer)
    map_config = get_map_config('harbours_config_point.json')
    alg.layer = layer
    alg._add_geom_to_fields()
    data = alg._extract_all_data()
    assert data == map_config.datasets[0].data.all_data


@pytest.mark.parametrize('layer', ['simple_harbour_points', 'simple_harbour_points_3067'])
def test__convert_to_dataset(layer, alg, request):
    layer: QgsVectorLayer = request.getfixturevalue(layer)
    layer.setName('harbours')
    map_config = get_map_config('harbours_config_point.json')
    alg.layer = layer
    status = alg.run()
    dataset = alg.result_dataset
    assert status, alg.exception
    assert dataset.to_dict() == map_config.datasets[0].to_dict()
