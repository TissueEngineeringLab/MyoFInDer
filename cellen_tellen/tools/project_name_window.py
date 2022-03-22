# coding: utf-8

from tkinter import Toplevel, ttk, StringVar, IntVar
from screeninfo import get_monitors
from typing import NoReturn

forbidden_chars = ['/', '\\', '>', '<', ':', '"', '|', '?', '*', '.']
forbidden_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                   'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                   'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']


class Project_name_window(Toplevel):
    """Popup window for choosing a name before saving a project."""

    def __init__(self, main_window, return_var: IntVar) -> None:
        """Creates the window, arranges its layout and displays it.

        Args:
            main_window: The main window of the project.
            return_var: A variable indicating whether the user chose a name or
                quit.
        """

        super().__init__(main_window)

        # Setting the variables
        self._return_var = return_var
        self._projects_path = main_window.projects_path
        self._warning_var = StringVar(value='')

        # Setting window properties
        self.resizable(False, False)
        self.grab_set()
        self.title("Saving the Current Project")

        # Setting a callback called when closing the window
        self.bind("<Destroy>", self._cancel)

        # Finish setting up the window
        self._set_layout()
        self.update()
        self._center()
        self._check_project_name_entry(self._name_entry.get())

    def _set_layout(self) -> NoReturn:
        """Creates the labels and the entry, places them and displays them."""

        # Setting the message label
        ask_label = ttk.Label(self,
                              text='Choose a name for your '
                                   'current project :')
        ask_label.pack(anchor='n', expand=False, fill='none', side='top',
                       padx=20, pady=10)

        # Setting the warning label
        self._warning_var.set('')
        warning_label = ttk.Label(self,
                                  textvariable=self._warning_var,
                                  foreground='red')
        warning_label.pack(anchor='n', expand=False, fill='none', side='top',
                           padx=20, pady=7)
        validate_command = warning_label.register(
            self._check_project_name_entry)

        # Setting the name entry
        self._name_entry = ttk.Entry(
            self, validate='key', state='normal',
            width=30,
            validatecommand=(validate_command, '%P'))
        self._name_entry.pack(anchor='n', expand=False, fill='none',
                              side='top', padx=20, pady=7)
        self._name_entry.focus()
        self._name_entry.icursor(len(self._name_entry.get()))

        # Setting the save button
        self._folder_name_window_save_button = ttk.Button(
            self, text='Save', width=30, command=self._enter_pressed)
        self._folder_name_window_save_button.pack(
            anchor='n', expand=False, fill='none', side='top', padx=20,
            pady=7)
        self.bind('<Return>', self._enter_pressed)

    def _center(self) -> NoReturn:
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

    def _check_project_name_entry(self, new_entry: str) -> True:
        """Checks whether a project name is valid or not.

        If it isn't, displays a warning message and disables the save button.

        Args:
            new_entry: The project name to evaluate.

        Returns:
            True to indicate that the check went fine. Never returns False.
        """

        # First, check that there's no forbidden character or that the name is
        # not empty
        if not new_entry or any(char in new_entry for char in forbidden_chars):
            self._folder_name_window_save_button['state'] = 'disabled'
            if len(new_entry) > 0:
                self._warning_var.set('This is not a valid projectname !')
            else:
                self._warning_var.set('')
            return True

        # Then, check that the name is not reserved
        if any(new_entry == name for name in forbidden_names):
            self._folder_name_window_save_button['state'] = 'disabled'
            self._warning_var.set('This name is reserved by the OS !')
            return True

        # Then, if the name is fine, check that it is not already used
        if (self._projects_path / new_entry).is_dir():
            self._warning_var.set('This project already exists')
            self._folder_name_window_save_button['state'] = 'disabled'
            return True

        # At this point, the name is fine and the project can be saved
        self._warning_var.set('')
        self._folder_name_window_save_button['state'] = 'enabled'
        return True

    def _enter_pressed(self, *_, **__) -> NoReturn:
        """Simply sets the return flag to 1 in case the user presses save."""

        if self._folder_name_window_save_button['state'] == 'enabled':
            self._return_var.set(1)

    def _cancel(self, *_, **__) -> NoReturn:
        """Simply sets the return flag to 0 in case the user closes the
        window."""

        self._return_var.set(0)

    def return_name(self) -> str:
        """Returns the name chosen by the user."""

        return self._name_entry.get()
