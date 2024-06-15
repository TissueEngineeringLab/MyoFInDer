# coding: utf-8

from pathlib import Path

from .util import BaseTestInterface, mock_filedialog, mock_warning_window


class Test04ClickTable(BaseTestInterface):

    def testClickTable(self) -> None:
        """This test checks that the currently selected and displayed image is
        updated when the user clicks on another entry of the files table."""

        # The mock selection window returns the paths to three images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that the first image is displayed in the image canvas
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')

        # Generating a click on the third entry of the files table
        (self._window._files_table.table_items.entries[2].graph_elt.
         event_generate('<ButtonPress-1>', when="now"))

        # Checking that the third image is displayed in the image canvas
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_3.jpg')
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_3.jpg')
