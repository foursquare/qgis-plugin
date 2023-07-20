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
import logging
from typing import List, Dict, Optional, Tuple

from qgis.core import QgsProject, QgsLayerTree, QgsLayerTreeNode, QgsMapLayer, QgsVectorLayer, QgsRasterLayer, \
    QgsLayerTreeLayer

from .exceptions import MapboxTokenMissing
from ..definitions.settings import Settings
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


class LayerHandler:
    basemap_group = tr('FSQ Studio Basemaps')

    @staticmethod
    def add_fsq_studio_basemaps() -> List[QgsRasterLayer]:
        """ Add FSQ Studio basemaps to the project """
        # noinspection PyArgumentList
        qgs_project = QgsProject.instance()

        base_url = Settings.basemap_wmts_url.get()
        token = Settings.mapbox_api_token.get()
        crs = Settings.project_crs.get()
        if not token:
            raise MapboxTokenMissing(tr('Mapbox token is missing'), bar_msg=bar_msg(
                tr('Please add a valid Mapbox token to the settings to view the base maps')))

        # Add group
        root: QgsLayerTree = qgs_project.layerTreeRoot()
        group = root.findGroup(LayerHandler.basemap_group)
        if not group:
            group = root.addGroup(LayerHandler.basemap_group)
            group.setIsMutuallyExclusive(True)

        existing_layers_in_group = [node.layer().name() for node in group.children()]

        default_params = {'format': Settings.basemap_wmts_default_format.get(), 'token': token, 'crs': crs}

        # Generate WMTS layers
        layers: List[QgsRasterLayer] = []
        wmts_basemap_config: Dict[str, Dict[str, Dict[str, str]]] = Settings.wmts_basemaps.get()
        for username, wmts_layers in wmts_basemap_config.items():
            for name, layer_params in wmts_layers.items():
                if name not in existing_layers_in_group:
                    params = {**default_params, **layer_params, 'username': username}
                    url = base_url.format(**params)
                    LOGGER.debug(f"{name}: {url.replace(token, '<mapbox-api-token>')}")
                    layer = QgsRasterLayer(url, name, "wms")
                    if layer.isValid():
                        layers.append(layer)
                    else:
                        LOGGER.warning(tr('Layer {} is not valid', name))

        if not layers and not existing_layers_in_group:
            raise MapboxTokenMissing(tr('No valid base maps found'),
                                     bar_msg=bar_msg(tr('Please check your Mapbox token')))

        # Add layers to the group
        for i, layer in enumerate(layers):
            if not group.findLayer(layer):
                qgs_project.addMapLayer(layer, False)
                layer_element: QgsLayerTreeLayer = group.addLayer(layer)
                layer_element.setItemVisibilityChecked(i == 0)

        return layers

    @staticmethod
    def get_current_basemap_name() -> Optional[str]:
        """ Get the name of the currently active basemap """
        # noinspection PyArgumentList
        qgs_project = QgsProject.instance()
        layer_name = None
        root: QgsLayerTree = qgs_project.layerTreeRoot()
        group = root.findGroup(LayerHandler.basemap_group)
        if group:
            layers = list(filter(lambda l: l[1], LayerHandler.get_layers_and_visibility_from_node(root, group)))
            layer_name = layers[0][0].name() if layers else None
        return layer_name

    # noinspection PyTypeChecker
    @staticmethod
    def get_vector_layers_and_visibility() -> List[Tuple[QgsVectorLayer, bool]]:
        """ Get all vector layers in correct order """
        # noinspection PyArgumentList
        root: QgsLayerTree = QgsProject.instance().layerTreeRoot()
        layers_with_visibility = LayerHandler.get_layers_and_visibility_from_node(root, root)
        return list(filter(lambda layer_and_visibility: isinstance(layer_and_visibility[0], QgsVectorLayer),
                           layers_with_visibility))

    @staticmethod
    def get_layers_and_visibility_from_node(root: QgsLayerTree, node: QgsLayerTreeNode) -> List[
        Tuple[QgsMapLayer, bool]]:
        layers = []
        child: QgsLayerTreeNode
        for child in node.children():
            if root.isGroup(child):
                # noinspection PyTypeChecker
                layers += LayerHandler.get_layers_and_visibility_from_node(root, child)
            else:
                layer = child.layer()
                visibility = child.itemVisibilityChecked() and node.itemVisibilityChecked()
                if layer:
                    layers.append((layer, visibility))
        return layers
