# coding: utf-8

from pathlib import Path

from .util import BaseTestInterface, mock_filedialog, mock_warning_window


class Test08SetChannels(BaseTestInterface):

    def testSetChannels(self) -> None:
        """This test checks that the checkboxes in the interface can
        successfully show or hide the channels of the displayed image."""

        # The mock selection window returns the path to one image to load
        # The image was modified so that all three channels have a non-zero
        # value in pixel (0, 0)
        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_3.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Reading the values of the checkboxes driving the display of the
        # channels
        init_r = self._window.settings.red_channel_bool.get()
        init_g = self._window.settings.green_channel_bool.get()
        init_b = self._window.settings.blue_channel_bool.get()

        # Reading the RGB value of the pixel in position (0, 0)
        r, g, b = (self._window._image_canvas._canvas.image_tk.
                   _PhotoImage__photo.get(0, 0))

        # Checking that the RGB values are consistent with the state of the
        # checkboxes
        self.assertIs(bool(r), init_r)
        self.assertIs(bool(g), init_g)
        self.assertIs(bool(b), init_b)

        # Generating a click on all the checkboxes to invert them
        self._window._red_channel_check_button.invoke()
        self._window._green_channel_check_button.invoke()
        self._window._blue_channel_check_button.invoke()

        # Reading the new RGB value of the pixel in position (0, 0)
        r, g, b = (self._window._image_canvas._canvas.image_tk.
                   _PhotoImage__photo.get(0, 0))

        # Reading the new values of the checkboxes driving the display of the
        # channels
        new_r = self._window.settings.red_channel_bool.get()
        new_g = self._window.settings.green_channel_bool.get()
        new_b = self._window.settings.blue_channel_bool.get()

        # Checking that the state of the checkboxes was successfully inverted
        # by clicking
        self.assertIs(new_r, not init_r)
        self.assertIs(new_g, not init_g)
        self.assertIs(new_b, not init_b)

        # Checking that the RGB values are consistent with the new state of the
        # checkboxes
        self.assertIs(bool(r), new_r)
        self.assertIs(bool(g), new_g)
        self.assertIs(bool(b), new_b)
