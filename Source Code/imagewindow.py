# -*- coding: utf-8 -*-
# Advanced zoom example. Like in Google Maps.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large
# zooms.

from tkinter import UNITS, Canvas, ttk, Scrollbar
from PIL import Image, ImageTk
from cv2 import cvtColor, imread, COLOR_BGR2RGB
from numpy import zeros
from platform import system

fibreNucleiColour = 'yellow'  # green
nonFibreNucleiColour = 'red'  # 2A7DDE


class Zoom_Advanced:
    """ Advanced zoom of the image """
    def __init__(self, mainframe, nuclei_table=None):
        """ Initialize the main Frame """
        self.nucleiTable = nuclei_table
        self.master = mainframe

        self.img_frame = ttk.Frame(self.master)
        self.img_frame.pack(expand=True, fill="both", anchor="w", side="left",
                            padx=5, pady=5)
        self.hbar_frame = ttk.Frame(self.img_frame)
        self.hbar_frame.pack(expand=False, fill="x", anchor="s", side="bottom")

        # Create canvas and put image on it
        self.canvas = Canvas(self.img_frame,
                             highlightthickness=3,
                             highlightbackground="black")
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.canvas.pack(expand=True, fill="both", side='left')

        self.vbar = Scrollbar(self.img_frame, orient="vertical")
        self.vbar.pack(fill='y', side='right')
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vbar.set)

        self.hbar = Scrollbar(self.hbar_frame, orient="horizontal")
        self.hbar.pack(fill='x')
        self.hbar.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.hbar.set)

        self.canvas.update()  # wait till canvas is create
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-2>', self.move_from)
        self.canvas.bind('<B2-Motion>',     self.move_to)
        if system() == "Linux":
            self.canvas.bind('<4>', self.wheel)
            self.canvas.bind('<5>', self.wheel)
        else:
            self.canvas.bind('<MouseWheel>', self.wheel)
        self.image = None  # open image
        self.imagePath = ""
        self.channelsRGB = (False, False, False)
        self.indicatorsNF = (False, False)
        self.indicatingNuclei = True
        self.imscale = 1.0  # scale for the canvas image
        self.canscale = 1.0
        self.delta = 1.3  # zoom delta
        self._zoom = 0
        self.nuclei = []
        self.fibres = []
        self.imageId = None
        # Put image into container rectangle and use it to set proper
        # coordinates to the image

    def set_table(self, table_):
        self.nucleiTable = table_

    def set_which_indcation(self, is_nuclei):
        self.indicatingNuclei = is_nuclei

    def left_click(self, widget, rel_x, rel_y):

        canvas_name = str(self.canvas.winfo_pathname(self.canvas.winfo_id()))

        if self.image is not None and widget == canvas_name:

            can_x = self.canvas.canvasx(rel_x)
            can_y = self.canvas.canvasy(rel_y)

            if can_x >= self.image.width * self.imscale or \
                    can_y >= self.image.height * self.imscale:
                return

            # put white nucleus or set from blue to green
            radius = max(int(3.0 * self.canscale), 1)
            square_size = max(int(9.0 * self.canscale), 1)

            # coordinaten tov de foto
            rel_x_scale = can_x / self.imscale
            rel_y_scale = can_y / self.imscale

            if self.indicatingNuclei and self.indicatorsNF[0]:
                # find a close nuclei
                closest_nuclei_index, closest_nuclei_id = \
                    self._find_closest_nuclei(rel_x_scale, rel_y_scale)
                if closest_nuclei_index != -1:
                    # convert the nucleus from blue to green
                    if not self.nuclei[closest_nuclei_index][3]:
                        self.canvas.itemconfig(closest_nuclei_id,
                                               fill=fibreNucleiColour)
                        self.nuclei[closest_nuclei_index][3] = True
                        self.nucleiTable.to_green(
                            [self.nuclei[closest_nuclei_index][0],
                             self.nuclei[closest_nuclei_index][1]])
                    else:
                        self.canvas.itemconfig(closest_nuclei_id,
                                               fill=nonFibreNucleiColour)
                        self.nuclei[closest_nuclei_index][3] = False
                        self.nucleiTable.to_blue(
                            [self.nuclei[closest_nuclei_index][0],
                             self.nuclei[closest_nuclei_index][1]])
                    return True

                # otherwise, add a new nucleus
                elif rel_y_scale >= 0 and rel_x_scale >= 0:
                    self.nucleiTable.add_blue([rel_x_scale, rel_y_scale])
                    new_oval = self.canvas.create_oval(
                        can_x - radius, can_y - radius, can_x + radius,
                        can_y + radius,
                        fill=nonFibreNucleiColour, outline='#fff', width=0)
                    # #65ADF5#2A7DDE (blue) #2B8915 (green)
                    self.nuclei.append([rel_x_scale, rel_y_scale,
                                        new_oval, False])
                    return True
                return False

            elif self.indicatorsNF[1]:
                # find a close fibre
                closest_fiber_index, closest_fiber_id = \
                    self._find_closest_fibre(rel_x_scale, rel_y_scale)
                if closest_fiber_index == -1 and rel_y_scale >= 0 \
                        and rel_x_scale >= 0:
                    # newRect = self.canvas.create_rectangle(
                    #     can_x - square_size,
                    #     can_y - square_size,can_x + square_size,
                    #     can_y + square_size,
                    #     fill='red', outline='#fff', width=2) # #2A7DDE (blue)
                    # #2B8915 (green)
                    hor_line = self.canvas.create_line(
                        can_x + square_size, can_y, can_x - square_size, can_y,
                        width=2, fill='red')
                    ver_line = self.canvas.create_line(
                        can_x, can_y + square_size, can_x, can_y - square_size,
                        width=2, fill='red')
                    self.fibres.append([rel_x_scale, rel_y_scale,
                                        (hor_line, ver_line)])
                    self.nucleiTable.add_fibre([rel_x_scale, rel_y_scale])
                    return True

        return False

    def right_click(self, widget, rel_x, rel_y):

        canvas_name = str(self.canvas.winfo_pathname(self.canvas.winfo_id()))

        if self.image is not None and widget == canvas_name:

            can_x = self.canvas.canvasx(rel_x)
            can_y = self.canvas.canvasy(rel_y)

            if can_x >= self.image.width * self.imscale or \
                    can_y >= self.image.height * self.imscale:
                return

            # coordinaten tov de foto
            rel_x_scale = can_x / self.imscale
            rel_y_scale = can_y / self.imscale

            # find a close nuclei
            if self.indicatingNuclei and self.indicatorsNF[0]:
                closest_nuclei_index, closest_nuclei_id = \
                    self._find_closest_nuclei(rel_x_scale, rel_y_scale)
                if closest_nuclei_index != -1:

                    # delete it
                    if self.nuclei[closest_nuclei_index][3]:
                        self.nucleiTable.remove_green(
                            [self.nuclei[closest_nuclei_index][0],
                             self.nuclei[closest_nuclei_index][1]])
                    else:
                        self.nucleiTable.remove_blue(
                            [self.nuclei[closest_nuclei_index][0],
                             self.nuclei[closest_nuclei_index][1]])

                    del self.nuclei[closest_nuclei_index]
                    self.canvas.delete(closest_nuclei_id)
                    return True

            elif self.indicatorsNF[1]:

                # find closest fibre
                closest_fibre_index, closest_fibre_id = \
                    self._find_closest_fibre(rel_x_scale, rel_y_scale)
                if closest_fibre_index != -1:

                    # delete it
                    self.nucleiTable.remove_fibre(
                        [self.fibres[closest_fibre_index][0],
                         self.fibres[closest_fibre_index][1]])
                    del self.fibres[closest_fibre_index]
                    self.canvas.delete(closest_fibre_id[0])
                    self.canvas.delete(closest_fibre_id[1])
                    return True

        return False

    def _find_closest_fibre(self, x, y):
        # find the closest fiber
        radius = max(9.0 * self.canscale / self.imscale, 9.0)
        closest_index = -1
        closest_distance_sq = -1
        for i, fiber in enumerate(self.fibres):
            if abs(x - fiber[0]) <= radius and \
                    abs(y - fiber[1]) <= radius:
                dis_sq = (fiber[0] - x) ** 2 + (fiber[1] - y) ** 2
                if dis_sq < closest_distance_sq or closest_distance_sq < 0:
                    closest_index = i
                    closest_distance_sq = dis_sq
        if closest_index != -1:
            return closest_index, self.fibres[closest_index][2]
        return -1, -1

    def _find_closest_nuclei(self, x, y):
        # find the closest nucleus
        radius = max(3.0 * self.canscale / self.imscale, 3.0)
        closest_index = -1
        closest_distance_sq = -1
        for i, nucleus in enumerate(self.nuclei):
            if abs(x - nucleus[0]) <= radius and \
                    abs(y - nucleus[1]) <= radius:
                dis_sq = (nucleus[0] - x) ** 2 + (nucleus[1] - y) ** 2
                if dis_sq < closest_distance_sq or closest_distance_sq < 0:
                    closest_index = i
                    closest_distance_sq = dis_sq
        if closest_index != -1:
            return closest_index, self.nuclei[closest_index][2]
        return -1, -1

    def set_channels(self, b, g, r):
        self.channelsRGB = (r, g, b)
        self._set_image(rgb=True)
        self.show_image()

    def _set_image(self, rgb=False):
        # load the image with the correct channels
        if self.imagePath:
            cv_img = cvtColor(imread(self.imagePath), COLOR_BGR2RGB)
            if not self.channelsRGB[0]:
                cv_img[:, :, 0] = zeros([cv_img.shape[0], cv_img.shape[1]])
            if not self.channelsRGB[1]:
                cv_img[:, :, 1] = zeros([cv_img.shape[0], cv_img.shape[1]])
            if not self.channelsRGB[2]:
                cv_img[:, :, 2] = zeros([cv_img.shape[0], cv_img.shape[1]])
            image_in = Image.fromarray(cv_img)

            can_width = self.canvas.winfo_width()
            can_height = self.canvas.winfo_height()
            can_ratio = can_width / can_height
            img_ratio = image_in.width / image_in.height
            if img_ratio >= can_ratio:
                resize = (can_width, int(can_width / img_ratio))
            else:
                resize = (int(can_height * img_ratio), can_height)
            # self.image = image_in.resize(resize)  # open image
            self.image = image_in
            if not rgb:
                self.imscale = resize[0] / image_in.width

    def set_indicators(self, nuclei, fibres):

        # nuclei
        if not nuclei:
            for nuc in self.nuclei:
                self.canvas.delete(nuc[2])
        elif not self.indicatorsNF[0]:

            radius = max(int(3.0 * self.canscale), 1)
            # coordinaten van linkerbovenhoek van de foto tov de window

            # draw
            for i, nuc in enumerate(self.nuclei):
                color = nonFibreNucleiColour
                if nuc[3]:
                    color = fibreNucleiColour
                x = nuc[0] * self.imscale
                y = nuc[1] * self.imscale
                new_oval = self.canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius,
                    fill=color, outline='#fff', width=0)
                # #2A7DDE (blue) #2B8915 (green)
                self.nuclei[i][2] = new_oval

        # fibers
        if not fibres:
            for fib in self.fibres:
                self.canvas.delete(fib[2][0])
                self.canvas.delete(fib[2][1])
        elif not self.indicatorsNF[1]:

            square_size = max(int(10.0 * self.canscale), 1)
            # coordinaten van linkerbovenhoek van de foto tov de window

            # draw
            for i, fibre in enumerate(self.fibres):
                x = fibre[0] * self.imscale
                y = fibre[1] * self.imscale
                hor_line = self.canvas.create_line(x + square_size, y,
                                                   x - square_size, y, width=2,
                                                   fill='red')
                ver_line = self.canvas.create_line(x, y + square_size, x,
                                                   y - square_size, width=2,
                                                   fill='red')
                self.fibres[i][2] = (hor_line, ver_line)

        self.indicatorsNF = (nuclei, fibres)

    def get_indicators(self):
        return self.indicatorsNF

    def load_image(self, path, nuclei_positions, fibre_positions):

        # reset image
        self.reset()

        # remove all the previous nuclei
        for nucleus in self.nuclei:
            self.canvas.delete(nucleus[2])
        self.nuclei = []
        for fibre in self.fibres:
            self.canvas.delete(fibre[2][0])
            self.canvas.delete(fibre[2][1])
        self.fibres = []

        # load the image
        self.imagePath = path
        self._set_image()

        # draw the nuclei on the screen
        radius = max(int(3.0 * self.canscale), 1)
        square_size = max(int(10.0 * self.canscale), 1)
        # coordinaten van linkerbovenhoek van de foto tov de window

        # blue nuclei
        for position in nuclei_positions[0]:
            x = position[0] * self.imscale
            y = position[1] * self.imscale
            new_oval = None
            if self.indicatorsNF[0]:
                new_oval = self.canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius,
                    fill=nonFibreNucleiColour, outline='#fff', width=0)
                # #2A7DDE (blue) #2B8915 (green)
            self.nuclei.append([position[0], position[1], new_oval, False])
        # green nuclei
        for position in nuclei_positions[1]:
            x = position[0] * self.imscale
            y = position[1] * self.imscale
            new_oval = None
            if self.indicatorsNF[0]:
                new_oval = self.canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius,
                    fill=fibreNucleiColour, outline='#fff', width=0)
                # #2A7DDE (blue) #2B8915 (green)
            self.nuclei.append([position[0], position[1], new_oval, True])

        # fibres
        for position in fibre_positions:
            x = position[0] * self.imscale
            y = position[1] * self.imscale
            hor_line = None
            ver_line = None
            if self.indicatorsNF[1]:
                # newrect = self.canvas.create_rectangle(x - square_size,
                # y - square_size,x + square_size, y + square_size, fill='red',
                # outline='#fff', width=2) # #2A7DDE (blue) #2B8915 (green)
                hor_line = self.canvas.create_line(
                    x + square_size, y, x - square_size, y, width=2,
                    fill='red')
                ver_line = self.canvas.create_line(
                    x, y + square_size, x, y - square_size, width=2,
                    fill='red')
            self.fibres.append([position[0], position[1],
                                (hor_line, ver_line)])

        # show the image
        self.show_image()

    def reset(self):
        # reset the canvas
        self.image = None  # open image
        self.imscale = 1.0  # scale for the canvas image
        self.canscale = 1.0
        self.delta = 1.3  # zoom delta
        self._zoom = 0
        for nuc in self.nuclei:
            self.canvas.delete(nuc[2])
        for fibre in self.fibres:
            self.canvas.delete(fibre[2][0])
            self.canvas.delete(fibre[2][1])
        self.nuclei = []
        self.canvas.delete(self.imageId)
        self.imageId = None
        # Put image into container rectangle and use it to set proper
        # coordinates to the image

        # show
        self.show_image()

    def arrows(self, arrow_index):

        # use the arrow keys to scroll around the image
        self.canvas.configure(yscrollincrement='110')
        self.canvas.configure(xscrollincrement='160')

        self.canvas.xview_scroll(1, UNITS)
        self.canvas.yview_scroll(1, UNITS)
        if arrow_index == 2:
            self.canvas.yview_scroll(-1, UNITS)
        elif arrow_index == 3:
            self.canvas.xview_scroll(-1, UNITS)
        elif arrow_index == 0:
            self.canvas.xview_scroll(-2, UNITS)
            self.canvas.yview_scroll(-1, UNITS)
        elif arrow_index == 1:
            self.canvas.xview_scroll(-1, UNITS)
            self.canvas.yview_scroll(-2, UNITS)

        self.show_image()  # redraw the image

        self.canvas.configure(yscrollincrement='0')
        self.canvas.configure(xscrollincrement='0')

    def move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        if self.image is not None:
            self.canvas.scan_mark(event.x, event.y)
            self.show_image()  # redraw the image

    def move_to(self, event):
        """ Drag (move) canvas to the new position """
        if self.image is not None:
            self.canvas.scan_dragto(event.x, event.y, gain=1)
            self.show_image()  # redraw the image

    def zoom(self, widget, delta, wheel=False):
        if self.image is not None:
            canvas_name = str(
                self.canvas.winfo_pathname(self.canvas.winfo_id()))
            if wheel and canvas_name != widget:
                return  # zoom only inside image area

            scale = 1.0
            # Respond to Linux (event.num) or Windows (event.delta) wheel event
            if delta < 0:  # scroll down
                if self._zoom < -4:
                    return  # image is less than 30 pixels
                self.imscale /= self.delta
                self.canscale /= self.delta
                scale /= self.delta
                self._zoom -= 1
            elif delta > 0:  # scroll up
                if self._zoom > 4:
                    return  # Arbitrary zoom limit
                self.imscale *= self.delta
                self.canscale *= self.delta
                scale *= self.delta
                self._zoom += 1
            self.canvas.scale('all', 0, 0, scale, scale)  # rescale all the
            # elements in the image
            self.show_image()

    def wheel(self, event):
        """ Zoom with mouse wheel """
        if system() == "Linux":
            self.zoom(str(event.widget),
                      1 if event.num == 4 else -1, wheel=True)
        else:
            self.zoom(str(event.widget), event.delta, wheel=True)

    def show_image(self, *_, **__):
        if self.image is not None:
            scaled_x = int(self.image.width * self.imscale)
            scaled_y = int(self.image.height * self.imscale)
            image = self.image.resize((scaled_x, scaled_y))
            imagetk = ImageTk.PhotoImage(image)
            self.imageId = self.canvas.create_image(0, 0, anchor='nw',
                                                    image=imagetk)
            self.canvas.lower(self.imageId)  # set image into background
            self.canvas.imagetk = imagetk
            self.canvas.configure(scrollregion=(0, 0, scaled_x, scaled_y))
