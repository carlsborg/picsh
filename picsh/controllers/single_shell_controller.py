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


class SingleShellController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.view.set_noderows(model.nodes)

    def handle_input(self, key):
        return key

    def quit(self):
        pass

    def ensure_shell(self, node):
        self.view.switch_to_terminal(node)

