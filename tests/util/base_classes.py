# coding: utf-8

import logging
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Optional
import os

from . import mock_filedialog, mock_messagebox, mock_warning_window


class BaseTestInterface(unittest.TestCase):
    """Base class for all the test cases of the test suite.

    It sets up a fresh environment for each new test, in a way that the actions
    performed during one test don't affect the following ones.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Sets the arguments and initializes the parent class."""

        super().__init__(*args, **kwargs)

        self._dir: Optional[TemporaryDirectory] = None
        self._logger: Optional[logging.Logger] = None
        self._exit: bool = False

    def setUp(self) -> None:
        """Method called before each test starts.

        Overrides the default Tkinter dialogs, creates a temporary directory
        for the tests, and starts the main window of MyoFInDer.
        """

        # Not strictly needed, but avoids initializing DeepCell in vain
        if os.environ.get('DEEPCELL_ACCESS_TOKEN') is None:
            raise EnvironmentError("The DEEPCELL_ACCESS_TOKEN environment "
                                   "variable is not set, cannot run the tests")

        # Overwriting the dialog windows so that no user input is required
        # These default windows cannot be controlled from the code
        sys.modules['tkinter.filedialog'] = mock_filedialog
        sys.modules['tkinter.messagebox'] = mock_messagebox
        sys.modules['myofinder.tools.warning_window'] = mock_warning_window
        from myofinder import MainWindow

        # Not properly defining a logger so that no messages are logged
        self._logger = logging.getLogger("MyoFInDer")

        # Used by one test case for overriding the behavior of tearDown
        self._exit = False

        # All files are recorded inside a temporary directory so that they're
        # automatically deleted when the tests end
        self._dir = TemporaryDirectory()
        self._dir.__enter__()

        # Instantiating the main window of MyoFInDer
        self._window = MainWindow(Path(self._dir.name))

    def tearDown(self) -> None:
        """Method called after each test end.

        Closes the main window if not already closed, and cleans up the
        temporary directory of the test.
        """

        # Closing the main window if not already done during the test
        if not self._exit:
            self._window.safe_destroy()

        # Cleaning up the files recorded in the temporary directory
        if self._dir is not None:
            self._dir.__exit__(None, None, None)
            self._dir.cleanup()


class BaseTestInterfaceProcessing(BaseTestInterface):
    """Base class for all the test cases performing image processing.

    It simply makes the _stop_thread() method available to all of them.
    """

    def _stop_thread(self) -> None:
        """This method waits for the process queue to be empty, i.e. all the
        images to be processed, and then sets the _stop_thread flag.

        It is meant to be called in a Thread in a child instance. It replaces a
        behavior implemented in the interface of MyoFInDer, but that cannot be
        used here because of the special context of unit testing.
        """

        sleep(5)
        while not self._window._queue.empty():
            sleep(1)
        self._window._stop_thread = True
