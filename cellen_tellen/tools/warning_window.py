# coding: utf-8

from tkinter import Toplevel, ttk


class Warning_window(Toplevel):

    def __init__(self, main_window, return_var):
        super().__init__(main_window)

        self._main_window = main_window
        self._return_var = return_var

        self.resizable(False, False)
        self.grab_set()

        self.title("Hold on!")
        self.bind('<Destroy>', self._cancel)

        self._set_layout()
        self.update()

    def _set_layout(self):
        ttk.Label(self,
                  text="Are you sure about closing an unsaved project ?"). \
            pack(anchor='n', expand=False, fill='none', side='top',
                 padx=20, pady=20)

        # create the buttons
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

    def _save(self):
        self._return_var.set(2)

    def _ignore(self):
        self._return_var.set(1)

    def _cancel(self, *_, **__):
        self._return_var.set(0)
