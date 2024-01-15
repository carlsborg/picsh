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
import logging
from picsh.controllers.base_controller import BaseController
from picsh.models.root_model import RootModel
from picsh.views.receive_buffer_view import ReceiveBufferView
from picsh.views.view_names import ViewNames


class ReceiveBufferController(BaseController):
    def __init__(self, view: ReceiveBufferView, model: RootModel):
        super().__init__()
        self.view: ReceiveBufferView = view
        self._model: RootModel = model

    def activate(self, node_idx):
        self.view.on_node_list_modified(self._model.nodes, node_idx)

    def handle_input_filter(self, keys, raw_input):
        new_view = None
        if "ctrl s" in keys:
            keys = []
            new_view = ViewNames.CLUSTERSHELL_VIEW
        elif "enter" in keys:
            new_view = ViewNames.SINGLESHELL_VIEW
            keys = []
        return keys, new_view

    def want_focus(self):
        return False
