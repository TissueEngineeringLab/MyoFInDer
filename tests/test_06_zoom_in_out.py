# coding: utf-8

from pathlib import Path
from platform import system

from .util import BaseTestInterface, mock_filedialog, mock_warning_window


class Test06ZoomInOut(BaseTestInterface):

    def testZoomInOut(self) -> None:
        """This test checks that the image in the image canvas is correctly
        resized when using the mousewheel."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Reading the scale and dimension of the image before any interaction
        scale_0 = self._window._image_canvas._img_scale
        width_0 = self._window._image_canvas._canvas.image_tk.width()
        height_0 = self._window._image_canvas._canvas.image_tk.height()

        # Checking that the displayed image is by default not zoomed in or out
        self.assertEqual(self._window._image_canvas._can_scale, 1.0)
        self.assertEqual(self._window._image_canvas._current_zoom, 0)

        # The zoom commands differ on Linux, Windows, and macOS
        # Generating a single zoom-in event with the mousewheel
        if system() == "Linux":
            self._window._image_canvas._canvas.event_generate(
                '<4>', when="now", x=5, y=5)
        else:
            self._window._image_canvas._canvas.event_generate(
                '<MouseWheel>', when="now", x=5, y=5, delta=1)

        # Checking that the zoom was correctly applied in the image canvas
        self.assertAlmostEqual(self._window._image_canvas._img_scale, scale_0 *
                               self._window._image_canvas._delta)
        self.assertEqual(self._window._image_canvas._can_scale,
                         self._window._image_canvas._delta)
        self.assertEqual(self._window._image_canvas._current_zoom, 1)
        self.assertGreater(self._window._image_canvas._canvas.image_tk.width(),
                           width_0)
        self.assertGreater(
            self._window._image_canvas._canvas.image_tk.height(), height_0)

        # Generating five zoom-in events with the mousewheel
        for _ in range(5):
            if system() == "Linux":
                self._window._image_canvas._canvas.event_generate(
                    '<4>', when="now", x=5, y=5)
            else:
                self._window._image_canvas._canvas.event_generate(
                    '<MouseWheel>', when="now", x=5, y=5, delta=1)

        # Checking that the zoom was correctly applied in the image canvas, and
        # that the limit of 5 zoom levels in enforced
        self.assertAlmostEqual(self._window._image_canvas._img_scale, scale_0 *
                               self._window._image_canvas._delta ** 5)
        self.assertAlmostEqual(self._window._image_canvas._can_scale,
                               self._window._image_canvas._delta ** 5)
        self.assertEqual(self._window._image_canvas._current_zoom, 5)
        self.assertGreater(self._window._image_canvas._canvas.image_tk.width(),
                           width_0)
        self.assertGreater(
            self._window._image_canvas._canvas.image_tk.height(), height_0)

        # Generating 11 zoom-out events with the mousewheel
        for _ in range(11):
            if system() == "Linux":
                self._window._image_canvas._canvas.event_generate(
                    '<5>', when="now", x=5, y=5)
            else:
                self._window._image_canvas._canvas.event_generate(
                    '<MouseWheel>', when="now", x=5, y=5, delta=-1)

        # Checking that the zoom was correctly applied in the image canvas, and
        # that the limit of 5 zoom levels in enforced
        self.assertAlmostEqual(self._window._image_canvas._img_scale, scale_0 *
                               self._window._image_canvas._delta ** -5)
        self.assertAlmostEqual(self._window._image_canvas._can_scale,
                               self._window._image_canvas._delta ** -5)
        self.assertEqual(self._window._image_canvas._current_zoom, -5)
        self.assertLess(self._window._image_canvas._canvas.image_tk.width(),
                        width_0)
        self.assertLess(self._window._image_canvas._canvas.image_tk.height(),
                        height_0)
