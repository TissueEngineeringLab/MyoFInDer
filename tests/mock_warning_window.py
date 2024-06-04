# coding: utf-8

from tkinter import IntVar, Tk


class WarningWindow:
    """Mock class for the myofinder.tools.WarningWindow class.

    Because some code in MyoFInDer will block waiting for a tkinter.IntVar to
    be updated by WarningWindow (normally with a click of the user), this class
    implements a simple mechanism for automatically updating the blocking
    variable.

    It also attributes the desired value to the variable, which has an
    influence on how MyoFInDer will handle the event that triggered the call to
    WarningWindow.
    """

    value: int = 0

    def __init__(self, parent: Tk, return_var: IntVar) -> None:
        """Takes the same arguments as myofinder.tools.WarningWindow.

        Plans a call to update_var in 0.5s.
        """

        self._return_var = return_var
        parent.after(500, self.update_var)

    def update_var(self) -> None:
        """Updates the value of the IntVar with the one given in self.value."""

        self._return_var.set(self.value)

    def destroy(self) -> None:
        """Implemented for compatibility but doesn't need to perform any
        action."""

        pass
