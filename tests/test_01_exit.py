# coding: utf-8

from tkinter import TclError

from .util import BaseTestInterface


class Test01Exit(BaseTestInterface):

    def testExit(self) -> None:
        """This test checks that the main window is destroyed as expected after
        a call to safe_destroy()."""

        # Destroying the main window
        self._window.safe_destroy()

        # This call should raise an error as the window shouldn't exist anymore
        with self.assertRaises(TclError):
            self._window.wm_state()

        # Indicating the tearDown() method not to destroy the window
        self._exit = True
