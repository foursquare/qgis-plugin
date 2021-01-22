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

"""
Initial version generated using https://app.quicktype.io/ from json file
"""

from typing import Any, List
from uuid import UUID

from .conversion_utils import (from_int, from_bool, from_float, to_float, from_str, from_list,
                               to_class, from_none)


class MapState:
    bearing: int
    drag_rotate: bool
    latitude: float
    longitude: float
    pitch: int
    zoom: float
    is_split: bool

    def __init__(self, bearing: int, drag_rotate: bool, latitude: float, longitude: float, pitch: int, zoom: float,
                 is_split: bool) -> None:
        self.bearing = bearing
        self.drag_rotate = drag_rotate
        self.latitude = latitude
        self.longitude = longitude
        self.pitch = pitch
        self.zoom = zoom
        self.is_split = is_split

    @staticmethod
    def from_dict(obj: Any) -> 'MapState':
        assert isinstance(obj, dict)
        bearing = from_int(obj.get("bearing"))
        drag_rotate = from_bool(obj.get("dragRotate"))
        latitude = from_float(obj.get("latitude"))
        longitude = from_float(obj.get("longitude"))
        pitch = from_int(obj.get("pitch"))
        zoom = from_float(obj.get("zoom"))
        is_split = from_bool(obj.get("isSplit"))
        return MapState(bearing, drag_rotate, latitude, longitude, pitch, zoom, is_split)

    def to_dict(self) -> dict:
        result: dict = {}
        result["bearing"] = from_int(self.bearing)
        result["dragRotate"] = from_bool(self.drag_rotate)
        result["latitude"] = to_float(self.latitude)
        result["longitude"] = to_float(self.longitude)
        result["pitch"] = from_int(self.pitch)
        result["zoom"] = to_float(self.zoom)
        result["isSplit"] = from_bool(self.is_split)
        return result


class AnyDict:
    pass

    def __init__(self, content: dict) -> None:
        self.content = content

    @staticmethod
    def from_dict(obj: Any) -> 'AnyDict':
        assert isinstance(obj, dict)
        return AnyDict(obj)

    def to_dict(self) -> dict:
        result: dict = self.content
        return result


class VisibleLayerGroups:
    label: bool
    road: bool
    border: bool
    building: bool
    water: bool
    land: bool
    the_3_d_building: bool

    def __init__(self, label: bool, road: bool, border: bool, building: bool, water: bool, land: bool,
                 the_3_d_building: bool) -> None:
        self.label = label
        self.road = road
        self.border = border
        self.building = building
        self.water = water
        self.land = land
        self.the_3_d_building = the_3_d_building

    @staticmethod
    def from_dict(obj: Any) -> 'VisibleLayerGroups':
        assert isinstance(obj, dict)
        label = from_bool(obj.get("label"))
        road = from_bool(obj.get("road"))
        border = from_bool(obj.get("border"))
        building = from_bool(obj.get("building"))
        water = from_bool(obj.get("water"))
        land = from_bool(obj.get("land"))
        the_3_d_building = from_bool(obj.get("3d building"))
        return VisibleLayerGroups(label, road, border, building, water, land, the_3_d_building)

    def to_dict(self) -> dict:
        result: dict = {}
        result["label"] = from_bool(self.label)
        result["road"] = from_bool(self.road)
        result["border"] = from_bool(self.border)
        result["building"] = from_bool(self.building)
        result["water"] = from_bool(self.water)
        result["land"] = from_bool(self.land)
        result["3d building"] = from_bool(self.the_3_d_building)
        return result


