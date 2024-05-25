# coding: utf-8

from tkinter import IntVar, Tk


class WarningWindow:
    """"""

    value: int = 0

    def __init__(self, parent: Tk, return_var: IntVar) -> None:
        """"""

        self._return_var = return_var
        parent.after(500, self.update_var)

    def update_var(self) -> None:
        """"""

        self._return_var.set(self.value)

    def destroy(self) -> None:
        """"""

        pass
