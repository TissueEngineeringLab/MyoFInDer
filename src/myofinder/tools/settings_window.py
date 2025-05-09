# coding: utf-8

from tkinter import Toplevel, ttk, Scale
from screeninfo import get_monitors


class SettingsWindow(Toplevel):
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
        self._main_window._settings_window = None
        super().destroy()

    def _set_layout(self) -> None:
        """Creates the buttons and sliders, places them and displays them."""

        # General layout
        self._frame = ttk.Frame(self, padding="20 20 20 20")
        self._frame.grid(sticky='NESW')

        # Buttons for selecting the nuclei channel
        self._nuclei_colour_label = ttk.Label(self._frame,
                                              text="Nuclei Channel :")
        self._nuclei_colour_label.grid(column=0, row=0, sticky='NE',
                                       padx=(0, 10))
        self._nuclei_colour_r1 = ttk.Radiobutton(
            self._frame, text="Blue", variable=self._settings.nuclei_colour,
            value="blue")
        self._nuclei_colour_r1.grid(column=1, row=0, sticky='NW')
        self._nuclei_colour_r2 = ttk.Radiobutton(
            self._frame, text="Green", variable=self._settings.nuclei_colour,
            value="green")
        self._nuclei_colour_r2.grid(column=1, row=1, sticky='NW')
        self._nuclei_colour_r3 = ttk.Radiobutton(
            self._frame, text="Red", variable=self._settings.nuclei_colour,
            value="red")
        self._nuclei_colour_r3.grid(column=1, row=2, sticky='NW')

        # Buttons for selecting the fibers channel
        self._fiber_colour_label = ttk.Label(self._frame,
                                             text="Fiber Channel :")
        self._fiber_colour_label.grid(column=0, row=3, sticky='NE',
                                      pady=(10, 0), padx=(0, 10))
        self._fiber_colour_r1 = ttk.Radiobutton(
            self._frame, text="Blue", variable=self._settings.fiber_colour,
            value="blue")
        self._fiber_colour_r1.grid(column=1, row=3, sticky='NW', pady=(10, 0))
        self._fiber_colour_r2 = ttk.Radiobutton(
            self._frame, text="Green", variable=self._settings.fiber_colour,
            value="green")
        self._fiber_colour_r2.grid(column=1, row=4, sticky='NW')
        self._fiber_colour_r3 = ttk.Radiobutton(
            self._frame, text="Red", variable=self._settings.fiber_colour,
            value="red")
        self._fiber_colour_r3.grid(column=1, row=5, sticky='NW')

        # Buttons to chose whether to save the overlay images or not
        self._overlay_label = ttk.Label(self._frame,
                                        text='Save Images with Overlay :')
        self._overlay_label.grid(column=0, row=11, sticky='NE', pady=(10, 0),
                                 padx=(0, 10))
        self._overlay_on_button = ttk.Radiobutton(
            self._frame, text="On", variable=self._settings.save_overlay,
            value=1)
        self._overlay_on_button.grid(column=1, row=11, sticky='NW',
                                     pady=(10, 0))
        self._overlay_off_button = ttk.Radiobutton(
            self._frame, text="Off", variable=self._settings.save_overlay,
            value=0)
        self._overlay_off_button.grid(column=1, row=12, sticky='NW')

        # Slider to adjust the minimum intensity for fiber detection
        self._min_fiber_int_label = ttk.Label(self._frame,
                                              text='Minimum fiber intensity :')
        self._min_fiber_int_label.grid(column=0, row=13, sticky='E',
                                       pady=(10, 0), padx=(0, 10))

        self._minimum_fiber_intensity_slider_frame = ttk.Frame(self._frame)

        self._min_fib_int_slide_val_label = ttk.Label(
            self._minimum_fiber_intensity_slider_frame,
            textvariable=self._settings.minimum_fiber_intensity,
            width=3)
        self._min_fib_int_slide_val_label.pack(
            side='left', anchor='w', fill='none', expand=False, padx=(0, 20))

        self._min_fib_int_slider = Scale(
            self._minimum_fiber_intensity_slider_frame, from_=0, to=100,
            orient="horizontal",
            variable=self._settings.minimum_fiber_intensity, showvalue=False,
            length=150, tickinterval=20)

        self._min_fib_int_slider.pack(side='left', anchor='w', fill='none',
                                      expand=False)

        self._minimum_fiber_intensity_slider_frame.grid(
            column=1, row=13, sticky='NW', pady=(10, 0))

        # Slider to adjust the maximum intensity for fiber detection
        self._max_fiber_int_label = ttk.Label(self._frame,
                                              text='Maximum fiber intensity :')
        self._max_fiber_int_label.grid(column=0, row=14, sticky='E',
                                       pady=(10, 0), padx=(0, 10))

        self._maximum_fiber_intensity_slider_frame = ttk.Frame(self._frame)

        self._max_fib_int_slide_val_label = ttk.Label(
            self._maximum_fiber_intensity_slider_frame,
            textvariable=self._settings.maximum_fiber_intensity, width=3)
        self._max_fib_int_slide_val_label.pack(
            side='left', anchor='w', fill='none', expand=False, padx=(0, 20))

        self._max_fib_int_slider = Scale(
            self._maximum_fiber_intensity_slider_frame, from_=155, to=255,
            orient="horizontal",
            variable=self._settings.maximum_fiber_intensity, showvalue=False,
            length=150, tickinterval=25)
        self._max_fib_int_slider.pack(side='left', anchor='w', fill='none',
                                      expand=False)

        self._maximum_fiber_intensity_slider_frame.grid(
            column=1, row=14, sticky='NW', pady=(10, 0))

        # Slider to adjust the minimum intensity for nuclei detection
        self._min_nucleus_int_label = ttk.Label(
            self._frame, text='Minimum nucleus intensity :')
        self._min_nucleus_int_label.grid(column=0, row=15, sticky='E',
                                         pady=(10, 0), padx=(0, 10))

        self._minimum_nuclei_intensity_slider_frame = ttk.Frame(self._frame)

        self._min_nuc_int_slide_val_label = ttk.Label(
            self._minimum_nuclei_intensity_slider_frame,
            textvariable=self._settings.minimum_nucleus_intensity, width=3)
        self._min_nuc_int_slide_val_label.pack(
            side='left', anchor='w', fill='none', expand=False, padx=(0, 20))

        self._min_nuc_int_slider = Scale(
            self._minimum_nuclei_intensity_slider_frame, from_=0, to=100,
            orient="horizontal",
            variable=self._settings.minimum_nucleus_intensity,
            showvalue=False, length=150, tickinterval=20)
        self._min_nuc_int_slider.pack(side='left', anchor='w', fill='none',
                                      expand=False)

        self._minimum_nuclei_intensity_slider_frame.grid(
            column=1, row=15, sticky='NW', pady=(10, 0))

        # Slider to adjust the maximum intensity for nuclei detection
        self._max_nucleus_int_label = ttk.Label(
            self._frame, text='Maximum nucleus intensity :')
        self._max_nucleus_int_label.grid(column=0, row=16, sticky='E',
                                         pady=(10, 0), padx=(0, 10))

        self._maximum_nuclei_intensity_slider_frame = ttk.Frame(self._frame)

        self._max_nuc_int_slide_val_label = ttk.Label(
            self._maximum_nuclei_intensity_slider_frame,
            textvariable=self._settings.maximum_nucleus_intensity, width=3)
        self._max_nuc_int_slide_val_label.pack(
            side='left', anchor='w', fill='none', expand=False, padx=(0, 20))

        self._max_nuc_int_slider = Scale(
            self._maximum_nuclei_intensity_slider_frame, from_=155, to=255,
            orient="horizontal",
            variable=self._settings.maximum_nucleus_intensity,
            showvalue=False, length=150, tickinterval=25)
        self._max_nuc_int_slider.pack(side='left', anchor='w', fill='none',
                                      expand=False)

        self._maximum_nuclei_intensity_slider_frame.grid(
            column=1, row=16, sticky='NW', pady=(10, 0))

        # Slider to adjust the minimum nucleus diameter
        self._min_nucleus_diam_label = ttk.Label(
            self._frame, text='Minimum nucleus diameter (px) :')
        self._min_nucleus_diam_label.grid(
            column=0, row=17, sticky='E', pady=(10, 0), padx=(0, 10))

        self._diameter_slider_frame = ttk.Frame(self._frame)

        self._min_nuc_diam_slide_val_label = ttk.Label(
            self._diameter_slider_frame,
            textvariable=self._settings.minimum_nuc_diameter, width=3)
        self._min_nuc_diam_slide_val_label.pack(
            side='left', anchor='w', fill='none', expand=False, padx=(0, 20))

        self._min_nuc_diam_slider = Scale(
            self._diameter_slider_frame, from_=0, to=100,
            variable=self._settings.minimum_nuc_diameter,
            orient="horizontal", length=150, showvalue=False,
            tickinterval=25)
        self._min_nuc_diam_slider.pack(side='left', anchor='w',
                                       fill='none', expand=False)

        self._diameter_slider_frame.grid(column=1, row=17, sticky='NW',
                                         pady=(10, 0))

        # Slider to adjust the minimum nucleus count
        self._min_nuclei_count_label = ttk.Label(
            self._frame, text='Minimum nuclei count :')
        self._min_nuclei_count_label.grid(
            column=0, row=18, sticky='E', pady=(10, 0), padx=(0, 10))

        self._count_slider_frame = ttk.Frame(self._frame)

        self._count_slide_val_label = ttk.Label(
            self._count_slider_frame,
            textvariable=self._settings.minimum_nuclei_count, width=3)
        self._count_slide_val_label.pack(
            side='left', anchor='w', fill='none', expand=False, padx=(0, 20))

        self._count_slider = Scale(
            self._count_slider_frame, from_=0, to=8,
            variable=self._settings.minimum_nuclei_count,
            orient="horizontal", length=150, showvalue=False,
            tickinterval=1)
        self._count_slider.pack(side='left', anchor='w',
                                fill='none', expand=False)

        self._count_slider_frame.grid(column=1, row=18, sticky='NW',
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
