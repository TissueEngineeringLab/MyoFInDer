# coding: utf-8

from tkinter import Canvas, ttk, Event, messagebox
from PIL import Image, ImageTk
from platform import system
from functools import partial
from copy import deepcopy
from pathlib import Path
from typing import Tuple, Optional, List
import logging

from .tools import Nucleus, Nuclei, Fibers, check_image, SelectionBox


class ImageCanvas(ttk.Frame):
    """This class manages the display of one image, its nuclei and its
    fibers."""

    def __init__(self, mainframe: ttk.Frame, main_window) -> None:
        """Initializes the frame, the layout, the callbacks and the
        variables."""

        # Setting the logger
        self._logger = logging.getLogger("MyoFInDer.ImageCanvas")

        super().__init__(mainframe)

        self.nuclei_table = None
        self._main_window = main_window
        self._settings = self._main_window.settings

        self._set_layout()
        self._set_bindings()

        self.log("Setting the images canvas's variables")

        self._image: Optional[Image] = None
        self._image_path: Optional[Path] = None
        self._img_scale: float = 1.0
        self._can_scale: float = 1.0
        self._delta: float = 1.3
        self._current_zoom: int = 0
        self._nuclei: Nuclei = Nuclei()
        self._fibers: Fibers = Fibers()
        self._image_id: Optional[int] = None
        self._selection_box: SelectionBox = SelectionBox()

    def log(self, msg: str) -> None:
        """Wrapper for reducing the verbosity of logging."""

        self._logger.log(logging.INFO, msg)

    def set_indicators(self) -> None:
        """Redraws the nuclei and/or fibers after the user changed the elements
        to display."""

        # Deletes all the elements in the canvas
        self._delete_nuclei()
        self._delete_fibers()

        # Draw the nuclei
        if self._settings.show_nuclei.get():
            self.log(f"Drawing all the {len(self._nuclei)} nuclei on the "
                     f"canvas")
            for nuc in self._nuclei:
                nuc.tk_obj = self._draw_nucleus(
                    nuc.x_pos, nuc.y_pos,
                    self.nuc_col_in if nuc.color == 'in'
                    else self.nuc_col_out)

        # Draw the fibers
        if self._settings.show_fibers.get():
            self.log(f"Drawing all the {len(self._fibers)} fiber contours on "
                     f"the canvas")
            for fiber in self._fibers:
                fiber.polygon = self._draw_fiber(fiber.position)

    def load_image(self,
                   path: Path,
                   nuclei: Nuclei,
                   fibers: Fibers) -> None:
        """Loads and displays an image and its fibers and nuclei.

        Args:
            path: The path to the image to load.
            nuclei: The Nuclei object containing the position and color of the
                nuclei to draw on top of the image.
            fibers: The Fibers object containing the position of the fibers to
                draw on top of the image.
        """

        self.log(f"Loading the image {path}")

        # First, checking that the image can be loaded
        # Otherwise, all data would be lost !
        if check_image(path)[0] is not None:

            # First, reset the canvas
            self.reset()
            self._delete_nuclei()
            self._delete_fibers()

            # Then, load and display the image
            self._image_path = path
            self._set_image()
            self.show_image()

            # Deep copy to have independent objects
            self._nuclei = deepcopy(nuclei)

            # Drawing the nuclei
            if self._settings.show_nuclei.get():
                self.log(f"Drawing all the {len(self._nuclei)} nuclei on the "
                         f"canvas")
                for nuc in self._nuclei:
                    nuc.tk_obj = self._draw_nucleus(
                        nuc.x_pos, nuc.y_pos,
                        self.nuc_col_in if nuc.color == 'in'
                        else self.nuc_col_out)

            # Deep copy to have independent objects
            self._fibers = deepcopy(fibers)

            # Drawing the fibers
            if self._settings.show_fibers.get():
                self.log(f"Drawing all the {len(self._fibers)} fiber contours "
                         f"on the canvas")
                for fib in self._fibers:
                    fib.polygon = self._draw_fiber(fib.position)

        # Informing the user that the image cannot be loaded
        else:
            messagebox.showerror(f'Error while loading the image !',
                                 f'Check that the image at '
                                 f'{path} still exists and '
                                 f'that it is accessible.')
            self.log(f"Could not load image {path}, aborting")

    def reset(self) -> None:
        """Resets every object in the canvas: the image, the nuclei and the
        fibers."""

        self.log("Resetting the entire image canvas")

        # Resetting the variables
        self._image = None
        self._image_path = None
        self._img_scale = 1.0
        self._can_scale = 1.0
        self._current_zoom = 0

        # Removing the fibers and nuclei from the canvas
        self._delete_nuclei()
        self._delete_fibers()

        # Resetting the fibers and nuclei objects
        self._nuclei = Nuclei()
        self._fibers = Fibers()

        # Removing the image from the canvas
        if self._image_id is not None:
            self._canvas.delete(self._image_id)
        self._image_id = None

        # Resetting the selection box
        self._selection_box = SelectionBox()

    @property
    def nuc_col_out(self) -> str:
        """Returns the color of the nuclei outside of fibers, that depends on
        the selected channels.

        The color returned is the RGB color that is neither the one of nuclei
        nor the one of fibers.
        """

        num_to_color = {0: 'blue', 1: '#32CD32', 2: 'red'}
        color_to_num = {'blue': 0, 'green': 1, 'red': 2}

        fiber_num = color_to_num[self._settings.fiber_colour.get()]
        nuclei_num = color_to_num[self._settings.nuclei_colour.get()]

        if not (fiber_num == 2 and nuclei_num == 0):
            return num_to_color[3 - fiber_num - nuclei_num]
        # Special case when the fiber channel is red and the nuclei are blue
        else:
            return 'red'

    @property
    def nuc_col_in(self) -> str:
        """Returns the color of the nuclei inside fibers, that depends on the
        selected channels."""

        if self._settings.nuclei_colour.get() == 'green':
            if self._settings.fiber_colour.get() == 'red':
                return 'magenta'
            else:
                return 'blue'

        elif self._settings.nuclei_colour.get() == 'red':
            if self._settings.fiber_colour.get() == 'blue':
                return '#646464'
            else:
                return 'white'

        return 'yellow'

    @property
    def fib_color(self) -> str:
        """returns the color of the fibers, that depends on the selected
        channels."""

        if self._settings.fiber_colour.get() == 'green':
            return 'magenta'

        elif self._settings.fiber_colour.get() == 'blue':
            if self._settings.nuclei_colour.get() == 'green':
                return 'magenta'
            else:
                return 'white'

        elif self._settings.fiber_colour.get() == 'red':
            if self._settings.nuclei_colour.get() == 'green':
                return 'cyan'
            else:
                return '#FFA500'

        else:
            raise ValueError(f"Got incorrect fiber color: "
                             f"{self._settings.fiber_colour.get()}")

    def show_image(self, *_: Event) -> None:
        """Displays the image on the canvas.

        Args:
            *_: Ignores the event in case the command was issued by one.
        """

        if self._image is not None:

            self.log(f"Displaying the image {self._image_path}")

            # Keeping only the channels the user wants
            multiplier = (self._settings.red_channel_bool.get(), 0, 0, 0,
                          0, self._settings.green_channel_bool.get(), 0, 0,
                          0, 0, self._settings.blue_channel_bool.get(), 0)
            image = self._image.convert("RGB", multiplier)

            # Resizing the image to the canvas size
            scaled_x = int(image.width * self._img_scale)
            scaled_y = int(image.height * self._img_scale)
            image = image.resize((scaled_x, scaled_y))

            # Actually displaying the image in the canvas
            image_tk = ImageTk.PhotoImage(image)
            self._image_id = self._canvas.create_image(0, 0, anchor='nw',
                                                       image=image_tk)
            self._canvas.lower(self._image_id)
            self._canvas.image_tk = image_tk
            self._canvas.configure(scrollregion=(0, 0, scaled_x, scaled_y))

            # Moving the image to the top left corner if it doesn't fill the
            # canvas
            if scaled_x < self._canvas.winfo_width() or \
                    scaled_y < self._canvas.winfo_height():
                self._canvas.xview_moveto(0),
                self._canvas.yview_moveto(0)

        else:
            self.log("Show image called but no image was set, aborting")
    
    def _delete_nuclei(self) -> None:
        """Removes all nuclei from the canvas, but doesn't delete the nuclei
        objects."""

        self.log("Deleting all the nuclei on the canvas")

        for nuc in self._nuclei:
            if nuc.tk_obj is not None:
                self._canvas.delete(nuc.tk_obj)
                nuc.tk_obj = None

    def _delete_fibers(self) -> None:
        """Removes all fibers from the canvas, but doesn't delete the fibers
         objects."""

        self.log("Deleting all the fibers on the canvas")

        for fiber in self._fibers:
            if fiber.polygon is not None:
                self._canvas.delete(fiber.polygon)
                fiber.polygon = None

    def _set_layout(self) -> None:
        """Creates the frame, canvas and scrollbar objects, places them and
        displays them."""

        self.log("Setting the images canvas's layout")

        # Creating the architecture
        self.pack(expand=True, fill="both", anchor="w", side="left",
                  padx=5, pady=5)
        self._hbar_frame = ttk.Frame(self)
        self._hbar_frame.pack(expand=False, fill="x", anchor="s",
                              side="bottom")

        # Creating the canvas
        self._canvas = Canvas(self,
                              highlightthickness=3,
                              highlightbackground="black")
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))
        self._canvas.pack(expand=True, fill="both", side='left')

        # Creating the vertical scrollbar
        self._vbar = ttk.Scrollbar(self, orient="vertical")
        self._vbar.pack(fill='y', side='right')
        self._vbar.config(command=self._canvas.yview)

        # Creating the horizontal scrollbar
        self._hbar = ttk.Scrollbar(self._hbar_frame, orient="horizontal")
        self._hbar.pack(fill='x')
        self._hbar.config(command=self._canvas.xview)

        # Linking the scrollbars to the canvas
        self._canvas.config(yscrollcommand=self._vbar.set)
        self._canvas.config(xscrollcommand=self._hbar.set)
        self._canvas.configure(xscrollincrement='1', yscrollincrement='1')

        # Finally, applying the changes
        self._canvas.update()

    def _set_bindings(self) -> None:
        """Sets the actions to perform for the different user inputs."""

        self.log("Setting the images canvas's bindings")

        self._canvas.bind('<ButtonPress-2>', self._move_from)
        self._canvas.bind('<B2-Motion>', self._move_to)

        # Different mousewheel management in Linux and Windows
        if system() == "Linux":
            self._canvas.bind('<4>', self._zoom)
            self._canvas.bind('<5>', self._zoom)
        else:
            self._canvas.bind('<MouseWheel>', self._zoom)

        # Moving with the arrow keys
        self.bind_all('<Left>', self._arrows)
        self.bind_all('<Right>', self._arrows)
        self.bind_all('<Up>', self._arrows)
        self.bind_all('<Down>', self._arrows)

        # Zooming in and out with keyboard keys
        self.bind_all('=', partial(self._zoom, delta=1, mouse=False))
        self.bind_all('+', partial(self._zoom, delta=1, mouse=False))
        self.bind_all('-', partial(self._zoom, delta=-1, mouse=False))
        self.bind_all('_', partial(self._zoom, delta=-1, mouse=False))

        # Clicking with the mouse
        self._canvas.bind('<ButtonRelease-1>', self._left_release)
        self._canvas.bind('<ButtonRelease-3>', self._right_release)
        self._canvas.bind('<ButtonPress-1>', self._click)
        self._canvas.bind('<ButtonPress-3>', self._click)
        self._canvas.bind('<B1-Motion>', self._motion)
        self._canvas.bind('<B3-Motion>', self._motion)

    def _draw_nucleus(self,
                      unscaled_x: float,
                      unscaled_y: float,
                      color: str) -> int:
        """Draws a single nucleus on the canvas.

        Args:
            unscaled_x: The x position of the nucleus on the raw image, in
                pixels.
            unscaled_y: The y position of the nucleus on the raw image, in
                pixels.
            color: The color of the nucleus.

        Returns:
            The index tkinter attributed to the nucleus it just drew.
        """

        # Adjusting the radius to the scale
        radius = max(int(3.0 * self._can_scale), 1)

        # Adjusting the position to the scale
        x = unscaled_x * self._img_scale
        y = unscaled_y * self._img_scale

        # Actually drawing the nucleus
        return self._canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline='#fff', width=0)

    def _draw_fiber(self, positions: List[Tuple[float,
                                                float]]) -> int:
        """Draws a single fiber on the canvas.

        Args:
            positions: List of all the points making together the polygon that
                represents the fiber.

        Returns:
            The index tkinter attributed to the polygon it just drew.
        """

        # Adjusting the width to the scale
        line_width = max(int(3 * self._can_scale), 1)

        # Adjusting the positions to the scale
        positions = [(self._img_scale * x, self._img_scale * y)
                     for x, y in positions]

        # Actually drawing the fiber
        positions = [val for pos in positions for val in pos]
        polygon = self._canvas.create_polygon(*positions,
                                              width=line_width,
                                              outline=self.fib_color,
                                              fill='')

        return polygon

    def _draw_box(self) -> int:
        """Draws the selection box for either inverting the nuclei or deleting
        them."""

        # Adjusting the width of the line to the scale
        line_width = max(int(3 * self._can_scale), 1)

        # Creating the rectangle
        return self._canvas.create_rectangle(
            (self._selection_box.x_start * self._img_scale,
             self._selection_box.y_start * self._img_scale,
             self._selection_box.x_end * self._img_scale,
             self._selection_box.y_end * self._img_scale),
            fill='', outline='#888', width=line_width)

    def _click(self, event: Event) -> None:
        """Binding method for a left or right click event.

        Checks whether the click is inside the displayed image, and if so
        stores its coordinates for potentially displaying later a selection
        box.

        Args:
            event: The tkinter event associated with the left or right click.
        """

        # Do nothing if there's no image displayed
        if self._image is not None:

            # The coordinates of the click on the unscaled image
            abs_x = self._canvas.canvasx(event.x) / self._img_scale
            abs_y = self._canvas.canvasy(event.y) / self._img_scale

            # Do something only if the click is inside the image
            if abs_x < self._image.width and abs_y < self._image.height:

                # Saving the position of the click
                self._selection_box.x_start = abs_x
                self._selection_box.y_start = abs_y

    def _motion(self, event: Event) -> None:
        """Binding method for a mouse motion event while either the left or
        the right click is being pressed.

        If all the conditions are met, is simply draws or updates the selection
        box.

        Args:
            event: The tkinter event associated with the mouse motion.
        """

        # Do nothing if there's no image displayed
        # Also nothing if the selection box wasn't initialized on first click
        if self._image is not None and self._selection_box.started:

            # The coordinates of the event on the unscaled image
            abs_x = self._canvas.canvasx(event.x) / self._img_scale
            abs_y = self._canvas.canvasy(event.y) / self._img_scale

            # Do something only if the event is inside the image
            if abs_x < self._image.width and abs_y < self._image.height:

                # Saving the end position of the selection box
                self._selection_box.x_end = abs_x
                self._selection_box.y_end = abs_y

                # Drawing the selection box if it is not already displayed
                if self._selection_box.tk_obj is None:
                    self._selection_box.tk_obj = self._draw_box()

                # Otherwise just updating the displayed selection box
                else:
                    self._canvas.coords(
                        self._selection_box.tk_obj,
                        (self._selection_box.x_start * self._img_scale,
                         self._selection_box.y_start * self._img_scale,
                         self._selection_box.x_end * self._img_scale,
                         self._selection_box.y_end * self._img_scale))

    def _left_release(self, event: Event) -> None:
        """Binding method for a left mouse button release event.

        It simply decides if this event should be handled as a single click or
        if a selection box was drawn.

        Args:
            event: The tkinter event associated with the left mouse button
                release.
        """

        # Selection box is only considered if it exists and if it's big enough
        if self._selection_box and \
                self._selection_box.area * self._img_scale ** 2 > 25:
            self._left_release_box(event)
        # Otherwise the event is treated as a sole click
        else:
            self._left_release_nucleus(event)

        # Cleans up all the selection box related objects before returning
        if self._selection_box.tk_obj is not None:
            self._canvas.delete(self._selection_box.tk_obj)
        self._selection_box = SelectionBox()

    def _left_release_box(self, event: Event) -> None:
        """Method called when the user releases the left mouse button after
        drawing a selection box.

        It inverts all the nuclei found inside the selection box.

        Args:
            event: The tkinter event associated with the left mouse button
                release.
        """

        # Do nothing if there's no image displayed
        if self._image is not None:

            # The coordinates of the click on the unscaled image
            abs_x = self._canvas.canvasx(event.x) / self._img_scale
            abs_y = self._canvas.canvasy(event.y) / self._img_scale

            # Update coordinates only if the click is inside the image
            if abs_x < self._image.width and abs_y < self._image.height:
                self._selection_box.x_end = abs_x
                self._selection_box.y_end = abs_y

            self.log(f"Inversion box drawn from ("
                     f"{self._selection_box.x_start}, "
                     f"{self._selection_box.y_start}) to ("
                     f"{self._selection_box.x_end}, "
                     f"{self._selection_box.y_end})")

            # Inverting all the nuclei found inside the selection box
            for nuc in self._nuclei:
                if self._selection_box.is_inside(nuc.x_pos, nuc.y_pos):
                    self._invert_nucleus(nuc)

    def _left_release_nucleus(self, event: Event) -> None:
        """Upon left click, either adds a new nucleus or a fiber, or switches
        the color of an existing nucleus.

        Args:
            event: The tkinter event associated with the left click.
        """

        # Do nothing if there's no image displayed
        if self._image is not None:

            # The coordinates of the click on the unscaled image
            abs_x = self._canvas.canvasx(event.x) / self._img_scale
            abs_y = self._canvas.canvasy(event.y) / self._img_scale

            # Do something only if the event is inside the image
            if abs_x < self._image.width and abs_y < self._image.height:

                # Do nothing if the nuclei are not being displayed
                if self._settings.show_nuclei.get():

                    # Trying to find a close nucleus
                    nuc = self._find_closest_nucleus(abs_x, abs_y)

                    # One close nucleus found, inverting it colour
                    if nuc is not None:
                        self._invert_nucleus(nuc)

                    # No close nucleus found, adding a new one
                    else:
                        self._add_nucleus(abs_x, abs_y)

    def _right_release(self, event: Event) -> None:
        """Binding method for a right mouse button release event.

        It simply decides if this event should be handled as a single click or
        if a selection box was drawn.

        Args:
            event: The tkinter event associated with the right mouse button
                release.
        """

        # Selection box is only considered if it exists and if it's big enough
        if self._selection_box and \
                self._selection_box.area * self._img_scale ** 2 > 25:
            self._right_release_box(event)
        # Otherwise the event is treated as a sole click
        else:
            self._right_release_nucleus(event)

        # Cleans up all the selection box related objects before returning
        if self._selection_box.tk_obj is not None:
            self._canvas.delete(self._selection_box.tk_obj)
        self._selection_box = SelectionBox()

    def _right_release_box(self, event: Event) -> None:
        """Method called when the user releases the right mouse button after
        drawing a selection box.

        It deletes all the nuclei found inside the selection box.

        Args:
            event: The tkinter event associated with the right mouse button
                release.
        """

        # Do nothing if there's no image displayed
        if self._image is not None:

            # The coordinates of the click on the unscaled image
            abs_x = self._canvas.canvasx(event.x) / self._img_scale
            abs_y = self._canvas.canvasy(event.y) / self._img_scale

            # Update coordinates only if the click is inside the image
            if abs_x < self._image.width and abs_y < self._image.height:
                self._selection_box.x_end = abs_x
                self._selection_box.y_end = abs_y

            self.log(f"Deletion box drawn from ("
                     f"{self._selection_box.x_start}, "
                     f"{self._selection_box.y_start}) to ("
                     f"{self._selection_box.x_end}, "
                     f"{self._selection_box.y_end})")

            to_delete = list()
            # Detecting all the nuclei to delete
            for nuc in self._nuclei:
                if self._selection_box.is_inside(nuc.x_pos, nuc.y_pos):
                    to_delete.append(nuc)
            # Actually deleting the detected nuclei
            for nuc in to_delete:
                self._delete_nucleus(nuc)

    def _right_release_nucleus(self, event: Event) -> None:
        """Method called when the user releases the right mouse button but did
        not draw a selection box.

        Tries to find a nucleus close to the click, and if one was found
        deletes it.

        Args:
            event: The tkinter event associated with the right mouse button
                release.
        """

        # Do nothing if there's no image displayed
        if self._image is not None:

            # The coordinates of the click on the unscaled image
            abs_x = self._canvas.canvasx(event.x) / self._img_scale
            abs_y = self._canvas.canvasy(event.y) / self._img_scale

            # Do something only if the click is inside the image
            if abs_x < self._image.width and abs_y < self._image.height:

                # Do nothing if the nuclei are not being displayed
                if self._settings.show_nuclei.get():

                    # Trying to find a close nucleus
                    nuc = self._find_closest_nucleus(abs_x, abs_y)

                    # One close nucleus found, deleting it
                    if nuc is not None:
                        self._delete_nucleus(nuc)

    def _find_closest_nucleus(self, x: float, y: float) -> Optional[Nucleus]:
        """Searches for a close nucleus among the existing nuclei.

        Args:
            x: The x position where to search for a nucleus.
            y: The y position where to search for a nucleus.

        Returns:
            The Nucleus object closest to the given coordinates, if any close
            enough nucleus was found.
        """

        # Adjusting the search radius to the scale
        radius = max(3.0 * self._can_scale / self._img_scale, 3.0)

        closest_nuc = None
        closest_distance = None

        # Iterating over the nuclei
        for nuc in self._nuclei:
            # Keeping only those within the radius of search
            if abs(x - nuc.x_pos) <= radius and abs(y - nuc.y_pos) <= radius:
                dis_sq = (nuc.x_pos - x) ** 2 + (nuc.y_pos - y) ** 2
                # Keeping only the closest one
                if closest_distance is None or dis_sq < closest_distance:
                    closest_distance = dis_sq
                    closest_nuc = nuc

        return closest_nuc if closest_nuc is not None else None

    def _add_nucleus(self, abs_x: float, abs_y: float) -> None:
        """Creates a Nucleus object, displays it and saves it to the nuclei
        table.

        Also sets the unsaved status for the current project.

        Args:
            abs_x: The x position of the nucleus on the unscaled image
            abs_y: The y position of the nucleus on the unscaled image
        """

        # Creating the nucleus and displaying it
        new_nuc = Nucleus(abs_x, abs_y,
                          self._draw_nucleus(abs_x, abs_y,
                                             self.nuc_col_out),
                          'out')

        self.log(f"Added nucleus at position ({abs_x}, {abs_y})")

        # Adding the nucleus to the nuclei table and to the current nuclei
        self.nuclei_table.add_nucleus(new_nuc)
        self._nuclei.append(new_nuc)

        # Setting the unsaved status
        self._main_window.set_unsaved_status()

    def _invert_nucleus(self, nuc: Nucleus) -> None:
        """Inverts the color and status of a given nucleus.

        Also sets the unsaved status for the current project.

        Args:
            nuc: The Nucleus object to invert
        """

        # Updating the display
        if nuc.color == 'out':
            self._canvas.itemconfig(nuc.tk_obj, fill=self.nuc_col_in)
            nuc.color = 'in'
        else:
            self._canvas.itemconfig(nuc.tk_obj, fill=self.nuc_col_out)
            nuc.color = 'out'

        self.log(f"Inverted nucleus at position ({nuc.x_pos}, {nuc.y_pos})")

        # Updating the nuclei table
        self.nuclei_table.switch_nucleus(nuc)

        # Setting the unsaved status
        self._main_window.set_unsaved_status()

    def _delete_nucleus(self, nuc: Nucleus) -> None:
        """Deletes a given Nucleus and all the references to it.

        Also sets the unsaved status for the current project.

        Args:
            nuc: The Nucleus object to delete
        """

        # Deleting all the references to the nucleus to delete
        self.nuclei_table.remove_nucleus(nuc)
        self._canvas.delete(nuc.tk_obj)
        self._nuclei.remove(nuc)

        self.log(f"Deleted nucleus at position ({nuc.x_pos}, {nuc.y_pos})")

        # Setting the unsaved status
        self._main_window.set_unsaved_status()

    def _set_image(self) -> None:
        """Simply loads an image and resizes it to the current size of the
        canvas."""

        if self._image_path:

            self.log(f"Loading image {self._image_path}")

            # Loading the image
            cv_img = check_image(self._image_path)
            # Handling the case when the image cannot be loaded
            if cv_img is None:
                messagebox.showerror(f'Error while loading the image !',
                                     f'Check that the image at '
                                     f'{self._image_path} still exists and '
                                     f'that it is accessible.')
                self.log(f"ERROR ! Could not load image {self._image_path}")
                return

            self._image = Image.fromarray(cv_img)

            # Getting the different parameters of interest
            can_width = self._canvas.winfo_width()
            can_height = self._canvas.winfo_height()
            can_ratio = can_width / can_height
            img_ratio = self._image.width / self._image.height

            # Calculating the new image width
            if img_ratio >= can_ratio:
                resize_width = can_width
            else:
                resize_width = int(can_height * img_ratio)

            # Deducing the new image scale
            self._img_scale = resize_width / self._image.width

        else:
            self.log("Image loading requested but no file was selected, "
                     "ignoring")

    def _arrows(self, event: Event) -> None:
        """Scrolls the image upon pressing on the arrow keys.

        Args:
            event: The event associated with the arrow press.
        """

        self._canvas.configure(xscrollincrement='10', yscrollincrement='10')

        if event.keysym == 'Left':
            self._canvas.xview_scroll(-1, "units")
        elif event.keysym == 'Right':
            self._canvas.xview_scroll(1, "units")
        elif event.keysym == 'Up':
            self._canvas.yview_scroll(-1, "units")
        elif event.keysym == 'Down':
            self._canvas.yview_scroll(1, "units")

        self._canvas.configure(xscrollincrement='1', yscrollincrement='1')

    def _move_from(self, event: Event) -> None:
        """Stores the previous coordinates for scrolling with the mouse."""

        if self._image is not None:
            self._canvas.scan_mark(event.x, event.y)

    def _move_to(self, event: Event) -> None:
        """Drags the canvas to a new position."""

        if self._image is not None:
            self._canvas.scan_dragto(event.x, event.y, gain=1)

    def _zoom(self,
              event: Event,
              delta: Optional[int] = None,
              mouse: bool = True) -> None:
        """Zooms in or out of the image.

        Args:
            event: The tkinter event associated with the scrolling command.
            delta: If positive, zooms in, if negative, zooms out.
            mouse: Does the zoom command come from the mouse wheel ? If yes,
                zoom to the current position of the mouse, else to the top left
                corner of the image.
        """

        if self._image is not None:

            # Linux mousewheel events do not hold information about the delta,
            # so we need to set it manually
            if delta is None:
                if system() == "Linux":
                    delta = 1 if event.num == 4 else -1
                else:
                    delta = int(event.delta / abs(event.delta))

            scale = 1.0
            # Setting the point where to zoom on the image
            x_can = self._canvas.canvasx(event.x) if mouse else 0
            y_can = self._canvas.canvasy(event.y) if mouse else 0

            # Zooming out
            if delta < 0:
                # Limit to 4 zooms out
                if self._current_zoom < -4:
                    return

                # Setting the new image and canvas scales
                self._img_scale /= self._delta
                self._can_scale /= self._delta
                scale /= self._delta
                self._current_zoom -= 1

                # Scrolling the canvas to keep the mouse on the same point
                self._canvas.xview_scroll(int((1 / self._delta - 1) * x_can),
                                          "units")
                self._canvas.yview_scroll(int((1 / self._delta - 1) * y_can),
                                          "units")

            # Zooming in
            elif delta > 0:
                # Limit to 4 zooms in
                if self._current_zoom > 4:
                    return

                # Setting the new image and canvas scales
                self._img_scale *= self._delta
                self._can_scale *= self._delta
                scale *= self._delta
                self._current_zoom += 1

            # Rescaling the canvas
            self._canvas.scale('all', 0, 0, scale, scale)
            # Updating the image
            self.show_image()

            # Scrolling the canvas to keep the mouse on the same point in case
            # we were zooming in and the image is bigger than the canvas
            if delta > 0 and self._current_zoom > 0:
                self._canvas.xview_scroll(int((self._delta - 1) * x_can),
                                          "units")
                self._canvas.yview_scroll(int((self._delta - 1) * y_can),
                                          "units")
