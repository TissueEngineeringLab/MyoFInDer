# coding: utf-8

from dataclasses import dataclass, field
from typing import Optional, List, Any, Tuple, Iterator, Union, Callable, Dict
from tkinter.ttk import Button, Separator, Label
from functools import partial
from tkinter import StringVar, IntVar, BooleanVar, Checkbutton, PhotoImage, \
    Frame, Event, EventType
from pathlib import Path
from platform import system
import logging


@dataclass
class Nucleus:
    """Class holding the data associated with a single nucleus."""

    x_pos: float
    y_pos: float
    tk_obj: Optional[int]
    color: str

    def __eq__(self, other: Any) -> bool:
        """Two nuclei are considered equal if and only if their x and y
        positions are equal."""

        if not isinstance(other, Nucleus):
            raise NotImplemented("Only two nuclei can be compared together")
        return self.x_pos == other.x_pos and self.y_pos == other.y_pos


@dataclass
class Fiber:
    """Class holding the data associated with a single fiber."""

    polygon: Optional[int]
    position: List[Tuple[float, float]] = field(default_factory=list)


@dataclass
class Nuclei:
    """Class for managing the data of all the nuclei in one image."""

    nuclei: List[Nucleus] = field(default_factory=list)

    def append(self, nuc: Nucleus) -> None:
        """Adds a nucleus to the list of nuclei."""

        self.nuclei.append(nuc)

    def remove(self, nuc: Nucleus) -> None:
        """Removes a given nucleus from the list of nuclei."""

        try:
            self.nuclei.remove(nuc)
        except ValueError:
            raise ValueError("No matching nucleus to delete")

    def reset(self) -> None:
        """Deletes all the saved Nucleus objects."""

        self.nuclei = list()

    def __iter__(self) -> Iterator[Nucleus]:
        """Returns an iterator over the saved Nucleus objects."""

        return iter(self.nuclei)

    @property
    def nuclei_in_count(self) -> int:
        """Returns the number of nuclei inside fibers."""

        return len([nuc for nuc in self.nuclei if nuc.color == 'in'])

    @property
    def nuclei_out_count(self) -> int:
        """Returns the number of nuclei outside fibers."""

        return len([nuc for nuc in self.nuclei if nuc.color == 'out'])

    def __len__(self) -> int:
        """Returns the number of nuclei."""

        return len(self.nuclei)


@dataclass
class Fibers:
    """Class for managing the data of all the fibers in one image."""

    area: float = field(default=0)
    fibers: List[Fiber] = field(default_factory=list)

    def append(self, fib: Fiber) -> None:
        """Adds a fiber to the list of fibers."""

        self.fibers.append(fib)

    def remove(self, fib: Fiber) -> None:
        """Removes a given fiber from the list of fibers."""

        try:
            self.fibers.remove(fib)
        except ValueError:
            raise ValueError("No matching fiber to delete")

    def reset(self) -> None:
        """Deletes all the saved Fiber objects."""

        self.fibers = list()
        self.area = 0

    def __iter__(self) -> Iterator[Fiber]:
        """Returns an iterator over the stored Fiber objects."""

        return iter(self.fibers)

    def __len__(self) -> int:
        """Returns the number of fibers."""

        return len(self.fibers)


