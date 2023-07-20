#  Gispo Ltd., hereby disclaims all copyright interest in the program kepler QGIS plugin by Foursquare
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
#
#
#  This file is part of kepler QGIS plugin by Foursquare.
#
#  kepler QGIS plugin by Foursquare is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  kepler QGIS plugin by Foursquare is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with kepler QGIS plugin by Foursquare.  If not, see <https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html>.
import datetime
import time
import uuid
from pathlib import Path
from unittest.mock import MagicMock
from zipfile import ZipFile

import pytest
from PyQt5.QtGui import QColor
from qgis._core import QgsPointXY

from .conftest import get_map_config, get_loaded_map_config
from ..core.config_creator import ConfigCreator
from ..core.exceptions import InvalidInputException

FAKE_NOW = datetime.datetime(2021, 1, 25, 11, 37, 43)


@pytest.fixture()
def mock_datetime_now(monkeypatch):
    """ copied from https://stackoverflow.com/a/60629703/10068922 """
    datetime_mock = MagicMock(wraps=datetime.datetime)
    datetime_mock.now.return_value = FAKE_NOW
    monkeypatch.setattr(datetime, "datetime", datetime_mock)


@pytest.fixture
def config_creator(tmpdir_pth, mock_datetime_now) -> ConfigCreator:
    map_config = get_map_config('harbours_config_point.json')
    creator = ConfigCreator("unfolded_nabzfz", "", tmpdir_pth)
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
    with config_creator as cf:
        time_zone = time.strftime('%Z%z')
        excpected_map_config = get_map_config('harbours_config_point.json')
        excpected_map_config.info.created_at = excpected_map_config.info.created_at.replace("EET+0200", time_zone)
        cf.add_layer(uuid.UUID('7d193484-21a7-47f4-8cbc-497474a39b64'), simple_harbour_points,
                     QColor.fromRgb(0, 92, 255), True)
        cf._start_config_creation()

        map_config = get_loaded_map_config(cf.created_configuration_path)

        assert map_config.config.to_dict() == excpected_map_config.config.to_dict()
    assert not cf._temp_dir.exists()


def test_map_config_creation_with_foursquare_format(config_creator, simple_harbour_points):
    with config_creator as cf:
        time_zone = time.strftime('%Z%z')
        excpected_map_config = get_map_config('harbours_config_with_foursquare_datasets.json')
        excpected_map_config.info.created_at = excpected_map_config.info.created_at.replace("EET+0200", time_zone)
        cf.add_layer(uuid.UUID('7d193484-21a7-47f4-8cbc-497474a39b64'), simple_harbour_points,
                     QColor.fromRgb(0, 92, 255), True)
        cf._start_config_creation()

        assert cf.created_configuration_path.exists()
        assert cf.created_configuration_path.name == 'unfolded_nabzfz.zip'
        with ZipFile(cf.created_configuration_path, 'r') as zip_file:
            assert [n for n in zip_file.namelist()] == ['config.json', 'harbours.csv']
        map_config = get_loaded_map_config(cf.created_configuration_path)
        assert map_config.to_dict() == excpected_map_config.to_dict()

    assert not cf._temp_dir.exists()


def test__create_config_info(config_creator):
    with config_creator as cf:
        time_zone = time.strftime('%Z%z')
        info = config_creator._create_config_info()
    assert not cf._temp_dir.exists()
    assert info.created_at == "Mon Jan 25 2021 11:37:43 " + time_zone
    assert info.source == "QGIS"


def test___validate_inputs():
    with ConfigCreator("", "", Path('nonexisting')) as cf:
        with pytest.raises(InvalidInputException) as e:
            cf._validate_inputs()
    assert str(e.value) == 'No layers selected'


def test___validate_inputs2(simple_harbour_points):
    with ConfigCreator("", "", Path('nonexisting')) as cf:
        cf.add_layer(uuid.UUID('7d193484-21a7-47f4-8cbc-497474a39b64'), simple_harbour_points,
                     QColor.fromRgb(0, 92, 255), True)
        with pytest.raises(InvalidInputException) as e:
            cf._validate_inputs()
    assert str(e.value) == 'Output directory "nonexisting" does not exist'


def test___validate_inputs3(simple_harbour_points, tmpdir_pth):
    with ConfigCreator("", "", tmpdir_pth) as cf:
        cf.add_layer(uuid.UUID('7d193484-21a7-47f4-8cbc-497474a39b64'), simple_harbour_points,
                     QColor.fromRgb(0, 92, 255), True)
        with pytest.raises(InvalidInputException) as e:
            cf._validate_inputs()
    assert str(e.value) == 'Title not filled'
