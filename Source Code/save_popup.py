# coding: utf-8

from tkinter import Toplevel, ttk


class Save_popup(Toplevel):

    def __init__(self, main_window, directory):
        super().__init__(main_window)

        self.title("Saving....")
        ttk.Label(self, text="Saving to '" + directory.name + "' ..."). \
            pack(anchor='center', expand=False, fill='none', padx=10, pady=10)

        self.update()
