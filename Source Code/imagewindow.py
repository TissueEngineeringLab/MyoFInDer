# -*- coding: utf-8 -*-
# Advanced zoom example. Like in Google Maps.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large
# zooms.

from tkinter import Canvas, ttk
from PIL import Image, ImageTk
from cv2 import cvtColor, imread, COLOR_BGR2RGB
from numpy import zeros
from platform import system
from functools import partial

fibre_nuclei_colour = 'yellow'  # green
non_fibre_nuclei_colour = 'red'  # 2A7DDE


class Zoom_Advanced(ttk.Frame):
    """ Advanced zoom of the image """
    def __init__(self, mainframe, main_window):
        """ Initialize the main Frame """
        super().__init__(mainframe)

        self._nuclei_table = None
        self._main_window = main_window

        self._set_layout()
        self._set_bindings()
        self._set_variables()

    def set_table(self, table_):
        self._nuclei_table = table_

    def set_channels(self):
        self._set_image()
        self._show_image()

    def set_indicators(self):

        self._delete_nuclei()
        self._delete_fibres()

        # nuclei
        if self._main_window.show_nuclei_bool.get():
            # draw
            for i, nuc in enumerate(self._nuclei):
                color = fibre_nuclei_colour if nuc[3] \
                    else non_fibre_nuclei_colour
                self._nuclei[i][2] = self._draw_nucleus(nuc[0], nuc[1], color)

        # fibers
        if self._main_window.show_fibres_bool.get():

            # draw
            for i, fibre in enumerate(self._fibres):
                self._fibres[i][2] = self._draw_fibre(fibre[0], fibre[1])

    def load_image(self, path, nuclei_positions, fibre_positions):

        # reset image
        self.reset()

        # remove all the previous nuclei
        self._delete_nuclei()
        self._nuclei = []
        self._delete_fibres()
        self._fibres = []

        # load the image
        self._image_path = path
        self._set_image()
        self._resize_to_canvas()
        self._show_image()

        # blue nuclei
        for pos in nuclei_positions[0]:
            if self._main_window.show_nuclei_bool.get():
                self._nuclei.append(
                    [pos[0], pos[1],
                     self._draw_nucleus(pos[0], pos[1],
                                        non_fibre_nuclei_colour),
                     False])
            else:
                self._nuclei.append([pos[0], pos[1], None, False])
        # green nuclei
        for pos in nuclei_positions[1]:
            if self._main_window.show_nuclei_bool.get():
                self._nuclei.append(
                    [pos[0], pos[1],
                     self._draw_nucleus(pos[0], pos[1], fibre_nuclei_colour),
                     False])
            else:
                self._nuclei.append([pos[0], pos[1], None, False])

        # fibres
        for pos in fibre_positions:
            if self._main_window.show_fibres_bool.get():
                self._fibres.append([pos[0], pos[1],
                                     self._draw_fibre(pos[0], pos[1])])
            else:
                self._fibres.append([pos[0], pos[1], (None, None)])

    def reset(self):
        # reset the canvas
        self._image = None  # open image
        self._img_scale = 1.0  # scale for the canvas image
        self._can_scale = 1.0
        self._delta = 1.3  # zoom delta
        self._current_zoom = 0
        self._delete_nuclei()
        self._delete_fibres()
        self._nuclei = []
        if self._image_id is not None:
            self._canvas.delete(self._image_id)
        self._image_id = None
        # Put image into container rectangle and use it to set proper
        # coordinates to the image

        # show
        self._show_image()
    
    def _delete_nuclei(self):
        for nuc in self._nuclei:
            self._canvas.delete(nuc[2])
    
    def _delete_fibres(self):
        for fibre in self._fibres:
            self._canvas.delete(fibre[2][0])
            self._canvas.delete(fibre[2][1])

    def _set_layout(self):
        self.pack(expand=True, fill="both", anchor="w", side="left",
                  padx=5, pady=5)
        self._hbar_frame = ttk.Frame(self)
        self._hbar_frame.pack(expand=False, fill="x", anchor="s",
                              side="bottom")

        # Create canvas and put image on it
        self._canvas = Canvas(self,
                              highlightthickness=3,
                              highlightbackground="black")
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))
        self._canvas.pack(expand=True, fill="both", side='left')

        self._vbar = ttk.Scrollbar(self, orient="vertical")
        self._vbar.pack(fill='y', side='right')
        self._vbar.config(command=self._canvas.yview)
        self._canvas.config(yscrollcommand=self._vbar.set)

        self._hbar = ttk.Scrollbar(self._hbar_frame, orient="horizontal")
        self._hbar.pack(fill='x')
        self._hbar.config(command=self._canvas.xview)
        self._canvas.config(xscrollcommand=self._hbar.set)

        self._canvas.update()  # wait till canvas is create

    def _set_bindings(self):
        # Bind events to the Canvas
        self._canvas.bind('<Configure>', self._show_image)  # canvas is resized
        self._canvas.bind('<ButtonPress-2>', self._move_from)
        self._canvas.bind('<B2-Motion>', self._move_to)

        if system() == "Linux":
            self._canvas.bind('<4>', self._zoom)
            self._canvas.bind('<5>', self._zoom)
        else:
            self._canvas.bind('<MouseWheel>', self._zoom)

        self.bind_all('<Left>', partial(self._arrows, arrow_index=0))
        self.bind_all('<Right>', partial(self._arrows, arrow_index=1))
        self.bind_all('<Up>', partial(self._arrows, arrow_index=2))
        self.bind_all('<Down>', partial(self._arrows, arrow_index=3))

        self.bind_all('=', partial(self._zoom, delta=1))
        self.bind_all('+', partial(self._zoom, delta=1))
        self.bind_all('-', partial(self._zoom, delta=-1))
        self.bind_all('_', partial(self._zoom, delta=-1))

        self._canvas.bind('<ButtonPress-1>', self._left_click)
        self._canvas.bind('<ButtonPress-3>', self._right_click)

    def _set_variables(self):
        self._image = None  # open image
        self._image_path = ""
        self._img_scale = 1.0  # scale for the canvas image
        self._can_scale = 1.0
        self._delta = 1.3  # zoom delta
        self._current_zoom = 0
        self._nuclei = []
        self._fibres = []
        self._image_id = None

    def _draw_nucleus(self, unscaled_x, unscaled_y, color):

        radius = max(int(3.0 * self._can_scale), 1)

        x = unscaled_x * self._img_scale
        y = unscaled_y * self._img_scale
        return self._canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline='#fff', width=0)

    def _draw_fibre(self, unscaled_x, unscaled_y):

        square_size = max(int(10.0 * self._can_scale), 1)

        x = unscaled_x * self._img_scale
        y = unscaled_y * self._img_scale
        hor_line = self._canvas.create_line(x + square_size, y,
                                            x - square_size, y,
                                            width=2,
                                            fill='red')
        ver_line = self._canvas.create_line(x, y + square_size, x,
                                            y - square_size, width=2,
                                            fill='red')
        return hor_line, ver_line

    def _left_click(self, event):

        if self._image is not None:

            can_x = self._canvas.canvasx(event.x)
            can_y = self._canvas.canvasy(event.y)

            if can_x >= self._image.width * self._img_scale or \
                    can_y >= self._image.height * self._img_scale:
                return

            # coordinaten tov de foto
            rel_x_scale = can_x / self._img_scale
            rel_y_scale = can_y / self._img_scale

            if self._main_window.draw_nuclei and \
                    self._main_window.show_nuclei_bool.get():
                # find a close nuclei
                closest_nucleus_index, closest_nucleus_obj = \
                    self._find_closest_nucleus(rel_x_scale, rel_y_scale)
                if closest_nucleus_index is not None:
                    # convert the nucleus from blue to green
                    if not self._nuclei[closest_nucleus_index][3]:
                        self._canvas.itemconfig(closest_nucleus_obj,
                                                fill=fibre_nuclei_colour)
                        self._nuclei[closest_nucleus_index][3] = True
                        self._nuclei_table.to_green(
                            [self._nuclei[closest_nucleus_index][0],
                             self._nuclei[closest_nucleus_index][1]])
                    else:
                        self._canvas.itemconfig(closest_nucleus_obj,
                                                fill=non_fibre_nuclei_colour)
                        self._nuclei[closest_nucleus_index][3] = False
                        self._nuclei_table.to_blue(
                            [self._nuclei[closest_nucleus_index][0],
                             self._nuclei[closest_nucleus_index][1]])

                # otherwise, add a new nucleus
                else:
                    self._nuclei_table.add_blue([rel_x_scale, rel_y_scale])
                    self._nuclei.append(
                        [rel_x_scale, rel_y_scale,
                         self._draw_nucleus(rel_x_scale, rel_y_scale,
                                            non_fibre_nuclei_colour),
                         False])

                self._main_window.set_unsaved_status()

            elif self._main_window.show_fibres_bool.get():
                # find a close fibre
                closest_fiber_index, _ = \
                    self._find_closest_fibre(rel_x_scale, rel_y_scale)
                if closest_fiber_index is None:
                    self._fibres.append([rel_x_scale, rel_y_scale,
                                         self._draw_fibre(rel_x_scale,
                                                          rel_y_scale)])
                    self._nuclei_table.add_fibre([rel_x_scale, rel_y_scale])

                    self._main_window.set_unsaved_status()

    def _right_click(self, event):

        if self._image is not None:

            can_x = self._canvas.canvasx(event.x)
            can_y = self._canvas.canvasy(event.y)

            if can_x >= self._image.width * self._img_scale or \
                    can_y >= self._image.height * self._img_scale:
                return

            # coordinaten tov de foto
            rel_x_scale = can_x / self._img_scale
            rel_y_scale = can_y / self._img_scale

            # find a close nuclei
            if self._main_window.draw_nuclei and \
                    self._main_window.show_nuclei_bool.get():
                closest_nucleus_index, closest_nucleus_obj = \
                    self._find_closest_nucleus(rel_x_scale, rel_y_scale)
                if closest_nucleus_index is not None:

                    # delete it
                    if self._nuclei[closest_nucleus_index][3]:
                        self._nuclei_table.remove_green(
                            [self._nuclei[closest_nucleus_index][0],
                             self._nuclei[closest_nucleus_index][1]])
                    else:
                        self._nuclei_table.remove_blue(
                            [self._nuclei[closest_nucleus_index][0],
                             self._nuclei[closest_nucleus_index][1]])

                    del self._nuclei[closest_nucleus_index]
                    self._canvas.delete(closest_nucleus_obj)

                    self._main_window.set_unsaved_status()

            elif self._main_window.show_fibres_bool.get():

                # find the closest fibre
                closest_fibre_index, closest_fibre_obj = \
                    self._find_closest_fibre(rel_x_scale, rel_y_scale)
                if closest_fibre_index is not None:

                    # delete it
                    self._nuclei_table.remove_fibre(
                        [self._fibres[closest_fibre_index][0],
                         self._fibres[closest_fibre_index][1]])
                    del self._fibres[closest_fibre_index]
                    self._canvas.delete(closest_fibre_obj[0])
                    self._canvas.delete(closest_fibre_obj[1])

                    self._main_window.set_unsaved_status()

    def _find_closest_fibre(self, x, y):
        # find the closest fiber
        radius = max(9.0 * self._can_scale / self._img_scale, 9.0)
        closest_index = None
        closest_distance = None
        for i, fiber in enumerate(self._fibres):
            if abs(x - fiber[0]) <= radius and \
                    abs(y - fiber[1]) <= radius:
                dis_sq = (fiber[0] - x) ** 2 + (fiber[1] - y) ** 2
                if closest_distance is None or dis_sq < closest_distance:
                    closest_index = i
                    closest_distance = dis_sq
        if closest_index is not None:
            return closest_index, self._fibres[closest_index][2]
        return None, None

    def _find_closest_nucleus(self, x, y):
        # find the closest nucleus
        radius = max(3.0 * self._can_scale / self._img_scale, 3.0)
        closest_index = None
        closest_distance = None
        for i, nucleus in enumerate(self._nuclei):
            if abs(x - nucleus[0]) <= radius and \
                    abs(y - nucleus[1]) <= radius:
                dis_sq = (nucleus[0] - x) ** 2 + (nucleus[1] - y) ** 2
                if closest_distance is None or dis_sq < closest_distance:
                    closest_index = i
                    closest_distance = dis_sq
        if closest_index is not None:
            return closest_index, self._nuclei[closest_index][2]
        return None, None

    def _set_image(self):
        # load the image with the correct channels
        if self._image_path:
            cv_img = cvtColor(imread(self._image_path), COLOR_BGR2RGB)
            if not self._main_window.red_channel_bool.get():
                cv_img[:, :, 0] = zeros([cv_img.shape[0], cv_img.shape[1]])
            if not self._main_window.green_channel_bool.get():
                cv_img[:, :, 1] = zeros([cv_img.shape[0], cv_img.shape[1]])
            if not self._main_window.blue_channel_bool.get():
                cv_img[:, :, 2] = zeros([cv_img.shape[0], cv_img.shape[1]])
            image_in = Image.fromarray(cv_img)

            self._image = image_in

    def _resize_to_canvas(self):
        can_width = self._canvas.winfo_width()
        can_height = self._canvas.winfo_height()
        can_ratio = can_width / can_height
        img_ratio = self._image.width / self._image.height
        if img_ratio >= can_ratio:
            resize_width = can_width
        else:
            resize_width = int(can_height * img_ratio)

        self._img_scale = resize_width / self._image.width

    def _arrows(self, _, arrow_index):

        if arrow_index == 0:
            self._canvas.xview_scroll(-1, "units")
        elif arrow_index == 1:
            self._canvas.xview_scroll(1, "units")
        elif arrow_index == 2:
            self._canvas.yview_scroll(-1, "units")
        elif arrow_index == 3:
            self._canvas.yview_scroll(1, "units")

        self._show_image()  # redraw the image

    def _move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        if self._image is not None:
            self._canvas.scan_mark(event.x, event.y)
            self._show_image()  # redraw the image

    def _move_to(self, event):
        """ Drag (move) canvas to the new position """
        if self._image is not None:
            self._canvas.scan_dragto(event.x, event.y, gain=1)
            self._show_image()  # redraw the image

    def _zoom(self, event, delta=None):
        if self._image is not None:
            if delta is None:
                if system() == "Linux":
                    delta = 1 if event.num == 4 else -1
                else:
                    delta = int(event.delta / abs(event.delta))

            scale = 1.0
            # Respond to Linux (event.num) or Windows (event.delta) wheel event
            if delta < 0:  # scroll down
                if self._current_zoom < -4:
                    return  # image is less than 30 pixels
                self._img_scale /= self._delta
                self._can_scale /= self._delta
                scale /= self._delta
                self._current_zoom -= 1
            elif delta > 0:  # scroll up
                if self._current_zoom > 4:
                    return  # Arbitrary zoom limit
                self._img_scale *= self._delta
                self._can_scale *= self._delta
                scale *= self._delta
                self._current_zoom += 1
            self._canvas.scale('all', 0, 0, scale, scale)  # rescale all the
            # elements in the image
            self._show_image()

    def _show_image(self, *_, **__):
        if self._image is not None:
            scaled_x = int(self._image.width * self._img_scale)
            scaled_y = int(self._image.height * self._img_scale)
            image = self._image.resize((scaled_x, scaled_y))
            image_tk = ImageTk.PhotoImage(image)
            self._image_id = self._canvas.create_image(0, 0, anchor='nw',
                                                       image=image_tk)
            self._canvas.lower(self._image_id)  # set image into background
            self._canvas.image_tk = image_tk
            self._canvas.configure(scrollregion=(0, 0, scaled_x, scaled_y))
