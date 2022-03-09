# coding: utf-8

from tkinter import Canvas, ttk, Event
from PIL import Image, ImageTk
from platform import system
from functools import partial
from copy import deepcopy
from pathlib import Path
from typing import NoReturn, Tuple, Optional

from .tools import Nucleus, Fibre, Nuclei, Fibres, check_image


class Image_canvas(ttk.Frame):
    """This class manages the display of one image, its nuclei and its
    fibers."""

    def __init__(self, mainframe: ttk.Frame, main_window) -> None:
        """Initializes the frame, the layout, the callbacks and the
        variables."""

        super().__init__(mainframe)

        self.nuclei_table = None
        self._main_window = main_window
        self._settings = self._main_window.settings
        self._draw_nuclei = self._main_window.draw_nuclei

        self._set_layout()
        self._set_bindings()
        self._set_variables()

    def set_channels(self) -> NoReturn:
        """Reloads the image after the user changed the selected channels."""

        self._set_image()
        self._show_image()

    def set_indicators(self) -> NoReturn:
        """Redraws the nuclei and/or fibres after the user changed the elements
        to display."""

        # Deletes all the elements in the canvas
        self._delete_nuclei()
        self._delete_fibres()

        # Draw the nuclei
        if self._settings.show_nuclei.get():
            for nuc in self._nuclei:
                nuc.tk_obj = self._draw_nucleus(
                    nuc.x_pos, nuc.y_pos,
                    self.nuc_color_in if nuc.color == 'in'
                    else self.nuc_color_out)

        # Draw the fibers
        if self._settings.show_fibres.get():
            for fibre in self._fibres:
                fibre.h_line,  fibre.v_line = \
                    self._draw_fibre(fibre.x_pos, fibre.y_pos)

    def load_image(self,
                   path: Path,
                   nuclei: Nuclei,
                   fibres: Fibres) -> NoReturn:
        """Loads and displays an image and its fibres and nuclei.

        Args:
            path: The path to the image to load.
            nuclei: The Nuclei object containing the position and color of the
                nuclei to draw on top of the image.
            fibres: The Fibres object containing the position of the fibres to
                draw on top of the image.
        """

        # First, reset the canvas
        self.reset()
        self._delete_nuclei()
        self._delete_fibres()

        # Then, load and display the image
        self._image_path = path
        self._set_image()
        self._resize_to_canvas()
        self._show_image()

        # Deep copy to have independent objects
        self._nuclei = deepcopy(nuclei)

        # Drawing the nuclei
        if self._settings.show_nuclei.get():
            for nuc in self._nuclei:
                nuc.tk_obj = self._draw_nucleus(
                    nuc.x_pos, nuc.y_pos,
                    self.nuc_color_in if nuc.color == 'in'
                    else self.nuc_color_out)

        # Deep copy to have independent objects
        self._fibres = deepcopy(fibres)

        # Drawing the fibres
        if self._settings.show_fibres.get():
            for fib in self._fibres:
                fib.h_line, fib.v_line = self._draw_fibre(fib.x_pos, fib.y_pos)

    def reset(self) -> NoReturn:
        """Resets every object in the canvas: the image, the nuclei and the
        fibres."""

        # Resetting the variables
        self._image = None
        self._img_scale = 1.0
        self._can_scale = 1.0
        self._current_zoom = 0

        # Removing the fibres and nuclei from the canvas
        self._delete_nuclei()
        self._delete_fibres()

        # Resetting the fibres and nuclei objects
        self._nuclei = Nuclei()
        self._fibres = Fibres()

        # removing the image from the canvas
        if self._image_id is not None:
            self._canvas.delete(self._image_id)
        self._image_id = None

    @property
    def nuc_color_out(self) -> str:
        """Returns the color of the nuclei outside of fibres, that depends on
        the selected channels.

        The color returned is the RGB color that is neither the one of nuclei
        nor the one of fibers.
        """

        num_to_color = {0: 'blue', 1: '#32CD32', 2: 'red'}
        color_to_num = {'blue': 0, 'green': 1, 'red': 2}

        fibre_num = color_to_num[self._settings.fibre_colour.get()]
        nuclei_num = color_to_num[self._settings.nuclei_colour.get()]

        if not (fibre_num == 2 and nuclei_num == 0):
            return num_to_color[3 - fibre_num - nuclei_num]
        else:
            return 'red'

    @property
    def nuc_color_in(self) -> str:
        """Returns the color of the nuclei inside fibres, that depends on the
        selected channels."""

        if self._settings.nuclei_colour.get() == 'green':
            if self._settings.fibre_colour.get() == 'red':
                return 'magenta'
            else:
                return 'blue'

        elif self._settings.nuclei_colour.get() == 'red':
            if self._settings.fibre_colour.get() == 'blue':
                return '#646464'
            else:
                return 'white'

        return 'yellow'

    @property
    def fib_color(self) -> str:
        """returns the color of the fibres, that depends on the selected
        channels."""

        if self._settings.fibre_colour.get() == 'green':
            return 'magenta'

        elif self._settings.fibre_colour.get() == 'blue':
            if self._settings.nuclei_colour.get() == 'green':
                return 'magenta'
            else:
                return 'white'

        elif self._settings.nuclei_colour.get() == 'green':
            return 'cyan'

        else:
            return '#FFA500'
    
    def _delete_nuclei(self) -> NoReturn:
        """Removes all nuclei from the canvas, but doesn't delete the nuclei
        objects."""

        for nuc in self._nuclei:
            self._canvas.delete(nuc.tk_obj)
    
    def _delete_fibres(self) -> NoReturn:
        """Removes all fibres from the canvas, but doesn't delete the fibres
         objects."""

        for fibre in self._fibres:
            self._canvas.delete(fibre.h_line)
            self._canvas.delete(fibre.v_line)

    def _set_layout(self) -> NoReturn:
        """Creates the frame, canvas and scrollbar objects, places them and
        displays them."""

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

    def _set_bindings(self) -> NoReturn:
        """Sets the actions to perform for the different user inputs."""

        self._canvas.bind('<Configure>', self._show_image)
        self._canvas.bind('<ButtonPress-2>', self._move_from)
        self._canvas.bind('<B2-Motion>', self._move_to)

        # Different mousewheel management in Linux and Windows
        if system() == "Linux":
            self._canvas.bind('<4>', self._zoom)
            self._canvas.bind('<5>', self._zoom)
        else:
            self._canvas.bind('<MouseWheel>', self._zoom)

        # Moving with the arrow keys
        self.bind_all('<Left>', partial(self._arrows, arrow_index=0))
        self.bind_all('<Right>', partial(self._arrows, arrow_index=1))
        self.bind_all('<Up>', partial(self._arrows, arrow_index=2))
        self.bind_all('<Down>', partial(self._arrows, arrow_index=3))

        # Zooming in and out with keyboard keys
        self.bind_all('=', partial(self._zoom, delta=1, mouse=False))
        self.bind_all('+', partial(self._zoom, delta=1, mouse=False))
        self.bind_all('-', partial(self._zoom, delta=-1, mouse=False))
        self.bind_all('_', partial(self._zoom, delta=-1, mouse=False))

        # Clicking with the mouse
        self._canvas.bind('<ButtonPress-1>', self._left_click)
        self._canvas.bind('<ButtonPress-3>', self._right_click)

    def _set_variables(self) -> NoReturn:
        """Sets the variables used in this class."""

        self._image = None
        self._image_path = None
        self._img_scale = 1.0
        self._can_scale = 1.0
        self._delta = 1.3
        self._current_zoom = 0
        self._nuclei = Nuclei()
        self._fibres = Fibres()
        self._image_id = None

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

    def _draw_fibre(self,
                    unscaled_x: float,
                    unscaled_y: float) -> Tuple[int, int]:
        """Draws a single fiber on the canvas.

        Args:
            unscaled_x: The x position of the fibre on the raw image, in
                pixels.
            unscaled_y: The y position of the fibre on the raw image, in
                pixels.

        Returns:
            The indexes tkinter attributed to the two lines of the fiber it
            just drew.
        """

        # Adjusting the length to the scale
        square_size = max(int(10.0 * self._can_scale), 1)

        # Adjusting the position to the scale
        x = unscaled_x * self._img_scale
        y = unscaled_y * self._img_scale

        # Actually drawing the fibre
        hor_line = self._canvas.create_line(x + square_size, y,
                                            x - square_size, y,
                                            width=2,
                                            fill=self.fib_color)
        ver_line = self._canvas.create_line(x, y + square_size, x,
                                            y - square_size, width=2,
                                            fill=self.fib_color)
        return hor_line, ver_line

    def _left_click(self, event: Event) -> None:
        """Upon left click, either adds a new nucleus or a fiber, or switches
        the color of an existing nucleus.

        Args:
            event: The tkinter event associated with the left click.
        """

        if self._image is not None:

            # Do nothing if the click is outside the image
            can_x = self._canvas.canvasx(event.x)
            can_y = self._canvas.canvasy(event.y)
            if can_x >= self._image.width * self._img_scale or \
                    can_y >= self._image.height * self._img_scale:
                return

            # Getting the position of the click on the unscaled image
            rel_x_scale = can_x / self._img_scale
            rel_y_scale = can_y / self._img_scale

            # Case when the nuclei mode is selected
            if self._draw_nuclei.get() and self._settings.show_nuclei.get():

                # Trying to find a close nucleus
                nuc = self._find_closest_nucleus(rel_x_scale, rel_y_scale)

                # One close nucleus found, inverting it colour
                if nuc is not None:
                    if nuc.color == 'out':
                        self._canvas.itemconfig(
                            nuc.tk_obj, fill=self.nuc_color_in)
                        nuc.color = 'in'
                    else:
                        self._canvas.itemconfig(
                            nuc.tk_obj, fill=self.nuc_color_out)
                        nuc.color = 'out'
                    self.nuclei_table.switch_nucleus(nuc)

                # No close nucleus found, adding a new one
                else:
                    new_nuc = Nucleus(rel_x_scale, rel_y_scale,
                                      self._draw_nucleus(rel_x_scale,
                                                         rel_y_scale,
                                                         self.nuc_color_out),
                                      'out')
                    self.nuclei_table.add_nucleus(new_nuc)
                    self._nuclei.append(new_nuc)

                # Setting the unsaved status
                self._main_window.set_unsaved_status()

            # Case when the fibre mode is selected
            elif self._settings.show_fibres.get():

                # Trying to find a close fibre
                fib = self._find_closest_fibre(rel_x_scale, rel_y_scale)

                # No close fibre found, adding a new one
                if fib is None:
                    new_fib = Fibre(rel_x_scale, rel_y_scale,
                                    *self._draw_fibre(rel_x_scale,
                                                      rel_y_scale))
                    self._fibres.append(new_fib)
                    self.nuclei_table.add_fibre(new_fib)

                    # Setting the unsaved status
                    self._main_window.set_unsaved_status()

    def _right_click(self, event: Event) -> None:
        """Upon right click, deletes a nucleus or a fiber.

        Args:
            event: The tkinter event associated with the right click.
        """

        if self._image is not None:

            # Do nothing if the click is outside the image
            can_x = self._canvas.canvasx(event.x)
            can_y = self._canvas.canvasy(event.y)
            if can_x >= self._image.width * self._img_scale or \
                    can_y >= self._image.height * self._img_scale:
                return

            # Getting the position of the click on the unscaled image
            rel_x_scale = can_x / self._img_scale
            rel_y_scale = can_y / self._img_scale

            # Case when the nuclei mode is selected
            if self._draw_nuclei.get() and self._settings.show_nuclei.get():

                # Trying to find a close nucleus
                nuc = self._find_closest_nucleus(rel_x_scale, rel_y_scale)

                # One close nucleus found, deleting it
                if nuc is not None:
                    self.nuclei_table.remove_nucleus(nuc)
                    self._canvas.delete(nuc.tk_obj)
                    self._nuclei.remove(nuc)

                    # Setting the unsaved status
                    self._main_window.set_unsaved_status()

            # Case when the fibre mode is selected
            elif self._settings.show_fibres.get():

                # Trying to find a close fibre
                fib = self._find_closest_fibre(rel_x_scale, rel_y_scale)

                # One close fibre found, deleting it
                if fib is not None:
                    self.nuclei_table.remove_fibre(fib)
                    self._canvas.delete(fib.h_line)
                    self._canvas.delete(fib.v_line)
                    self._fibres.remove(fib)

                    # Setting the unsaved status
                    self._main_window.set_unsaved_status()

    def _find_closest_fibre(self, x: float, y: float) -> Optional[Fibre]:
        """Searches for a close fiber among the existing fibers.

        Args:
            x: The x position where to search for a fiber.
            y: The y position where to search for a fiber.

        Returns:
            The Fiber object closest to the given coordinates, if any close
            enough fiber was found.
        """

        # Adjusting the search radius to the scale
        radius = max(9.0 * self._can_scale / self._img_scale, 9.0)

        closest_fib = None
        closest_distance = None

        # Iterating over the fibers
        for fib in self._fibres:
            # Keeping only those within the radius of search
            if abs(x - fib.x_pos) <= radius and abs(y - fib.y_pos) <= radius:
                dis_sq = (fib.x_pos - x) ** 2 + (fib.y_pos - y) ** 2
                # Keeping only the closest one
                if closest_distance is None or dis_sq < closest_distance:
                    closest_fib = fib
                    closest_distance = dis_sq

        return closest_fib if closest_fib is not None else None

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

    def _set_image(self) -> NoReturn:
        """Loads an image and keeps only the desired channels."""

        if self._image_path:

            # Loading the image
            cv_img, zero_channel = check_image(
                self._image_path,
                self._main_window.base_path / 'app_images' / 'error_image.png')

            # Keeping only the necessary channels
            if not self._settings.red_channel_bool.get():
                cv_img[:, :, 0] = zero_channel
            if not self._settings.green_channel_bool.get():
                cv_img[:, :, 1] = zero_channel
            if not self._settings.blue_channel_bool.get():
                cv_img[:, :, 2] = zero_channel

            image_in = Image.fromarray(cv_img)
            self._image = image_in

    def _resize_to_canvas(self) -> NoReturn:
        """Resizes an image to the current size of the canvas."""

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

    def _arrows(self, _: Event, arrow_index: int) -> NoReturn:
        """Scrolls the image upon pressing on the arrow keys.

        Args:
            _: The event associated with the arrow press.
            arrow_index: The index attributed to the arrow, to differentiate
                them easily.
        """

        if arrow_index == 0:
            self._canvas.xview_scroll(-1, "units")
        elif arrow_index == 1:
            self._canvas.xview_scroll(1, "units")
        elif arrow_index == 2:
            self._canvas.yview_scroll(-1, "units")
        elif arrow_index == 3:
            self._canvas.yview_scroll(1, "units")

        # Redraw the image
        self._show_image()

    def _move_from(self, event: Event) -> NoReturn:
        """Stores the previous coordinates for scrolling with the mouse."""

        if self._image is not None:
            self._canvas.scan_mark(event.x, event.y)
            self._show_image()

    def _move_to(self, event: Event) -> NoReturn:
        """Drags the canvas to a new position."""

        if self._image is not None:
            self._canvas.scan_dragto(event.x, event.y, gain=1)
            self._show_image()

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
            # Setting the point whee to zoom on the image
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
            self._show_image(x=x_can if delta > 0 else None,
                             y=y_can if delta > 0 else None)

    def _show_image(self,
                    *_: Event,
                    x: Optional[float] = None,
                    y: Optional[float] = None) -> None:
        """Displays the image on the canvas.

        Args:
            *_: Ignores the event in case the command was issued by one.
            x: The x position of the mouse, where to zoom.
            y: The y position of the mouse, where to zoom.
        """

        if self._image is not None:
            # Resizing the image to the canvas size
            scaled_x = int(self._image.width * self._img_scale)
            scaled_y = int(self._image.height * self._img_scale)
            image = self._image.resize((scaled_x, scaled_y))

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
                return

            # Scrolling the canvas to keep the mouse on the same point in case
            # we were zooming in
            if x is not None or y is not None:
                self._canvas.xview_scroll(int((self._delta - 1) * x), "units")
                self._canvas.yview_scroll(int((self._delta - 1) * y), "units")
