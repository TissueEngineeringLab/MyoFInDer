# coding: utf-8

from pathlib import Path
from PIL import Image

from .util import BaseTestInterface, mock_filedialog, mock_warning_window


class Test03LoadImages(BaseTestInterface):

    def testLoadImages(self) -> None:
        """This test checks that MyoFInDer successfully loads several images,
        displays the first one in the image canvas, and displays them all in
        the file table."""

        # The mock selection window returns the paths to three images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that an image is displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')

        # Checking that the images have entries in the files table
        self.assertEqual(len(self._window._files_table.table_items), 3)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (1, 2, 3)])