class MapStyle:
    style_type: str
    top_layer_groups: AnyDict
    visible_layer_groups: VisibleLayerGroups
    three_d_building_color: List[float]
    map_styles: AnyDict

    def __init__(self, style_type: str, top_layer_groups: AnyDict, visible_layer_groups: VisibleLayerGroups,
                 three_d_building_color: List[float], map_styles: AnyDict) -> None:
        self.style_type = style_type
        self.top_layer_groups = top_layer_groups
        self.visible_layer_groups = visible_layer_groups
        self.three_d_building_color = three_d_building_color
        self.map_styles = map_styles

    @staticmethod
    def from_dict(obj: Any) -> 'MapStyle':
        assert isinstance(obj, dict)
        style_type = from_str(obj.get("styleType"))
        top_layer_groups = AnyDict.from_dict(obj.get("topLayerGroups"))
        visible_layer_groups = VisibleLayerGroups.from_dict(obj.get("visibleLayerGroups"))
        three_d_building_color = from_list(from_float, obj.get("threeDBuildingColor"))
        map_styles = AnyDict.from_dict(obj.get("mapStyles"))
        return MapStyle(style_type, top_layer_groups, visible_layer_groups, three_d_building_color, map_styles)

    def to_dict(self) -> dict:
        result: dict = {}
        result["styleType"] = from_str(self.style_type)
        result["topLayerGroups"] = to_class(AnyDict, self.top_layer_groups)
        result["visibleLayerGroups"] = to_class(VisibleLayerGroups, self.visible_layer_groups)
        result["threeDBuildingColor"] = from_list(to_float, self.three_d_building_color)
        result["mapStyles"] = to_class(AnyDict, self.map_styles)
        return result


class AnimationConfig:
    current_time: None
    speed: int

    def __init__(self, current_time: None, speed: int) -> None:
        self.current_time = current_time
        self.speed = speed

    @staticmethod
    def from_dict(obj: Any) -> 'AnimationConfig':
        assert isinstance(obj, dict)
        current_time = from_none(obj.get("currentTime"))
        speed = from_int(obj.get("speed"))
        return AnimationConfig(current_time, speed)

    def to_dict(self) -> dict:
        result: dict = {}
        result["currentTime"] = from_none(self.current_time)
        result["speed"] = from_int(self.speed)
        return result


class FieldDisplayNames:
    # TODO: type and field checks
    content: AnyDict

    def __init__(self, content: AnyDict) -> None:
        self.content = content

    @staticmethod
    def from_dict(obj: Any) -> 'FieldDisplayNames':
        assert isinstance(obj, dict)
        content = AnyDict.from_dict(obj)
        return FieldDisplayNames(content)

    def to_dict(self) -> dict:
        result: dict = self.content.to_dict()
        return result


class Datasets:
    field_display_names: FieldDisplayNames

    def __init__(self, field_display_names: FieldDisplayNames) -> None:
        self.field_display_names = field_display_names

    @staticmethod
    def from_dict(obj: Any) -> 'Datasets':
        assert isinstance(obj, dict)
        field_display_names = FieldDisplayNames.from_dict(obj.get("fieldDisplayNames"))
        return Datasets(field_display_names)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fieldDisplayNames"] = to_class(FieldDisplayNames, self.field_display_names)
        return result


class Brush:
    size: float
    enabled: bool

    def __init__(self, size: float, enabled: bool) -> None:
        self.size = size
        self.enabled = enabled

    @staticmethod
    def from_dict(obj: Any) -> 'Brush':
        assert isinstance(obj, dict)
        size = from_float(obj.get("size"))
        enabled = from_bool(obj.get("enabled"))
        return Brush(size, enabled)

    def to_dict(self) -> dict:
        result: dict = {}
        result["size"] = to_float(self.size)
        result["enabled"] = from_bool(self.enabled)
        return result


class Coordinate:
    enabled: bool

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    @staticmethod
    def from_dict(obj: Any) -> 'Coordinate':
        assert isinstance(obj, dict)
        enabled = from_bool(obj.get("enabled"))
        return Coordinate(enabled)

    def to_dict(self) -> dict:
        result: dict = {}
        result["enabled"] = from_bool(self.enabled)
        return result


class FieldsToShow:
    # TODO: type and field checks
    # name: str
    # format: None
    content: AnyDict

    def __init__(self, content: AnyDict) -> None:
        self.content = content

    @staticmethod
    def from_dict(obj: Any) -> 'FieldsToShow':
        assert isinstance(obj, dict)
        content = AnyDict.from_dict(obj)
        return FieldsToShow(content)

    def to_dict(self) -> dict:
        result: dict = self.content.to_dict()
        return result


