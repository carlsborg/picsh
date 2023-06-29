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


from cmath import sin
from re import L
from typing import List, Callable
import os
import urwid
from picsh.widgets.selectable_row import SelectableRow
from picsh.node import Node


class _SingleShellTerminal:

    def __init__(self, node, loop):
        self._node = node
        self._loop = loop
        self.terminal_widget = urwid.Terminal(self._run_ssh_command, main_loop=loop, env=None, encoding="utf-8", escape_sequence="ctrl a")
        self.exited = False

    def _run_ssh_command(self):
        os.system(f"TERM=linux ssh -i {self._node.get_ssh_key_path()} {self._node.get_login_user()}@{self._node.get_ip()}")
        # self.terminal_widget.terminate()
        self.exited = True


class SingleShellView:

    def __init__(self, state_change_notifier:Callable):
        self._state_change_notifier = state_change_notifier
        self._terminals = {} # node_idx : 
        self._loop = None
        footer_text = "Ctrl A => return to node view"
        self.column_headers = urwid.AttrMap(
            urwid.Columns(
                [
                    ("fixed", 40, urwid.Text("IP", align="left")),
                    ("fixed", 6, urwid.Text("", align="left"))
                ]
            ),
            "column_headers",
        )
        self.listbox_content = urwid.SimpleFocusListWalker([self.column_headers])
        listbox = urwid.ListBox(self.listbox_content)
        self._left_column_listbox = urwid.AttrWrap(listbox, "body")
        self._footer = urwid.Text(footer_text)
        
        self._cols = urwid.Columns(
            [("fixed", 46, self._left_column_listbox), ("weight", 75, urwid.Filler(urwid.Text("")))]
        )
        self._frame = urwid.Frame(
            body=urwid.Filler(urwid.Text("")),
            header=self._get_header(""),
            footer=urwid.AttrMap(self._footer, "footer_style"),
            focus_part="body",
        )

    def _get_header(self, s_info):
        s_txt = "picsh >> single shell view"
        if s_info:
            s_txt += " [" + s_info + "]"
        return urwid.AttrMap(urwid.Text(s_txt), "header_style")

    def set_noderows(self, nodes: List[Node]):
        listbox_content = [self.column_headers]
        for idx, node in enumerate(nodes):
            node_str = f"{str(node.idx).rjust(2)}] {node.get_ip()}"
            coldata = (node_str, str(len(node.recv_buf)))
            listbox_content.append(SelectableRow(coldata, node.idx))
        self.listbox_content[:] = urwid.SimpleFocusListWalker(listbox_content)

    def set_loop(self, loop):
        self._loop = loop

    def outer_widget(self):
        return self._frame

    def log(self, msg):
        self._footer.set_text(msg)

    def switch_to_terminal(self, node):
        single_shell_term = self._terminals.get(node.idx)
        # if single_shell_term:
        #     self.log("shell.exited =" + str(single_shell_term.terminal_widget.terminated))
        if single_shell_term and single_shell_term.terminal_widget.terminated:
            del self._terminals[node.idx]
            single_shell_term = None

        if not single_shell_term:
            single_shell_term = _SingleShellTerminal(node, self._loop)
            self._terminals[node.idx] = single_shell_term
        self._frame.header = self._get_header(node.get_ip())
        self._frame.body = self._terminals[node.idx].terminal_widget
        return

