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
from typing import List, Callable
import os
import urwid
from picsh.node import Node


class _SingleShellTerminal:
    def __init__(self, node, loop):
        self._node = node
        self._loop = loop
        self.terminal_widget = urwid.Terminal(
            self._run_ssh_command,
            main_loop=loop,
            env=None,
            encoding="utf-8",
            escape_sequence="ctrl a",
        )
        self.exited = False

    def _run_ssh_command(self):
        key_opt = ""
        key_path = self._node.get_ssh_key_path()
        if key_path:
            key_opt = f"-i {self._node.get_ssh_key_path()}"
        ssh_cmd = f"TERM=linux ssh {key_opt} {self._node.get_login_user()}@{self._node.get_ip()}"
        logging.info(ssh_cmd)
        os.system(ssh_cmd)
        # self.terminal_widget.terminate()
        self.exited = True


class SingleShellView:
    def __init__(self, state_change_notifier: Callable):
        self._state_change_notifier = state_change_notifier
        self._terminals = {}  # node_idx : term
        self._outer_widget = urwid.Filler(urwid.Text(""))
        self._cur_node_ip = ""

    def outer_widget(self):
        return self._outer_widget

    def switch_to_terminal(self, node, urwid_loop):
        single_shell_term = self._terminals.get(node.idx)
        if single_shell_term and single_shell_term.terminal_widget.terminated:
            del self._terminals[node.idx]
            single_shell_term = None
        if not single_shell_term:
            single_shell_term = _SingleShellTerminal(node, urwid_loop)
            self._terminals[node.idx] = single_shell_term
        self._cur_node_ip = f"[{node.idx}] ({node.get_ip()})"
        self._outer_widget = self._terminals[node.idx].terminal_widget
        return

    def on_node_list_modified(self, nodes: List[Node], node_idx):
        pass

    def header_nav_text(self):
        return f"picsh >> ssh to node {self._cur_node_ip}"

    def footer_text(self):
        return "Ctrl a => response buffers | Ctrl s => cluster shell  | Ctrl q => quit"