class Tooltip:
    fields_to_show: FieldsToShow
    compare_mode: bool
    compare_type: str
    enabled: bool

    def __init__(self, fields_to_show: FieldsToShow, compare_mode: bool, compare_type: str, enabled: bool) -> None:
        self.fields_to_show = fields_to_show
        self.compare_mode = compare_mode
        self.compare_type = compare_type
        self.enabled = enabled

    @staticmethod
    def from_dict(obj: Any) -> 'Tooltip':
        assert isinstance(obj, dict)
        fields_to_show = FieldsToShow.from_dict(obj.get("fieldsToShow"))
        compare_mode = from_bool(obj.get("compareMode"))
        compare_type = from_str(obj.get("compareType"))
        enabled = from_bool(obj.get("enabled"))
        return Tooltip(fields_to_show, compare_mode, compare_type, enabled)

    def to_dict(self) -> dict:
        result: dict = {}
        result["fieldsToShow"] = to_class(FieldsToShow, self.fields_to_show)
        result["compareMode"] = from_bool(self.compare_mode)
        result["compareType"] = from_str(self.compare_type)
        result["enabled"] = from_bool(self.enabled)
        return result


class InteractionConfig:
    tooltip: Tooltip
    brush: Brush
    geocoder: Coordinate
    coordinate: Coordinate

    def __init__(self, tooltip: Tooltip, brush: Brush, geocoder: Coordinate, coordinate: Coordinate) -> None:
        self.tooltip = tooltip
        self.brush = brush
        self.geocoder = geocoder
        self.coordinate = coordinate

    @staticmethod
    def from_dict(obj: Any) -> 'InteractionConfig':
        assert isinstance(obj, dict)
        tooltip = Tooltip.from_dict(obj.get("tooltip"))
        brush = Brush.from_dict(obj.get("brush"))
        geocoder = Coordinate.from_dict(obj.get("geocoder"))
        coordinate = Coordinate.from_dict(obj.get("coordinate"))
        return InteractionConfig(tooltip, brush, geocoder, coordinate)

    def to_dict(self) -> dict:
        result: dict = {}
        result["tooltip"] = to_class(Tooltip, self.tooltip)
        result["brush"] = to_class(Brush, self.brush)
        result["geocoder"] = to_class(Coordinate, self.geocoder)
        result["coordinate"] = to_class(Coordinate, self.coordinate)
        return result


class Columns:
    geojson: str

    def __init__(self, geojson: str) -> None:
        self.geojson = geojson

    @staticmethod
    def from_dict(obj: Any) -> 'Columns':
        assert isinstance(obj, dict)
        geojson = from_str(obj.get("geojson"))
        return Columns(geojson)

    def to_dict(self) -> dict:
        result: dict = {}
        result["geojson"] = from_str(self.geojson)
        return result


class TextLabel:
    field: None
    color: List[int]
    size: int
    offset: List[int]
    anchor: str
    alignment: str

    def __init__(self, field: None, color: List[int], size: int, offset: List[int], anchor: str,
                 alignment: str) -> None:
        self.field = field
        self.color = color
        self.size = size
        self.offset = offset
        self.anchor = anchor
        self.alignment = alignment

    @staticmethod
    def from_dict(obj: Any) -> 'TextLabel':
        assert isinstance(obj, dict)
        field = from_none(obj.get("field"))
        color = from_list(from_int, obj.get("color"))
        size = from_int(obj.get("size"))
        offset = from_list(from_int, obj.get("offset"))
        anchor = from_str(obj.get("anchor"))
        alignment = from_str(obj.get("alignment"))
        return TextLabel(field, color, size, offset, anchor, alignment)

    def to_dict(self) -> dict:
        result: dict = {}
        result["field"] = from_none(self.field)
        result["color"] = from_list(from_int, self.color)
        result["size"] = from_int(self.size)
        result["offset"] = from_list(from_int, self.offset)
        result["anchor"] = from_str(self.anchor)
        result["alignment"] = from_str(self.alignment)
        return result


