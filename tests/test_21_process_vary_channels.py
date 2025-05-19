# coding: utf-8

from pathlib import Path
from time import sleep
from threading import Thread

from .util import (BaseTestInterfaceProcessing, mock_warning_window,
                   mock_filedialog)


class Test21ProcessVaryChannels(BaseTestInterfaceProcessing):

    def testProcessVaryChannels(self) -> None:
        """This test checks that the image processing gives a similar output
        with all the possible combinations of channels colors.

        To this end, a same image was duplicated but with its colors shuffled
        across all the possible channel combinations.
        """

        # The mock selection window returns the path to one image to load
        # The nuclei are on the blue channel, the fibers on the green channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to blue, the fibers channel to green
        self._window._settings_window._nuclei_colour_r1.invoke()
        self._window._settings_window._fiber_colour_r2.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Reading the processing output to later compare it with other runs
        nuc = len(self._window._files_table.table_items.entries[0].nuclei)
        nuc_in = (self._window._files_table.table_items.entries[0].
                  nuclei.nuclei_in_count)
        nuc_out = (self._window._files_table.table_items.entries[0].
                   nuclei.nuclei_out_count)
        fib = len(self._window._files_table.table_items.entries[0].fibers)
        area = self._window._files_table.table_items.entries[0].fibers.area

        # Making sure that some nuclei and some fibers were detected
        self.assertGreater(nuc, 0)
        self.assertGreater(nuc_in, 0)
        self.assertGreater(nuc_out, 0)
        self.assertGreater(fib, 0)
        self.assertGreater(area, 0)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the green channel, the fibers on the blue channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_4.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to green, the fibers channel to blue
        self._window._settings_window._nuclei_colour_r2.invoke()
        self._window._settings_window._fiber_colour_r1.invoke()
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

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 5)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 8)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 6)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the blue channel, the fibers on the red channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_5.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to blue, the fibers channel to red
        self._window._settings_window._nuclei_colour_r1.invoke()
        self._window._settings_window._fiber_colour_r3.invoke()
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

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 5)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 5)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 5)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the green channel, the fibers on the red channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_6.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to green, the fibers channel to red
        self._window._settings_window._nuclei_colour_r2.invoke()
        self._window._settings_window._fiber_colour_r3.invoke()
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

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 5)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 5)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 8)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the red channel, the fibers on the blue channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_7.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to red, the fibers channel to blue
        self._window._settings_window._nuclei_colour_r3.invoke()
        self._window._settings_window._fiber_colour_r1.invoke()
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

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 5)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 5)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 5)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the red channel, the fibers on the green channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_8.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to red, the fibers channel to green
        self._window._settings_window._nuclei_colour_r3.invoke()
        self._window._settings_window._fiber_colour_r2.invoke()
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

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 6)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 6)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 6)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)
