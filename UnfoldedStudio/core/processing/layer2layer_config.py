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
import logging
import uuid
from typing import Optional, List, Tuple

from qgis.core import (QgsTask, QgsVectorLayer, QgsSymbol, QgsFeatureRenderer, QgsSymbolLayer, QgsMarkerSymbol)

from ..exceptions import ProcessInterruptedException, InvalidInputException
from ...definitions.settings import Settings
from ...definitions.types import UnfoldedLayerType, SymbolType, SymbolLayerType
from ...model.map_config import Layer, LayerConfig, VisualChannels, VisConfig, Columns, TextLabel, ColorRange
from ...qgis_plugin_tools.tools.custom_logging import bar_msg
from ...qgis_plugin_tools.tools.exceptions import QgsPluginException, QgsPluginNotImplementedException
from ...qgis_plugin_tools.tools.i18n import tr
from ...qgis_plugin_tools.tools.layers import LayerType
from ...qgis_plugin_tools.tools.resources import plugin_name

# This logger is safe to use inside the task
LOGGER = logging.getLogger(f'{plugin_name()}_task')

# Main thread logger meant to be used in finished method
LOGGER_MAIN = logging.getLogger(plugin_name())


class LayerToLayerConfig(QgsTask):
    """
    Creates VisState.Layer object

    Some of the code is inspired by QGIS plugin Spatial Data Package Export created by Gispo Ltd.
    https://github.com/cividi/spatial-data-package-export/blob/master/SpatialDataPackageExport/core/styles2attributes.py
    Licensed by GPLv3
    """

    def __init__(self, layer_uuid: uuid.UUID, layer: QgsVectorLayer):
        super().__init__('LayerToLayerConfig', QgsTask.CanCancel)
        self.layer_uuid = layer_uuid
        self.layer = layer
        self.supported_size_unit = Settings.SUPPORTED_SIZE_UNIT.get()
        self.result_layer_conf: Optional[Layer] = None
        self.exception: Optional[Exception] = None

    def run(self) -> bool:
        try:
            self.__check_if_canceled()
            self.result_layer_conf = self._extract_layer()
            self.setProgress(100)
            return True
        except Exception as e:
            self.exception = e
            return False

    def _extract_layer(self) -> Layer:
        """ Extract VisState.layer configuration based on layer renderer and type """
        LOGGER.info(tr('Extracting layer configuration for {}', self.layer.name()))

        renderer: QgsFeatureRenderer = self.layer.renderer()
        symbol_type = SymbolType[renderer.type()]
        LOGGER.info(tr('Symbol type: {}', symbol_type))

        if symbol_type == SymbolType.singleSymbol:
            self.setProgress(50)
            # noinspection PyUnresolvedReferences
            color, vis_config = self._extract_layer_style(renderer.symbol())
            visual_channels = VisualChannels.create_single_color_channels()
        else:
            raise QgsPluginNotImplementedException()

        id_ = str(self.layer_uuid).replace("-", "")[:7]
        layer_type = LayerType.from_layer(self.layer)
        if layer_type == LayerType.Point:
            layer_type_ = UnfoldedLayerType.Point
            columns = Columns.for_point_2d()
        else:
            raise QgsPluginNotImplementedException()

        is_visible = True
        hidden = False
        text_label = [TextLabel.create_default()]

        layer_config = LayerConfig(self.layer_uuid, self.layer.name(), color, columns, is_visible, vis_config, hidden,
                                   text_label)

        # noinspection PyTypeChecker
        return Layer(id_, layer_type_.value, layer_config, visual_channels)

    @staticmethod
    def _extract_color(color: str):
        _color = list(map(int, color.split(",")))
        rgb_value = _color[:-1]
        hex_value = '#{:02x}{:02x}{:02x}'.format(*rgb_value)
        alpha = _color[-1] / 255.0
        return rgb_value, hex_value, alpha

    def _extract_layer_style(self, symbol: QgsSymbol) -> Tuple[List[int], VisConfig]:
        symbol_opacity: float = symbol.opacity()
        symbol_layer: QgsSymbolLayer = symbol.symbolLayers()[0]
        if symbol_layer.subSymbol() is not None:
            return self._extract_layer_style(symbol_layer.subSymbol())

        sym_type = SymbolLayerType[symbol_layer.layerType()]
        properties = symbol_layer.properties()

        size_range, height_range, elevation_scale, stroked, enable3_d, wireframe, fixed_radius = [None] * 7

        if isinstance(symbol, QgsMarkerSymbol):
            fill_rgb, _, aplha = self._extract_color(properties['color'])
            opacity = round(symbol_opacity * aplha, 2)
            stroke_rgb, _, stroke_aplha = self._extract_color(properties['outline_color'])
            stroke_opacity = round(symbol_opacity * stroke_aplha, 2)
            thickness = float(properties['outline_width'])
            radius = int(properties['size'])
            size_unit = properties['size_unit']
            if size_unit != self.supported_size_unit:
                raise InvalidInputException(tr('Size unit "{}" is unsupported.', size_unit),
                                            bar_msg=bar_msg(tr('Please use unit {} instead', self.supported_size_unit)))
            # Fixed radius seems to always be False with point types
            fixed_radius = False
        else:
            raise QgsPluginNotImplementedException()

        outline = stroke_opacity > 0.0 and properties['outline_style'] != 'no'
        stroke_opacity = stroke_opacity if outline else None
        stroke_color = stroke_rgb if outline else None
        filled = opacity > 0.0
        thickness = thickness if thickness > 0.0 else VisConfig.thickness

        color_range = ColorRange.create_default()

        radius_range = VisConfig.radius_range

        vis_config = VisConfig(opacity, stroke_opacity, thickness, stroke_color, color_range, color_range, radius,
                               size_range, radius_range, height_range, elevation_scale, stroked, filled, enable3_d,
                               wireframe, fixed_radius, outline)

        return fill_rgb, vis_config

    def __check_if_canceled(self) -> None:
        if self.isCanceled():
            raise ProcessInterruptedException()

    def finished(self, result: bool) -> None:
        """
        This function is automatically called when the task has completed (successfully or not).

        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.

        :param result: the return value from self.run
        """
        if result:
            pass
        else:
            if self.exception is None:
                LOGGER_MAIN.warning(tr('Task was not successful'),
                                    extra=bar_msg(tr('Task was probably cancelled by user')))
            else:
                try:
                    raise self.exception
                except QgsPluginException as e:
                    LOGGER.exception(str(e), extra=e.bar_msg)
                except Exception as e:
                    LOGGER.exception(tr('Unhandled exception occurred'), extra=bar_msg(e))
