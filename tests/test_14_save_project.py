# coding: utf-8

import filecmp
import shutil
from pathlib import Path
from threading import Thread
from time import sleep

from .util import (BaseTestInterfaceProcessing, mock_filedialog,
                   mock_warning_window)


class Test14SaveProject(BaseTestInterfaceProcessing):

    def testSaveProject(self) -> None:
        """This test checks that the correct files are being created when
        saving a project."""

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

        # Checking that all the files that should be saved were indeed created
        save_path = Path(mock_filedialog.save_folder)
        self.assertTrue(save_path.exists())
        self.assertTrue(save_path.is_dir())
        self.assertTrue((save_path / 'settings.pickle').exists())
        self.assertTrue((save_path / 'save_folder.xlsx').exists())
        self.assertTrue((save_path / 'data.pickle').exists())
        self.assertTrue((save_path / 'Original Images').exists())
        self.assertTrue((save_path / 'Original Images').is_dir())
        self.assertGreater(len(tuple((save_path /
                                      'Original Images').iterdir())), 0)

        # Copying all the files that were just saved to a different folder
        shutil.copytree(save_path, save_path / 'copy')

        # Triggering for a second time a save action using the "Save" button
        self._window._save_button.invoke()

        # Checking that the recorded files are still the same as the first ones
        comp = filecmp.cmpfiles(save_path, save_path / 'copy',
                                ('data.pickle', 'settings.pickle',
                                 'save_folder.xlsx',
                                 'Original Images/image_1.jpg'), shallow=False)
        self.assertCountEqual(('data.pickle', 'settings.pickle',
                               'save_folder.xlsx',
                               'Original Images/image_1.jpg'), comp[0])
        self.assertFalse(comp[1] or comp[2])

        # Adding a single nucleus by clicking on the image canvas, so that the
        # project is now different
        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-1>', when="now", x=10, y=10)
        self._window._image_canvas._canvas.event_generate(
            '<ButtonRelease-1>', when="now", x=10, y=10)
        self._window._show_nuclei_check_button.invoke()

        # Triggering a third save action using the "Save" button
        self._window._save_button.invoke()

        # Checking that some recorded files are now different to the original
        # due to the modification
        comp = filecmp.cmpfiles(save_path, save_path / 'copy',
                                ('data.pickle', 'settings.pickle',
                                 'save_folder.xlsx',
                                 'Original Images/image_1.jpg'), shallow=False)
        self.assertCountEqual(('Original Images/image_1.jpg',), comp[0])
        self.assertCountEqual(('data.pickle', 'save_folder.xlsx',
                               'settings.pickle'), comp[1])
        self.assertFalse(comp[2])
