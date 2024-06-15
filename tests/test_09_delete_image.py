# coding: utf-8

from pathlib import Path
from PIL import Image

from .util import BaseTestInterface, mock_filedialog, mock_warning_window


class Test09DeleteImage(BaseTestInterface):

    def testDeleteImage(self) -> None:
        """This test checks that an image can be successfully deleted from the
        files table and the image canvas by clicking on the delete button of
        the files table."""

        # The mock selection window returns the paths to two images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that the first image is displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')

        # Checking that two images are referenced in the files table
        self.assertEqual(len(self._window._files_table.table_items), 2)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (1, 2)])

        # Generating a delete event on the first image in the files table
        (self._window._files_table.table_items.current_entry.graph_elt.
         close_button.invoke())

        # Checking that the second image is now displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_2.jpg')

        # Checking that only one image is left in the files table
        self.assertEqual(len(self._window._files_table.table_items), 1)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_2.jpg')

        # Generating a delete event on the second image in the files table
        (self._window._files_table.table_items.current_entry.graph_elt.
         close_button.invoke())

        # Checking that no image is displayed in the image canvas
        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)

        # Checking that no image is left in the files table
        self.assertEqual(len(self._window._files_table.table_items), 0)
