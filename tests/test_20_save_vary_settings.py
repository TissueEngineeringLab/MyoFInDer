# coding: utf-8

from pathlib import Path
from threading import Thread
from time import sleep

from .util import (BaseTestInterfaceProcessing, mock_filedialog, 
                   mock_warning_window)


class Test20SaveVarySettings(BaseTestInterfaceProcessing):

    def testSaveVarySettings(self) -> None:
        """This test checks that the project recording process is influenced as
        expected by the value of some settings."""

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

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Disabling the recording of overlay images
        self._window._settings_window._overlay_off_button.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Checking that the project was recorded but not the overlay images
        save_path = Path(mock_filedialog.save_folder)
        self.assertTrue(save_path.exists())
        self.assertFalse((save_path / 'Overlay Images').exists())

        # Deleting the current project and flushing the interface
        index = self._window._file_menu.index("Delete Current Project")
        self._window._file_menu.invoke(index)

        # Re-loading the same image in the interface as previously
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
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Enabling the recording of overlay images
        self._window._settings_window._overlay_on_button.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Checking that the project was recorded along with the overlay images
        self.assertTrue(save_path.exists())
        self.assertTrue((save_path / 'Overlay Images' /
                         'image_1.jpg').exists())
