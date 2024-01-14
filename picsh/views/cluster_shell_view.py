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
from picsh.widgets.listbox_with_mouse_events import ListBoxWithMouseEvents


class ClusterShellView:
    def __init__(self, state_change_notifier: Callable):
        self._state_change_notifier = state_change_notifier
        self._footer = urwid.Text("Esc => node view | Alt-C reconnect all")
        self._listbox_content = urwid.SimpleListWalker([])
        self._listbox = ListBoxWithMouseEvents(self._listbox_content)
        self._terminal_input_cmd = None
        self._outer_widget = urwid.Filler(urwid.Text(""))
        self._node_selection_filter = ""
        self.term = None

    def set_selection_filter(self, selection_filter):
        self._node_selection_filter = selection_filter

    def register_terminal_input_cmd(self, func):
        self._terminal_input_cmd = func

    def terminal_command(self):
        self._terminal_input_cmd()

    def initialize_input_terminal(self, urwid_loop):
        self.term = urwid.Terminal(
            self.terminal_command, encoding="utf-8", main_loop=urwid_loop, escape_sequence="ctrl a"
        )
        term_attr = urwid.AttrMap(self.term, "bottom")
        # urwid.connect_signal(self.term, 'closed', quit)
        self._outer_widget = urwid.Pile([
                    self._listbox,
                    ("fixed", 5,  urwid.LineBox(
                        term_attr,
                        title="cluster shell",
                        title_attr="reveal_focus",
                        title_align="left",
                        bline="",
                        lline="",
                        rline="",
                     ))
            ]
        )

    def repaint_shell_output(self, nodes: List[Node]):
        list_contents = []
        for node in nodes:
            if not node.hide:
                separater = f"[{str(node.idx)}] {node.ip_addr}==>"
                list_contents.append(
                    urwid.AttrMap(urwid.Text(separater), "output_separater")
                )
                list_contents.append(urwid.Text(node.recv_buf))
        self._listbox_content[:] = urwid.SimpleListWalker(list_contents)

    def outer_widget(self):
        return self._outer_widget

    def log(self, msg):
        self._footer.set_text(msg)

    def on_node_list_modified(self, nodes: List[Node], node_idx):
        pass

    def set_initial_focus(self):
        self._outer_widget.set_focus(1)

    def header_nav_text(self):
        return "picsh >> cluster shell"

    def footer_text(self):
        return "Ctrl a => response buffers | Ctrl q => quit"
 
