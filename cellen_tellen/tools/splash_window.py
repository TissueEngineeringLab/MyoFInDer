# coding: utf-8

from tkinter import Tk, Canvas
from PIL import ImageTk, Image
from screeninfo import get_monitors
from time import sleep

from ..image_segmentation import Image_segmentation


class Splash_window(Tk):

    def __init__(self, main_window):
        super().__init__()
        self.overrideredirect(True)
        self.grab_set()

        self._image = Image.open(main_window.base_path / 'app_images' /
                                 "splash_background.png")

    def resize_image(self):
        size_factor = 0.35

        monitors = get_monitors()
        candidates = [monitor for monitor in monitors if
                      0 <= self.winfo_x() - monitor.x <= monitor.width and
                      0 <= self.winfo_y() - monitor.y <= monitor.height]
        current_monitor = candidates[0] if candidates else monitors[0]
        scr_width = current_monitor.width
        scr_height = current_monitor.height
        x_offset = current_monitor.x
        y_offset = current_monitor.y
        img_ratio = self._image.width / self._image.height
        scr_ratio = scr_width / scr_height

        if img_ratio > scr_ratio:
            self._image = self._image.resize(
                (int(scr_width * size_factor),
                 int(scr_width * size_factor / img_ratio)),
                Image.ANTIALIAS)
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
                Image.ANTIALIAS)
            self.geometry('%dx%d+%d+%d' % (
                int(scr_height * size_factor * img_ratio),
                int(scr_height * size_factor),
                x_offset + (scr_width - int(scr_height * size_factor *
                                            img_ratio)) / 2,
                y_offset + scr_height * (1 - size_factor) / 2))

    def display(self):
        image_tk = ImageTk.PhotoImage(self._image)
        self._canvas = Canvas(self, bg="brown")
        self._canvas.create_image(0, 0, image=image_tk, anchor="nw")
        self._canvas.create_text(
            20, int(0.70 * self._image.height),
            anchor='w',
            text="Cellen Tellen - A P&O project by Quentin De Rore, Ibrahim El"
                 " Kaddouri, Emiel Vanspranghels and Henri Vermeersch, "
                 "assisted by Desmond Kabus, Rebecca Wüst and Maria Olenic",
            fill="white",
            font='Helvetica 7 bold',
            width=self._image.width - 40)

        self._loading_label = self._canvas.create_text(
            20, int(0.9 * self._image.height),
            anchor="w",
            text='Importing dependencies...',
            fill="white",
            font='Helvetica 7 bold',
            width=self._image.width - 40)

        self._canvas.pack(fill="both", expand=True)
        self.update()

        sleep(1)

        self._canvas.itemconfig(self._loading_label,
                                text="Initialising Mesmer...")
        self.update()
        segmentation = Image_segmentation()

        self._canvas.itemconfig(self._loading_label,
                                text="Starting program...")
        self.update()

        sleep(1)

        return segmentation
