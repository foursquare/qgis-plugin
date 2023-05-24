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

from typing import Callable, Optional
import requests

from PyQt5.QtCore import QTranslator, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QWidget
from qgis.gui import QgisInterface

from .qgis_plugin_tools.tools.custom_logging import setup_logger, setup_task_logger, teardown_logger, \
    use_custom_msg_bar_in_logger
from .qgis_plugin_tools.tools.i18n import setup_translation, tr
from .qgis_plugin_tools.tools.resources import plugin_name, resources_path
from .ui.dialog import Dialog

# There's no easy way to distribute a QGIS plugin with extra dependencies, and
# one way is to make sure that pip is installed and then install the required deps.
# see: https://gis.stackexchange.com/questions/196002/development-of-a-plugin-which-depends-on-an-external-python-library
# prep
try:
    import pip
except:
    r = requests.get('https://bootstrap.pypa.io/get-pip.py',
                     allow_redirects=False)
    exec(r.content)
    import pip
    # just in case the included version is old
    pip.main(['install', '--upgrade', 'pip'])
try:
    import sentry_sdk
except:
    pip.main(['install', 'sentry_sdk==1.24.0'])
    import sentry_sdk
# prep end

class Plugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):

        self.iface = iface

        setup_logger(plugin_name(), iface)
        setup_task_logger(plugin_name())

        # initialize locale
        locale, file_path = setup_translation()
        if file_path:
            self.translator = QTranslator()
            self.translator.load(file_path)
            # noinspection PyCallByClass
            QCoreApplication.installTranslator(self.translator)
        else:
            pass

        self.actions = []
        self.menu = tr(plugin_name())

        sentry_sdk.init(
            dsn="https://27e762d598b8418bb41980c2acc16e4c@o305787.ingest.sentry.io/5417824",
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0,
        )

        division_by_zero = 1 / 0

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: Callable,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: Optional[str] = None,
        whats_this: Optional[str] = None,
        parent: Optional[QWidget] = None) -> QAction:
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.

        :param text: Text that should be shown in menu items for this action.

        :param callback: Function to be called when the action is triggered.

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.

        :param parent: Parent widget for the new action. Defaults None.

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        # noinspection PyUnresolvedReferences
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.add_action(
            resources_path('icons', 'icon.svg'),
            text=tr('Export to Web'),
            callback=self.run,
            parent=self.iface.mainWindow(),
            add_to_toolbar=True
        )

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        pass

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.menu,
                action)
            self.iface.removeToolBarIcon(action)
        teardown_logger(plugin_name())

    def run(self):
        """Run method that performs all the real work"""
        dialog = Dialog()
        use_custom_msg_bar_in_logger(plugin_name(), dialog.message_bar)
        dialog.exec()