class ColorRange:
    name: str
    type: str
    category: str
    colors: List[str]

    def __init__(self, name: str, type: str, category: str, colors: List[str]) -> None:
        self.name = name
        self.type = type
        self.category = category
        self.colors = colors

    @staticmethod
    def from_dict(obj: Any) -> 'ColorRange':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        type = from_str(obj.get("type"))
        category = from_str(obj.get("category"))
        colors = from_list(from_str, obj.get("colors"))
        return ColorRange(name, type, category, colors)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["type"] = from_str(self.type)
        result["category"] = from_str(self.category)
        result["colors"] = from_list(from_str, self.colors)
        return result


class VisConfig:
    opacity: float
    stroke_opacity: float
    thickness: float
    stroke_color: None
    color_range: ColorRange
    stroke_color_range: ColorRange
    radius: int
    size_range: List[int]
    radius_range: List[int]
    height_range: List[int]
    elevation_scale: int
    stroked: bool
    filled: bool
    enable3_d: bool
    wireframe: bool

    def __init__(self, opacity: float, stroke_opacity: float, thickness: float, stroke_color: None,
                 color_range: ColorRange, stroke_color_range: ColorRange, radius: int, size_range: List[int],
                 radius_range: List[int], height_range: List[int], elevation_scale: int, stroked: bool, filled: bool,
                 enable3_d: bool, wireframe: bool) -> None:
        self.opacity = opacity
        self.stroke_opacity = stroke_opacity
        self.thickness = thickness
        self.stroke_color = stroke_color
        self.color_range = color_range
        self.stroke_color_range = stroke_color_range
        self.radius = radius
        self.size_range = size_range
        self.radius_range = radius_range
        self.height_range = height_range
        self.elevation_scale = elevation_scale
        self.stroked = stroked
        self.filled = filled
        self.enable3_d = enable3_d
        self.wireframe = wireframe

    @staticmethod
    def from_dict(obj: Any) -> 'VisConfig':
        assert isinstance(obj, dict)
        opacity = from_float(obj.get("opacity"))
        stroke_opacity = from_float(obj.get("strokeOpacity"))
        thickness = from_float(obj.get("thickness"))
        stroke_color = from_none(obj.get("strokeColor"))
        color_range = ColorRange.from_dict(obj.get("colorRange"))
        stroke_color_range = ColorRange.from_dict(obj.get("strokeColorRange"))
        radius = from_int(obj.get("radius"))
        size_range = from_list(from_int, obj.get("sizeRange"))
        radius_range = from_list(from_int, obj.get("radiusRange"))
        height_range = from_list(from_int, obj.get("heightRange"))
        elevation_scale = from_int(obj.get("elevationScale"))
        stroked = from_bool(obj.get("stroked"))
        filled = from_bool(obj.get("filled"))
        enable3_d = from_bool(obj.get("enable3d"))
        wireframe = from_bool(obj.get("wireframe"))
        return VisConfig(opacity, stroke_opacity, thickness, stroke_color, color_range, stroke_color_range, radius,
                         size_range, radius_range, height_range, elevation_scale, stroked, filled, enable3_d, wireframe)

    def to_dict(self) -> dict:
        result: dict = {}
        result["opacity"] = to_float(self.opacity)
        result["strokeOpacity"] = to_float(self.stroke_opacity)
        result["thickness"] = to_float(self.thickness)
        result["strokeColor"] = from_none(self.stroke_color)
        result["colorRange"] = to_class(ColorRange, self.color_range)
        result["strokeColorRange"] = to_class(ColorRange, self.stroke_color_range)
        result["radius"] = from_int(self.radius)
        result["sizeRange"] = from_list(from_int, self.size_range)
        result["radiusRange"] = from_list(from_int, self.radius_range)
        result["heightRange"] = from_list(from_int, self.height_range)
        result["elevationScale"] = from_int(self.elevation_scale)
        result["stroked"] = from_bool(self.stroked)
        result["filled"] = from_bool(self.filled)
        result["enable3d"] = from_bool(self.enable3_d)
        result["wireframe"] = from_bool(self.wireframe)
        return result


