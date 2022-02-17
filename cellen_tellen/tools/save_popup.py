# coding: utf-8

from tkinter import Toplevel, ttk
from screeninfo import get_monitors


class Save_popup(Toplevel):

    def __init__(self, main_window, directory):
        super().__init__(main_window)

        self.title("Saving....")
        ttk.Label(self, text="Saving to '" + directory.name + "' ..."). \
            pack(anchor='center', expand=False, fill='none', padx=10, pady=10)

        self.update()
        self._center()

    def _center(self):
        monitors = get_monitors()
        candidates = [monitor for monitor in monitors if
                      0 <= self.winfo_x() - monitor.x <= monitor.width and
                      0 <= self.winfo_y() - monitor.y <= monitor.height]
        current_monitor = candidates[0] if candidates else monitors[0]
        scr_width = current_monitor.width
        scr_height = current_monitor.height
        x_offset = current_monitor.x
        y_offset = current_monitor.y
        height = self.winfo_height()
        width = self.winfo_width()

        self.geometry('+%d+%d' % (x_offset + (scr_width - width) / 2,
                                  y_offset + (scr_height - height) / 2))
