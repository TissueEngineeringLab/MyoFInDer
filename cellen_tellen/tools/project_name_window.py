# coding: utf-8

from tkinter import Toplevel, ttk, StringVar


class Project_name_window(Toplevel):

    def __init__(self, main_window, return_var):
        super().__init__(main_window)

        self._return_var = return_var

        self._projects_path = main_window.projects_path

        self._warning_var = StringVar(value='')

        self.resizable(False, False)
        self.grab_set()

        self.bind("<Destroy>", self._cancel)
        self.title("Saving the Current Project")

        self._set_layout()
        self.update()
        self._check_project_name_entry(self._name_entry.get())

    def _set_layout(self):

        ask_label = ttk.Label(self,
                              text='Choose a name for your '
                                   'current Project :')
        ask_label.pack(anchor='n', expand=False, fill='none', side='top',
                       padx=20, pady=10)

        # set the warning label (gives warnings when the name is bad)
        self._warning_var.set('')
        warning_label = ttk.Label(self,
                                  textvariable=self._warning_var,
                                  foreground='red')
        warning_label.pack(anchor='n', expand=False, fill='none', side='top',
                           padx=20, pady=7)
        validate_command = warning_label.register(
            self._check_project_name_entry)

        # set the entry box to input the name
        self._name_entry = ttk.Entry(
            self, validate='key', state='normal',
            width=30,
            validatecommand=(validate_command, '%P'))
        self._name_entry.pack(anchor='n', expand=False, fill='none',
                              side='top', padx=20, pady=7)
        self._name_entry.focus()
        self._name_entry.icursor(len(self._name_entry.get()))

        # save button
        self._folder_name_window_save_button = ttk.Button(
            self, text='Save', width=30, command=self._enter_pressed)
        self._folder_name_window_save_button.pack(
            anchor='n', expand=False, fill='none', side='top', padx=20,
            pady=7)
        self.bind('<Return>', self._enter_pressed)

    def _check_project_name_entry(self, new_entry):

        # check if it is a valid name
        if '/' in new_entry or '.' in new_entry or not new_entry:
            self._folder_name_window_save_button['state'] = 'disabled'
            if len(new_entry) > 0:
                self._warning_var.set('This is not a valid projectname !')
            else:
                self._warning_var.set('')
            return True

        # check if it already exists
        if (self._projects_path / new_entry).is_dir():
            self._warning_var.set('This project already exists')
            self._folder_name_window_save_button['state'] = 'disabled'
            return True

        # no warnings
        self._warning_var.set('')
        self._folder_name_window_save_button['state'] = 'enabled'
        return True

    def _enter_pressed(self, *_, **__):

        # if the window exists and the save button is enabled
        if self._folder_name_window_save_button['state'] == 'enabled':
            self._return_var.set(1)

    def _cancel(self, *_, **__):
        self._return_var.set(0)

    def return_name(self):
        return self._name_entry.get()
