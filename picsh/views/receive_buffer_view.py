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


from typing import Callable, List
import urwid
from picsh.widgets.selectable_row import SelectableRow
from picsh.node import Node
from picsh.widgets.listbox_with_mouse_events import ListBoxWithMouseEvents


class ReceiveBufferView:
    def __init__(self, state_change_notifier: Callable):
        self._state_change_notifier = state_change_notifier
        self._output_textbox = urwid.Text("  ")
        textbox = self._output_textbox
        self._outer_widget = ListBoxWithMouseEvents(
            urwid.SimpleFocusListWalker([textbox])
        )
        self._focus = "nodes"

    def on_node_list_modified(self, nodes: List[Node], node_idx):
        self._output_textbox.set_text(nodes[node_idx].recv_buf)

    def outer_widget(self):
        return self._outer_widget

    def header_nav_text(self):
        return "picsh >> response buffers"

    def footer_text(self):
        return "Ctrl s => cluster shell | Enter => single node ssh | Ctrl q => quit"
