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

from picsh.node import SSHTargetNode
from typing import List, Mapping, Dict, Any, MutableMapping

# store all application state in one place a la Flux
# https://youtu.be/nYkdrAPrdcw?t=635
# all state change occurs via a state_change_notifier


class RootModel:
    def __init__(self, nodes=None, cluster_spec_paths=None, node_selection_filter=""):
        self.nodes: List[SSHTargetNode] = nodes or []
        self.cluster_spec_paths: List[str] = cluster_spec_paths or []
        self.node_selection_filter: str = node_selection_filter

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in self.__dict__:
            raise Exception("root_model: use state change listener to modify")
        else:
            super().__setattr__(__name, __value)

    def state_change_listener(self, update_dict: Mapping):
        for key, val in update_dict.items():
            if key not in self.__dict__:
                raise Exception("root_model: bad state variable")
            state_var = self.__dict__.get(key)
            if isinstance(state_var, dict):
                state_var.update(val)
            elif isinstance(state_var, list):
                state_var[:] = val
            else:
                self.__dict__[key] = val
