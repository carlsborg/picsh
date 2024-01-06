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


import urwid


class ListBoxWithMouseEvents(urwid.ListBox):
    def mouse_event(self, size, event, button, col, row, focus):
        if event == "mouse press":
            if button == 4:
                for _ in range(2):
                    self.keypress(size, "up")
                return True
            if button == 5:
                for _ in range(2):
                    self.keypress(size, "down")
                return True
        return super().mouse_event(size, event, button, col, row, focus)
