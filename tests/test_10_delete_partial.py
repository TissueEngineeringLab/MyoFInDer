# coding: utf-8

from pathlib import Path
from PIL import Image

from .util import BaseTestInterface, mock_filedialog, mock_warning_window


class Test10DeletePartial(BaseTestInterface):

    def testDeletePartial(self) -> None:
        """This test checks that the partial deletion of images using the
        checkboxes and master delete button in the files table works as
        expected."""

        # The mock selection window returns the paths to three images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that the first image is displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')

        # Checking that three images are referenced in the files table
        self.assertEqual(len(self._window._files_table.table_items), 3)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (1, 2, 3)])

        # Invoking the master select button to unselect all the images in the
        # files table
        self._window._select_all_button.invoke()
        # Selecting only the first image using its individual select checkbox
        (self._window._files_table.table_items.current_entry.graph_elt.
         check_button.invoke())
        # Invoking the master delete button in the files table
        self._window._delete_all_button.invoke()

        # Checking that the second image is now displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_2.jpg')

        # Checking that only two images are left in the files table
        self.assertEqual(len(self._window._files_table.table_items), 2)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_2.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (2, 3)])

        # Invoking the master delete button in the files table
        self._window._delete_all_button.invoke()

        # Checking that no image is displayed in the image canvas
        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)

        # Checking that no image is left in the files table
        self.assertEqual(len(self._window._files_table.table_items), 0)
