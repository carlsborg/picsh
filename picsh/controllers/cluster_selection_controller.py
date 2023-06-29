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
from picsh.views.cluster_selection_view import ClusterSelectionView
from picsh.models.cluster_selection_model import ClusterSelectionModel


class ClusterSelectionController:
    def __init__(self, view: ClusterSelectionView, model: ClusterSelectionModel):
        self.view: ClusterSelectionView = view
        self.model: ClusterSelectionModel = model
        self.view.set_cluster_specs(model.cluster_spec_paths)
        urwid.connect_signal(self.view.listbox_content, "modified", self.on_modified)

    def on_modified(self):
        self.view.show_cluster_spec(self.model.cluster_spec_paths)

    def handle_input(self, keys):
        return keys

