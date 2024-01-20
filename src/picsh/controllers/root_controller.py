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
from picsh.state_change_notifier import StateChangeNotifier
from picsh.views.view_names import ViewNames
from picsh.cluster_spec import ObjClusterSpec


class RootController(BaseController):
    def __init__(
        self,
        pallette,
        root_model: RootModel,
        state_change_notifier: StateChangeNotifier,
        cluster_selection_controller: ClusterSelectionController,
        node_panel_controller: NodePanelController,
    ):
        self._root_model = root_model
        self._state_change_notifier = state_change_notifier
        self._cluster_selection_controller = cluster_selection_controller
        self._node_panel_controller = node_panel_controller

        initial_view = (
            self._cluster_selection_controller.view
            if self._show_cluster_selection()
            else self._node_panel_controller.view
        )
        aio_event_loop = asyncio.get_event_loop()
        self._urwid_loop = urwid.MainLoop(
            initial_view.outer_widget(),
            palette=pallette,
            unhandled_input=self.handle_input,
            input_filter=self._input_filter,
            event_loop=urwid.AsyncioEventLoop(loop=aio_event_loop),
        )
        self._node_panel_controller.set_urwid_loop(self._urwid_loop)
        self._node_panel_controller.set_aio_event_loop(aio_event_loop)

        if self._show_cluster_selection():
            self.switch_to(self._cluster_selection_controller)
        else:
            cluster_spec = ObjClusterSpec(root_model.cluster_spec)
            self._state_change_notifier.notify({"nodes": cluster_spec.nodes})
            self.switch_to(self._node_panel_controller)

    def _show_cluster_selection(self):
        return len(self._root_model.cluster_spec_paths) > 0

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

    def run(self):
        try:
            self._urwid_loop.run()
        except KeyboardInterrupt:
            pass
