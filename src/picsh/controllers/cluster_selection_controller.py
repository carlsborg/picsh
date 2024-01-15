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
import logging
import urwid
from picsh.controllers.base_controller import BaseController
from picsh.state_change_notifier import StateChangeNotifier
from picsh.views.cluster_selection_view import ClusterSelectionView
from picsh.models.root_model import RootModel
from picsh.cluster_spec import ClusterSpec
from picsh.views.view_names import ViewNames


class ClusterSelectionController(BaseController):
    def __init__(
        self,
        view: ClusterSelectionView,
        model: RootModel,
        state_change_notifier: StateChangeNotifier,
    ):
        super().__init__()
        self.view: ClusterSelectionView = view
        self._model: RootModel = model
        self._state_change_notifier: StateChangeNotifier = state_change_notifier
        self.view.set_cluster_specs(model.cluster_spec_paths)
        urwid.connect_signal(self.view.listbox_content, "modified", self.on_modified)

    def on_modified(self):
        self.view.show_cluster_spec(self._model.cluster_spec_paths)

    def handle_input_filter(self, keys, raw_input):
        new_view = None
        if "enter" in keys:
            nodeidx = self.view.get_selected_spec_idx()
            cluster_spec_path = self._model.cluster_spec_paths[nodeidx]
            cluster_spec = ClusterSpec(cluster_spec_path)
            self._state_change_notifier.notify({"nodes": cluster_spec.nodes})
            keys = []
            new_view = ViewNames.NODE_PANEL_VIEW
        elif "ctrl c" in keys:
            new_view = ViewNames.EXIT_SCREEN
            keys = []
        return keys, new_view