class LayerConfig:
    data_id: UUID
    label: str
    color: List[int]
    columns: Columns
    is_visible: bool
    vis_config: VisConfig
    hidden: bool
    text_label: List[TextLabel]

    def __init__(self, data_id: UUID, label: str, color: List[int], columns: Columns, is_visible: bool,
                 vis_config: VisConfig, hidden: bool, text_label: List[TextLabel]) -> None:
        self.data_id = data_id
        self.label = label
        self.color = color
        self.columns = columns
        self.is_visible = is_visible
        self.vis_config = vis_config
        self.hidden = hidden
        self.text_label = text_label

    @staticmethod
    def from_dict(obj: Any) -> 'LayerConfig':
        assert isinstance(obj, dict)
        data_id = UUID(obj.get("dataId"))
        label = from_str(obj.get("label"))
        color = from_list(from_int, obj.get("color"))
        columns = Columns.from_dict(obj.get("columns"))
        is_visible = from_bool(obj.get("isVisible"))
        vis_config = VisConfig.from_dict(obj.get("visConfig"))
        hidden = from_bool(obj.get("hidden"))
        text_label = from_list(TextLabel.from_dict, obj.get("textLabel"))
        return LayerConfig(data_id, label, color, columns, is_visible, vis_config, hidden, text_label)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dataId"] = str(self.data_id)
        result["label"] = from_str(self.label)
        result["color"] = from_list(from_int, self.color)
        result["columns"] = to_class(Columns, self.columns)
        result["isVisible"] = from_bool(self.is_visible)
        result["visConfig"] = to_class(VisConfig, self.vis_config)
        result["hidden"] = from_bool(self.hidden)
        result["textLabel"] = from_list(lambda x: to_class(TextLabel, x), self.text_label)
        return result


