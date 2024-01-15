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


from typing import Callable, List
import urwid
from picsh.widgets.selectable_row import SelectableRow
from picsh.node import Node
from picsh.widgets.listbox_with_mouse_events import ListBoxWithMouseEvents
import os


class ClusterSelectionView:
    def __init__(self, state_change_notifier: Callable):
        self._state_change_notifier = state_change_notifier
        footer_text = "cluster specs dir /home/cborg/.picsh"
        self.column_headers = urwid.AttrMap(
            urwid.Columns(
                [
                    ("fixed", 80, urwid.Text("cluster yaml spec", align="left")),
                    ("fixed", 6, urwid.Text("", align="left")),
                ]
            ),
            "column_headers",
        )
        self.listbox_content = urwid.SimpleFocusListWalker([self.column_headers])
        listbox = urwid.ListBox(self.listbox_content)
        listbox = urwid.AttrWrap(listbox, "body")
        self._output_textbox = urwid.Text("This is some text. " * 200)
        textbox = self._output_textbox

        self._footer = urwid.Text(footer_text)
        header = urwid.AttrMap(urwid.Text("picsh >> select cluster"), "header_style")
        self._cols = urwid.Columns(
            [
                ("fixed", 46, listbox),
                (
                    "weight",
                    75,
                    ListBoxWithMouseEvents(urwid.SimpleFocusListWalker([textbox])),
                ),
            ]
        )
        self._frame = urwid.Frame(
            self._cols,
            header=header,
            footer=urwid.AttrMap(self._footer, "footer_style"),
        )
        self._focus = "nodes"

    def set_cluster_specs(self, cluster_spec_paths: List[str]):
        listbox_content = [self.column_headers]
        for idx, cluster_spec_path in enumerate(cluster_spec_paths):
            base_name = os.path.basename(cluster_spec_path)
            listbox_content.append(SelectableRow((base_name, ""), idx))
        self.listbox_content[:] = urwid.SimpleFocusListWalker(listbox_content)

    def show_cluster_spec(self, cluster_spec_paths: List[str]):
        spec_idx = self.get_selected_spec_idx()
        with open(cluster_spec_paths[spec_idx], "rt") as fh:
            buf = fh.read()
            self._output_textbox.set_text(buf)

    def outer_widget(self):
        return self._frame

    def log(self, msg):
        self._footer.set_text(msg)

    def toggle_focus(self):
        if self._focus == "specs":
            self._cols.set_focus(1)
            self._focus == "defn"
        else:
            self._cols.set_focus(0)
            self._focus == "specs"

    def get_selected_spec_idx(self):
        return self.listbox_content.focus - 1
