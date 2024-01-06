# Copyright (c) Ran Dugal 2023
#
# This file is part of picsh
#
# Licensed under the GNU Affero General Public License v3, which is available at
# http://www.gnu.org/licenses/agpl-3.0.html
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero GPL for more details.
#

import asyncio
import urwid
from picsh.controllers.base_controller import BaseController
from picsh.controllers.cluster_selection_controller import ClusterSelectionController
from picsh.controllers.node_panel_controller import NodePanelController
from picsh.models.root_model import RootModel
from picsh.views.view_names import ViewNames


class RootController(BaseController):
    def __init__(
        self,
        root_model: RootModel,
        pallette,
        cluster_selection_controller: ClusterSelectionController,
        node_panel_controller: NodePanelController,
    ):
        self._root_model = root_model

        self._cluster_selection_controller = cluster_selection_controller
        self._node_panel_controller = node_panel_controller

        self._active_controller = self._cluster_selection_controller
        self._active_view = self._cluster_selection_controller.view

    def switch_to(self, controller):
        self._active_controller = controller
        self._active_view = controller.view
        self._active_controller.activate()
        self._urwid_loop.widget = self._active_view.outer_widget()

    def handle_input(self, key):
        return self._active_controller.handle_input(key)

    def _input_filter(self, keys, raw_input):
        new_keys, new_view = self._active_controller.handle_input_filter(
            keys, raw_input
        )
        if new_view == ViewNames.NODE_PANEL_VIEW:
            self.switch_to(self._node_panel_controller)
        elif new_view == ViewNames.EXIT_SCREEN:
            self._cluster_selection_controller.quit()
            self._node_panel_controller.quit()
            raise urwid.ExitMainLoop()
        return new_keys

    def run(self, pallette):
        try:
            aio_event_loop = asyncio.get_event_loop()
            self._urwid_loop = urwid.MainLoop(
                self._active_view.outer_widget(),
                palette=pallette,
                unhandled_input=self.handle_input,
                input_filter=self._input_filter,
                event_loop=urwid.AsyncioEventLoop(loop=aio_event_loop),
            )
            self._node_panel_controller.set_urwid_loop(self._urwid_loop)
            self._node_panel_controller.set_aio_event_loop(aio_event_loop)
            self._urwid_loop.run()
        except KeyboardInterrupt:
            pass
