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
from enum import Enum
import urwid
from picsh.models.root_model import RootModel
from picsh.cluster_spec import ClusterSpec
from picsh.views.node_view import NodeView
from picsh.controllers.node_controller import NodeController
from picsh.models.nodel_model import NodeModel
from picsh.views.cluster_shell_view import ClusterShellView
from picsh.controllers.cluster_shell_controller import ClusterShellController
from picsh.models.cluster_shell_model import ClusterShellModel
from picsh.views.single_shell_view import SingleShellView
from picsh.controllers.single_shell_controller import SingleShellController

from picsh.models.cluster_selection_model import ClusterSelectionModel
from picsh.views.cluster_selection_view import ClusterSelectionView
from picsh.controllers.cluster_selection_controller import ClusterSelectionController

from picsh.models.single_shell_model import SingleShellModel
from picsh.state_change_notifier import StateChangeNotifier
import copy 
import functools

class CurrentView(Enum):
    CLUSTER_SELECTION_VIEW = 0
    NODE_VIEW = 1
    CLUSTERSHELL_VIEW = 2
    SINGLESHELL_VIEW = 3

class RootController:
    def __init__(self, cluster_spec_paths):
        urwid.set_encoding("utf8")
        self.root_model = RootModel()
        self.state_change_notifier = StateChangeNotifier(self.root_model.state_change_listener)
        self.root_model.set_state("nodes", [])
        self.root_model.set_state("spec_paths", cluster_spec_paths)
        self.root_model.set_state("node_selection_filter", "")
        self.current_view = CurrentView.CLUSTER_SELECTION_VIEW

        self.node_view = NodeView(self.state_change_notifier)
        self.node_model = NodeModel(self.root_model.get_state("nodes"))
        self.node_controller = NodeController(self.node_view, self.node_model)

        self.cluster_shell_view = ClusterShellView(self.state_change_notifier)
        self.cluster_shell_model = ClusterShellModel(self.root_model.get_state("nodes"))
        self.cluster_shell_controller = ClusterShellController(
            self.cluster_shell_view, self.cluster_shell_model)

        self.single_shell_view = SingleShellView(self.state_change_notifier)
        self.single_shell_model = SingleShellModel(self.root_model.get_state("nodes"))
        self.single_shell_controller = SingleShellController(
            self.single_shell_view, self.single_shell_model
        )

        self.cluster_selection_view = ClusterSelectionView(self.state_change_notifier)
        self.cluster_selection_model = ClusterSelectionModel(cluster_spec_paths)
        self.cluster_selection_controller = ClusterSelectionController(self.cluster_selection_view, self.cluster_selection_model)

        palette = [
            ("separater", "white", "dark cyan"),
            ("body", "dark cyan", "black", "standout"),
            ("header_style", "dark cyan", "black"),
            ("footer", "black", "yellow"),
            ("footer_title", "white", "dark red"),
            ("footer_style", "black", "white"),
            ("reveal_focus", "black", "dark blue", "standout"),
            ("node_text", "light gray", "black"),
            ("column_headers", "white", "dark gray", "standout"),
            ("output_separater", "black", "dark gray", "standout"),
            ("cmdshell", "white", "black",  "standout")
        ]
        self._aio_event_loop = asyncio.get_event_loop()
        self._loop = urwid.MainLoop(
            self._get_active_view().outer_widget(),
            palette=palette,
            unhandled_input=self.handle_input,
            input_filter=self._input_filter,
            event_loop=urwid.AsyncioEventLoop(loop=self._aio_event_loop),
        )

        self.single_shell_view.set_loop(self._loop)
        self.cluster_shell_controller.set_loop(self._loop, self._aio_event_loop)
        self._prev_filter_keys = ""

    def _switch_to(self, node, *args, **argv):
        self._loop.widget = self.node_view.outer_widget()
        self.current_view = CurrentView.NODE_VIEW

    def handle_input(self, key):
        # delegate to the active child controller
        return self._get_active_controller().handle_input(key)

    def _input_filter(self, keys, raw_input):
        # switch between views or exit
        # self._get_active_view().log("input_filter:" + str(keys))
        if self.current_view == CurrentView.CLUSTER_SELECTION_VIEW:
            if "enter" in keys:
                nodeidx = self.cluster_selection_view.get_selected_spec_idx()
                cluster_spec_path = self.cluster_selection_model.cluster_spec_paths[nodeidx]
                cluster_spec = ClusterSpec(cluster_spec_path)
                nodes = self.root_model.get_state("nodes")
                nodes[:] = cluster_spec.nodes
                #self._get_active_view().log("node model:" + str([node for node in self.node_controller.model.nodes]))
                self.node_controller.refresh_nodes()
                self.cluster_shell_controller.refresh_nodes()
                self.current_view = CurrentView.NODE_VIEW
                # self.node_view.log( str(self.node_model.nodes) )
                self._loop.widget = self.node_view.outer_widget()
                keys = []
        elif self.current_view == CurrentView.NODE_VIEW:
            if "/" in keys:
                self._loop.widget = self.cluster_shell_view.outer_widget()
                self.current_view = CurrentView.CLUSTERSHELL_VIEW
                keys = []
            elif "enter" in keys:
                nodeidx = self.node_view.get_selected_node_idx()
                node = next(filter(lambda x: x.idx == nodeidx, self.node_model.nodes), None)
                self.single_shell_controller.ensure_shell(node)
                urwid.connect_signal(
                    self.single_shell_view._terminals[node.idx].terminal_widget,
                    "closed",
                    functools.partial(self._switch_to, node),
                )
                self.current_view = CurrentView.SINGLESHELL_VIEW
                self._loop.widget = self.single_shell_view.outer_widget()
                keys = []
                # Terminal handles its own input and uses message bus to inform when its closed
            elif "ctrl c" in keys:
                self.cluster_shell_controller.quit()
                self.single_shell_controller.quit()
                raise urwid.ExitMainLoop()
        elif self.current_view == CurrentView.CLUSTERSHELL_VIEW:
            if "esc" in keys:
                self.node_controller.refresh_nodes() # show new rec buf lens
                self._loop.widget = self.node_view.outer_widget()
                self.current_view = CurrentView.NODE_VIEW
        elif self.current_view == CurrentView.SINGLESHELL_VIEW:
            if "ctrl a" in keys:
                self._loop.widget = self.node_view.outer_widget()
                self.current_view = CurrentView.NODE_VIEW
                keys = []
        return keys

    def _get_active_view(self):
        if self.current_view == CurrentView.CLUSTER_SELECTION_VIEW:
            return self.cluster_selection_view
        elif self.current_view == CurrentView.NODE_VIEW:
            return self.node_view
        elif self.current_view == CurrentView.CLUSTERSHELL_VIEW:
            return self.cluster_shell_view
        elif self.current_view == CurrentView.SINGLESHELL_VIEW:
            return self.single_shell_view
        raise ValueError("Unknown current view")

    def _get_active_controller(self):
        if self.current_view == CurrentView.CLUSTER_SELECTION_VIEW:
            return self.cluster_selection_controller
        if self.current_view == CurrentView.NODE_VIEW:
            return self.node_controller
        elif self.current_view == CurrentView.CLUSTERSHELL_VIEW:
            return self.cluster_shell_controller
        elif self.current_view == CurrentView.SINGLESHELL_VIEW:
            return self.single_shell_controller
        raise ValueError("Unknown current view")

    def run(self):
        try:
            self._loop.run()
        except KeyboardInterrupt:
            pass

