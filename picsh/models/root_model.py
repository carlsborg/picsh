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


from typing import Mapping, Dict, Any

# top level state shared with all child views
# child views call notifier to modify this state 

class RootModel:
    def __init__(self):
        self.state: Dict[Any, Any] = {}

    def set_state(self, key: Any, value: Any):
        self.state[key] = value

    def get_state(self, key):
        return self.state[key]

    def state_change_listener(self, update_dict: Mapping):
        for key in update_dict:
            state_var = self.state[key]
            if isinstance(state_var, dict):
                state_var.update(update_dict[key])
            elif isinstance(state_var, list):
                old_val = self.state[key]
                old_val[:] = update_dict[key]
            else:
                self.state[key] = update_dict[key]