class GraphicalElement(Frame):
    """Class holding all the canvas elements for one image."""

    def __init__(self,
                 canvas: Frame,
                 number: int,
                 name: str,
                 delete_cmd: Callable,
                 check_cmd: Callable,
                 scroll_cmd: Callable,
                 select_cmd: Callable) -> None:
        """Sets the args, the attributes, the layout and the bindings.

        Args:
            canvas: The parent canvas in which the Frame is contained.
            number: The index of the Frame in the list of opened files.
            name: The name of the associated file, as displayed in the
                interface.
            delete_cmd: The callback command associated with the delete button.
            check_cmd: The callback command associated with the checkbox check.
            scroll_cmd: The callback command to call when a scroll action is
                performed.
            select_cmd: The callback command to call when a mouse click action
                is performed.
        """

        super().__init__(canvas)

        # Saving some attributes for later
        self._scroll_cmd = scroll_cmd
        self._select_cmd = select_cmd
        self._number = number

        # Instantiating variables
        self.selected = BooleanVar(self, value=False)
        self.button_var = BooleanVar(self, value=True)

        # Displaying the layout
        self._set_layout(number=number,
                         name=name,
                         delete_cmd=delete_cmd,
                         check_cmd=check_cmd)
        self.config(highlightthickness=3)
        self.config(highlightbackground='grey')

        # Adding traces and bindings
        self.selected.trace_add('write', self._select_trace)
        self.bind('<Enter>', self._hover)
        self.bind('<Leave>', self._hover)
        self._bind_wheel(self)
        self._bind_button(self)

    def _select_trace(self, _: str, __: str, ___: str) -> None:
        """A simple wrapper for calling the _hover method when the value of the
        selected boolean var is modified."""

        e = Event()
        e.type = None
        self._hover(e)

    def _bind_wheel(self, obj) -> None:
        """Method binding the mouse wheel action of an object to the
        associated scroll callback."""

        # Different wheel management in Windows and Linux
        if system() == "Linux":
            obj.bind('<4>', self._scroll_cmd)
            obj.bind('<5>', self._scroll_cmd)
        else:
            obj.bind('<MouseWheel>', self._scroll_cmd)

    def _bind_button(self, obj) -> None:
        """Method binding the mouse click action of an object to the
        associated click callback."""

        obj.bind('<ButtonPress-1>', partial(self._select_cmd,
                                            index=self._number))

    def _set_layout(self,
                    number: int,
                    name: str,
                    delete_cmd: Callable,
                    check_cmd: Callable) -> None:
        """Sets the layout of the Frame.

        Args:
            number: The index of the Frame in the list of opened files.
            name: The name of the associated file, as displayed in the
                interface.
            delete_cmd: The callback command associated with the delete button.
            check_cmd: The callback command associated with the checkbox check.
        """

        self.pack(expand=True, fill='x', pady=0, padx=0,
                  side='top', anchor='n')

        # The upper half of the frame
        self.frame_up = Frame(self)
        self.frame_up.pack(expand=True, fill='x', side='top', anchor='n')
        self._bind_wheel(self.frame_up)
        self._bind_button(self.frame_up)

        # Horizontal separator between the two halves of the frame
        self.sep_h = Separator(self, orient='horizontal')
        self.sep_h.pack(expand=True, fill='x', side='top', anchor='n')
        self._bind_wheel(self.sep_h)
        self._bind_button(self.sep_h)

        # The upper half of the frame
        self.frame_down = Frame(self)
        self.frame_down.pack(expand=True, fill='x', side='top', anchor='n')
        self._bind_wheel(self.frame_down)
        self._bind_button(self.frame_down)

        # The number of the frame in the list of all the frames
        self.label = Label(self.frame_up, text=str(number))
        self.label.pack(expand=False, fill='none', pady=15, padx=15,
                        side='left', anchor='w')
        self._bind_wheel(self.label)
        self._bind_button(self.label)

        # The button for deleting the frame
        self.close_button = Button(self.frame_up, text='X', width=2,
                                   command=delete_cmd)
        self.close_button.pack(expand=True, fill='none', side='right',
                               anchor='e', padx=(0, 2))
        self._bind_wheel(self.close_button)

        # The check button associated with the frame
        self.img = PhotoImage(width=1, height=1)
        self.check_button = Checkbutton(self.frame_up, image=self.img, width=6,
                                        height=24, variable=self.button_var,
                                        command=check_cmd)
        self.check_button.pack(expand=True, fill='none', side='right',
                               anchor='e')
        self._bind_wheel(self.check_button)

        # A vertical separator between the index of the frame and its name
        self.sep_v = Separator(self.frame_up, orient='vertical')
        self.sep_v.pack(expand=True, fill='y', side='left', anchor='w')
        self._bind_wheel(self.sep_v)
        self._bind_button(self.sep_v)

        # The name of the file associated with the frame
        self.name = Label(self.frame_up, text=name, width=40,
                          font=('Helvetica', 10))
        self.name.pack(expand=False, fill='none', padx=3, pady=15,
                       side='left', anchor='w')
        self._bind_wheel(self.name)
        self._bind_button(self.name)

        # The total number of detected nuclei
        self.total = Label(self.frame_down, text='error',
                           font=('Helvetica', 10))
        self.total.pack(expand=True, fill='x', side='left', anchor='w',
                        padx=0, pady=15)
        self._bind_wheel(self.total)
        self._bind_button(self.total)

        # The number of positive detected nuclei
        self.positive = Label(self.frame_down, text='error',
                              font=('Helvetica', 10))
        self.positive.pack(expand=True, fill='x', side='left', anchor='w',
                           padx=0, pady=15)
        self._bind_wheel(self.positive)
        self._bind_button(self.positive)

        # The ratio of positive nuclei over the total detected nuclei
        self.ratio = Label(self.frame_down, text='error',
                           font=('Helvetica', 10))
        self.ratio.pack(expand=True, fill='x', side='left', anchor='w',
                        padx=0, pady=15)
        self._bind_wheel(self.ratio)
        self._bind_button(self.ratio)

        # The percentage of area covered by fibers over the total image area
        self.area = Label(self.frame_down, text='error',
                          font=('Helvetica', 10))
        self.area.pack(expand=True, fill='x', side='left', anchor='w',
                       padx=0, pady=15)
        self._bind_wheel(self.area)
        self._bind_button(self.area)

    def _hover(self, event: Event) -> None:
        """Callback method called when the mouse enters or exits the Frame, or
        when the selected status of the Frame is updated."""

        # Highlight the frame if it's selected or being hovered
        if self.selected.get() or event.type == EventType.Enter:
            color = 'black'
        else:
            color = 'grey'

        self.config(highlightbackground=color)


