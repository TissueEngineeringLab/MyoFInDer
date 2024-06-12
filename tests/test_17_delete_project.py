# coding: utf-8

from pathlib import Path
from threading import Thread
from time import sleep

from .util import (BaseTestInterfaceProcessing, mock_filedialog,
                   mock_warning_window)


class Test17DeleteProject(BaseTestInterfaceProcessing):

    def testDeleteProject(self) -> None:
        """This test checks that deleting the current project successfully
        removes all the recorded files and resets the image canvas and the
        files table."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        # The images will be saved to the existing temporary folder created
        # before starting the test
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
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

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Checking quickly that the project was saved as expected
        self.assertTrue((Path(self._dir.name) / 'save_folder').exists())

        # Deleting the current project and flushing the interface
        index = self._window._file_menu.index("Delete Current Project")
        self._window._file_menu.invoke(index)

        # Checking that the image canvas and the files table are now empty
        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)
        self.assertEqual(len(self._window._files_table.table_items), 0)

        # Checking that all the recorded files were now deleted
        self.assertFalse((Path(self._dir.name) / 'save_folder').exists())