class ColorField:
    name: str
    type: str

    def __init__(self, name: str, type: str) -> None:
        self.name = name
        self.type = type

    @staticmethod
    def from_dict(obj: Any) -> 'ColorField':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        type = from_str(obj.get("type"))
        return ColorField(name, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["type"] = from_str(self.type)
        return result


class VisualChannels:
    color_field: ColorField
    color_scale: str
    stroke_color_field: None
    stroke_color_scale: str
    size_field: None
    size_scale: str
    height_field: None
    height_scale: str
    radius_field: None
    radius_scale: str

    def __init__(self, color_field: ColorField, color_scale: str, stroke_color_field: None, stroke_color_scale: str,
                 size_field: None, size_scale: str, height_field: None, height_scale: str, radius_field: None,
                 radius_scale: str) -> None:
        self.color_field = color_field
        self.color_scale = color_scale
        self.stroke_color_field = stroke_color_field
        self.stroke_color_scale = stroke_color_scale
        self.size_field = size_field
        self.size_scale = size_scale
        self.height_field = height_field
        self.height_scale = height_scale
        self.radius_field = radius_field
        self.radius_scale = radius_scale

    @staticmethod
    def from_dict(obj: Any) -> 'VisualChannels':
        assert isinstance(obj, dict)
        color_field = ColorField.from_dict(obj.get("colorField"))
        color_scale = from_str(obj.get("colorScale"))
        stroke_color_field = from_none(obj.get("strokeColorField"))
        stroke_color_scale = from_str(obj.get("strokeColorScale"))
        size_field = from_none(obj.get("sizeField"))
        size_scale = from_str(obj.get("sizeScale"))
        height_field = from_none(obj.get("heightField"))
        height_scale = from_str(obj.get("heightScale"))
        radius_field = from_none(obj.get("radiusField"))
        radius_scale = from_str(obj.get("radiusScale"))
        return VisualChannels(color_field, color_scale, stroke_color_field, stroke_color_scale, size_field, size_scale,
                              height_field, height_scale, radius_field, radius_scale)

    def to_dict(self) -> dict:
        result: dict = {}
        result["colorField"] = to_class(ColorField, self.color_field)
        result["colorScale"] = from_str(self.color_scale)
        result["strokeColorField"] = from_none(self.stroke_color_field)
        result["strokeColorScale"] = from_str(self.stroke_color_scale)
        result["sizeField"] = from_none(self.size_field)
        result["sizeScale"] = from_str(self.size_scale)
        result["heightField"] = from_none(self.height_field)
        result["heightScale"] = from_str(self.height_scale)
        result["radiusField"] = from_none(self.radius_field)
        result["radiusScale"] = from_str(self.radius_scale)
        return result


class Layer:
    id: str
    type: str
    config: LayerConfig
    visual_channels: VisualChannels

    def __init__(self, id: str, type: str, config: LayerConfig, visual_channels: VisualChannels) -> None:
        self.id = id
        self.type = type
        self.config = config
        self.visual_channels = visual_channels

    @staticmethod
    def from_dict(obj: Any) -> 'Layer':
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        type = from_str(obj.get("type"))
        config = LayerConfig.from_dict(obj.get("config"))
        visual_channels = VisualChannels.from_dict(obj.get("visualChannels"))
        return Layer(id, type, config, visual_channels)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["type"] = from_str(self.type)
        result["config"] = to_class(LayerConfig, self.config)
        result["visualChannels"] = to_class(VisualChannels, self.visual_channels)
        return result


class VisState:
    filters: List[Any]
    layers: List[Layer]
    interaction_config: InteractionConfig
    layer_blending: str
    split_maps: List[Any]
    animation_config: AnimationConfig
    metrics: List[Any]
    geo_keys: List[Any]
    group_bys: List[Any]
    datasets: Datasets
    joins: List[Any]

    def __init__(self, filters: List[Any], layers: List[Layer], interaction_config: InteractionConfig,
                 layer_blending: str, split_maps: List[Any], animation_config: AnimationConfig, metrics: List[Any],
                 geo_keys: List[Any], group_bys: List[Any], datasets: Datasets, joins: List[Any]) -> None:
        self.filters = filters
        self.layers = layers
        self.interaction_config = interaction_config
        self.layer_blending = layer_blending
        self.split_maps = split_maps
        self.animation_config = animation_config
        self.metrics = metrics
        self.geo_keys = geo_keys
        self.group_bys = group_bys
        self.datasets = datasets
        self.joins = joins

    @staticmethod
    def from_dict(obj: Any) -> 'VisState':
        assert isinstance(obj, dict)
        filters = from_list(lambda x: x, obj.get("filters"))
        layers = from_list(Layer.from_dict, obj.get("layers"))
        interaction_config = InteractionConfig.from_dict(obj.get("interactionConfig"))
        layer_blending = from_str(obj.get("layerBlending"))
        split_maps = from_list(lambda x: x, obj.get("splitMaps"))
        animation_config = AnimationConfig.from_dict(obj.get("animationConfig"))
        metrics = from_list(lambda x: x, obj.get("metrics"))
        geo_keys = from_list(lambda x: x, obj.get("geoKeys"))
        group_bys = from_list(lambda x: x, obj.get("groupBys"))
        datasets = Datasets.from_dict(obj.get("datasets"))
        joins = from_list(lambda x: x, obj.get("joins"))
        return VisState(filters, layers, interaction_config, layer_blending, split_maps, animation_config, metrics,
                        geo_keys, group_bys, datasets, joins)

    def to_dict(self) -> dict:
        result: dict = {}
        result["filters"] = from_list(lambda x: x, self.filters)
        result["layers"] = from_list(lambda x: to_class(Layer, x), self.layers)
        result["interactionConfig"] = to_class(InteractionConfig, self.interaction_config)
        result["layerBlending"] = from_str(self.layer_blending)
        result["splitMaps"] = from_list(lambda x: x, self.split_maps)
        result["animationConfig"] = to_class(AnimationConfig, self.animation_config)
        result["metrics"] = from_list(lambda x: x, self.metrics)
        result["geoKeys"] = from_list(lambda x: x, self.geo_keys)
        result["groupBys"] = from_list(lambda x: x, self.group_bys)
        result["datasets"] = to_class(Datasets, self.datasets)
        result["joins"] = from_list(lambda x: x, self.joins)
        return result


class ConfigConfig:
    vis_state: VisState
    map_state: MapState
    map_style: MapStyle

    def __init__(self, vis_state: VisState, map_state: MapState, map_style: MapStyle) -> None:
        self.vis_state = vis_state
        self.map_state = map_state
        self.map_style = map_style

    @staticmethod
    def from_dict(obj: Any) -> 'ConfigConfig':
        assert isinstance(obj, dict)
        vis_state = VisState.from_dict(obj.get("visState"))
        map_state = MapState.from_dict(obj.get("mapState"))
        map_style = MapStyle.from_dict(obj.get("mapStyle"))
        return ConfigConfig(vis_state, map_state, map_style)

    def to_dict(self) -> dict:
        result: dict = {}
        result["visState"] = to_class(VisState, self.vis_state)
        result["mapState"] = to_class(MapState, self.map_state)
        result["mapStyle"] = to_class(MapStyle, self.map_style)
        return result


class Config:
    version: str
    config: ConfigConfig

    def __init__(self, version: str, config: ConfigConfig) -> None:
        self.version = version
        self.config = config

    @staticmethod
    def from_dict(obj: Any) -> 'Config':
        assert isinstance(obj, dict)
        version = from_str(obj.get("version"))
        config = ConfigConfig.from_dict(obj.get("config"))
        return Config(version, config)

    def to_dict(self) -> dict:
        result: dict = {}
        result["version"] = from_str(self.version)
        result["config"] = to_class(ConfigConfig, self.config)
        return result


class Data:
    id: UUID
    label: str
    color: List[int]
    all_data: List[Any]
    fields: List[Any]

    def __init__(self, id: UUID, label: str, color: List[int], all_data: List[Any], fields: List[Any]) -> None:
        self.id = id
        self.label = label
        self.color = color
        self.all_data = all_data
        self.fields = fields

    @staticmethod
    def from_dict(obj: Any) -> 'Data':
        assert isinstance(obj, dict)
        id = UUID(obj.get("id"))
        label = from_str(obj.get("label"))
        color = from_list(from_int, obj.get("color"))
        all_data = from_list(lambda x: x, obj.get("allData"))
        fields = from_list(lambda x: x, obj.get("fields"))
        return Data(id, label, color, all_data, fields)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id)
        result["label"] = from_str(self.label)
        result["color"] = from_list(from_int, self.color)
        result["allData"] = from_list(lambda x: x, self.all_data)
        result["fields"] = from_list(lambda x: x, self.fields)
        return result


