# coding: utf-8

from tkinter import Scrollbar, VERTICAL, Frame, Canvas, RIGHT, Y, LEFT, BOTH
from xlsxwriter import Workbook
from shutil import copyfile, rmtree
from numpy import load, asarray, save
from cv2 import imread, line, ellipse, imwrite
from os import path, mkdir

# get the absolute path of the exe
BASE_PATH = path.abspath('')  # [:-7]
BASE_PATH += "/"

# define the image canvas size
ImageCanvasSize = (1266, 955)
ImageCanvasStandardFactor = 955 / 1266

# colorcodes
backgroundColour = '#EAECEE'
backgroundColour_Selected = '#ABB2B9'
labelLineColour = '#646464'
labelLineColour_Selected = 'black'


class Table:

    def __init__(self, root):

        # initialise the canvas and scrollbar
        padding = 10
        scrollbar_width = 26
        self.width = 1920 - ImageCanvasSize[0] - 2 * padding - scrollbar_width
        self.height = 795
        self.rowHeight = 50
        self.topLeftX = ImageCanvasSize[0] + padding
        self.topLeftY = 150

        self.frame = Frame(root, width=self.width, height=self.height)
        self.frame.place(x=self.topLeftX, y=self.topLeftY)
        self.canvas = Canvas(self.frame, bg='#FFFFFF', width=self.width,
                             height=self.height, highlightbackground='black',
                             highlightthickness=3,
                             scrollregion=(0, 0, self.width, self.height))
        self.imageCanvas = None

        self.vbar = Scrollbar(self.frame, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(width=self.width, height=self.height)
        self.canvas.config(yscrollcommand=self.vbar.set)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)
        # data about the images
        self.nucleiPositions = []
        self.fibrePositions = []
        self.filenames = []
        self.currentImageIndex = 0
        self.hoveringIndex = -1

        # handles to widgets on the canvas
        self.itemLines = []
        self.labels = []
        self.rectangles = []

    def save_table(self, directory):

        # save to an Excel
        workbook = Workbook(BASE_PATH + 'Projects/' + directory +
                            '/' + directory + '.xlsx')
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True, 'align': 'center'})

        # write filenames
        worksheet.write(0, 0, "Image names", bold)
        max_size = 11
        for i, name in enumerate(self.filenames):
            name = path.basename(self.filenames[i])
            worksheet.write(i+2, 0, name)
            max_size = max(len(name), max_size)
        worksheet.set_column(0, 0, width=max_size)

        # write total nuclei
        worksheet.write(0, 1, "Total number of nuclei", bold)
        worksheet.set_column(1, 1, width=22)
        for i, name in enumerate(self.filenames):
            worksheet.write(i+2, 1, len(self.nucleiPositions[i][0]) +
                            len(self.nucleiPositions[i][1]))

        # write green nuclei
        worksheet.write(0, 2, "Number of tropomyosin positive nuclei", bold)
        worksheet.set_column(2, 2, width=37)
        for i, name in enumerate(self.filenames):
            worksheet.write(i+2, 2, len(self.nucleiPositions[i][1]))

        # write ratio
        worksheet.write(0, 3, "Fusion index", bold)
        worksheet.set_column(3, 3, width=17)
        for i, name in enumerate(self.filenames):
            if len(self.nucleiPositions[i][0]) > 0:
                worksheet.write(i+2, 3, (len(self.nucleiPositions[i][1])) /
                                (len(self.nucleiPositions[i][0]) +
                                 len(self.nucleiPositions[i][1])))
            else:
                worksheet.write(i + 2, 3, 'NA')

        # write fibers
        worksheet.write(0, 4, "Number of Fibres", bold)
        worksheet.set_column(4, 4, width=16)
        for i, name in enumerate(self.filenames):
            worksheet.write(i + 2, 4, len(self.fibrePositions[i]))

        workbook.close()

    def load_project(self, directory):

        # reset
        self.reset()

        # load the data
        if path.isfile(directory + '/data.npy') and \
                path.isdir(directory + '/Original Images'):
            data = load(directory + '/data.npy', allow_pickle=True).tolist()
            for item in data:
                if len(item) == 4:
                    if type(item[0]) == str and type(item[1]) == list and \
                            type(item[2]) == list and type(item[3]) == list:
                        if path.isfile(item[0]):
                            self.filenames.append(BASE_PATH + item[0])
                            self.nucleiPositions.append([item[1], item[2]])
                            self.fibrePositions.append(item[3])

        # make the table
        self._make_table()

    def images_available(self):
        return len(self.filenames) != 0

    def save_data(self, directory):

        # make array
        to_save = []
        for i, filename in enumerate(self.filenames):
            to_save.append(["Projects/" + directory + '/Original Images/' +
                            path.basename(filename),
                            self.nucleiPositions[i][0],
                            self.nucleiPositions[i][1],
                            self.fibrePositions[i]])

        # convert to numpy
        arr = asarray(to_save)
        save(BASE_PATH + 'Projects/' + directory + '/data', arr)

    def save_originals(self, directory):

        # create a directory with the original images
        if not path.isdir(BASE_PATH + 'Projects/' + directory +
                          '/Original Images'):
            mkdir(BASE_PATH + 'Projects/' + directory + '/Original Images')

        # save the images
        for filename in self.filenames:
            basename = path.basename(filename)
            if filename != BASE_PATH + 'Projects/' + directory + \
                    '/Original Images/' + basename:
                copyfile(filename, BASE_PATH + 'Projects/' + directory
                         + '/Original Images/' + basename)

    def save_altered_images(self, directory):

        # create a directory with the altered images
        if path.isdir(BASE_PATH + 'Projects/' + directory +
                      '/Altered Images'):
            rmtree(BASE_PATH + 'Projects/' + directory + '/Altered Images')
        mkdir(BASE_PATH + 'Projects/' + directory + '/Altered Images')

        # read the images and then save them
        for i, filename in enumerate(self.filenames):
            self._draw_nuclei_save(i, directory)

    def _draw_nuclei_save(self, index, project_name):

        # loop through the fibres
        cv_img = imread(BASE_PATH + "Projects/" + project_name +
                        "/Original Images/" +
                        path.basename(self.filenames[index]))
        square_size = 9
        for i in range(len(self.fibrePositions[index])):
            centre = (int(self.fibrePositions[index][i][0] * cv_img.shape[1]),
                      int(self.fibrePositions[index][i][1] * cv_img.shape[0]))
            line(cv_img, (centre[0] + square_size, centre[1]),
                 (centre[0] - square_size, centre[1]), (0, 0, 255), 2)
            line(cv_img, (centre[0], centre[1] + square_size),
                 (centre[0], centre[1] - square_size), (0, 0, 255), 2)

        # loop through the nuclei
        for i in range(len(self.nucleiPositions[index][0]) +
                       len(self.nucleiPositions[index][1])):

            if i < len(self.nucleiPositions[index][0]):
                # red (negative)
                centre = (int(self.nucleiPositions[index][0][i][0] *
                              cv_img.shape[1]),
                          int(self.nucleiPositions[index][0][i][1] *
                              cv_img.shape[0]))
                ellipse(cv_img, centre, (3, 3), 0, 0, 360,
                        (0, 0, 255), -1)
                ellipse(cv_img, centre, (4, 4), 0, 0, 360,
                        (255, 255, 255), 1)
            else:
                # yellow (positive)
                centre = (int(self.nucleiPositions[index][1]
                              [i - len(self.nucleiPositions[index][0])][0] *
                              cv_img.shape[1]),
                          int(self.nucleiPositions[index][1]
                              [i - len(self.nucleiPositions[index][0])][1] *
                              cv_img.shape[0]))
                ellipse(cv_img, centre, (3, 3), 0, 0, 360,
                        (0, 255, 255), -1)
                ellipse(cv_img, centre, (4, 4), 0, 0, 360,
                        (255, 255, 255), 1)

        # save it
        imwrite(BASE_PATH + "Projects/" + project_name + "/Altered Images/"
                + path.basename(self.filenames[index])[:-4] + ".png",
                cv_img)

    def onwheel(self, delta, x, y, frm_start):

        # scroll down the canvas if we are inside the canvas
        relx = x - self.topLeftX
        rely = y - self.topLeftY - frm_start  # frmStart is menubar height
        if self.filenames and 0 <= rely <= len(self.filenames) * \
                self.rowHeight * 2 - 1 and 0 <= relx <= self.width:
            self.canvas.yview_scroll(int(-1 * (delta / 120)), "units")

       # update the imagecanvas handle
    def set_image_canvas(self, image_canvas):
        self.imageCanvas = image_canvas

    def update_data(self, index):
        # set the variables labels for the image
        total_nuclei = len(self.nucleiPositions[index][0]) + \
                       len(self.nucleiPositions[index][1])
        self.canvas.itemconfig(self.labels[index][1], text='Total : ' +
                                                           str(total_nuclei))
        self.canvas.itemconfig(self.labels[index][2],
                               text='Positive : ' +
                                    str(len(self.nucleiPositions[index][1])))
        if total_nuclei != 0:
            self.canvas.itemconfig(self.labels[index][3],
                                   text="Ratio : {:.2f}%".format(
                100 * len(self.nucleiPositions[index][1]) / total_nuclei))
        else:
            self.canvas.itemconfig(self.labels[index][3], text='Ratio : NA')
        self.canvas.itemconfig(self.labels[index][5],
                               text='Fibres : ' +
                                    str(len(self.fibrePositions[index])))

        # these functions are called by imagewindow to update the lists
        # in the table

    def add_fibre(self, position):
        self.fibrePositions[self.currentImageIndex].append(position)
        self.update_data(self.currentImageIndex)

    def remove_fibre(self, position):
        self.fibrePositions[self.currentImageIndex].remove(position)
        self.update_data(self.currentImageIndex)

    def to_blue(self, position):
        self.nucleiPositions[self.currentImageIndex][0].append(position)
        self.nucleiPositions[self.currentImageIndex][1].remove(position)
        self.update_data(self.currentImageIndex)

    def add_blue(self, position):
        self.nucleiPositions[self.currentImageIndex][0].append(position)
        self.update_data(self.currentImageIndex)

    def remove_blue(self, position):
        self.nucleiPositions[self.currentImageIndex][0].remove(position)
        self.update_data(self.currentImageIndex)

    def remove_green(self, position):
        self.nucleiPositions[self.currentImageIndex][1].remove(position)
        self.update_data(self.currentImageIndex)

    def to_green(self, position):
        self.nucleiPositions[self.currentImageIndex][1].append(position)
        self.nucleiPositions[self.currentImageIndex][0].remove(position)
        self.update_data(self.currentImageIndex)

    def motion(self, x, y, frm_start):

        # only if there are items and we are in the bounds
        relx = x - self.topLeftX
        rely = y - self.topLeftY - frm_start  # frmStart is menubar height
        if self.filenames and 0 <= rely <= len(self.filenames) * \
                self.rowHeight * 2 - 1 and 0 <= relx <= self.width:
            # unhover previous
            if self.hoveringIndex != -1:
                self.unhover(self.hoveringIndex)

            # hover over new item
            self.hover(int(self.canvas.canvasy(rely) / (self.rowHeight * 2)))
        elif self.hoveringIndex != -1:
            self.unhover(self.hoveringIndex)
            self.hoveringIndex = -1

    def hover(self, index):
        # set the esthetics of hovering over a table entry (like making the
        # text more black)
        self.hoveringIndex = index
        if index > 0:
            self.canvas.itemconfig(self.itemLines[index-1][1],
                                   fill=labelLineColour_Selected, width=3)
        self.canvas.itemconfig(self.itemLines[index][0],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.itemLines[index][1],
                               fill=labelLineColour_Selected, width=3)
        self.canvas.itemconfig(self.itemLines[index][2],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][0],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][1],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][2],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][3],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][4],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][5],
                               fill=labelLineColour_Selected)

    def unhover(self, index):
        # reset the esthetics of hovering over a table entry
        if index != self.currentImageIndex:
            if index > 0:
                self.canvas.itemconfig(self.itemLines[index-1][1],
                                       fill=labelLineColour, width=3)
            self.canvas.itemconfig(self.itemLines[index][0],
                                   fill=labelLineColour)
            self.canvas.itemconfig(self.itemLines[index][1],
                                   fill=labelLineColour, width=3)
            self.canvas.itemconfig(self.itemLines[index][2],
                                   fill=labelLineColour)
            self.canvas.itemconfig(self.labels[index][0], fill=labelLineColour)
            self.canvas.itemconfig(self.labels[index][1], fill=labelLineColour)
            self.canvas.itemconfig(self.labels[index][2], fill=labelLineColour)
            self.canvas.itemconfig(self.labels[index][3], fill=labelLineColour)
            self.canvas.itemconfig(self.labels[index][4], fill=labelLineColour)
            self.canvas.itemconfig(self.labels[index][5], fill=labelLineColour)

    def _unselect_image(self, index):
        # set the esthetics of selectibg a table entry (like making the text
        # more black)
        if index != 0:
            self.canvas.itemconfig(self.itemLines[index-1][1],
                                   fill=labelLineColour, width=3)
        self.canvas.itemconfig(self.rectangles[index], fill=backgroundColour)
        self.canvas.itemconfig(self.itemLines[index][0], fill=labelLineColour)
        self.canvas.itemconfig(self.itemLines[index][1],
                               fill=labelLineColour, width=3)
        self.canvas.itemconfig(self.itemLines[index][2], fill=labelLineColour)
        self.canvas.itemconfig(self.labels[index][0], fill=labelLineColour)
        self.canvas.itemconfig(self.labels[index][1], fill=labelLineColour)
        self.canvas.itemconfig(self.labels[index][2], fill=labelLineColour)
        self.canvas.itemconfig(self.labels[index][3], fill=labelLineColour)
        self.canvas.itemconfig(self.labels[index][4], fill=labelLineColour)
        self.canvas.itemconfig(self.labels[index][5], fill=labelLineColour)

    def _select_image(self, index):
        # reset the esthetics of selecting a table entry
        self.imageCanvas.load_image(self.filenames[index],
                                    self.nucleiPositions[index],
                                    self.fibrePositions[index])
        self.currentImageIndex = index
        if index != 0:
            self.canvas.itemconfig(self.itemLines[index-1][1],
                                   fill=labelLineColour_Selected, width=3)
        self.canvas.itemconfig(self.rectangles[index],
                               fill=backgroundColour_Selected)
        self.canvas.itemconfig(self.itemLines[index][0],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.itemLines[index][1],
                               fill=labelLineColour_Selected, width=3)
        self.canvas.itemconfig(self.itemLines[index][2],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][0],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][1],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][2],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][3],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][4],
                               fill=labelLineColour_Selected)
        self.canvas.itemconfig(self.labels[index][5],
                               fill=labelLineColour_Selected)

    def left_click(self, x, y, frm_start):

        # only if there are items, and we are in the bounds
        relx = x - self.topLeftX
        rely = y - self.topLeftY - frm_start  # frmStart is menubar height enal
        if self.filenames and 0 <= rely <= len(self.filenames) * \
                self.rowHeight * 2 - 1 and 0 <= relx <= self.width:
            # unselect previous
            self._unselect_image(self.currentImageIndex)

            # select new image
            self._select_image(int(self.canvas.canvasy(rely) /
                                   (self.rowHeight * 2)))

    def reset(self):
        # remove everything previous
        for item in self.labels:
            for it in item:
                self.canvas.delete(it)
        for item in self.itemLines:
            for it in item:
                self.canvas.delete(it)
        for it in self.rectangles:
            self.canvas.delete(it)

        self.labels = []
        self.rectangles = []
        self.itemLines = []
        self.currentImageIndex = 0
        self.hoveringIndex = -1
        self.nucleiPositions = []
        self.fibrePositions = []
        self.filenames = []

    def add_images(self, filenames):

        # remove everything previous
        for item in self.labels:
            for it in item:
                self.canvas.delete(it)
        for item in self.itemLines:
            for it in item:
                self.canvas.delete(it)
        for it in self.rectangles:
            self.canvas.delete(it)
        self.labels = []
        self.rectangles = []
        self.itemLines = []

        # add the filenames
        self.filenames += filenames
        self.nucleiPositions += [[[], []] for _ in self.filenames]
        self.fibrePositions += [[] for _ in self.filenames]

        # make the table
        self._make_table()

    def _make_table(self):

        # make the table
        for i in range(len(self.filenames)):

            # horizontal lines
            half_line = self.canvas.create_line(-1,
                                                (2 * i + 1) * self.rowHeight,
                                                self.width,
                                                (2 * i + 1) * self.rowHeight,
                                                width=1, fill=labelLineColour)
            full_line = self.canvas.create_line(-1,
                                                (2 * i + 2) * self.rowHeight,
                                                self.width,
                                                (2 * i + 2) * self.rowHeight,
                                                width=2, fill=labelLineColour)

            # rectangle
            rect = self.canvas.create_rectangle(-1, self.rowHeight*2*i,
                                                self.width,
                                                self.rowHeight * (2*i+2),
                                                fill=backgroundColour)
            self.canvas.tag_lower(rect)  # lower it (background)

            index_text = self.canvas.create_text(25, (2 * i) * self.rowHeight +
                                                 int(self.rowHeight / 2),
                                                 text=str(i + 1),
                                                 anchor='center',
                                                 font=('Helvetica', 10,
                                                       'bold'),
                                                 fill=labelLineColour)
            index_line = self.canvas.create_line(50,
                                                 (2 * i) * self.rowHeight, 50,
                                                 (2 * i + 1) * self.rowHeight,
                                                 width=1, fill=labelLineColour)

            # set the filename
            file_name = path.basename(self.filenames[i])
            if len(file_name) >= 59:
                file_name = '...' + file_name[-59:]

            padding = 10
            file_name_text = self.canvas.create_text(60,
                                                     (2 * i) * self.rowHeight +
                                                     int(self.rowHeight / 4),
                                                     text=file_name,
                                                     anchor='nw',
                                                     fill=labelLineColour)
            nuclei_text = self.canvas.create_text(padding,
                                                  (2 * i + 1) * self.rowHeight
                                                  + int(self.rowHeight / 4),
                                                  text='error',
                                                  anchor='nw',
                                                  fill=labelLineColour)
            positive_text = self.canvas.create_text(
                padding + (self.width - 2 * padding) / 4,
                (2 * i + 1) * self.rowHeight + int(self.rowHeight / 4),
                text='error', anchor='nw', fill=labelLineColour)
            ratio_text = self.canvas.create_text(
                padding + (self.width - 2 * padding) * 2 / 4,
                (2 * i + 1) * self.rowHeight + int(self.rowHeight / 4),
                text='error', anchor='nw', fill=labelLineColour)
            fiber_text = self.canvas.create_text(
                padding * 3 + (self.width - 2 * padding) * 3 / 4,
                (2 * i + 1) * self.rowHeight + int(self.rowHeight / 4),
                text='error', anchor='nw', fill=labelLineColour)

            # append the handles
            self.labels.append([file_name_text, nuclei_text, positive_text,
                                ratio_text, index_text, fiber_text])
            self.itemLines.append([half_line, full_line, index_line])
            self.rectangles.append(rect)

            # update the text
            self.update_data(i)

        # set scrollregion
        self.canvas.config(scrollregion=(0, 0, self.width,
                                         (2 * len(self.filenames)) *
                                         self.rowHeight))

        # create hightlighted parts
        if not len(self.filenames) == 0:
            self._select_image(self.currentImageIndex)
        else:
            self.imageCanvas.reset()

    def get_file_names(self):
        return self.filenames

    def get_current_image_index(self):
        return self.currentImageIndex

    def input_processed_data(self, nuclei_negative_positions,
                             nuclei_positive_positions, fibre_centres, index):

        # update the data
        self.nucleiPositions[index] = [nuclei_negative_positions,
                                       nuclei_positive_positions]
        if len(fibre_centres) > 0:
            self.fibrePositions[index] = fibre_centres
        self.update_data(index)

        # load the new image if necessary
        if index == self.currentImageIndex:
            self.imageCanvas.load_image(self.filenames[self.currentImageIndex],
                                        self.nucleiPositions[
                                            self.currentImageIndex],
                                        self.fibrePositions[
                                            self.currentImageIndex])
