from typing import List

class BaseController:
    def __init__(self):
        self._urwid_loop = None
        self._aio_event_loop = None
        self.child_controllers: List["BaseController"] = []
        self._repaint_notifier = None

    def register_child_controller(self, controller: "BaseController"):
        controller.set_repaint_notifier(self.repaint_notifer)
        self.child_controllers.append(controller)

    def set_urwid_loop(self, urwid_loop):
        self._urwid_loop = urwid_loop
        for c in self.child_controllers:
            c.set_urwid_loop(urwid_loop)

    def set_aio_event_loop(self, aio_event_loop):
        self._aio_event_loop = aio_event_loop
        for c in self.child_controllers:
            c.set_aio_event_loop(aio_event_loop)

    def activate(self, **kwargs):
        pass

    def handle_input(self, keys):
        return keys

    def handle_input_filter(self, keys, raw_input):
        return keys, None

    def switch_to(self):
        pass

    def repaint(self):
        pass

    def repaint_notifer(self):
        # child nodes can notify a parent node to repaint the tree
        self.repaint()
        for c in self.child_controllers:
            c.repaint()
        if self._urwid_loop:
            self._urwid_loop.draw_screen()

    def set_repaint_notifier(self, notifier):
        self._repaint_notifier = notifier

    def quit(self):
        for c in self.child_controllers:
            c.quit()
