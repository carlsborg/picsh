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


import os 
import asyncio
import urwid
import concurrent.futures
from collections import defaultdict
from picsh.views.cluster_shell_view import ClusterShellView
from picsh.models.cluster_shell_model import ClusterShellModel
from picsh.command_engine import CommandEngine
import readline


class _TerminalSubProcess:

    def __init__(self):
        self._data_fd = None
        self._control_fd = None
        self.done = False

    def set_pipe(self, data_fd, control_fd):
        self._data_fd = data_fd
        self._control_fd = control_fd

    def run_input_loop(self):
        inp = ""
        while not self.done:
            try:
                inp = input("cluster-shell$ ")
                if inp.strip():
                    os.write(self._data_fd, inp.encode('utf-8'))
            except Exception as ex:
                os.write(self._data_fd, str(ex).encode('utf-8'))
            except KeyboardInterrupt as ex:
                print("Esc then Ctrl c to exit picsh")
        #os.write(self._control_fd, "done")


class ClusterShellController:
    def __init__(self, view: ClusterShellView, model: ClusterShellModel):
        # self._write_fd = self._loop.watch_pipe(self._on_msg)
        self._proc = None
        self._view = view
        self._model = model
        for node in self._model.nodes:
            node.register_notify(self.on_command_output)
        self._command_queue = asyncio.Queue(-1)
        self._command_engine = CommandEngine(self._model.nodes, self.on_command_output, self._command_queue)
        self._terminal_proc = _TerminalSubProcess()
        self._view.register_terminal_input_cmd(self._terminal_proc.run_input_loop)

    def on_command_output(self):
        self._view.repaint_shell_output(self._model.nodes)

    def refresh_nodes(self):
        for node in self._model.nodes:
            node.register_notify(self.on_command_output)

    def set_loop(self, mainloop, aioloop):
        data_fd = mainloop.watch_pipe(self.on_data_pipe_data)
        control_fd = mainloop.watch_pipe(self.on_control_pipe_data)
        self._terminal_proc.set_pipe(data_fd, control_fd)
        aioloop.create_task(self._command_engine.run_command_loop())

    def on_data_pipe_data(self, s_cmdline):
        s_cmdline = s_cmdline.decode("utf-8")
        self._model.reset_buffers()
        self._command_queue.put_nowait(s_cmdline)

    def on_control_pipe_data(self, data):
        raise urwid.ExitMainLoop()

    def handle_input(self, key):
        return key

    def quit(self):
        if self._view.term.pid:
            self._view.term.terminate()

