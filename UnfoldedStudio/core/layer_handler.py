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
from typing import List

from qgis.core import QgsProject, QgsLayerTree, QgsLayerTreeNode, QgsMapLayer, QgsVectorLayer

from ..qgis_plugin_tools.tools.exceptions import QgsPluginNotImplementedException
from ..qgis_plugin_tools.tools.i18n import tr


class LayerHandler:
    basemap_group = tr('Unfolded Basemaps')

    @staticmethod
    def add_unfolded_basemaps():
        """ Add unfolded basemaps to the project """
        raise QgsPluginNotImplementedException()

    @staticmethod
    def get_all_visible_vector_layers():
        """ Get all vector layers in correct order """
        # noinspection PyArgumentList
        root: QgsLayerTree = QgsProject.instance().layerTreeRoot()
        layers = LayerHandler.get_layers_from_node(root, root)
        return list(filter(lambda layer: isinstance(layer, QgsVectorLayer), layers))

    @staticmethod
    def get_layers_from_node(root: QgsLayerTree, node: QgsLayerTreeNode) -> List[QgsMapLayer]:
        layers = []
        for child in node.children():
            if root.isGroup(child):
                # noinspection PyTypeChecker
                layers += LayerHandler.get_layers_from_node(root, child)
            else:
                layer = child.layer()
                if layer:
                    layers.append(layer)
        return layers
