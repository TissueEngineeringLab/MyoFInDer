# coding: utf-8

from copy import deepcopy
from pathlib import Path
from threading import Thread
from time import sleep

from .util import (BaseTestInterfaceProcessing, mock_filedialog,
                   mock_warning_window)


class Test19ProcessVarySettings(BaseTestInterfaceProcessing):

    def testProcessVarySettings(self) -> None:
        """This test checks that the output of the processing is influenced as
        expected by the value of some settings."""

        # Copying the initial state of the settings for later restoring it
        init_settings = deepcopy(self._window.settings.get_all())

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

        # Recording the result of the first computation for later comparing it
        nuc = len(self._window._files_table.table_items.entries[0].nuclei)
        nuc_in = (self._window._files_table.table_items.entries[0].
                  nuclei.nuclei_in_count)
        nuc_out = (self._window._files_table.table_items.entries[0].
                   nuclei.nuclei_out_count)
        fib = len(self._window._files_table.table_items.entries[0].fibers)
        area = self._window._files_table.table_items.entries[0].fibers.area

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the minimum fiber intensity setting to the maximum
        self._window._settings_window._min_fib_int_slider.set(
            self._window._settings_window._min_fib_int_slider.cget('to'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertNotEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertNotEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the maximum fiber intensity setting to the minimum
        self._window._settings_window._max_fib_int_slider.set(
            self._window._settings_window._max_fib_int_slider.cget('from'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertNotEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertNotEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the minimum nucleus intensity setting to the maximum
        self._window._settings_window._min_nuc_int_slider.set(
            self._window._settings_window._min_nuc_int_slider.cget('to'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertNotEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the maximum nucleus intensity setting to the minimum
        self._window._settings_window._max_nuc_int_slider.set(
            self._window._settings_window._max_nuc_int_slider.cget('from'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertNotEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the minimum nucleus diameter setting to the maximum
        self._window._settings_window._min_nuc_diam_slider.set(
            self._window._settings_window._min_nuc_diam_slider.cget('to'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertNotEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the minimum fiber intensity setting to 50
        self._window._settings_window._min_fib_int_slider.set(50)

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Setting a new standard specifically for the last test
        nuc = len(self._window._files_table.table_items.entries[0].nuclei)
        nuc_in = (self._window._files_table.table_items.entries[0].
                  nuclei.nuclei_in_count)
        nuc_out = (self._window._files_table.table_items.entries[0].
                   nuclei.nuclei_out_count)
        fib = len(self._window._files_table.table_items.entries[0].fibers)
        area = self._window._files_table.table_items.entries[0].fibers.area

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the minimum nuclei count setting to the maximum
        self._window._settings_window._count_slider.set(
            self._window._settings_window._count_slider.cget('to'))
        # Also setting the fiber threshold to 50, otherwise there is no effect
        self._window._settings_window._min_fib_int_slider.set(50)

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)
