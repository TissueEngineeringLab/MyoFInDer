# coding: utf-8

from copy import deepcopy
from pathlib import Path
from threading import Thread
from time import sleep

from .util import (BaseTestInterfaceProcessing, mock_filedialog,
                   mock_warning_window)


class Test16LoadProject(BaseTestInterfaceProcessing):

    def testLoadProject(self) -> None:
        """This test checks that the settings and image data can successfully
        be loaded from a previously saved project without altering the
        information."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        # The images will be saved to the existing temporary folder created
        # before starting the test
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        mock_filedialog.load_directory = mock_filedialog.save_folder
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Copying the current parameters and image data to later compare it
        settings = deepcopy(self._window.settings.get_all())
        table = deepcopy(self._window._files_table.table_items.save_version)

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Overriding the current changes with a new empty project
        index = self._window._file_menu.index("New Empty Project")
        self._window._file_menu.invoke(index)

        # Re-loading the data that was just saved and erased
        index = self._window._file_menu.index("Load From Explorer")
        self._window._file_menu.invoke(index)

        # Checking that the loaded data matches the one copied earlier
        self.assertEqual(settings, self._window.settings.get_all())
        self.assertEqual(table,
                         self._window._files_table.table_items.save_version)
