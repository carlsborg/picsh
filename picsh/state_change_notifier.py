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


from typing import Mapping, Callable


class StateChangeNotifier:
    def __init__(self, state_change_listener: Callable):
        self._state_change_listener: Callable = state_change_listener

    def notify(self, state_update: Mapping):
        self._state_change_listener(state_update)
