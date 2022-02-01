# coding: utf-8

from tkinter import ttk, Canvas, messagebox
from xlsxwriter import Workbook
from shutil import copyfile, rmtree
from numpy import load, asarray, save
from cv2 import imread, line, ellipse, imwrite
from pathlib import Path
from platform import system
from typing import List, Dict
from copy import deepcopy
from functools import partial
from structure_classes import Nucleus, Fibre, Nuclei, Fibres, Labels, Lines, \
    Rectangle, Table_element

# color codes
background = '#EAECEE'
background_selected = '#ABB2B9'
label_line = '#646464'
label_line_selected = 'black'

in_fibre = 'yellow'  # green
out_fibre = 'red'  # 2A7DDE


class Table(ttk.Frame):

    def __init__(self, root):

        super().__init__(root)

        # initialise the canvas and scrollbar
        self._row_height = 50
        self._base_path = Path(__file__).parent
        self._projects_path = self._base_path / 'Projects'

        self._set_layout()
        self._set_bindings()
        self._set_variables()

    def _save_table(self, directory: Path):

        # save to an Excel
        workbook = Workbook(str(directory / str(directory.name + '.xlsx')))
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True, 'align': 'center'})

        # write filenames
        worksheet.write(0, 0, "Image names", bold)
        max_size = 11
        for i, file in enumerate(self.filenames):
            name = file.name
            worksheet.write(i+2, 0, name)
            max_size = max(len(name), max_size)
        worksheet.set_column(0, 0, width=max_size)

        # write total nuclei
        worksheet.write(0, 1, "Total number of nuclei", bold)
        worksheet.set_column(1, 1, width=22)
        for i, file in enumerate(self.filenames):
            worksheet.write(i + 2, 1, len(self._nuclei[file]))

        # write green nuclei
        worksheet.write(0, 2, "Number of tropomyosin positive nuclei", bold)
        worksheet.set_column(2, 2, width=37)
        for i, file in enumerate(self.filenames):
            worksheet.write(i + 2, 2, self._nuclei[file].nuclei_in_count)

        # write ratio
        worksheet.write(0, 3, "Fusion index", bold)
        worksheet.set_column(3, 3, width=17)
        for i, file in enumerate(self.filenames):
            if self._nuclei[file].nuclei_out_count > 0:
                worksheet.write(i + 2, 3, self._nuclei[file].nuclei_in_count /
                                len(self._nuclei[file]))
            else:
                worksheet.write(i + 2, 3, 'NA')

        # write fibers
        worksheet.write(0, 4, "Number of Fibres", bold)
        worksheet.set_column(4, 4, width=16)
        for i, file in enumerate(self.filenames):
            worksheet.write(i + 2, 4, len(self._fibres[file]))

        workbook.close()

    def load_project(self, directory: Path):

        # reset
        self.reset()

        data = load(str(directory / 'data.npy'),
                    allow_pickle=True).tolist()
        if isinstance(data, list):
            for item in data:
                if len(item) == 4:
                    if isinstance(item[0], str) and \
                            isinstance(item[1], list) and \
                            isinstance(item[2], list) and \
                            isinstance(item[3], list):
                        if (directory / 'Original Images' / item[0]).is_file():
                            self.filenames.append(
                                directory / 'Original Images' / item[0])
                            self._nuclei[directory / 'Original Images' /
                                         item[0]] = Nuclei(
                                [Nucleus(x, y, None, out_fibre) for x, y in
                                 item[1]] +
                                [Nucleus(x, y, None, in_fibre) for x, y in
                                 item[2]])
                            self._fibres[directory / 'Original Images' /
                                         item[0]] = Fibres(
                                [Fibre(x, y, None, None) for x, y in item[3]])

        # make the table
        self._make_table()

    def save_project(self, directory: Path, save_altered: bool):

        # save the table
        self._save_table(directory)

        # save the originals
        self._save_originals(directory)

        # save the altered images
        if save_altered:
            self._save_altered_images(directory)

        # save the data
        self._save_data(directory)

    def _save_data(self, directory: Path):

        # make array
        to_save = []
        for file in self.filenames:
            nuc_out = [(nuc.x_pos, nuc.y_pos) for nuc in self._nuclei[file]
                       if nuc.color == out_fibre]
            nuc_in = [(nuc.x_pos, nuc.y_pos) for nuc in self._nuclei[file]
                      if nuc.color == in_fibre]
            fib = [(fib.x_pos, fib.y_pos) for fib in self._fibres[file]]
            to_save.append([file.name,
                            nuc_out,
                            nuc_in,
                            fib])

        # convert to numpy
        save(str(directory / 'data'), asarray(to_save))

    def _save_originals(self, directory: Path):

        # create a directory with the original images
        if not (directory / 'Original Images').is_dir():
            Path.mkdir(directory / 'Original Images')

        # save the images
        for i, filename in enumerate(self.filenames):
            if self._projects_path not in filename.parents:
                new_path = directory / 'Original Images' / filename.name
                copyfile(filename, new_path)

                if self._current_image == filename:
                    self._current_image = new_path

                self._items[new_path] = self._items[filename]
                self._items.pop(filename)

                self._fibres[new_path] = self._fibres[filename]
                self._fibres.pop(filename)

                self._nuclei[new_path] = self._nuclei[filename]
                self._nuclei.pop(filename)

                index = self._img_to_index[filename]
                self._index_to_img[index] = new_path
                self._img_to_index[new_path] = index
                self._img_to_index.pop(filename)

                self.filenames[i] = new_path

    def _save_altered_images(self, directory: Path):

        # create a directory with the altered images
        if (directory / 'Altered Images').is_dir():
            rmtree(directory / 'Altered Images')
        Path.mkdir(directory / 'Altered Images')

        # read the images and then save them
        for file in self.filenames:
            self._draw_nuclei_save(file, directory)

       # update the image canvas handle
    def set_image_canvas(self, image_canvas):
        self._image_canvas = image_canvas

    def add_fibre(self, fibre):
        self._fibres[self._current_image].append(deepcopy(fibre))
        self._update_data(self._current_image)

    def remove_fibre(self, fibre):
        self._fibres[self._current_image].remove(fibre)
        self._update_data(self._current_image)

    def add_nucleus(self, nucleus):
        self._nuclei[self._current_image].append(deepcopy(nucleus))
        self._update_data(self._current_image)

    def remove_nucleus(self, nucleus):
        self._nuclei[self._current_image].remove(nucleus)
        self._update_data(self._current_image)

    def switch_nucleus(self, nucleus):
        for nuc in self._nuclei[self._current_image]:
            if nuc == nucleus:
                nuc.color = out_fibre if nuc.color == in_fibre else in_fibre
        self._update_data(self._current_image)

    def reset(self):
        # remove everything previous
        for item in self._canvas.find_all():
            self._canvas.delete(item)

        self._items: Dict[Path, Table_element] = {}
        self._index_to_img = {}
        self._img_to_index = {}
        self._current_image = None
        self._hovering_index = None
        self._nuclei: Dict[Path, Nuclei] = {}
        self._fibres: Dict[Path, Fibres] = {}
        self.filenames: List[Path] = []

    def add_images(self, filenames: List[Path]):

        # remove everything previous
        for item in self._canvas.find_all():
            self._canvas.delete(item)

        self._items: Dict[Path, Table_element] = {}

        # add the filenames
        for file in filenames:
            if file in self.filenames:
                messagebox.showerror("Error loading files",
                                     f"The file {file.name} is already opened,"
                                     f"ignoring.")
                filenames.remove(file)

        self.filenames += filenames
        for file in filenames:
            self._nuclei[file] = Nuclei()
            self._fibres[file] = Fibres()

        # make the table
        self._make_table()

    def input_processed_data(self, nuclei_negative_positions,
                             nuclei_positive_positions, fibre_centres,
                             file: Path):

        # update the data
        self._nuclei[file] = Nuclei()
        for x, y in nuclei_negative_positions:
            self._nuclei[file].append(Nucleus(x, y, None, out_fibre))
        for x, y in nuclei_positive_positions:
            self._nuclei[file].append(Nucleus(x, y, None, in_fibre))

        self._fibres[file] = Fibres()
        for x, y in fibre_centres:
            self._fibres[file].append(Fibre(x, y, None, None))

        self._update_data(file)

        # load the new image if necessary
        if file == self._current_image:
            self._image_canvas.load_image(
                self._current_image,
                self._nuclei[self._current_image],
                self._fibres[self._current_image])

    def _set_layout(self):
        self.pack(expand=True, fill="both", anchor="n", side='top')

        self._canvas = Canvas(self, bg='#FFFFFF',
                              highlightbackground='black',
                              highlightthickness=3)
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))
        self._canvas.pack(expand=True, fill="both", anchor="w", side='left',
                          pady=5)

        self._vbar = ttk.Scrollbar(self, orient="vertical")
        self._vbar.pack(side='right', fill='y', pady=5)
        self._vbar.config(command=self._canvas.yview)
        self._canvas.config(yscrollcommand=self._vbar.set)

        self.update()

    def _set_bindings(self):
        if system() == "Linux":
            self._canvas.bind('<4>', self._on_wheel)
            self._canvas.bind('<5>', self._on_wheel)
        else:
            self._canvas.bind('<MouseWheel>', self._on_wheel)
        self._canvas.bind('<ButtonPress-1>', self._left_click)
        self._canvas.bind_all('<Motion>', self._motion)

    def _set_variables(self):
        # data about the images
        self._nuclei: Dict[Path, Nuclei] = {}
        self._fibres: Dict[Path, Fibres] = {}
        self.filenames = []
        self._current_image = None
        self._hovering_index = None
        self._image_canvas = None

        # handles to widgets on the canvas
        self._items: Dict[Path, Table_element] = {}
        self._index_to_img = {}
        self._img_to_index = {}

    def _draw_nuclei_save(self, file: Path, project_name: Path):

        # loop through the fibres
        cv_img = imread(str(project_name / "Original Images" / file.name))
        square_size = 20
        for fib in self._fibres[file]:
            x, y = int(fib.x_pos), int(fib.y_pos)
            line(cv_img, (x + square_size, y), (x - square_size, y),
                 (0, 0, 255), 4)
            line(cv_img, (x, y + square_size), (x, y - square_size),
                 (0, 0, 255), 4)

        # loop through the nuclei
        for nuc in self._nuclei[file]:
            centre = (int(nuc.x_pos), int(nuc.y_pos))
            if nuc.color == out_fibre:
                ellipse(cv_img, centre, (6, 6), 0, 0, 360,
                        (0, 0, 255), -1)
            else:
                ellipse(cv_img, centre, (6, 6), 0, 0, 360,
                        (0, 255, 255), -1)

        # save it
        imwrite(str(project_name / "Altered Images" / file.name), cv_img)

    def _on_wheel(self, event):

        if system() == "Linux":
            delta = 1 if event.num == 4 else -1
        else:
            delta = int(event.delta / abs(event.delta))

        if self._table_height > self._canvas.winfo_height():
            self._canvas.yview_scroll(-delta, "units")

    def _update_data(self, file: Path):
        # set the variables labels for the image
        nuclei = self._nuclei[file]
        items = self._items[file]
        total_nuclei = len(nuclei)
        self._canvas.itemconfig(items.labels.nuclei,
                                text='Total : ' + str(total_nuclei))
        self._canvas.itemconfig(
            items.labels.positive,
            text='Positive : ' + str(nuclei.nuclei_in_count))
        if total_nuclei > 0:
            self._canvas.itemconfig(
                items.labels.ratio,
                text="Ratio : {:.2f}%".format(
                    100 * nuclei.nuclei_in_count /
                    total_nuclei))
        else:
            self._canvas.itemconfig(items.labels.ratio,
                                    text='Ratio : NA')
        self._canvas.itemconfig(
            items.labels.fiber,
            text='Fibres : ' + str(len(self._fibres[file])))

        # these functions are called by image window to update the lists
        # in the table

    def _motion(self, event):

        if self.filenames:
            # un hover previous
            if self._hovering_index is not None:
                self._un_hover(self._hovering_index)

            # hover over new item
            if 0 < self._canvas.canvasy(event.y) < self._table_height and \
                    event.widget == self._canvas:
                self._hover(int(self._canvas.canvasy(event.y) /
                                (self._row_height * 2)))

            elif self._hovering_index is not None:
                self._un_hover(self._hovering_index)
                self._hovering_index = None

    def _hover(self, index):

        self._hovering_index = index
        self._set_aesthetics(index, selected=True, hover=True)

    def _un_hover(self, index):

        if index != self._img_to_index[self._current_image]:
            self._set_aesthetics(index, selected=False, hover=True)

    def _unselect_image(self, index):

        self._set_aesthetics(index, selected=False, hover=False)

    def _select_image(self, index):

        file = self._index_to_img[index]
        self._image_canvas.load_image(file,
                                      self._nuclei[file], self._fibres[file])
        self._current_image = file
        self._set_aesthetics(index, selected=True, hover=False)

    def _set_aesthetics(self, index: int, selected, hover):

        line_color = label_line_selected if selected else label_line
        rect_color = background_selected if selected else background

        file = self._index_to_img[index]

        if index > 0:
            self._canvas.itemconfig(self._items[self._index_to_img[index - 1]].
                                    lines.full_line, fill=line_color)

        if not hover:
            self._canvas.itemconfig(self._items[file].rect.rect,
                                    fill=rect_color)

        self._canvas.itemconfig(self._items[file].lines.half_line,
                                fill=line_color)
        self._canvas.itemconfig(self._items[file].lines.full_line,
                                fill=line_color)
        self._canvas.itemconfig(self._items[file].lines.index_line,
                                fill=line_color)

        self._canvas.itemconfig(self._items[file].labels.name,
                                fill=line_color)
        self._canvas.itemconfig(self._items[file].labels.nuclei,
                                fill=line_color)
        self._canvas.itemconfig(self._items[file].labels.ratio,
                                fill=line_color)
        self._canvas.itemconfig(self._items[file].labels.positive,
                                fill=line_color)
        self._canvas.itemconfig(self._items[file].labels.index,
                                fill=line_color)
        self._canvas.itemconfig(self._items[file].labels.fiber,
                                fill=line_color)

    def _left_click(self, event):

        if self._canvas.canvasy(event.y) < self._table_height:
            # unselect previous
            self._unselect_image(self._img_to_index[self._current_image])

            # select new image
            self._select_image(int(self._canvas.canvasy(event.y) /
                                   (self._row_height * 2)))

    @property
    def _table_height(self):
        return self._row_height * 2 * len(self.filenames)

    def _delete_image(self, file: Path):

        ret = messagebox.askyesno('Hold on !',
                                  f"Do you really want to remove {file.name} ?"
                                  f"\nAll the unsaved data will be lost.")

        if not ret:
            return

        if self._hovering_index is not None:
            self._un_hover(self._hovering_index)
            self._hovering_index = None

        # remove everything previous
        for item in self._canvas.find_all():
            self._canvas.delete(item)

        self._items.pop(file)
        self._index_to_img.pop(self._img_to_index[file])
        index = self._img_to_index.pop(file)
        self._nuclei.pop(file)
        self._fibres.pop(file)
        self.filenames.remove(file)

        if not self.filenames:
            self._current_image = None
            self._hovering_index = None

        if self._current_image == file:
            if index + 1 in self._index_to_img:
                self._current_image = self._index_to_img[index + 1]
            else:
                self._current_image = self._index_to_img[index - 1]

        self._make_table()

    def _make_table(self):

        # make the table
        width = self._canvas.winfo_width()
        for i, file in enumerate(self.filenames):
            top = 2 * i * self._row_height
            middle = (2 * i + 1) * self._row_height
            bottom = (2 * i + 2) * self._row_height

            # horizontal lines
            half_line = self._canvas.create_line(
                -1, middle, width, middle, width=1, fill=label_line)
            full_line = self._canvas.create_line(
                -1, bottom, width, bottom, width=3, fill=label_line)

            button = ttk.Button(self._canvas, text="X", width=2,
                                command=partial(self._delete_image, file))
            self._canvas.create_window(width - 17, top + 16, window=button)

            # rectangle
            rect = self._canvas.create_rectangle(
                -1, top, width, bottom, fill=background)
            self._canvas.tag_lower(rect)  # lower it (background)

            index_text = self._canvas.create_text(
                25, top + int(self._row_height / 2),
                text=str(i + 1), anchor='center',
                font=('Helvetica', 10, 'bold'), fill=label_line)
            index_line = self._canvas.create_line(
                50, top, 50, middle, width=1, fill=label_line)

            # set the filename
            file_name = file.name
            if len(file_name) >= 59:
                file_name = '...' + file_name[-59:]

            padding = 10
            name_text = self._canvas.create_text(
                60, top + int(self._row_height / 4),
                text=file_name, anchor='nw', fill=label_line)
            nuclei_text = self._canvas.create_text(
                padding, middle + int(self._row_height / 4),
                text='error', anchor='nw', fill=label_line)
            positive_text = self._canvas.create_text(
                padding + (width - 2 * padding) / 4,
                middle + int(self._row_height / 4),
                text='error', anchor='nw', fill=label_line)
            ratio_text = self._canvas.create_text(
                padding + (width - 2 * padding) * 2 / 4,
                middle + int(self._row_height / 4),
                text='error', anchor='nw', fill=label_line)
            fiber_text = self._canvas.create_text(
                padding * 3 + (width - 2 * padding) * 3 / 4,
                middle + int(self._row_height / 4),
                text='error', anchor='nw', fill=label_line)

            # append the handles
            self._items[file] = (Table_element(Labels(name_text,
                                                      nuclei_text,
                                                      positive_text,
                                                      ratio_text,
                                                      index_text,
                                                      fiber_text),
                                               Lines(half_line,
                                                     full_line,
                                                     index_line),
                                               Rectangle(rect)))

            self._index_to_img[i] = file
            self._img_to_index[file] = i

            # update the text
            self._update_data(file)

        # set scroll region
        self._canvas.config(scrollregion=(0, 0, width, self._table_height))

        # create highlighted parts
        if self.filenames:
            if self._current_image is None:
                self._current_image = self._index_to_img[0]
            self._select_image(self._img_to_index[self._current_image])
        else:
            self._image_canvas.reset()
