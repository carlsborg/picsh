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


import urwid

from picsh.controllers.cluster_selection_controller import ClusterSelectionController
from picsh.controllers.cluster_shell_controller import ClusterShellController
from picsh.controllers.node_panel_controller import NodePanelController
from picsh.controllers.receive_buffer_controller import ReceiveBufferController
from picsh.controllers.root_controller import RootController
from picsh.controllers.single_shell_controller import SingleShellController
from picsh.models.root_model import RootModel
from picsh.state_change_notifier import StateChangeNotifier
from picsh.views.cluster_selection_view import ClusterSelectionView
from picsh.views.cluster_shell_view import ClusterShellView
from picsh.views.node_panel_view import NodePanelView
from picsh.views.receive_buffer_view import ReceiveBufferView
from picsh.views.single_shell_view import SingleShellView


class App:
    def __init__(self, cluster_specs):
        self._cluster_specs = cluster_specs

    def run(self):
        urwid.set_encoding("utf8")

        palette = [
            ("separater", "white", "dark cyan"),
            ("body", "dark cyan", "black", "standout"),
            ("node_list", "dark gray", "black", "standout"),
            ("header_style", "dark cyan", "black"),
            ("footer", "black", "yellow"),
            ("footer_title", "white", "dark red"),
            ("footer_style", "black", "white"),
            ("reveal_focus", "black", "dark cyan", "standout"),
            ("node_text", "light gray", "black"),
            ("column_headers", "dark cyan", "black", "standout"),
            ("output_separater", "black", "dark gray", "standout"),
            ("cmdshell", "white", "black", "standout"),
        ]

        root_model = RootModel(cluster_spec_paths=self._cluster_specs)
        state_change_notifier = StateChangeNotifier(root_model.state_change_listener)

        root_controller = self._controller_hierarchy(state_change_notifier, root_model)
        root_controller.run(palette)

    def _controller_hierarchy(self, state_change_notifier, root_model):
        # RootController
        #   -> ClusterSelectionController
        #   -> NodePanelController
        #          -> ReceiveBufferController
        #          -> ClusterShellController
        #          -> SingleShellController

        cluster_selection_view = ClusterSelectionView(state_change_notifier)
        cluster_selection_controller = ClusterSelectionController(
            cluster_selection_view, root_model, state_change_notifier
        )

        receive_buffer_view = ReceiveBufferView(state_change_notifier)
        receive_buffer_controller = ReceiveBufferController(
            receive_buffer_view, root_model
        )

        cluster_shell_view = ClusterShellView(state_change_notifier)
        cluster_shell_controller = ClusterShellController(
            cluster_shell_view, root_model
        )

        single_shell_view = SingleShellView(state_change_notifier)
        single_shell_controller = SingleShellController(single_shell_view, root_model)

        node_panel_view = NodePanelView(
            state_change_notifier,
            receive_buffer_view,
            cluster_shell_view,
            single_shell_view,
        )
        node_panel_controller = NodePanelController(
            node_panel_view,
            root_model,
            cluster_shell_controller,
            single_shell_controller,
            receive_buffer_controller,
        )

        root_controller = RootController(
            state_change_notifier,
            root_model,
            cluster_selection_controller,
            node_panel_controller,
        )

        return root_controller
