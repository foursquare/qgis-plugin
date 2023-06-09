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

#  Gispo Ltd., hereby disclaims all copyright interest in the program Unfolded QGIS plugin
#  Copyright (C) 2021 Gispo Ltd (https://www.gispo.fi/).
import datetime
import json
import locale
import logging
import tempfile
import time
import uuid
import zipfile
from functools import partial
from pathlib import Path
from typing import Optional, Dict, List
from zipfile import ZipFile

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QColor
from qgis.core import (QgsVectorLayer, QgsApplication, QgsPointXY)

from .exceptions import InvalidInputException
from .processing.layer2dataset import LayerToDatasets
from .processing.layer2layer_config import LayerToLayerConfig
from ..model.map_config import (MapConfig, MapState, MapStyle, Layer,
                                ConfigConfig, Config, Info)
from ..model.map_config import (VisState, InteractionConfig, AnimationConfig, Datasets,
                                FieldDisplayNames, AnyDict, VisibleLayerGroups, Globe, Tooltip, FieldsToShow, Brush,
                                Coordinate, Dataset)
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name, resources_path

ENGLISH_LOCALE = 'en_US.utf8'

LOGGER = logging.getLogger(plugin_name())


class ConfigCreator(QObject):
    """
    Create Unfolded Studio compatible configuration based on QGIS project. This class can be used in context manager in
    single threaded environments (such as tests).
    """

    UNFOLDED_CONFIG_FILE_NAME = 'config.json'

    progress_bar_changed = pyqtSignal([int, int])
    finished = pyqtSignal(dict)
    canceled = pyqtSignal()
    completed = pyqtSignal()
    tasks_complete = pyqtSignal()

    def __init__(self, title: str, description: str, output_directory: Path):
        """
        :param title: Title of the configuration
        :param description: Description of the configuration
        """

        super().__init__()
        self.title = title
        self.description = description
        self.output_directory = output_directory

        self.tasks = {}
        self.layers: Dict[uuid.UUID, QgsVectorLayer] = {}

        self.created_configuration_path: Path = Path()
        self.created_configuration_path: Path = (self.output_directory / f"{self.title.replace(' ', '_')}.zip")

        self._shown_fields: Dict[uuid.UUID, List[str]] = {}
        self._vis_state_values = {}
        self._interaction_config_values = {}
        self._map_state: Optional[MapState] = None
        self._map_style: Optional[MapStyle] = None
        self._temp_dir_obj = tempfile.TemporaryDirectory(dir=resources_path())
        self._temp_dir = Path(self._temp_dir_obj.name)

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        self.__cleanup()

    def __cleanup(self):
        """ Remove temporary directory """
        LOGGER.debug("Cleaning up")
        self._temp_dir_obj.cleanup()

    def _validate_inputs(self):
        """ Validate user given input """
        LOGGER.info('Validating inputs')
        error_message_title = ''
        bar_msg_ = None
        if not self.layers:
            error_message_title = tr('No layers selected')
            bar_msg_ = bar_msg(tr('Select at least on layer to continue export'))

        elif not (self.output_directory.name and self.output_directory.exists()):
            error_message_title = tr('Output directory "{}" does not exist', self.output_directory)
            bar_msg_ = bar_msg(tr('Set a correct output directory in the Settings'))

        elif not self.title:
            error_message_title = tr('Title not filled')
            bar_msg_ = bar_msg(tr('Please add a proper title for the map. This is used in a filename of the output'))

        if error_message_title:
            # noinspection PyUnresolvedReferences
            self.canceled.emit()
            raise InvalidInputException(error_message_title, bar_msg=bar_msg_)

    def set_animation_config(self, current_time: any = None, speed: int = AnimationConfig.speed):
        """ Set animation configuration with current time and speed """
        try:
            self._vis_state_values['animation_config'] = AnimationConfig(current_time, speed)
        except Exception as e:
            raise InvalidInputException(tr('Check the animation configuration values'), bar_msg=bar_msg(e))

    # noinspection PyDefaultArgument
    def set_vis_state_values(self, layer_blending: str, filters: List = list(),
                             split_maps: List = list(), metrics: List = list(), geo_keys: List = list(),
                             group_bys: List = list(), joins: List = list()):
        """ Set visualization state values """
        vals = dict(**locals())
        vals.pop('self')
        self._vis_state_values = {**self._vis_state_values, **vals}

    def set_interaction_config_values(self, tooltip_enabled: bool, brush_enabled: bool,
                                      geocoder_enabled: bool,
                                      coordinate_enabled: bool, brush_size: float = 0.5):
        """ Set interaction configuration values """
        self._interaction_config_values = {"brush": Brush(brush_size, brush_enabled),
                                           "geocoder": Coordinate(geocoder_enabled),
                                           "coordinate": Coordinate(coordinate_enabled),
                                           "tooltip_enabled": tooltip_enabled}

    def set_map_state(self, center: QgsPointXY, zoom: float, bearing: int = 0, drag_rotate: bool = False,
                      pitch: int = 0, is_split: bool = False, map_view_mode: str = MapState.map_view_mode):
        """ Set map state values """

        try:
            self._map_state = MapState(bearing, drag_rotate, center.y(), center.x(), pitch, zoom, is_split,
                                       map_view_mode, Globe.create_default())
        except Exception as e:
            raise InvalidInputException(tr('Check the map state configuration values'), bar_msg=bar_msg(e))

    def set_map_style(self, style_type: str):
        """ Set map style values """
        try:
            self._map_style = MapStyle(style_type, MapStyle.top_layer_groups, VisibleLayerGroups.create_default(),
                                       MapStyle.three_d_building_color, MapStyle.map_styles)
        except Exception as e:
            raise InvalidInputException(tr('Check the map style configuration values'), bar_msg=bar_msg(e))

    def add_layer(self, layer_uuid: uuid.UUID, layer: QgsVectorLayer, layer_color: QColor, is_visible: bool):
        """ Add layer to the config creation """
        color = (layer_color.red(), layer_color.green(), layer_color.blue())
        output_dir = self._temp_dir
        self.layers[layer_uuid] = layer
        self.tasks[uuid.uuid4()] = {'task': LayerToDatasets(layer_uuid, layer, color, output_dir), 'finished': False}
        self.tasks[uuid.uuid4()] = {'task': LayerToLayerConfig(layer_uuid, layer, is_visible), 'finished': False}

        # Save information about shown fields based
        shown_fields = []
        for column in layer.attributeTableConfig().columns():
            name = column.name
            if name:
                if not column.hidden:
                    shown_fields.append(name)
        self._shown_fields[str(layer_uuid)] = shown_fields

    def start_config_creation(self) -> None:
        """ Start config creation using background processing tasks """

        self._validate_inputs()
        LOGGER.info('Started config creation')
        LOGGER.debug(f"Tasks are: {self.tasks}")

        for task_id, task_dict in self.tasks.items():
            # noinspection PyArgumentList
            QgsApplication.taskManager().addTask(task_dict['task'])
            task_dict['task'].progressChanged.connect(partial(self._progress_changed, task_id))
            task_dict['task'].taskCompleted.connect(partial(self._task_completed, task_id))
            task_dict['task'].taskTerminated.connect(partial(self._task_terminated, task_id))

    def abort(self) -> None:
        """ Aborts config creation manually """
        for task_id, task_dict in self.tasks.items():
            if not task_dict['finished'] and not task_dict['task'].isCanceled():
                LOGGER.warning(f"Cancelling task {task_id}")
                task_dict['task'].cancel()
        self.__cleanup()

    def _progress_changed(self, task_id: uuid.UUID):
        """ Increments progress """
        # noinspection PyUnresolvedReferences
        self.progress_bar_changed.emit(list(self.tasks.keys()).index(task_id), self.tasks[task_id]['task'].progress())

    def _task_completed(self, task_id: uuid.UUID) -> None:
        """ One of the background processing tasks if finished succesfully """
        LOGGER.debug(f"Task {task_id} completed!")
        self.tasks[task_id]['finished'] = True
        self.tasks[task_id]['successful'] = True
        at_least_one_running = False
        for id_, task_dict in self.tasks.items():
            if id_ != task_id and not task_dict['finished']:
                at_least_one_running = True

        if not at_least_one_running:
            # noinspection PyUnresolvedReferences
            self.tasks_complete.emit()
            self._create_map_config()

    def _task_terminated(self, task_id: uuid.UUID) -> None:
        """ One of the background processing tasks failed """

        LOGGER.warning(tr("Task {} terminated", task_id))
        self.tasks[task_id]['finished'] = True
        at_least_one_running = False
        for id_, task_dict in self.tasks.items():
            if id_ != task_id and not task_dict['finished'] and not task_dict['task'].isCanceled():
                at_least_one_running = True
                task_dict['task'].cancel()

        if not at_least_one_running:
            # noinspection PyUnresolvedReferences
            self.canceled.emit()

    def _create_map_config(self):
        """ Generates map configuration file """

        LOGGER.info(tr('Creating map config'))

        try:
            # noinspection PyTypeChecker
            datasets: List[Dataset] = [None] * len(self.layers)
            # noinspection PyTypeChecker
            layers: List[Layer] = [None] * len(self.layers)

            layer_uuids = list(self.layers.keys())

            for id_, task_dict in self.tasks.items():
                task = task_dict['task']
                if isinstance(task, LayerToDatasets):
                    datasets[layer_uuids.index(task.layer_uuid)] = task.result_dataset
                elif isinstance(task, LayerToLayerConfig):
                    layers[layer_uuids.index(task.layer_uuid)] = task.result_layer_conf

            tooltip_data = {}
            for layer_uuid, fields in self._shown_fields.items():
                field_list = []
                for field_name in fields:
                    # try to find a field in a dataset so we can get its format
                    datasetIdx = layer_uuids.index(task.layer_uuid)
                    dataset = datasets[datasetIdx]
                    for dataset_field in dataset.data.fields:
                        if dataset_field.name == field_name:
                            field_list.append({"name": field_name, "format": dataset_field.format})

                tooltip_data[layer_uuid] = field_list

            tooltip = Tooltip(
                FieldsToShow(AnyDict(tooltip_data)),
                Tooltip.compare_mode,
                Tooltip.compare_type,
                self._interaction_config_values["tooltip_enabled"]
            )

            interaction_config = InteractionConfig(tooltip, self._interaction_config_values["brush"],
                                                   self._interaction_config_values["geocoder"],
                                                   self._interaction_config_values["coordinate"])

            vis_state = VisState(layers=layers, datasets=self._extract_datasets(),
                                 interaction_config=interaction_config, **self._vis_state_values)

            config = Config(Config.version, ConfigConfig(vis_state, self._map_state, self._map_style))
            info = self._create_config_info()

            map_config = MapConfig(datasets, config, info)

            self._write_output(map_config)

            LOGGER.info(tr('Configuration created successfully'),
                        extra=bar_msg(tr('The file can be found in {}', str(self.created_configuration_path)),
                                      success=True, duration=30))

            # noinspection PyUnresolvedReferences
            self.completed.emit()

        except Exception as e:
            LOGGER.exception('Config creation failed. Check the log for more details', extra=bar_msg(e))
            # noinspection PyUnresolvedReferences
            self.canceled.emit()
        finally:
            self.__cleanup()

    def _write_output(self, map_config):
        """ Write the configuration as a ZIP file"""

        config_file = self._temp_dir / self.UNFOLDED_CONFIG_FILE_NAME
        with open(config_file, 'w') as f:
            json.dump(map_config.to_dict(), f)

        # Create a zip for the configuration and datasets
        with ZipFile(self.created_configuration_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(config_file, config_file.name)
            # Add multiple files to the zip
            for dataset in map_config.datasets:
                zip_file.write(self._temp_dir / dataset.source, dataset.source)

    def _create_config_info(self):
        """ Create info for the configuration """
        try:
            locale.setlocale(locale.LC_ALL, ENGLISH_LOCALE)
        except locale.Error:
            LOGGER.warning(tr("Unsupported locale {}. Using system default.", ENGLISH_LOCALE))
        timestamp = datetime.datetime.now().strftime('%a %b %d %Y %H:%M:%S ')
        time_zone = time.strftime('%Z%z')
        created_at = timestamp + time_zone
        source = Info.source

        return Info(Info.app, created_at, self.title, self.description, source)

    def _start_config_creation(self) -> None:
        """ This method runs the config creation in one thread. Mainly meant for testing """

        LOGGER.info(tr('Started config creation'))

        for id_, task_dict in self.tasks.items():
            task = task_dict['task']
            success = task.run()
            if not success:
                raise task.exception
        self._create_map_config()

    def _extract_datasets(self) -> Datasets:
        """ Exrtact datasets from QGIS layers """
        # TODO: configure fields to display
        return Datasets(FieldDisplayNames(AnyDict({str(uuid_): {} for uuid_ in self.layers})))
