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
import logging
import uuid
from typing import Optional, List, Tuple, Union

from qgis.core import (QgsVectorLayer, QgsSymbol, QgsFeatureRenderer, QgsSymbolLayer, QgsMarkerSymbol,
                       QgsLineSymbol, QgsFillSymbol, QgsRendererRange,
                       QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer, QgsRendererCategory)

from .base_config_creator_task import BaseConfigCreatorTask
from ..exceptions import InvalidInputException
from ..utils import extract_color, rgb_to_hex
from ...definitions.settings import Settings
from ...definitions.types import UnfoldedLayerType, SymbolType, SymbolLayerType
from ...model.map_config import Layer, LayerConfig, VisualChannels, VisConfig, Columns, TextLabel, ColorRange
from ...qgis_plugin_tools.tools.custom_logging import bar_msg
from ...qgis_plugin_tools.tools.exceptions import QgsPluginNotImplementedException
from ...qgis_plugin_tools.tools.i18n import tr
from ...qgis_plugin_tools.tools.layers import LayerType
from ...qgis_plugin_tools.tools.resources import plugin_name

# This logger is safe to use inside the task
LOGGER = logging.getLogger(f'{plugin_name()}_task')

# Main thread logger meant to be used in finished method
LOGGER_MAIN = logging.getLogger(plugin_name())


