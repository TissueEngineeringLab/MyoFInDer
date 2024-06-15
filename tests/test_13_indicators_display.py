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

        # Checking that no Tkinter objects representing nuclei or fibers are
        # present on the image canvas
        self.assertTrue(not any(nuc.tk_obj is not None for nuc
                                in self._window._image_canvas._nuclei))
        self.assertTrue(not any(fib.polygon is not None for fib
                                in self._window._image_canvas._fibers))

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        display_nuc = self._window.settings.show_nuclei.get()
        display_fib = self._window.settings.show_fibers.get()

        if display_nuc:
            self.assertTrue(all(nuc.tk_obj is not None for nuc
                                in self._window._image_canvas._nuclei))
        else:
            self.assertTrue(not any(nuc.tk_obj is not None for nuc
                                    in self._window._image_canvas._nuclei))
        if display_fib:
            self.assertTrue(all(fib.polygon is not None for fib
                                in self._window._image_canvas._fibers))
        else:
            self.assertTrue(not any(fib.polygon is not None for fib
                                    in self._window._image_canvas._fibers))

        self._window._show_nuclei_check_button.invoke()
        self._window._show_fibers_check_button.invoke()

        if display_nuc:
            self.assertTrue(not any(nuc.tk_obj is not None for nuc
                                    in self._window._image_canvas._nuclei))
        else:
            self.assertTrue(all(nuc.tk_obj is not None for nuc
                                in self._window._image_canvas._nuclei))
        if display_fib:
            self.assertTrue(not any(fib.polygon is not None for fib
                                    in self._window._image_canvas._fibers))
        else:
            self.assertTrue(all(fib.polygon is not None for fib
                                in self._window._image_canvas._fibers))
