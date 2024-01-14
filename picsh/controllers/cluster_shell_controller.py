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
import os
import asyncio
import urwid
import concurrent.futures
from collections import defaultdict
from picsh.views.cluster_shell_view import ClusterShellView
from picsh.views.view_names import ViewNames
from picsh.models.root_model import RootModel
from picsh.command_engine import CommandEngine
from picsh.controllers.base_controller import BaseController
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
                inp = input("$ ")
                if inp.strip():
                    os.write(self._data_fd, inp.encode("utf-8"))
                    logging.info(f"cmd={inp}")
            except Exception as ex:
                os.write(self._data_fd, str(ex).encode("utf-8"))
            except KeyboardInterrupt as ex:
                print("Esc then Ctrl c to exit picsh")
        # os.write(self._control_fd, "done")


class ClusterShellController(BaseController):
    def __init__(self, view: ClusterShellView, root_model: RootModel):
        super().__init__()
        self._proc = None
        self.view: ClusterShellView = view
        self._model: RootModel = root_model
        for node in self._model.nodes:
            node.register_notify(self.on_command_output)
        self._command_queue = asyncio.Queue(-1)
        self._command_engine = CommandEngine(
            self._model.nodes, self.on_command_output, self._command_queue
        )
        self._terminal_proc = _TerminalSubProcess()
        self._activated = False

    def on_command_output(self):
        logging.info("got command output")
        self._repaint_notifier()

    def repaint(self):
        logging.info("repainting shell output")
        self.view.repaint_shell_output(self._model.nodes)

    def activate(self, **kwargs):
        if not self._activated:
            self.make_pipes(self._urwid_loop, self._aio_event_loop)
            self.start_command_loop(self._aio_event_loop)
            for node in self._model.nodes:
                node.register_notify(self.on_command_output)
            self.view.register_terminal_input_cmd(self._terminal_proc.run_input_loop)
            self.view.initialize_input_terminal(self._urwid_loop)
            self._activated = True
        self.view.set_initial_focus()

    def make_pipes(self, mainloop, aioloop):
        data_fd = mainloop.watch_pipe(self.on_data_pipe_data)
        control_fd = mainloop.watch_pipe(self.on_control_pipe_data)
        self._terminal_proc.set_pipe(data_fd, control_fd)

    def start_command_loop(self, aioloop):
        aioloop.create_task(self._command_engine.run_command_loop())

    def on_data_pipe_data(self, s_cmdline):
        s_cmdline = s_cmdline.decode("utf-8")
        self._reset_buffers()
        self._command_queue.put_nowait(s_cmdline)

    def _reset_buffers(self):
        for node in self._model.nodes:
            node.recv_buf = ""

    def on_control_pipe_data(self, data):
        raise urwid.ExitMainLoop()

    def quit(self):
        if self.view.term and self.view.term.pid:
            self.view.term.terminate()

    def handle_input_filter(self, keys, raw_input):
        new_view = None
        if "ctrl a" in keys:
            keys = []
            new_view = ViewNames.BUFFER_VIEW
        return keys, new_view

    def want_focus(self):
        return True
