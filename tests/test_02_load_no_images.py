# coding: utf-8

from .util import BaseTestInterface, mock_filedialog


class Test02LoadNoImages(BaseTestInterface):

    def testLoadNoImages(self) -> None:
        """This test checks that MyoFInDer successfully handles the situation
        when the user aborts an image selection for loading into the interface.
        """

        # None so that no image is returned by the mock selection window
        mock_filedialog.file_name = None
        self._window._select_images()

        # Checking that no image was loaded in the image canvas and file table
        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)
        self.assertEqual(len(self._window._files_table.table_items), 0)
