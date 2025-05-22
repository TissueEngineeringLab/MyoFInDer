# coding: utf-8

from tkinter import Tk, Canvas, TclError
from PIL import ImageTk, Image
from screeninfo import get_monitors
from time import sleep
import importlib.resources as resources


class SplashWindow(Tk):
    """Window displayed while loading the software.

    It gives information about the loading status.
    """

    def __init__(self) -> None:
        """Sets a few instance attributes."""

        super().__init__()
        # On macOS, some Tkinter versions crash on this call
        try:
            self.overrideredirect(True)
        except TclError:
            pass
        self.grab_set()

        ref = (resources.files('myofinder') / 'app_images'
               / 'splash_background.png')
        with resources.as_file(ref) as path:
            self._image = Image.open(str(path))

    def resize_image(self) -> None:
        """Centers the window on the monitor currently in use."""

        size_factor = 0.35

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
        img_ratio = self._image.width / self._image.height
        scr_ratio = scr_width / scr_height

        # Resizing the window, taking into account the screen proportions
        if img_ratio > scr_ratio:
            self._image = self._image.resize(
                (int(scr_width * size_factor),
                 int(scr_width * size_factor / img_ratio)),
                Image.LANCZOS)
            self.geometry('%dx%d+%d+%d' % (
                int(scr_width * size_factor),
                int(scr_width * size_factor / img_ratio),
                x_offset + scr_width * (1 - size_factor) / 2,
                y_offset + (scr_height - int(scr_width * size_factor /
                                             img_ratio)) / 2))

        else:
            self._image = self._image.resize(
                (int(scr_height * size_factor * img_ratio),
                 int(scr_height * size_factor)),
                Image.LANCZOS)
            self.geometry('%dx%d+%d+%d' % (
                int(scr_height * size_factor * img_ratio),
                int(scr_height * size_factor),
                x_offset + (scr_width - int(scr_height * size_factor *
                                            img_ratio)) / 2,
                y_offset + scr_height * (1 - size_factor) / 2))

    def display(self):
        """Sets the layout of the window, displays it, and loads the modules.

        Returns:
            An instance of the image segmentation class.
        """

        # Sets the background of the window
        image_tk = ImageTk.PhotoImage(self._image)
        canvas = Canvas(self, bg="brown")
        canvas.create_image(0, 0, image=image_tk, anchor="nw")

        # Sets the static text of the window
        canvas.create_text(
            20, int(0.70 * self._image.height),
            anchor='w',
            text="MyoFInDer - A project of the Tissue Engineering Lab at "
                 "KU Leuven\nBy Antoine Weisrock, Rebecca Wüst and "
                 "Maria Olenic",
            fill="white",
            font='Helvetica 7 bold',
            width=self._image.width - 40)

        # Sets the dynamic text of the window
        label = canvas.create_text(
            20, int(0.9 * self._image.height),
            anchor="w",
            text='Importing dependencies...',
            fill="white",
            font='Helvetica 7 bold',
            width=self._image.width - 40)

        # Finish setting the layout
        canvas.pack(fill="both", expand=True)
        self.update()

        from ..image_segmentation import ImageSegmentation

        # Load the image segmentation and update the display
        canvas.itemconfig(label, text="Initializing Mesmer...")
        self.update()
        segmentation = ImageSegmentation()

        # Update the display before starting the software
        canvas.itemconfig(label, text="Starting program...")
        self.update()

        sleep(1)

        return segmentation
