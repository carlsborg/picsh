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
import yaml
from picsh.exceptions.picsh_exception import PicshException
from picsh.node import Node


class ClusterSpec:
    def __init__(self, path_to_yaml: str):
        if not os.path.exists(path_to_yaml):
            raise PicshException(
                f"Cluster spec [{path_to_yaml}] yaml file does not exist."
            )
        with open(path_to_yaml, "r") as fh:
            self.cluster_spec = yaml.safe_load(fh.read())
        self.nodes = self._nodes_from_cluster_spec(self.cluster_spec)
        self.name = "(missing)"

    def _nodes_from_cluster_spec(self, cluster):
        # globals
        hydrated_nodes = []
        login_user = cluster.get("login_user")
        key_path = cluster.get("ssh_key_path")
        self.name = cluster.get("cluster_name")
        for idx, node in enumerate(cluster.get("nodes")):
            n = Node()
            n.ip_addr = node["ip"]
            n.login_user = node.get("login_user") or login_user
            n.ssh_key_path = node.get("ssh_key_path") or key_path
            n.idx = idx
            hydrated_nodes.append(n)
        return hydrated_nodes
