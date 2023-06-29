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


class NodeView:
    def __init__(self, state_change_notifier:Callable):
        self._state_change_notifier = state_change_notifier
        footer_text = "/ => cluster shell | Enter => exec single ssh session | Up/Down => show recv buf | Ctrl-C => Exit picsh"
        self.column_headers = urwid.AttrMap(
            urwid.Columns(
                [
                    ("fixed", 40, urwid.Text("IP", align="left")),
                    ("fixed", 6, urwid.Text("rbytes", align="left"))
                ]
            ),
            "column_headers",
        )
        self.listbox_content = urwid.SimpleFocusListWalker([self.column_headers])
        listbox = urwid.ListBox(self.listbox_content)
        listbox = urwid.AttrWrap(listbox, "body")
        self._output_textbox = urwid.Text("  ")
        #textbox = urwid.Filler(self._output_textbox, valign="top")
        #textbox = urwid.AttrMap(textbox, "node_text")
        textbox = self._output_textbox

        self._footer = urwid.Text(footer_text)
        header = urwid.AttrMap(
            urwid.Text("picsh >> node view"), "header_style"
        )
        self._cols = urwid.Columns([("fixed", 46, listbox), ("weight", 75, ListBoxWithMouseEvents(urwid.SimpleFocusListWalker([textbox])))])
        self._frame = urwid.Frame(
            self._cols,
            header=header,
            footer=urwid.AttrMap(self._footer, "footer_style"),
        )
        self._focus = "nodes"


    def set_noderows(self, nodes: List[Node]):
        listbox_content = [self.column_headers]
        for idx, node in enumerate(nodes):
            node_str = f"{str(node.idx).rjust(2)}] {node.get_ip()}"
            coldata = (node_str, str(len(node.recv_buf)))
            listbox_content.append(SelectableRow(coldata, node.idx))
        self.listbox_content[:] = urwid.SimpleFocusListWalker(listbox_content)

    def show_recv_buffer(self, nodes: List[Node]):
        node_idx = self.get_selected_node_idx()
        self._output_textbox.set_text(nodes[node_idx].recv_buf)

    def outer_widget(self):
        return self._frame

    def log(self, msg):
        self._footer.set_text(msg)

    def toggle_focus(self):
        if self._focus == "nodes":
            self._cols.set_focus(1)
            self._focus == "text"
        else:
            self._cols.set_focus(0)
            self._focus == "nodes"

    def get_selected_node_idx(self):
        return self.listbox_content.focus -1 
