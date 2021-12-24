# -*- coding: utf-8 -*-
# Advanced zoom example. Like in Google Maps.
# It zooms only a tile, but not the whole image. So the zoomed tile occupies
# constant memory and not crams it with a huge resized image for the large
# zooms.

import tkinter as tk
from PIL import Image, ImageTk
import table
import cv2
import PIL.Image
import PIL.ImageTk
import numpy as np

fibreNucleiColour = 'yellow'  # green
nonFibreNucleiColour = 'red'  # 2A7DDE


class Zoom_Advanced:
    """ Advanced zoom of the image """
    def __init__(self, mainframe, nucleiTable):
        """ Initialize the main Frame """
        self.nucleiTable = nucleiTable
        self.master = mainframe

        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, width=table.ImageCanvasSize[0],
                                height=table.ImageCanvasSize[1],
                                highlightthickness=3,
                                highlightbackground="black")
        self.canvas.grid(column=0, row=0, sticky=(tk.N, tk.W))
        self.canvas.update()  # wait till canvas is create
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-2>', self.move_from)
        self.canvas.bind('<B2-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and
        # MacOS, but not Linux
        self.image = None  # open image
        self.imagePath = ""
        self.channelsRGB = (False, False, False)
        self.indicatorsNF = (False, False)
        self.indicatingNuclei = True
        self.width, self.height = table.ImageCanvasSize
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom delta
        self.nuclei = []
        self.fibres = []
        self.imageId = None
        # Put image into container rectangle and use it to set proper
        # coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width,
                                                      self.height, width=0)

    def updateSize(self, size):
        self.canvas.config(width=size[0], height=size[1])
        self.width, self.height = size

    def setTable(self, table):
        self.nucleiTable = table

    def setWhichIndcation(self, isNuclei):
        self.indicatingNuclei = isNuclei

    def leftClick(self, windowX, windowY, frmStart):

        eventx = windowX - 1
        eventy = windowY - frmStart
        if self.image is not None and eventy < table.ImageCanvasSize[1] and \
                eventx < table.ImageCanvasSize[0]:

            # put white nucleus or set from blue to green
            radius = int(3.0 * self.imscale)
            square_size = int(9.0 * self.imscale)
            x = self.canvas.canvasx(eventx)
            y = self.canvas.canvasy(eventy)

            # coordinaten van linkerbovenhoek van de foto tov de window
            top_left_x = self.canvas.coords(self.container)[0] - \
                self.canvas.canvasx(0)
            top_left_y = self.canvas.coords(self.container)[1] - \
                self.canvas.canvasy(0)

            # coordinaten tov de foto
            photo_x = (eventx - top_left_x) / (self.width * self.imscale)
            photo_y = (eventy - top_left_y) / (self.height * self.imscale)

            if self.indicatingNuclei and self.indicatorsNF[0]:
                # find a close nuclei
                closest_nuclei_index, closest_nuclei_id = \
                    self.findClosestNuclei(photo_x, photo_y)
                if closest_nuclei_index != -1:
                    # convert the nucleus from blue to green
                    if not self.nuclei[closest_nuclei_index][3]:
                        self.canvas.itemconfig(closest_nuclei_id,
                                               fill=fibreNucleiColour)
                        self.nuclei[closest_nuclei_index][3] = True
                        self.nucleiTable.toGreen(
                            [self.nuclei[closest_nuclei_index][0],
                             self.nuclei[closest_nuclei_index][1]])
                    else:
                        self.canvas.itemconfig(closest_nuclei_id,
                                               fill=nonFibreNucleiColour)
                        self.nuclei[closest_nuclei_index][3] = False
                        self.nucleiTable.toBlue(
                            [self.nuclei[closest_nuclei_index][0],
                             self.nuclei[closest_nuclei_index][1]])
                    return True

                # otherwise, add a new nucleus
                elif photo_y >= 0 and photo_x >= 0:
                    self.nucleiTable.addBlue([photo_x, photo_y])
                    new_oval = self.canvas.create_oval(
                        x - radius, y - radius, x + radius, y + radius,
                        fill=nonFibreNucleiColour, outline='#fff', width=0)
                    # #65ADF5#2A7DDE (blue) #2B8915 (green)
                    self.nuclei.append([photo_x, photo_y, new_oval, False])
                    return True
                return False

            elif self.indicatorsNF[1]:
                # find a close fibre
                closest_fiber_index, closest_fiber_id = \
                    self.findClosestFibre(photo_x, photo_y)
                if closest_fiber_index == -1 and photo_y >= 0 and photo_x >= 0:
                    # newRect = self.canvas.create_rectangle(x - square_size,
                    # y - square_size,x + square_size, y + square_size,
                    # fill='red', outline='#fff', width=2) # #2A7DDE (blue)
                    # #2B8915 (green)
                    hor_line = self.canvas.create_line(x + square_size, y,
                                                       x - square_size, y,
                                                       width=2, fill='red')
                    ver_line = self.canvas.create_line(x, y + square_size,
                                                       x, y - square_size,
                                                       width=2, fill='red')
                    self.fibres.append([photo_x, photo_y,
                                        (hor_line, ver_line)])
                    self.nucleiTable.addFibre([photo_x, photo_y])
                    return True

        return False

    def rightClick(self, windowX, windowY, frmStart):

        eventx = windowX - 1
        eventy = windowY - frmStart
        if self.image is not None and eventy < table.ImageCanvasSize[1] \
                and eventx < table.ImageCanvasSize[0]:

            # delete nucleus
            # coordinaten van linkerbovenhoek van de foto tov de window
            top_left_x = self.canvas.coords(self.container)[0] - \
                self.canvas.canvasx(0)
            top_left_y = self.canvas.coords(self.container)[1] - \
                self.canvas.canvasy(0)

            # coordinaten tov de foto
            photo_x = (eventx - top_left_x) / (self.width * self.imscale)
            photo_y = (eventy - top_left_y) / (self.height * self.imscale)

            # find a close nuclei
            if self.indicatingNuclei and self.indicatorsNF[0]:
                closest_nuclei_index, closest_nuclei_id = \
                    self.findClosestNuclei(photo_x, photo_y)
                if closest_nuclei_index != -1:

                    # delete it
                    if self.nuclei[closest_nuclei_index][3]:
                        self.nucleiTable.removeGreen(
                            [self.nuclei[closest_nuclei_index][0],
                             self.nuclei[closest_nuclei_index][1]])
                    else:
                        self.nucleiTable.removeBlue(
                            [self.nuclei[closest_nuclei_index][0],
                             self.nuclei[closest_nuclei_index][1]])

                    del self.nuclei[closest_nuclei_index]
                    self.canvas.delete(closest_nuclei_id)
                    return True

            elif self.indicatorsNF[1]:

                # find closest fibre
                closest_fibre_index, closest_fibre_id = \
                    self.findClosestFibre(photo_x, photo_y)
                print(closest_fibre_index, closest_fibre_id)
                if closest_fibre_index != -1:

                    # delete it
                    self.nucleiTable.removeFibre(
                        [self.fibres[closest_fibre_index][0],
                         self.fibres[closest_fibre_index][1]])
                    del self.fibres[closest_fibre_index]
                    self.canvas.delete(closest_fibre_id[0])
                    self.canvas.delete(closest_fibre_id[1])
                    return True

        return False

    def findClosestFibre(self, x, y):
        # find the closest fiber
        radius = 20.0
        closest_index = -1
        closest_distance_sq = -1
        for i, fiber in enumerate(self.fibres):
            if fiber[0] - radius / self.width < x and \
                    fiber[0] + radius / self.width > x and \
                    fiber[1] - radius / self.height < y and \
                    fiber[1] + radius / self.height > y:
                dis_sq = (fiber[0] - x) ** 2 + (fiber[1] - y) ** 2
                if dis_sq < closest_distance_sq or closest_distance_sq < 0:
                    closest_index = i
                    closest_distance_sq = dis_sq
        if closest_index != -1:
            return closest_index, self.fibres[closest_index][2]
        return -1, -1

    def findClosestNuclei(self, x, y):
        # find the closest nucleus
        radius = 4.0
        closest_index = -1
        closest_distance_sq = -1
        for i, nucleus in enumerate(self.nuclei):
            if nucleus[0] - radius / self.width < x and \
                    nucleus[0] + radius / self.width > x and \
                    nucleus[1] - radius / self.height < y and \
                    nucleus[1] + radius / self.height > y:
                dis_sq = (nucleus[0] - x) ** 2 + (nucleus[1] - y) ** 2
                if dis_sq < closest_distance_sq or closest_distance_sq < 0:
                    closest_index = i
                    closest_distance_sq = dis_sq
        if closest_index != -1:
            return closest_index, self.nuclei[closest_index][2]
        return -1, -1

    def setChannels(self, b, g, r):
        self.channelsRGB = (r, g, b)
        self.setImage()

    def setImage(self):
        # load the image with the correct channels
        if self.imagePath != '':
            cv_img = cv2.cvtColor(cv2.imread(self.imagePath),
                                  cv2.COLOR_BGR2RGB)
            if not self.channelsRGB[0]:
                cv_img[:, :, 0] = np.zeros([cv_img.shape[0], cv_img.shape[1]])
            if not self.channelsRGB[1]:
                cv_img[:, :, 1] = np.zeros([cv_img.shape[0], cv_img.shape[1]])
            if not self.channelsRGB[2]:
                cv_img[:, :, 2] = np.zeros([cv_img.shape[0], cv_img.shape[1]])
            image_in = PIL.Image.fromarray(cv_img)

            self.image = image_in.resize(table.ImageCanvasSize)  # open image
            self.width, self.height = table.ImageCanvasSize
            self.show_image()

    def setIndicators(self, nuclei, fibres):

        # nuclei
        if not nuclei:
            for nuc in self.nuclei:
                self.canvas.delete(nuc[2])
        elif not self.indicatorsNF[0]:

            radius = int(3.0 * self.imscale)
            # coordinaten van linkerbovenhoek van de foto tov de window
            top_left_x = self.canvas.coords(self.container)[0] - \
                self.canvas.canvasx(0)
            top_left_y = self.canvas.coords(self.container)[1] - \
                self.canvas.canvasy(0)

            # draw
            for i, nuc in enumerate(self.nuclei):
                color = nonFibreNucleiColour
                if nuc[3]:
                    color = fibreNucleiColour
                x = self.canvas.canvasx(nuc[0] * (self.width * self.imscale) +
                                        top_left_x)
                y = self.canvas.canvasy(nuc[1] * (self.height * self.imscale) +
                                        top_left_y)
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

            square_size = int(10.0 * self.imscale)
            # coordinaten van linkerbovenhoek van de foto tov de window
            top_left_x = self.canvas.coords(self.container)[0] - \
                self.canvas.canvasx(0)
            top_left_y = self.canvas.coords(self.container)[1] - \
                self.canvas.canvasy(0)

            # draw
            for i, fibre in enumerate(self.fibres):
                x = self.canvas.canvasx(fibre[0] * (self.width * self.imscale)
                                        + top_left_x)
                y = self.canvas.canvasy(fibre[1] * (self.height * self.imscale)
                                        + top_left_y)
                horLine = self.canvas.create_line(x + square_size, y,
                                                  x - square_size, y, width=2,
                                                  fill='red')
                verLine = self.canvas.create_line(x, y + square_size, x,
                                                  y - square_size, width=2,
                                                  fill='red')
                self.fibres[i][2] = (horLine, verLine)

        self.indicatorsNF = (nuclei, fibres)

    def getIndicators(self):
        return self.indicatorsNF

    def loadImage(self, path, nucleiPositions, fibrepositions):

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
        self.setImage()

        # draw the nuclei on the screen
        radius = int(3.0 * self.imscale)
        square_size = int(10.0 * self.imscale)
        # coordinaten van linkerbovenhoek van de foto tov de window
        top_left_x = self.canvas.coords(self.container)[0] - \
            self.canvas.canvasx(0)
        top_left_y = self.canvas.coords(self.container)[1] - \
            self.canvas.canvasy(0)

        # blue nuclei
        for position in nucleiPositions[0]:
            x = self.canvas.canvasx(position[0] * (self.width * self.imscale)
                                    + top_left_x)
            y = self.canvas.canvasy(position[1] * (self.height * self.imscale)
                                    + top_left_y)
            new_oval = None
            if self.indicatorsNF[0]:
                new_oval = self.canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius,
                    fill=nonFibreNucleiColour, outline='#fff', width=0)
                # #2A7DDE (blue) #2B8915 (green)
            self.nuclei.append([position[0], position[1], new_oval, False])
        # green nuclei
        for position in nucleiPositions[1]:
            x = self.canvas.canvasx(position[0] * (self.width * self.imscale)
                                    + top_left_x)
            y = self.canvas.canvasy(position[1] * (self.height * self.imscale)
                                    + top_left_y)
            new_oval = None
            if self.indicatorsNF[0]:
                new_oval = self.canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius,
                    fill=fibreNucleiColour, outline='#fff', width=0)
                # #2A7DDE (blue) #2B8915 (green)
            self.nuclei.append([position[0], position[1], new_oval, True])

        # fibres
        for position in fibrepositions:
            x = self.canvas.canvasx(position[0] * (self.width * self.imscale)
                                    + top_left_x)
            y = self.canvas.canvasy(position[1] * (self.height * self.imscale)
                                    + top_left_y)
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
        self.canvas.yview_moveto('0.0')
        self.canvas.xview_moveto('0.0')
        self.show_image()

    def reset(self):
        # reset the canvas
        self.image = None  # open image
        self.width, self.height = table.ImageCanvasSize
        self.imscale = 1.0  # scale for the canvas image
        self.delta = 1.3  # zoom delta
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
        self.container = self.canvas.create_rectangle(0, 0, self.width,
                                                      self.height, width=0)

        # show
        self.show_image()

    def arrows(self, arrowIndex):

        # use the arrow keys to scroll around the image
        self.canvas.configure(yscrollincrement='110')
        self.canvas.configure(xscrollincrement='160')

        self.canvas.xview_scroll(1, tk.UNITS)
        self.canvas.yview_scroll(1, tk.UNITS)
        if arrowIndex == 2:
            self.canvas.yview_scroll(-1, tk.UNITS)
        elif arrowIndex == 3:
            self.canvas.xview_scroll(-1, tk.UNITS)
        elif arrowIndex == 0:
            self.canvas.xview_scroll(-2, tk.UNITS)
            self.canvas.yview_scroll(-1, tk.UNITS)
        elif arrowIndex == 1:
            self.canvas.xview_scroll(-1, tk.UNITS)
            self.canvas.yview_scroll(-2, tk.UNITS)

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

    def zoom(self, eventx, eventy, delta):
        if self.image is not None:
            x = self.canvas.canvasx(eventx)
            y = self.canvas.canvasy(eventy)

            bbox = self.canvas.bbox(self.container)  # get image area
            if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]:
                pass  # Ok! Inside the image
            else:
                return  # zoom only inside image area
            scale = 1.0
            # Respond to Linux (event.num) or Windows (event.delta) wheel event
            if delta == -120:  # scroll down
                i = min(self.width, self.height)
                if int(i * self.imscale) < 30:
                    return  # image is less than 30 pixels
                self.imscale /= self.delta
                scale /= self.delta
            if delta == 120:  # scroll up
                i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
                if i < self.imscale:
                    return  # 1 pixel is bigger than the visible area
                self.imscale *= self.delta
                scale *= self.delta
            self.canvas.scale('all', x, y, scale, scale)  # rescale all the
            # elements in the image
            self.show_image()

    def wheel(self, event):
        """ Zoom with mouse wheel """
        self.zoom(event.x, event.y, event.delta)

    def show_image(self, event=None):
        """ Show image on the Canvas """
        if self.image is not None:
            bbox1 = self.canvas.bbox(self.container)  # get image area
            # Remove 1 pixel shift at the sides of the bbox1
            bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
            bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                     self.canvas.canvasy(0),
                     self.canvas.canvasx(self.canvas.winfo_width()),
                     self.canvas.canvasy(self.canvas.winfo_height()))
            bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),
                    # get scroll region box
                    max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
            if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:
                # whole image in the visible area
                bbox[0] = bbox1[0]
                bbox[2] = bbox1[2]
            if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:
                # whole image in the visible area
                bbox[1] = bbox1[1]
                bbox[3] = bbox1[3]
            self.canvas.configure(scrollregion=bbox)  # set scroll region
            x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2)
            # of the image tile
            y1 = max(bbox2[1] - bbox1[1], 0)
            x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
            y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
            if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in
                # the visible area
                x = min(int(x2 / self.imscale), self.width)
                # sometimes it is larger on 1 pixel...
                y = min(int(y2 / self.imscale), self.height)
                # ...and sometimes not
                image = self.image.crop((int(x1 / self.imscale),
                                         int(y1 / self.imscale), x, y))
                imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1),
                                                           int(y2 - y1))))
                self.imageId = self.canvas.create_image(max(bbox2[0],
                                                            bbox1[0]),
                                                        max(bbox2[1],
                                                            bbox1[1]),
                                                        anchor='nw',
                                                        image=imagetk)
                self.canvas.lower(self.imageId)  # set image into background
                self.canvas.imagetk = imagetk  # keep an extra reference to
                # prevent garbage-collection