class LayerToLayerConfig(BaseConfigCreatorTask):
    """
    Creates VisState.Layer object

    Some of the code is inspired by QGIS plugin Spatial Data Package Export created by Gispo Ltd.
    https://github.com/cividi/spatial-data-package-export/blob/master/SpatialDataPackageExport/core/styles2attributes.py
    Licensed by GPLv3
    """

    SUPPORTED_GRADUATED_METHODS = {"EqualInterval": "quantize", "Quantile": "quantile", "Logarithmic": "log"}
    CATEGORIZED_SCALE = "ordinal"

    def __init__(self, layer_uuid: uuid.UUID, layer: QgsVectorLayer, is_visible: bool = True):
        super().__init__('LayerToLayerConfig')
        self.layer_uuid = layer_uuid
        self.layer = layer
        self.is_visible = is_visible
        self.result_layer_conf: Optional[Layer] = None
        self.__pixel_unit = Settings.pixel_size_unit.get()
        self.__millimeter_unit = Settings.millimeter_size_unit.get()
        self.__millimeters_to_pixels = Settings.millimeters_to_pixels.get()
        self.__width_pixel_factor = Settings.width_pixel_factor.get()

    def run(self) -> bool:
        try:
            self._check_if_canceled()
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
        try:
            symbol_type = SymbolType[renderer.type()]
        except Exception:
            raise QgsPluginNotImplementedException(tr("Symbol type {} is not supported yet", renderer.type()),
                                                   bar_msg=bar_msg())

        layer_type = LayerType.from_layer(self.layer)
        LOGGER.info(tr('Symbol type: {}', symbol_type))

        self.setProgress(50)
        if symbol_type == SymbolType.singleSymbol:
            renderer: QgsSingleSymbolRenderer
            color, vis_config = self._extract_layer_style(renderer.symbol())
            visual_channels = VisualChannels.create_single_color_channels()
        elif symbol_type in (SymbolType.graduatedSymbol, SymbolType.categorizedSymbol):
            color, vis_config, visual_channels = self._extract_advanced_layer_style(renderer, layer_type, symbol_type)
        else:
            raise QgsPluginNotImplementedException()

        if layer_type == LayerType.Point:
            layer_type_ = UnfoldedLayerType.Point
            columns = Columns.for_point_2d()
        elif layer_type in [LayerType.Line, LayerType.Polygon]:
            layer_type_ = UnfoldedLayerType.Geojson
            columns = Columns.for_geojson()
            visual_channels.height_scale = VisualChannels.height_scale
            visual_channels.radius_scale = VisualChannels.radius_scale
        else:
            raise QgsPluginNotImplementedException(tr('Layer type {} is not implemented', layer_type),
                                                   bar_msg=bar_msg())

        hidden = False
        text_label = [TextLabel.create_default()]

        layer_config = LayerConfig(self.layer_uuid, self.layer.name(), color, columns, self.is_visible, vis_config,
                                   hidden, text_label)

        id_ = str(self.layer_uuid).replace("-", "")[:7]
        # noinspection PyTypeChecker
        return Layer(id_, layer_type_.value, layer_config, visual_channels)

    def _extract_advanced_layer_style(self, renderer, layer_type: LayerType, symbol_type: SymbolType) -> Tuple[
        List[int], VisConfig, VisualChannels]:
        """ Extract layer style when layer has graduated or categorized style """
        requires_custom_breaks: bool = False
        if symbol_type == SymbolType.graduatedSymbol:
            classification_method = renderer.classificationMethod()
            if classification_method.id() == 'Logarithmic':
                requires_custom_breaks = True
            scale_name = self.SUPPORTED_GRADUATED_METHODS.get(classification_method.id())

            if not scale_name:
                raise InvalidInputException(tr('Unsupported classification method "{}"', classification_method.id()),
                                            bar_msg=bar_msg(tr(
                                                'Use Equal Count (Quantile), Equal Interval (Quantize) or Logarithmic')))
            symbol_range: QgsRendererRange
            styles = [self._extract_layer_style(symbol_range.symbol()) for symbol_range in renderer.ranges()]
            if not styles:
                raise InvalidInputException(tr('Graduated layer should have at least 1 class'), bar_msg=bar_msg())
        else:
            renderer: QgsCategorizedSymbolRenderer
            category: QgsRendererCategory
            scale_name = self.CATEGORIZED_SCALE
            styles = [self._extract_layer_style(category.symbol()) for category in renderer.categories()]
            if not styles:
                raise InvalidInputException(tr('Categorized layer should have at least 1 class'), bar_msg=bar_msg())

        color = styles[0][0]
        vis_config = styles[0][1]
        fill_colors = [rgb_to_hex(style[0]) for style in styles]
        stroke_colors = [rgb_to_hex(style[1].stroke_color) for style in styles if style[1].stroke_color]

        if layer_type == LayerType.Line:
            # For lines, swap the color ranges
            tmp = [] + fill_colors
            fill_colors = [] + stroke_colors
            stroke_colors = tmp

        if fill_colors:
            vis_config.color_range = ColorRange.create_custom(fill_colors)
        if stroke_colors:
            vis_config.stroke_color_range = ColorRange.create_custom(stroke_colors)
        categorizing_field = self._qgis_field_to_unfolded_field(
            self.layer.fields()[self.layer.fields().indexOf(renderer.classAttribute())])
        categorizing_field.analyzer_type = None
        categorizing_field.format = None
        color_field, stroke_field = [None] * 2
        if len(set(fill_colors)) > 1:
            color_field = categorizing_field
        if len(set(stroke_colors)) > 1:
            stroke_field = categorizing_field
        visual_channels = VisualChannels(color_field, scale_name if color_field else VisualChannels.color_scale,
                                         stroke_field,
                                         scale_name if stroke_field else VisualChannels.stroke_color_scale, None,
                                         VisualChannels.size_scale)

        # provide color map for certain graduated symbols
        if requires_custom_breaks:
            symbol_ranges = renderer.ranges()
            vis_config.color_range.color_map = []
            for i, col in enumerate(fill_colors):
                upperValue = symbol_ranges[i].upperValue()
                vis_config.color_range.color_map.append([upperValue, col])
            visual_channels.color_scale = 'custom'

        return color, vis_config, visual_channels

    def _extract_layer_style(self, symbol: QgsSymbol) -> Tuple[List[int], VisConfig]:
        symbol_opacity: float = symbol.opacity()
        symbol_layer: QgsSymbolLayer = symbol.symbolLayers()[0]
        if symbol_layer.subSymbol() is not None:
            return self._extract_layer_style(symbol_layer.subSymbol())

        sym_type = SymbolLayerType[symbol_layer.layerType()]
        properties = symbol_layer.properties()

        # Default values
        radius = VisConfig.radius
        color_range = ColorRange.create_default()
        radius_range = VisConfig.radius_range

        if isinstance(symbol, QgsMarkerSymbol) or isinstance(symbol, QgsFillSymbol):
            fill_rgb, alpha = extract_color(properties['color'])
            opacity = round(symbol_opacity * alpha, 2)
            stroke_rgb, stroke_alpha = extract_color(properties['outline_color'])
            stroke_opacity = round(symbol_opacity * stroke_alpha, 2)
            thickness = self._convert_to_pixels(float(properties['outline_width']), properties['outline_width_unit'])
            outline = stroke_opacity > 0.0 and properties['outline_style'] != 'no'
            stroke_opacity = stroke_opacity if outline else None
            stroke_color = stroke_rgb if outline else None
            filled = opacity > 0.0 and properties.get('style', 'solid') != 'no'

            if isinstance(symbol, QgsMarkerSymbol):
                size_range, height_range, elevation_scale, stroked, enable3_d, wireframe = [None] * 6

                # Fixed radius seems to always be False with point types
                fixed_radius = False

                radius = self._convert_to_pixels(float(properties['size']), properties['size_unit'], radius=True)
                thickness = thickness if thickness > 0.0 else 1.0  # Hairline in QGIS
            else:
                size_range = VisConfig.size_range
                height_range = VisConfig.height_range
                elevation_scale = VisConfig.elevation_scale
                if outline:
                    stroked = True
                else:
                    stroked = False
                    stroke_color = None
                wireframe, enable3_d = [False] * 2
                fixed_radius, outline = [None] * 2
        elif isinstance(symbol, QgsLineSymbol):
            fill_rgb, stroke_alpha = extract_color(properties['line_color'])
            opacity = round(symbol_opacity * stroke_alpha, 2)
            stroke_opacity = opacity
            thickness = self._convert_to_pixels(float(properties['line_width']), properties['line_width_unit'])

            size_range = VisConfig.size_range
            height_range = VisConfig.height_range
            elevation_scale = VisConfig.elevation_scale
            stroked = True
            wireframe, enable3_d, filled = [False] * 3
            stroke_color, fixed_radius, outline = [None] * 3
        else:
            raise QgsPluginNotImplementedException(tr('Symbol type {} is not supported yet', symbol.type()),
                                                   bar_msg=bar_msg())

        thickness = thickness if thickness > 0.0 else VisConfig.thickness

        vis_config = VisConfig(opacity, stroke_opacity, thickness, stroke_color, color_range, color_range, radius,
                               size_range, radius_range, height_range, elevation_scale, stroked, filled, enable3_d,
                               wireframe, fixed_radius, outline)

        return fill_rgb, vis_config

    def _convert_to_pixels(self, size_value: float, size_unit: str, radius: bool = False) -> Union[int, float]:
        """ Convert size value to pixels"""
        value = size_value if radius else size_value / self.__width_pixel_factor
        if size_unit == self.__millimeter_unit:
            value = value / self.__millimeters_to_pixels

        if size_unit in (self.__millimeter_unit, self.__pixel_unit):
            return int(value) if radius else round(value, 1)
        else:
            raise InvalidInputException(tr('Size unit "{}" is unsupported.', size_unit),
                                        bar_msg=bar_msg(
                                            tr('Please use {} instead',
                                               tr('or').join((self.__millimeter_unit, self.__pixel_unit)))))
