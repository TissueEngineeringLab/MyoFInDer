# coding: utf-8

from pathlib import Path
from threading import Thread
from time import sleep

from .util import (BaseTestInterfaceProcessing, mock_filedialog,
                   mock_warning_window)


class Test11ProcessImages(BaseTestInterfaceProcessing):

    def testProcessImages(self) -> None:
        """This test checks that images can be successfully processed by
        MyoFInDer, and the partial selection checkboxes in the files table also
        work for partial processing."""

        # The mock selection window returns the paths to three images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Checking that the image canvas is empty of nuclei
        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)
        # Checking that the files table is empty of nuclei and fibers
        for i in range(3):
            self.assertEqual(
                len(self._window._files_table.table_items.entries[i].nuclei),
                0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              nuclei.nuclei_in_count), 0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              nuclei.nuclei_out_count), 0)
            self.assertEqual(
                len(self._window._files_table.table_items.entries[i].fibers),
                0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              fibers.area), 0)

        # Invoking the selection checkbox of the last image in the files table
        # to unselect it
        (self._window._files_table.table_items.entries[-1].graph_elt.
         check_button.invoke())
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Thread for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Checking that both positive and negative nuclei have been detected on
        # the image canvas
        self.assertGreater(len(self._window._image_canvas._nuclei), 0)
        self.assertGreater(self._window._image_canvas._nuclei.nuclei_in_count,
                           0)
        self.assertGreater(self._window._image_canvas._nuclei.nuclei_out_count,
                           0)
        # Checking that the two first images have their nuclei and fiber counts
        # updated in the files table
        for i in range(2):
            self.assertGreater(
                len(self._window._files_table.table_items.entries[i].nuclei),
                0)
            self.assertGreater((self._window._files_table.table_items.
                                entries[i].nuclei.nuclei_in_count), 0)
            self.assertGreater((self._window._files_table.table_items.
                                entries[i].nuclei.nuclei_out_count), 0)
            self.assertGreater(
                len(self._window._files_table.table_items.entries[i].fibers),
                0)
            self.assertGreater((self._window._files_table.table_items.
                                entries[i].fibers.area), 0)

        # Checking that the nuclei and fibers count of the last image remained
        # unchanged in the files table
        self.assertEqual(
            len(self._window._files_table.table_items.entries[2].nuclei),
            0)
        self.assertEqual((self._window._files_table.table_items.entries[2].
                          nuclei.nuclei_in_count), 0)
        self.assertEqual((self._window._files_table.table_items.entries[2].
                          nuclei.nuclei_out_count), 0)
        self.assertEqual(
            len(self._window._files_table.table_items.entries[2].fibers),
            0)
        self.assertEqual((self._window._files_table.table_items.entries[2].
                          fibers.area), 0)
