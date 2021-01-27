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
from typing import Dict

from PyQt5.QtWidgets import QDialog

from ..definitions.gui import Panels
from ..qgis_plugin_tools.tools.custom_logging import bar_msg
from ..qgis_plugin_tools.tools.exceptions import QgsPluginException, QgsPluginNotImplementedException
from ..qgis_plugin_tools.tools.i18n import tr
from ..qgis_plugin_tools.tools.resources import plugin_name

LOGGER = logging.getLogger(plugin_name())


def process(fn):
    """
    This decoration should be used when same effect as BasePanel.run is wanted for multiple methods
    """
    from functools import wraps

    @wraps(fn)
    def wrapper(self: BasePanel, *args, **kwargs):
        self._start_process()
        try:
            if args and args != (False,):
                if len(kwargs):
                    fn(self, *args, **kwargs)
                else:
                    fn(self, *args)
            elif len(kwargs):
                fn(self, **kwargs)
            else:
                fn(self)
        except QgsPluginException as e:
            LOGGER.exception(str(e), extra=e.bar_msg)
        except Exception as e:
            LOGGER.exception(tr('Unhandled exception occurred'), extra=bar_msg(e))
        finally:
            self._end_process()

    return wrapper


class BasePanel:
    """
    Base panel for dialog. Adapted from https://github.com/GispoCoding/qaava-qgis-plugin and
    https://github.com/3liz/QuickOSM. Both projects are licenced under GPL version 2.
    """

    def __init__(self, dialog: QDialog):
        self._panel = None
        self._dialog = dialog
        self.elem_map: Dict[int, bool] = {}

    @property
    def panel(self) -> Panels:
        if self._panel:
            return self._panel
        else:
            raise NotImplemented

    @panel.setter
    def panel(self, panel: Panels):
        self._panel = panel

    @property
    def dlg(self) -> QDialog:
        """Return the dialog.
        """
        return self._dialog

    def setup_panel(self):
        """Setup the UI for the panel."""
        raise QgsPluginNotImplementedException()

    def teardown_panel(self):
        """Teardown for the panels"""

    def on_update_map_layers(self):
        """Occurs when map layers are updated"""

    def is_active(self):
        """ Is the panel currently active (selected)"""
        curr_panel = list(self.dlg.panels.keys())[self.dlg.menu_widget.currentRow()]
        return curr_panel == self.panel

    def run(self, method='_run'):
        if not method:
            method = '_run'
        self._start_process()
        try:
            # use dispatch pattern to invoke method with same name
            if not hasattr(self, method):
                raise QgsPluginException(f'Class does not have a method {method}')
            getattr(self, method)()
        except QgsPluginException as e:
            LOGGER.exception(str(e), extra=e.bar_msg)
        except Exception as e:
            LOGGER.exception(tr('Unhandled exception occurred'), extra=bar_msg(e))
        finally:
            self._end_process()

    def _run(self):
        raise QgsPluginNotImplementedException()

    def _start_process(self):
        """Make some stuff before launching the process."""
        self.dlg.is_running = True
        for i, elem in enumerate(self.dlg.responsive_elements[self.panel]):
            self.elem_map[i] = elem.isEnabled()
            elem.setEnabled(False)

    def _end_process(self):
        """Make some stuff after the process."""
        self.dlg.is_running = False
        for i, elem in enumerate(self.dlg.responsive_elements[self.panel]):
            # Some process could change the status to True
            is_enabled = elem.isEnabled()
            if not is_enabled:
                elem.setEnabled(self.elem_map.get(i, True))
