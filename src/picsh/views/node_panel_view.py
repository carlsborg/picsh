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

from picsh.node import Node
from picsh.widgets.selectable_row import SelectableRow


class NodePanelView:
    def __init__(
        self,
        state_change_notifier: Callable,
        receive_buffer_view,
        cluster_shell_view,
        single_shell_view,
    ):
        self._state_change_notifier = state_change_notifier
        self._receive_buffer_view = receive_buffer_view
        self._cluster_shell_view = cluster_shell_view
        self._single_shell_view = single_shell_view

        self.active_right_pane = self._cluster_shell_view

        self.column_headers = urwid.AttrMap(
            urwid.Columns(
                [
                    ("fixed", 40, urwid.Text("    IP", align="left")),
                    ("fixed", 6, urwid.Text("bytes", align="left")),
                ]
            ),
            "column_headers",
        )
        self.listbox_content = urwid.SimpleFocusListWalker([self.column_headers])
        self._left_panel_listbox = urwid.AttrWrap(
            urwid.ListBox(self.listbox_content), "node_list"
        )

        self._header_text = urwid.Text(self.active_right_pane.header_nav_text())
        header = urwid.AttrMap(self._header_text, "header_style")

        self._output_textbox = urwid.Text("(no right panel rendered)")
        textbox = urwid.Filler(self._output_textbox, valign="top")
        right_panel = urwid.AttrMap(textbox, "node_text")

        self._footer = urwid.Text("")

        self._cols = urwid.Columns(
            [
                ("fixed", 47, urwid.LineBox(self._left_panel_listbox)),
                ("weight", 75, right_panel),
            ]
        )
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
        left_panel = (
            urwid.LineBox(
                self._left_panel_listbox, lline="", rline="", bline="", tline=""
            ),
            urwid.Columns.options("given", 47, True),
        )
        right_panel = (
            self.active_right_pane.outer_widget(),
            urwid.Columns.options("weight", 75, True),
        )
        self._frame.body.contents = [left_panel, right_panel]
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
        return self.listbox_content.focus - 1

    def set_focus(self, on_right_panel: bool):
        self._cols.set_focus(1 if on_right_panel else 0)

    def set_header_nav_text(self, text: str):
        self._header_text.set_text(text)

    def set_footer_text(self, text: str):
        self._footer.set_text(text)
