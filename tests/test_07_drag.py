# coding: utf-8

from pathlib import Path
from platform import system, python_version_tuple
from unittest import skipIf
import os

from .util import BaseTestInterface, mock_filedialog, mock_warning_window

condition = (os.getenv('MYOFINDER_GITHUB_ACTION', 0) == '1'
             and system() == 'Windows'
             and int(python_version_tuple()[1]) < 9)


@skipIf(condition,
        "For some reason, this test fails on Windows with a Python version "
        "anterior to 3.8. It was manually checked that the drag feature was "
        "working as expected in the interface nevertheless.")
class Test07Drag(BaseTestInterface):

    def testDrag(self) -> None:
        """This test checks that a mousewheel click-and-drag successfully moves
        the image in the image canvas."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Reading the initial coordinates of the upper-left corner of the image
        # on the image canvas
        init_x = self._window._image_canvas._canvas.canvasx(0)
        init_y = self._window._image_canvas._canvas.canvasy(0)

        # The zoom commands differ on Linux, Windows, and macOS
        # Generating five zoom-in events with the mousewheel
        for _ in range(5):
            if system() == "Linux":
                self._window._image_canvas._canvas.event_generate(
                    '<4>', when="now", x=100, y=100)
            else:
                self._window._image_canvas._canvas.event_generate(
                    '<MouseWheel>', when="now", x=100, y=100, delta=1)

        # checking that the coordinates of the upper-left corner of the image
        # in the image canvas have changed
        self.assertGreater(self._window._image_canvas._canvas.canvasx(0),
                           init_x)
        self.assertGreater(self._window._image_canvas._canvas.canvasy(0),
                           init_y)
        # Reading the new coordinates of the upper-left corner of the image on
        # the image canvas
        new_x = self._window._image_canvas._canvas.canvasx(0)
        new_y = self._window._image_canvas._canvas.canvasy(0)

        # Generating a mousewheel click-and-drag event on the image canvas
        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-2>', when="now", x=100, y=100)
        self._window._image_canvas._canvas.event_generate(
            '<B2-Motion>', when="now", x=50, y=50)

        # Checking that the position of the image in the image canvas has been
        # updated with the correct value
        self.assertEqual(self._window._image_canvas._canvas.canvasx(0) - new_x,
                         50)
        self.assertEqual(self._window._image_canvas._canvas.canvasy(0) - new_y,
                         50)
