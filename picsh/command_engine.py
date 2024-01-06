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


from typing import Optional
import asyncio, asyncssh
from functools import partial
from picsh.node import Node


class InteractiveClientSession(asyncssh.SSHClientSession):
    login_complete_guid = "B79D8677-F58A-4E09-B917-855A6619A951"

    def __init__(self, node: Node, notify_func):
        self._node = node
        self._login_guid_found = False
        self._notify_func = notify_func

    def data_received(self, data: str, datatype: asyncssh.DataType) -> None:
        self._node.recv_buf += data
        # if not self._login_guid_found:
        #     # surpress login banner.
        #     # Note: RFC-4254 reccomends the use of magic cookeis to surpress spurious
        #     # output when starting a subsystem via the shell "to distinguish it from
        #     # arbitrary output generated by shell initialization scripts, etc. This spurious
        #     # output from the shell may be filtered out either at the server or at the client"
        #     pos1 = self._node.recv_buf.find(InteractiveClientSession.login_complete_guid)
        #     if pos1 != -1:
        #         self._login_guid_found = True
        #         guid_len = len(InteractiveClientSession.login_complete_guid)
        #         self._node.recv_buf = self._node.recv_buf[pos1 + guid_len + 1:]
        if self._node.recv_buf:
            self._notify_func()

    def connection_lost(self, exc: Optional[Exception]) -> None:
        err_str = "\npicsh: Connection lost. "
        if exc:
            err_str += "SSH session error: " + str(exc)
        self._node.recv_buf += err_str
        self._notify_func()


class CommandEngine:
    def __init__(self, nodes, notify_func, command_queue, loop=None):
        self._nodes = nodes
        self._notify_func = notify_func
        self._command_queue = command_queue
        self.done = False
        self._connections = {}
        self._sessions = {}
        self._using = []
        self._loop = loop

    def get_node_selection(self):
        return self._using

    async def _run_cmd_on_nodes(self, cmd, nodes):
        loop = self._loop or asyncio.get_event_loop()
        tasks = []
        for node in nodes:
            t = loop.create_task(node.run_cmd(cmd))
            tasks.append(t)

        for task in tasks:
            await task

    async def run_command_loop(self):
        while not self.done:
            cmd: str = await self._command_queue.get()
            try:
                if cmd.strip():
                    if cmd == "@*" or cmd == "@":
                        self._using = []
                        for node in self._nodes:
                            node.hide = False
                        self._notify_func()
                    elif cmd.startswith("@"):
                        target_nodes, cmd = self.target_nodes_from_at_str(cmd)
                        if not cmd.strip():
                            self._using = target_nodes
                            for node in self._nodes:
                                if node not in self._using:
                                    node.hide = True
                            self._notify_func()
                        else:
                            await self._run_cmd_on_nodes(cmd, target_nodes)
                    else:
                        target_nodes = self._using or self._nodes
                        await self._run_cmd_on_nodes(cmd, target_nodes)
            except Exception as ex:
                # TODO: send on control channel
                print("Oops. Error: " + str(ex))

    def target_nodes_from_at_str(self, cmd):
        parts = cmd.split()
        target_node_str = parts[0][1:]
        targets = target_node_str.split(",")
        target_idxs = [int(t.strip()) for t in targets]
        target_nodes = []
        for node in self._nodes:
            if node.idx in target_idxs:
                target_nodes.append(node)
        cmd = cmd[len(parts[0]) :]
        return target_nodes, cmd

    async def ensure_session(self, node):
        node_id = node.idx
        conn = self._connections.get(node_id)
        if not conn:
            conn = await self._make_connection(node)
            self._connections[node_id] = conn
        session_tuple = self._sessions.get(node_id)
        if not session_tuple:
            ssh_client_factory = partial(
                InteractiveClientSession, node, self._notify_func
            )
            session_tuple = await conn.create_session(ssh_client_factory)
            self._sessions[node_id] = session_tuple
        chan, sess = session_tuple
        return chan, sess

    async def _cmd(self, node, scmd: str):
        chan, sess = await self.ensure_session(node)
        chan.write(scmd + "\n")

    async def _make_connection(self, node: Node):
        conn, client = await asyncssh.create_connection(
            client_factory=None,
            host=node.ip_addr,
            username=node.login_user,
            known_hosts=None,
            options=asyncssh.SSHClientConnectionOptions(
                client_keys=node.ssh_key_path, username=node.login_user
            ),
        )
        return conn