@dataclass
class TableEntry:
    """Class holding all the information associated with one image."""

    path: Union[Path, str]
    nuclei: Nuclei
    fibers: Fibers
    graph_elt: Optional[GraphicalElement] = None

    @property
    def save_version(self):
        """Returns a simpler version of the current class, with no canvas
        object and with the path truncated to only the file name."""

        return TableEntry(path=self.path.name,
                          nuclei=self.nuclei,
                          fibers=self.fibers,
                          graph_elt=None)


@dataclass
class TableItems:
    """Class storing all the TableEntry classes of the opened project.

    It also implements many helper functions for simplifying the code in the
    rest of the project.
    """

    entries: List[TableEntry] = field(default_factory=list)
    current_index: Optional[int] = None

    def __getitem__(self, item: Path) -> TableEntry:
        """Returns the TableEntry object whose path corresponds to the given
        one."""

        # Searches for the first (hopefully the only) entry with a given path
        for entry in self.entries:
            if entry.path == item:
                return entry

        # In the (unlikely) case when there's no entry for the requested path
        raise KeyError

    def __iter__(self) -> Iterator[TableEntry]:
        """Returns an iterator over the stored TableEntry objects."""

        return iter(self.entries)

    def __bool__(self) -> bool:
        """Returns True if there's at least one stored TableEntry, False
        otherwise."""

        return bool(self.entries)

    def __len__(self) -> int:
        """Returns the number of stored TableEntry objects."""

        return len(self.entries)

    @property
    def file_names(self) -> List[Path]:
        """Returns a list of all the paths of the stored TableEntry
        objects."""

        return [entry.path for entry in self]

    @property
    def current_entry(self) -> Optional[TableEntry]:
        """Returns the TableEntry instance corresponding to the currently
        displayed image."""

        if self.selected is None:
            return

        return self[self.selected]

    @property
    def selected(self) -> Optional[Path]:
        """Returns the path of the TableEntry instance corresponding to the
        currently displayed image."""

        for entry in self.entries:
            if entry.graph_elt.selected.get():
                return entry.path

    @property
    def save_version(self):
        """Returns a simpler version of the current class, with no canvas
        object and with the paths of the TableEntry objects truncated to only
        the file name."""

        return TableItems(entries=[entry.save_version for entry
                                   in self.entries])

    def reset(self) -> None:
        """Resets all the graphics and deletes all the stored TableEntry
        objects."""

        self.reset_graphics()
        self.entries = list()

    def reset_graphics(self) -> None:
        """Deletes all the displayed Frames of the Table_entries, but keeps the
        other attributes of the entries."""

        for entry in self:
            entry.graph_elt.pack_forget()
            entry.graph_elt.destroy()
            del entry.graph_elt

    def append(self, entry: TableEntry) -> None:
        """Adds a TableEntry object to the list of the stored ones."""

        self.entries.append(entry)

    def remove(self, path: Path) -> None:
        """Removes the TableEntry object corresponding to the given path from
        the list of the stored ones."""

        try:
            self.entries.remove(self[path])
        except KeyError:
            raise ValueError(f"No table entry associated with the path {path}")

    def index(self, path: Path) -> int:
        """Returns the position of the TableEntry corresponding to the given
        path in the list of all the stored TableEntry objects."""

        for i, entry in enumerate(self):
            if entry.path == path:
                return i

        raise ValueError(f"No table entry associated with the path {path}")


