# coding: utf-8

from pathlib import Path
from threading import Thread
from time import sleep

from .util import (BaseTestInterfaceProcessing, mock_filedialog,
                   mock_warning_window)


class Test13IndicatorsDisplay(BaseTestInterfaceProcessing):

    def testIndicatorsDisplay(self) -> None:
        """This test checks that the checkboxes driving the display of the
        detected nuclei and fibers are working as expected."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Checking that no Tkinter objects representing nuclei are present on
        # the image canvas
        self.assertTrue(not any(nuc.tk_obj is not None for nuc
                                in self._window._image_canvas._nuclei))
        # The fiber overlay should be present whatever happens though
        self.assertIsNotNone(self._window._image_canvas._fib_overlay_tk)

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()
        self._window._handle_ui_queue()
        self._window._handle_ui_queue()

        display_nuc = self._window.settings.show_nuclei.get()
        display_fib = self._window.settings.show_fibers.get()

        self.assertTrue(all(nuc.tk_obj is not None for nuc
                            in self._window._image_canvas._nuclei))
        if display_nuc:
            self.assertTrue(all(self._window._image_canvas._canvas.itemcget(
                nuc.tk_obj, "state") == 'normal' for nuc
                in self._window._image_canvas._nuclei))
        else:
            self.assertTrue(all(self._window._image_canvas._canvas.itemcget(
                nuc.tk_obj, "state") == 'hidden' for nuc
                in self._window._image_canvas._nuclei))

        self.assertIsNotNone(self._window._image_canvas._fib_overlay_tk)
        if display_fib:
            self.assertEqual(self._window._image_canvas._canvas.itemcget(
                self._window._image_canvas._fib_overlay_idx, "state"),
                'normal')
        else:
            self.assertEqual(self._window._image_canvas._canvas.itemcget(
                self._window._image_canvas._fib_overlay_idx, "state"),
                'hidden')

        self._window._show_nuclei_check_button.invoke()
        self._window._show_fibers_check_button.invoke()

        if display_nuc:
            self.assertTrue(all(self._window._image_canvas._canvas.itemcget(
                nuc.tk_obj, "state") == 'hidden' for nuc
                in self._window._image_canvas._nuclei))
        else:
            self.assertTrue(all(self._window._image_canvas._canvas.itemcget(
                nuc.tk_obj, "state") == 'normal' for nuc
                in self._window._image_canvas._nuclei))

        self.assertIsNotNone(self._window._image_canvas._fib_overlay_tk)
        if display_fib:
            self.assertEqual(self._window._image_canvas._canvas.itemcget(
                self._window._image_canvas._fib_overlay_idx, "state"),
                'hidden')
        else:
            self.assertEqual(self._window._image_canvas._canvas.itemcget(
                self._window._image_canvas._fib_overlay_idx, "state"),
                'normal')
