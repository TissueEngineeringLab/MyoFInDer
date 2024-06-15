# coding: utf-8

from pathlib import Path

from .util import BaseTestInterface, mock_filedialog, mock_warning_window


class Test05ClickImage(BaseTestInterface):

    def testClickImage(self) -> None:
        """This test checks that the nuclei are correctly added, inverted, or
        deleted on the image canvas when left- or right-clicking on it, and
        checks that the files table is updated accordingly."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that the image canvas and file table are empty of nuclei
        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei), 0)

        # Checking that the image canvas and file table are empty of fibers
        self.assertEqual(len(self._window._image_canvas._fibers), 0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.fibers), 0)

        # Generating 10 left-clicks on the image canvas
        for i in range(1, 11):
            self._window._image_canvas._canvas.event_generate(
                '<ButtonPress-1>', when="now", x=10 * i, y=10 * i)
            self._window._image_canvas._canvas.event_generate(
                '<ButtonRelease-1>',  when="now", x=10 * i, y=10 * i)

        # Checking that the image canvas and the files table have the correct
        # nuclei count
        self.assertEqual(len(self._window._image_canvas._nuclei), 10)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         10)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            10)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 0)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 10)

        # Generating left-clicks on 5 of the 10 created nuclei
        for i in range(1, 6):
            self._window._image_canvas._canvas.event_generate(
                '<ButtonPress-1>', when="now", x=20 * i, y=20 * i)
            self._window._image_canvas._canvas.event_generate(
                '<ButtonRelease-1>',  when="now", x=20 * i, y=20 * i)

        # Checking that the corresponding nuclei have been inverted on the
        # image canvas and the files table
        self.assertEqual(len(self._window._image_canvas._nuclei), 10)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         5)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         5)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            10)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 5)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 5)

        # Generating right-clicks on 5 of the 10 created nuclei
        for i in range(1, 6):
            self._window._image_canvas._canvas.event_generate(
                '<ButtonPress-3>', when="now", x=20 * i, y=20 * i)
            self._window._image_canvas._canvas.event_generate(
                '<ButtonRelease-3>',  when="now", x=20 * i, y=20 * i)

        # Checking that the corresponding nuclei have been deleted on the
        # image canvas and the files table
        self.assertEqual(len(self._window._image_canvas._nuclei), 5)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         5)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            5)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 0)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 5)

        # Generating a left click-and-drag over the 5 remaining nuclei
        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-1>', when="now", x=5, y=5)
        self._window._image_canvas._canvas.event_generate(
            '<B1-Motion>', when="now", x=105, y=105)
        self._window._image_canvas._canvas.event_generate(
            '<ButtonRelease-1>', when="now", x=105, y=105)

        # Checking that the corresponding nuclei have been inverted on the
        # image canvas and the files table
        self.assertEqual(len(self._window._image_canvas._nuclei), 5)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         5)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            5)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 5)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 0)

        # Generating a right click-and-drag over the 5 remaining nuclei
        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-3>', when="now", x=5, y=5)
        self._window._image_canvas._canvas.event_generate(
            '<B3-Motion>', when="now", x=105, y=105)
        self._window._image_canvas._canvas.event_generate(
            '<ButtonRelease-3>', when="now", x=105, y=105)

        # Checking that the corresponding nuclei have been deleted on the
        # image canvas and the files table
        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            0)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 0)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 0)
