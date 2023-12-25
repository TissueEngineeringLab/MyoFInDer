# coding: utf-8

from tkinter import Toplevel, ttk, Tk
from screeninfo import get_monitors
from pathlib import Path


class SavePopup(Toplevel):
    """Popup window displayed while the project is being saved to inform the
    user that saving is in progress."""

    def __init__(self, main_window: Tk, directory: Path) -> None:
        """Sets the layout of the popup window.

        Args:
            main_window: The parent window of which this popup depends.
            directory: The directory where the project is being saved.
        """

        super().__init__(main_window)

        # Setting the layout
        self.title("Saving....")
        ttk.Label(self, text=f"Saving to '{directory.name}' ..."). \
            pack(anchor='center', expand=False, fill='none', padx=10, pady=10)

        # Centering on the screen
        self.update()
        self._center()

    def _center(self) -> None:
        """Centers the popup window on the currently used monitor."""

        # Getting the current monitor
        monitors = get_monitors()
        candidates = [monitor for monitor in monitors if
                      0 <= self.winfo_x() - monitor.x <= monitor.width and
                      0 <= self.winfo_y() - monitor.y <= monitor.height]
        current_monitor = candidates[0] if candidates else monitors[0]

        # Getting the parameters of interest
        scr_width = current_monitor.width
        scr_height = current_monitor.height
        x_offset = current_monitor.x
        y_offset = current_monitor.y
        height = self.winfo_height()
        width = self.winfo_width()

        # Actually centering the window
        self.geometry('+%d+%d' % (x_offset + (scr_width - width) / 2,
                                  y_offset + (scr_height - height) / 2))
