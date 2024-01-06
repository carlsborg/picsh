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


class SelectableRow(urwid.WidgetWrap):
    def __init__(self, contents, idx, on_select=None):
        self.contents = contents
        self.idx = idx
        self.on_select = on_select
        self._columns = urwid.Columns(
            [
                ("fixed", 40, urwid.Text(contents[0], align="left")),
                ("fixed", 6, urwid.Text(" " + contents[1], align="center")),
            ]
        )
        self._focusable_columns = urwid.AttrMap(self._columns, "", "reveal_focus")
        super(SelectableRow, self).__init__(self._focusable_columns)

    def selectable(self):
        return True

    def keypress(self, size, key):
        if self.on_select and key in ("enter",):
            self.on_select(self)
        return key

    def __repr__(self):
        return "%s(contents=%r)" % (self.__class__.__name__, self.contents)
