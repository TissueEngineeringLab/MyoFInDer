# coding: utf-8

from tkinter import Toplevel, ttk, Scale
from screeninfo import get_monitors


class Settings_window(Toplevel):
    """Popup window for setting the parameters of the software."""

    def __init__(self, main_window) -> None:
        """Creates the window, arranges its layout and displays it.

        Args:
            main_window: The main window of the project.
        """

        super().__init__(main_window)

        # Setting the variables
        self._main_window = main_window
        self._settings = self._main_window.settings

        # Setting window properties
        self.resizable(False, False)
        self.grab_set()
        self.title("Settings")

        # Finish setting up the window
        self._set_layout()
        self.update()
        self._center()

    def destroy(self) -> None:
        """Before exiting, saves the settings to a file in the application
        folder."""

        if self._main_window.app_folder is not None:
            self._main_window.save_settings(self._main_window.app_folder)
        super().destroy()

    def _set_layout(self) -> None:
        """Creates the buttons and sliders, places them and displays them."""

        # General layout
        frame = ttk.Frame(self, padding="20 20 20 20")
        frame.grid(sticky='NESW')

        # Buttons for selecting the nuclei channel
        ttk.Label(frame, text="Nuclei Channel :").grid(column=0, row=0,
                                                       sticky='NE',
                                                       padx=(0, 10))
        nuclei_colour_r1 = ttk.Radiobutton(
            frame, text="Blue", variable=self._settings.nuclei_colour,
            value="blue")
        nuclei_colour_r1.grid(column=1, row=0, sticky='NW')
        nuclei_colour_r2 = ttk.Radiobutton(
            frame, text="Green", variable=self._settings.nuclei_colour,
            value="green")
        nuclei_colour_r2.grid(column=1, row=1, sticky='NW')
        nuclei_colour_r3 = ttk.Radiobutton(
            frame, text="Red", variable=self._settings.nuclei_colour,
            value="red")
        nuclei_colour_r3.grid(column=1, row=2, sticky='NW')

        # Buttons for selecting the fibers channel
        ttk.Label(frame, text="Fiber Channel :").grid(
            column=0, row=3, sticky='NE', pady=(10, 0), padx=(0, 10))
        fiber_colour_r1 = ttk.Radiobutton(
            frame, text="Blue", variable=self._settings.fiber_colour,
            value="blue")
        fiber_colour_r1.grid(column=1, row=3, sticky='NW', pady=(10, 0))
        fiber_colour_r2 = ttk.Radiobutton(
            frame, text="Green", variable=self._settings.fiber_colour,
            value="green")
        fiber_colour_r2.grid(column=1, row=4, sticky='NW')
        fiber_colour_r3 = ttk.Radiobutton(
            frame, text="Red", variable=self._settings.fiber_colour,
            value="red")
        fiber_colour_r3.grid(column=1, row=5, sticky='NW')

        # Buttons to chose whether to save the overlay images or not
        ttk.Label(frame, text='Save Images with Overlay :').grid(
            column=0, row=11, sticky='NE', pady=(10, 0), padx=(0, 10))
        ttk.Radiobutton(
            frame, text="On", variable=self._settings.save_overlay,
            value=1).grid(column=1, row=11, sticky='NW', pady=(10, 0))
        ttk.Radiobutton(
            frame, text="Off", variable=self._settings.save_overlay,
            value=0).grid(column=1, row=12, sticky='NW')

        # Slider to adjust the threshold for fiber detection
        ttk.Label(frame, text='Fiber detection threshold :').grid(
            column=0, row=13, sticky='E', pady=(10, 0), padx=(0, 10))

        fiber_threshold_slider_frame = ttk.Frame(frame)

        ttk.Label(fiber_threshold_slider_frame,
                  textvariable=self._settings.fiber_threshold,
                  width=3). \
            pack(side='left', anchor='w', fill='none', expand=False,
                 padx=(0, 20))

        Scale(fiber_threshold_slider_frame, from_=0, to=100,
              orient="horizontal",
              variable=self._settings.fiber_threshold, showvalue=False,
              length=150, tickinterval=20). \
            pack(side='left', anchor='w', fill='none', expand=False)

        fiber_threshold_slider_frame.grid(column=1, row=13, sticky='NW',
                                          pady=(10, 0))

        # Slider to adjust the small objects threshold
        ttk.Label(frame, text='Small Objects Threshold :').grid(
            column=0, row=14, sticky='E', pady=(10, 0), padx=(0, 10))

        threshold_slider_frame = ttk.Frame(frame)

        ttk.Label(threshold_slider_frame,
                  textvariable=self._settings.small_objects_threshold,
                  width=3). \
            pack(side='left', anchor='w', fill='none', expand=False,
                 padx=(0, 20))

        Scale(threshold_slider_frame, from_=0, to=100,
              variable=self._settings.small_objects_threshold,
              orient="horizontal", length=150, showvalue=False,
              tickinterval=25). \
            pack(side='left', anchor='w', fill='none', expand=False)

        threshold_slider_frame.grid(column=1, row=14, sticky='NW',
                                    pady=(10, 0))

    def _center(self) -> None:
        """Centers the popup window on the currently used monitor."""

        # Getting the current monitor
        monitors = get_monitors()
        candidates = [monitor for monitor in monitors if
                      0 <= self.winfo_x() - monitor.x <= monitor.width and
                      0 <= self.winfo_y() - monitor.y <= monitor.height]
        current_monitor = candidates[0] if candidates else monitors[0]

        # Getting the parameters of interest
        scr_width = current_monitor.width
        scr_height = current_monitor.height
        x_offset = current_monitor.x
        y_offset = current_monitor.y
        height = self.winfo_height()
        width = self.winfo_width()

        # Actually centering the window
        self.geometry('+%d+%d' % (x_offset + (scr_width - width) / 2,
                                  y_offset + (scr_height - height) / 2))
