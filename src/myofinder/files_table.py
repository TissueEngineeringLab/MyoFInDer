# coding: utf-8

from tkinter import ttk, Canvas, messagebox, Event, Frame
from xlsxwriter import Workbook
from shutil import copyfile, rmtree
from cv2 import polylines, ellipse, imwrite, cvtColor, COLOR_RGB2BGR
from pathlib import Path
from platform import system
from typing import List, Tuple
from copy import deepcopy
from functools import partial
from pickle import dump, load
from numpy import ndarray, array
import logging

from .tools import Nucleus, Fiber, Nuclei, Fibers, GraphicalElement, \
    check_image, TableItems, TableEntry


class FilesTable(ttk.Frame):
    """This frame stores and displays the different images of the project.

    It also stores the nuclei and fiber count, and handles the saving of images
    and data.
    """

    def __init__(self,
                 root: ttk.Frame,
                 main_window) -> None:
        """Sets the appearance of the frame.

        Args:
            root: The parent frame in which this one is included.
            main_window: the main window of the GUI.
        """

        # Setting the logger
        self._logger = logging.getLogger("MyoFInDer.FilesTable")

        super().__init__(root)

        self._main_window = main_window

        # Setting the appearance
        self._set_layout()

        self.log("Setting the file table's bindings")
        self._canvas.bind('<Configure>', self._on_resize)

        self.image_canvas = None
        self.table_items = TableItems()

    def log(self, msg: str) -> None:
        """Wrapper for reducing the verbosity of logging."""

        self._logger.log(logging.INFO, msg)

    def load_project(self, directory: Path) -> None:
        """Loads an existing project.

        Gets the images names and paths, the fibers positions, and the nuclei
        positions and colors from the data.pickle file.

        Args:
            directory: The path to the directory where the project to load is.
        """

        # First, resetting the project
        self.log("Resetting all the table items")
        self.table_items.reset()

        # Loading the simple version of the stored data
        with open(directory / 'data.pickle', 'rb') as save_file:
            self.log(f"Loading project data from {directory / 'data.pickle'}")
            table_items = load(save_file)

        # Keeping only the data corresponding to existing images
        self.table_items = TableItems(
            entries=[entry for entry in table_items if
                     (directory / 'Original Images' / entry.path).is_file()])

        # Completing the paths to match that of the directory to load
        for entry in self.table_items:
            entry.path = directory / 'Original Images' / entry.path
        loaded = (entry.path for entry in self.table_items)
        self.log(f"Loaded data for images: {', '.join(map(str, loaded))}")

        # Removing any reference to Tkinter objects
        for entry in self.table_items:
            for nucleus in entry.nuclei:
                nucleus.tk_obj = None
            for fiber in entry.fibers:
                fiber.polygon = None

        # Redrawing the canvas
        if self.table_items:
            self._make_table()

    def save_project(self, directory: Path, save_overlay: bool) -> None:
        """Saves a project.

        Saves the images names and paths, the fibers positions, the nuclei
        positions and colors, the images themselves, a .xlsx file containing
        stats of the project, and optionally the images with nuclei and fibers
        drawn on it.

        Args:
            directory: The path to the directory where the project has to be
                saved.
            save_overlay: Should the images with nuclei and fibers drawn be
                saved ?
        """

        self.log(f"Saving the project {directory}")

        # First, save the stats in a .xlsx file
        self._save_table(directory)

        # Then, save the original images
        self._save_originals(directory)

        # If needed, save the overlay images
        if save_overlay:
            self._save_overlay_images(directory)

        # Finally, save the data
        self._save_data(directory)

    def add_nucleus(self, nucleus: Nucleus) -> None:
        """Adds a Nucleus to the Nuclei object associated with the current
        image.

        Args:
            nucleus: The Nucleus object to add.
        """

        self.log(f"Nucleus added at position {nucleus.x_pos}, {nucleus.y_pos}")
        self.table_items.current_entry.nuclei.append(deepcopy(nucleus))
        self._update_data(self.table_items.current_entry)

    def remove_nucleus(self, nucleus: Nucleus) -> None:
        """Removes a Nucleus from the Nuclei object associated with the current
        image.

        Args:
            nucleus: The Nucleus object to remove.
        """

        self.log(f"Nucleus removed at position "
                 f"{nucleus.x_pos}, {nucleus.y_pos}")
        self.table_items.current_entry.nuclei.remove(nucleus)
        self._update_data(self.table_items.current_entry)

    def switch_nucleus(self, nucleus: Nucleus) -> None:
        """Switches the color of a nucleus.

        Args:
            nucleus: The Nucleus object whose color should be switched.
        """

        self.log(f"Nucleus switched at position "
                 f"{nucleus.x_pos}, {nucleus.y_pos}")
        for nuc in self.table_items.current_entry.nuclei:
            if nuc == nucleus:
                nuc.color = 'out' if nuc.color == 'in' else 'in'
        self._update_data(self.table_items.current_entry)

    def add_images(self, filenames: List[Path]) -> None:
        """Adds images to the current frame.

        The new images are added under the existing list of images.

        Args:
            filenames: A list containing the paths to the images to load.
        """

        # Deleting every element in the canvas
        self.log("Deleting all the elements in the image canvas")
        self.table_items.reset_graphics()

        # Making sure there's no conflict between the new and previous images
        for file in filenames:
            if file in self.table_items.file_names:
                messagebox.showerror("Error while loading files",
                                     f"The file {file.name} is already opened,"
                                     f"ignoring.")
                self.log(f"Removing file {file} from the images to add as it "
                         f"is already opened")
                filenames.remove(file)
            elif file.name in [file_.name for file_
                               in self.table_items.file_names]:
                messagebox.showerror("Error while  loading files",
                                     f"A file with the same name ({file.name})"
                                     f"is already opened, ignoring.")
                self.log(f"Removing file {file} from the images to add as an "
                         f"image with the same name is already opened")
                filenames.remove(file)

        self.log(f"Adding the images {', '.join(map(str, filenames))}")

        # Adding the new images to the frame
        for file in filenames:
            self.table_items.append(TableEntry(path=file,
                                               nuclei=Nuclei(),
                                               fibers=Fibers()))

        # Redrawing the canvas
        self._make_table()

    def input_processed_data(
            self,
            nuclei_negative_positions: List[Tuple[float, float]],
            nuclei_positive_positions: List[Tuple[float, float]],
            fiber_contours: Tuple[ndarray],
            area: float,
            file: Path) -> None:
        """Adds the nuclei and fibers positions to the frame after they've been
        computed.

        Args:
            nuclei_negative_positions: The positions of the nuclei outside the
                fibers.
            nuclei_positive_positions: The positions of the nuclei inside the
                fibers.
            fiber_contours: The positions of the contour points of the fibers.
            area: The ratio of fiber area over the total image area.
            file: The path to the file whose nuclei and fibers have been
                computed.
        """

        # Adds the received nuclei to the Nuclei object and draws them
        self.table_items[file].nuclei.reset()
        for x, y in nuclei_negative_positions:
            self.table_items[file].nuclei.append(Nucleus(x, y, None, 'out'))
        for x, y in nuclei_positive_positions:
            self.table_items[file].nuclei.append(Nucleus(x, y, None, 'in'))

        # Adds the received fibers to the Fibers object and draws them
        self.table_items[file].fibers.reset()
        self.table_items[file].fibers.area = area
        for contour in fiber_contours:
            # Ensuring single points are not being outlined
            if len(contour.shape) < 2:
                continue
            contour = list(map(tuple, contour))
            self.table_items[file].fibers.append(Fiber(None, contour))

        # Updates the display
        self._update_data(self.table_items[file])

        # Refreshes the image display if necessary
        if file == self.table_items.selected:
            self.image_canvas.load_image(
                self.table_items.current_entry.path,
                self.table_items.current_entry.nuclei,
                self.table_items.current_entry.fibers)

    def enable_buttons(self, enable: bool) -> None:
        """Enables or disables the close buttons and checkboxes of the images.

        They should be disabled when the program is computing, as the images
        shouldn't be removed at this moment.

        Args:
            enable: Whether the buttons should be enabled or disabled.
        """

        if enable:
            self.log("Enabling the buttons")
        else:
            self.log("Disabling the buttons")

        state = 'normal' if enable else 'disabled'

        for entry in self.table_items:
            entry.graph_elt.check_button['state'] = state
            entry.graph_elt.close_button['state'] = state

    @property
    def all_checked(self) -> bool:
        """Returns True when all the checkboxes of the images are set."""

        # If there's no image, default is True
        if not self.table_items:
            return True

        return all(entry.graph_elt.button_var.get() for entry
                   in self.table_items)

    @property
    def checked_files(self) -> List[Path]:
        """Returns the paths to the files whose checkboxes are checked."""

        return [entry.path for entry in self.table_items
                if entry.graph_elt.button_var.get()]

    def delete_image(self, to_delete: Tuple[Path, ...]) -> None:
        """Removes images from the canvas, and discards all the associated
        data.

        Also handles the update of the index of the image currently displayed.

        Args:
            to_delete: A tuple containing the paths to the images to remove
                from the canvas.
        """

        self.log("Image deletion requested by the user")

        # Security to prevent unwanted deletions
        if len(to_delete) == 1:
            ret = messagebox.askyesno('Hold on !',
                                      f"Do you really want to remove "
                                      f"{to_delete[0].name} ?\n"
                                      f"All the unsaved data will be lost.")

        else:
            ret = messagebox.askyesno('Hold on !',
                                      f"Do you really want to remove "
                                      f"{len(to_delete)} files ?\n"
                                      f"All the unsaved data will be lost.")
        if not ret:
            self.log("Image deletion canceled by the user")
            return

        # Cleaning up the canvas
        self.log("Deleting all the elements in the image canvas")
        self.table_items.reset_graphics()

        # Iterating over the files to delete
        for file in to_delete:

            self.log(f"Deleting the file: {file}")

            # Removing any reference to the image being deleted
            index = self.table_items.index(file)
            self.table_items.remove(file)

            # If there's no entry left in the canvas, resetting the image
            if not self.table_items:
                self.table_items.current_index = None
                self.image_canvas.reset()

            # Selecting a new current image if the prev one was just deleted
            elif self.table_items.current_index == index:
                if len(self.table_items) <= index:
                    self.table_items.current_index = len(self.table_items) - 1

            # Updating the current index if a lower index image was deleted
            elif self.table_items.current_index > index:
                self.table_items.current_index -= 1

        # Re-drawing the canvas
        self._make_table()

        # Updating the master checkbox
        self._main_window.update_master_check()

    def _save_data(self, directory: Path) -> None:
        """Saves the names of the images, the positions of the fibers and the
        positions and colors of the nuclei.

        All this information is stored in a data.pickle file.

        Args:
            directory: The directory where the file should be saved.
        """

        with open(directory / 'data.pickle', 'wb+') as save_file:
            self.log(f"Saving the data to file {directory / 'data.pickle'}")
            dump(self.table_items.save_version, save_file, protocol=4)

    def _save_originals(self, directory: Path) -> None:
        """Saves the original images in a sub-folder of the project folder.

        Args:
            directory: The path to the project folder.
        """

        # Creating the directory if it doesn't exit
        if not (directory / 'Original Images').is_dir():
            self.log(f"Creating the folder for saving the original images at: "
                     f"{directory / 'Original Images'}")
            Path.mkdir(directory / 'Original Images')

        self.log("Saving the original images")

        # Actually saving the images
        for item in self.table_items:
            # Saving only if the images are not saved yet
            if directory not in item.path.parents:
                new_path = directory / 'Original Images' / item.path.name
                self.log(f"Saving the image: {new_path}")

                # Handling the case when the image cannot be loaded
                try:
                    copyfile(item.path, new_path)
                except FileNotFoundError:
                    messagebox.showerror(f'Error while saving the image !',
                                         f'Check that the image at '
                                         f'{item.path} still exists and '
                                         f'that it is accessible.')
                    self.log(f"ERROR! Could not save file {new_path}")
                    continue

                # Changing the saved path for the image
                item.path = new_path

            else:
                self.log(f"Skipping {item.path} as it is already saved")

    def _save_table(self, directory: Path) -> None:
        """Saves a .xlsx file containing stats about the images of the project.

        Args:
            directory: The path to the project folder.
        """

        # Creating the Excel file
        workbook = Workbook(str(directory / str(directory.name + '.xlsx')))
        worksheet = workbook.add_worksheet()

        self.log(f"Saving an overview of the data as an Excel file at "
                 f"{directory / str(directory.name + '.xlsx')}")

        # Bold style for a nicer layout
        bold = workbook.add_format({'bold': True, 'align': 'center'})

        # Writing the labels
        worksheet.write(0, 0, "Image names", bold)
        worksheet.write(0, 1, "Total number of nuclei", bold)
        worksheet.write(0, 2, "Number of tropomyosin positive nuclei", bold)
        worksheet.write(0, 3, "Fusion index", bold)
        worksheet.write(0, 4, "Fiber area ratio", bold)

        # Setting the column widths
        worksheet.set_column(
            0, 0, width=max(11, max(len(file.name) for file
                                    in self.table_items.file_names)
                            if self.table_items else 0))
        worksheet.set_column(1, 1, width=22)
        worksheet.set_column(2, 2, width=37)
        worksheet.set_column(3, 3, width=17)
        worksheet.set_column(4, 4, width=16)

        for i, item in enumerate(self.table_items):
            # Writing the names of the images
            worksheet.write(i + 2, 0, item.path.name)

            # Writing the total number of nuclei
            worksheet.write(i + 2, 1, len(item.nuclei))

            # Writing the number of nuclei in fibers
            worksheet.write(i + 2, 2, item.nuclei.nuclei_in_count)

            # Writing the ratio of nuclei in over the total number of nuclei
            if item.nuclei.nuclei_out_count > 0:
                worksheet.write(i + 2, 3, item.nuclei.nuclei_in_count /
                                len(item.nuclei))
            else:
                worksheet.write(i + 2, 3, 'NA')

            # Writing the percentage area of fibers
            worksheet.write(i + 2, 4, f'{item.fibers.area * 100:.2f}')

        workbook.close()

    def _save_overlay_images(self, directory: Path) -> None:
        """Saves the images with the nuclei and fibers drawn on them.

        Args:
            directory: The path to the project folder.
        """

        # Creates the directory if it doesn't exist yet
        if (directory / 'Overlay Images').is_dir():
            rmtree(directory / 'Overlay Images')
            self.log(f"Creating the folder for saving the overlay images at: "
                     f"{directory / 'Overlay Images'}")
        Path.mkdir(directory / 'Overlay Images')

        self.log("Saving the overlay images")

        # Saves the images
        for entry in self.table_items:
            self._draw_nuclei_save(entry, directory)

    def _draw_nuclei_save(self,
                          entry: TableEntry,
                          project_name: Path) -> None:
        """Draws fibers and nuclei on an images and then saves it.

        Args:
            entry: The table entry whose image to save.
            project_name: The path to the project folder.
        """

        color_to_bgr = {'blue': (255, 0, 0),
                        'green': (0, 255, 0),
                        'red': (0, 0, 255),
                        'yellow': (0, 255, 255),
                        'cyan': (255, 255, 0),
                        'magenta': (255, 0, 255),
                        'black': (0, 0, 0),
                        'white': (255, 255, 255),
                        '#FFA500': (0, 165, 255),
                        '#32CD32': (50, 205, 50),
                        '#646464': (100, 100, 100)}

        # Reads the image
        cv_img = check_image(project_name / "Original Images" /
                             entry.path.name)

        destination = project_name / "Overlay Images" / entry.path.name

        # Aborting if the image cannot be loaded
        if cv_img is None:
            self.log(f"Skipping the image {destination} as the original image "
                     f"could not be loaded")
            return

        cv_img = cvtColor(cv_img, COLOR_RGB2BGR)

        # Adjusting the indicator sizes to the size of the image
        max_dim = max(cv_img.shape)
        line_width = max(1, round(max_dim / 1080))
        spot_size = max(1, round(max_dim / 1080 * 2))

        # Drawing the fibers
        for fib in entry.fibers:
            positions = array(fib.position)
            positions = positions.reshape((-1, 1, 2))
            polylines(cv_img, [positions], True,
                      color_to_bgr[self.image_canvas.fib_color], line_width)

        # Drawing the nuclei
        for nuc in entry.nuclei:
            centre = (int(nuc.x_pos), int(nuc.y_pos))
            if nuc.color == 'out':
                ellipse(cv_img, centre, (spot_size, spot_size), 0, 0, 360,
                        color_to_bgr[self.image_canvas.nuc_col_out], -1)
            else:
                ellipse(cv_img, centre, (spot_size, spot_size), 0, 0, 360,
                        color_to_bgr[self.image_canvas.nuc_col_in], -1)

        # Now saving the image
        self.log(f"Saving the image {destination}")
        imwrite(str(destination), cv_img)

    def _set_layout(self) -> None:
        """Sets the layout of the frame by creating the canvas and the
        scrollbar."""

        self.log("Setting the file table's layout")

        self.pack(expand=True, fill="both", anchor="n", side='top')

        # Creating a frame to put a black border around the canvas
        self._canvas_frame = Frame(self,
                                   highlightbackground='black',
                                   highlightthickness=3)
        self._canvas_frame.pack(expand=True, fill="both", anchor="w",
                                side='left', pady=5)

        # Creating the canvas containing the opened images
        self._canvas = Canvas(self._canvas_frame, bg='#FFFFFF')
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))
        self._canvas.pack(expand=True, fill="both", anchor="w", side='left')

        # Creating a frame inside the canvas that will contain all the
        # individual file frames
        self._scroll_window = Frame(self._canvas, bg='#FFFFFF')
        self._id = self._canvas.create_window(0, 0,
                                              window=self._scroll_window,
                                              anchor='nw')

        # Creating the scrollbar
        self._vbar = ttk.Scrollbar(self, orient="vertical")
        self._vbar.pack(side='right', fill='y', pady=5)
        self._vbar.config(command=self._canvas.yview)
        self._canvas.config(yscrollcommand=self._vbar.set)

        self.update()

    def _on_resize(self, event: Event) -> None:
        """Updates the canvas scroll region and the entries width when the
        overall size of the canvas changes.

        Args:
            event: The resize event.
        """

        # When first drawing the canvas an event of width 0 is received
        width = event.width if event.width > 0 else self._canvas.winfo_width()

        # To make the next lines easier to read
        req_height = self._scroll_window.winfo_reqheight()
        can_height = self._canvas.winfo_height()

        # Event of height 0 received and entries do not fill the canvas
        if event.height == 0 and req_height <= can_height:
            height = can_height
        # Event of height 0 received and entries do not fit in the canvas
        elif event.height == 0:
            height = req_height
        # Entries do not fill the canvas
        elif req_height <= event.height:
            height = event.height
        # Entries do not fit in the canvas
        else:
            height = req_height

        # Re-dimensioning the scroll region and the canvas for a nice layout
        self._canvas.config(scrollregion=(0, 0, width, height))
        self._canvas.itemconfig(self._id, width=width)

    def _on_wheel(self, event: Event) -> None:
        """Scrolls the canvas up or down upon wheel motion."""

        # Different wheel management in Windows and Linux
        if system() == "Linux":
            delta = 1 if event.num == 4 else -1
        else:
            delta = int(event.delta / abs(event.delta))

        if self._scroll_window.winfo_reqheight() > self._canvas.winfo_height():
            self._canvas.yview_scroll(-delta, "units")

    def _select_image(self, _: Event, index: int) -> None:
        """Unselects the previous entry, selects the new one and displays the
        associated image and data.

        Args:
            _: The mouse click event that triggered the image selection.
            index: The index in the canvas of the entry that was just clicked.
        """

        self.log(f"Entry with index {index} selected by the user")

        # Getting the entry at the given index
        entry = self.table_items.entries[index]

        # If the entry is already the selected one, do nothing
        if entry.graph_elt.selected.get():
            self.log(f"Skipping as it is already the current selected one")
            return

        # Unselecting the previously selected entry
        if self.table_items.selected is not None:
            self.table_items.current_entry.graph_elt.selected.set(False)

        # Selecting the new entry
        entry.graph_elt.selected.set(True)
        self.table_items.current_index = index

        # Displaying the selected image with its nuclei and fibers
        self.image_canvas.load_image(entry.path, entry.nuclei, entry.fibers)

        self.log(f"Loaded data for the entry {entry.path}")

    def _make_table(self) -> None:
        """Draws the entire canvas."""

        self.log("Drawing the entire files table")

        # The canvas is built iteratively
        for i, entry in enumerate(self.table_items):

            # Setting the file name
            file_name = entry.path.name
            if len(file_name) >= 39:
                file_name = f'...{file_name[-36:]}'

            # Creating a graphical element representing the entry
            entry.graph_elt = GraphicalElement(
                canvas=self._scroll_window,
                number=i,
                name=file_name,
                delete_cmd=partial(self.delete_image, (entry.path,)),
                check_cmd=self._main_window.update_master_check,
                scroll_cmd=self._on_wheel,
                select_cmd=self._select_image)

            # Updating the displayed text according to the data
            self._update_data(entry)

        # Highlighting the selected image
        if self.table_items:
            # Keeping the current index if it exists
            if self.table_items.current_index is not None:
                index = self.table_items.current_index
            # Setting the current index to 0 otherwise
            else:
                index = 0
            # Sending an event for displaying the selected image
            self.table_items.entries[index].graph_elt.event_generate(
                '<ButtonPress-1>', when="tail")

        # Updating the canvas and making sure it configures itself as requested
        self.update()
        self._canvas.event_generate("<Configure>", when="tail")

    def _update_data(self, entry: TableEntry) -> None:
        """Updates the display when data about an image has changed.

        Args:
            entry: The path to the image whose data should be updated.
        """

        self.log(f"Updating the data for the entry {entry.path}")

        # To avoid repeated calls to the same attribute
        nuclei = entry.nuclei
        fibers = entry.fibers
        items = entry.graph_elt
        total_nuclei = len(nuclei)

        # Updating the labels
        items.total.configure(text=f'Total : {total_nuclei}')
        items.positive.configure(text=f'Positive : {nuclei.nuclei_in_count}')
        if total_nuclei > 0:
            items.ratio.configure(
                text=f'Ratio : '
                     f'{int(100 * nuclei.nuclei_in_count / total_nuclei)}%')
        else:
            items.ratio.configure(text='Ratio : NA')
        items.area.configure(text=f'Fiber area : {int(fibers.area * 100)}%')
