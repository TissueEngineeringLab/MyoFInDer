# coding: utf-8

from tkinter import Toplevel, ttk, IntVar
from screeninfo import get_monitors


class WarningWindow(Toplevel):
    """Popup window warning the user that the selected action may cause a data
    loss, and proposing to user save before continuing, continue without
    saving, or cancel."""

    def __init__(self, main_window, return_var: IntVar) -> None:
        """Creates the window, arranges its layout and displays it.

        Args:
            main_window: The main window of the project.
            return_var: A variable indicating the option the user chose.
        """

        super().__init__(main_window)

        # Setting variable
        self._return_var = return_var

        # Setting window properties
        self.resizable(False, False)
        self.grab_set()
        self.title("Hold on!")
        self.bind('<Destroy>', self._cancel)

        # Setting the layout and displaying the window
        self._set_layout()
        self.update()
        self._center()

    def _set_layout(self) -> None:
        """Creates the labels and the buttons, places them and displays
        them."""

        # Setting the label
        ttk.Label(self,
                  text="Are you sure about closing an unsaved project ?"). \
            pack(anchor='n', expand=False, fill='none', side='top',
                 padx=20, pady=20)

        # Setting the buttons
        ttk.Button(self, text='Save Before Continuing',
                   command=self._save, width=40). \
            pack(anchor='n', expand=False, fill='none', side='top',
                 padx=20, pady=7)
        ttk.Button(self, text='Continue Without Saving',
                   command=self._ignore,
                   width=40). \
            pack(anchor='n', expand=False, fill='none', side='top',
                 padx=20, pady=7)
        ttk.Button(self, text='Cancel', command=self.destroy, width=40). \
            pack(anchor='n', expand=False, fill='none', side='top',
                 padx=20, pady=7)

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

    def _save(self) -> None:
        """Simply sets the return flag to 2 in case the user wants to save
        before continuing."""

        self._return_var.set(2)

    def _ignore(self) -> None:
        """Simply sets the return flag to 1 in case the user wants to continue
        without saving."""

        self._return_var.set(1)

    def _cancel(self, *_, **__) -> None:
        """Simply sets the return flag to 0 in case the user cancels or closes
        the window."""

        self._return_var.set(0)