@dataclass
class SelectionBox:
    """Class holding the data associated with the selection box of the image
    canvas."""

    x_start: Optional[int] = None
    y_start: Optional[int] = None
    x_end: Optional[int] = None
    y_end: Optional[int] = None
    tk_obj: Optional[int] = None

    def __bool__(self) -> bool:
        """Returns True if all four corners of the selection box have been
        defined, else False."""

        return all(item is not None for item in (self.x_start, self.y_start,
                                                 self.x_end, self.y_end))

    def is_inside(self, x: float, y: float) -> bool:
        """Checks whether a given point is inside or outside the selection box.

        Args:
            x: The x coordinate of the point to check.
            y: The y coordinate of the point to check.

        Returns:
            True if the given coordinates lie inside the selection box, False
            otherwise.
        """

        if not bool(self):
            return False

        x_min = min(self.x_start, self.x_end)
        x_max = max(self.x_start, self.x_end)
        y_min = min(self.y_start, self.y_end)
        y_max = max(self.y_start, self.y_end)

        return (x_min <= x <= x_max) and (y_min <= y <= y_max)

    @property
    def started(self) -> bool:
        """Returns True if the first corner of the selection box has been
        defined, else False."""

        return self.x_start is not None and self.y_start is not None

    @property
    def area(self) -> int:
        """Returns the area of the selection box."""

        return abs((self.x_end - self.x_start) * (self.y_end - self.y_start))


@dataclass
class Settings:
    """Class holding the current values of all the settings."""

    # Here a default factory is needed so that the tkinter vars are not
    # instantiated before the tkinter app is initialized
    fiber_colour: StringVar = field(
        default_factory=partial(StringVar, value="green", name='fiber_colour'))
    nuclei_colour: StringVar = field(
        default_factory=partial(StringVar, value="blue", name='nuclei_colour'))
    save_overlay: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False, name='save_overlay'))
    minimum_fiber_intensity: IntVar = field(
        default_factory=partial(IntVar, value=25,
                                name='minimum_fiber_intensity'))
    maximum_fiber_intensity: IntVar = field(
        default_factory=partial(IntVar, value=255,
                                name='maximum_fiber_intensity'))
    minimum_nucleus_intensity: IntVar = field(
        default_factory=partial(IntVar, value=25,
                                name='minimum_nucleus_intensity'))
    maximum_nucleus_intensity: IntVar = field(
        default_factory=partial(IntVar, value=255,
                                name='maximum_nucleus_intensity'))
    minimum_nuc_diameter: IntVar = field(
        default_factory=partial(IntVar, value=20, name='minimum_diameter'))
    minimum_nuclei_count: IntVar = field(
        default_factory=partial(IntVar, value=3, name='minimum_nuclei_count'))
    blue_channel_bool: BooleanVar = field(
        default_factory=partial(BooleanVar, value=True, name='blue_channel'))
    green_channel_bool: BooleanVar = field(
        default_factory=partial(BooleanVar, value=True, name='green_channel'))
    red_channel_bool: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False, name='red_channel'))
    show_nuclei: BooleanVar = field(
        default_factory=partial(BooleanVar, value=True, name='show_nuclei'))
    show_fibers: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False, name='show_fibers'))

    _logger: Optional[logging.Logger] = None

    def __post_init__(self) -> None:
        """This method defines a logger for this class to be able to log
        messages."""

        self._logger = logging.getLogger("MyoFInDer.FilesTable")

    def get_all(self) -> Dict[str, Any]:
        """Returns a dict containing all the settings and their values."""

        return {
            'fiber_colour': self.fiber_colour.get(),
            'nuclei_colour': self.nuclei_colour.get(),
            'save_overlay': self.save_overlay.get(),
            'minimum_fiber_intensity': self.minimum_fiber_intensity.get(),
            'maximum_fiber_intensity': self.maximum_fiber_intensity.get(),
            'minimum_nucleus_intensity': self.minimum_nucleus_intensity.get(),
            'maximum_nucleus_intensity': self.maximum_nucleus_intensity.get(),
            'minimum_nuc_diameter': self.minimum_nuc_diameter.get(),
            'minimum_nuclei_count': self.minimum_nuclei_count.get(),
            'blue_channel_bool': self.blue_channel_bool.get(),
            'green_channel_bool': self.green_channel_bool.get(),
            'red_channel_bool': self.red_channel_bool.get(),
            'show_nuclei': self.show_nuclei.get(),
            'show_fibers': self.show_fibers.get()}

    def update(self, settings: Dict[str, Any]) -> None:
        """Updates the values of the settings based on the provided dictionary.

        If a key is provided that is not a valid setting, ignores it and
        displays a warning.
        """

        for key, value in settings.items():
            try:
                getattr(self, key).set(value)
            except AttributeError:
                self._logger.log(logging.WARNING, f"The {key} setting is not "
                                                  f"supported, ignoring it !")

    def __str__(self) -> str:
        """Nice string representation of the current settings and their values,
        used for logging."""

        return ', '.join(f"{setting}: {value}" for setting, value
                         in self.get_all().items())