class Dataset:
    version: str
    data: Data

    def __init__(self, version: str, data: Data) -> None:
        self.version = version
        self.data = data

    @staticmethod
    def from_dict(obj: Any) -> 'Dataset':
        assert isinstance(obj, dict)
        version = from_str(obj.get("version"))
        data = Data.from_dict(obj.get("data"))
        return Dataset(version, data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["version"] = from_str(self.version)
        result["data"] = to_class(Data, self.data)
        return result


class Info:
    app: str
    created_at: str
    title: str
    description: str

    def __init__(self, app: str, created_at: str, title: str, description: str) -> None:
        self.app = app
        self.created_at = created_at
        self.title = title
        self.description = description

    @staticmethod
    def from_dict(obj: Any) -> 'Info':
        assert isinstance(obj, dict)
        app = from_str(obj.get("app"))
        created_at = from_str(obj.get("created_at"))
        title = from_str(obj.get("title"))
        description = from_str(obj.get("description"))
        return Info(app, created_at, title, description)

    def to_dict(self) -> dict:
        result: dict = {}
        result["app"] = from_str(self.app)
        result["created_at"] = from_str(self.created_at)
        result["title"] = from_str(self.title)
        result["description"] = from_str(self.description)
        return result


class MapConfig:
    datasets: List[Dataset]
    config: Config
    info: Info

    def __init__(self, datasets: List[Dataset], config: Config, info: Info) -> None:
        self.datasets = datasets
        self.config = config
        self.info = info

    @staticmethod
    def from_dict(obj: Any) -> 'MapConfig':
        assert isinstance(obj, dict)
        datasets = from_list(Dataset.from_dict, obj.get("datasets"))
        config = Config.from_dict(obj.get("config"))
        info = Info.from_dict(obj.get("info"))
        return MapConfig(datasets, config, info)

    def to_dict(self) -> dict:
        result: dict = {}
        result["datasets"] = from_list(lambda x: to_class(Dataset, x), self.datasets)
        result["config"] = to_class(Config, self.config)
        result["info"] = to_class(Info, self.info)
        return result
