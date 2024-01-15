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
from picsh.models.root_model import RootModel
from picsh.views.single_shell_view import SingleShellView
from picsh.views.view_names import ViewNames
from picsh.controllers.base_controller import BaseController


class SingleShellController(BaseController):
    def __init__(self, view: SingleShellView, model: RootModel):
        super().__init__()
        self.view: SingleShellView = view
        self._model: RootModel = model

    def handle_input(self, key):
        return key

    def handle_input_filter(self, keys, raw_input):
        new_view = None
        if "ctrl s" in keys:
            keys = []
            new_view = ViewNames.CLUSTERSHELL_VIEW
        elif "ctrl a" in keys:
            keys = []
            new_view = ViewNames.BUFFER_VIEW
        return keys, new_view

    def activate(self, node_idx):
        node = next(filter(lambda x: x.idx == node_idx, self._model.nodes), None)
        self.view.switch_to_terminal(node, self._urwid_loop)
        # urwid.connect_signal(
        #     self.view._terminals[node.idx].terminal_widget,
        #     "closed",
        #     functools.partial(self._switch_to, node),
        # )

    def want_focus(self):
        return True
