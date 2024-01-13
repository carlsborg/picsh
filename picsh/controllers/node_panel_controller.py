import logging
import urwid
from picsh.controllers.cluster_selection_controller import ClusterSelectionController
from picsh.controllers.receive_buffer_controller import ReceiveBufferController
from picsh.controllers.single_shell_controller import SingleShellController
from picsh.models.root_model import RootModel
from picsh.views.node_panel_view import NodePanelView
from picsh.views.view_names import ViewNames
from picsh.controllers.base_controller import BaseController


class NodePanelController(BaseController):
    def __init__(
        self,
        node_panel_view: NodePanelView,
        root_model: RootModel,
        cluster_shell_controller: ClusterSelectionController,
        single_shell_controller: SingleShellController,
        receive_buffer_controller: ReceiveBufferController,
    ):
        super().__init__()
        self._urwid_loop = None
        self._aio_event_loop = None

        self.view: NodePanelView = node_panel_view
        self._root_model: RootModel = root_model

        self._cluster_shell_controller = cluster_shell_controller
        self._single_shell_controller = single_shell_controller
        self._receive_buffer_controller = receive_buffer_controller

        self.register_child_controller(cluster_shell_controller)
        self.register_child_controller(single_shell_controller)
        self.register_child_controller(receive_buffer_controller)

        self._active_controller = self._cluster_shell_controller
        self._active_view_name = ViewNames.CLUSTERSHELL_VIEW

        self._activated = False

    def handle_input(self, key):
        self._active_controller.handle_input(key)

    def switch_to(self, controller):
        self._active_controller = controller
        self._active_controller.activate(node_idx=self.view.get_selected_node_idx())
        self.view.set_focus(self._active_controller.want_focus())
        self.view.set_header_nav_text(self._active_controller.view.header_nav_text())
        self.view.set_footer_text(self._active_controller.view.footer_text())
        self.view.active_right_pane = self._active_controller.view
        self._urwid_loop.widget = self.view.outer_widget()

    def activate(self, **kwargs):
        if not self._activated:
            self.view.set_noderows(self._root_model.nodes)
            urwid.connect_signal(
                self.view.listbox_content, "modified", self.on_node_list_modified
            )
            self._activated = True
        self.switch_to(self._active_controller)

    def on_node_list_modified(self):
        node_idx = self.view.get_selected_node_idx()
        self.view.active_right_pane.on_node_list_modified(
            self._root_model.nodes, node_idx
        )

    def repaint(self):
        self.view.set_noderows(self._root_model.nodes)

    def handle_input_filter(self, keys, raw_input):
        if "ctrl q" in keys:
            keys = []
            new_view = ViewNames.EXIT_SCREEN
        else:
            keys, new_view = self._active_controller.handle_input_filter(keys, raw_input)
            if new_view == ViewNames.BUFFER_VIEW:
                self.switch_to(self._receive_buffer_controller)
            elif new_view == ViewNames.CLUSTERSHELL_VIEW:
                self.switch_to(self._cluster_shell_controller)
            elif new_view == ViewNames.SINGLESHELL_VIEW:
                self.switch_to(self._single_shell_controller)
            if new_view:
                self._active_view_name = new_view
        return keys, new_view

