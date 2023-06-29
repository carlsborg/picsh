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

class NodeController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.view.set_noderows(model.nodes)
        urwid.connect_signal(self.view.listbox_content, "modified", self.on_modified)

    def on_modified(self):
        self.view.show_recv_buffer(self.model.nodes)
        pass

    def handle_input(self, keys):
        return keys

    def refresh_nodes(self):
        self.view.set_noderows(self.model.nodes)

