# coding: utf-8

from dataclasses import dataclass, field
from typing import Optional, List, Any, Tuple, Iterator, Union
from tkinter.ttk import Button
from functools import partial
from tkinter import StringVar, IntVar, BooleanVar, Checkbutton, PhotoImage
from pathlib import Path


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
class Fibre:
    """Class holding the data associated with a single fibre."""

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
        """Returns the number of nuclei inside fibres."""

        return len([nuc for nuc in self.nuclei if nuc.color == 'in'])

    @property
    def nuclei_out_count(self) -> int:
        """Returns the number of nuclei outside fibres."""

        return len([nuc for nuc in self.nuclei if nuc.color == 'out'])

    def __len__(self) -> int:
        """Returns the number of nuclei."""

        return len(self.nuclei)


@dataclass
class Fibres:
    """Class for managing the data of all the fibres in one image."""

    area: float = field(default=0)
    fibres: List[Fibre] = field(default_factory=list)

    def append(self, fib: Fibre) -> None:
        """Adds a fiber to the list of fibres."""

        self.fibres.append(fib)

    def remove(self, fib: Fibre) -> None:
        """Removes a given fiber from the list of fibres."""

        try:
            self.fibres.remove(fib)
        except ValueError:
            raise ValueError("No matching fibre to delete")

    def reset(self) -> None:
        """Deletes all the saved Fibre objects."""

        self.fibres = list()
        self.area = 0

    def __iter__(self) -> Iterator[Fibre]:
        """Returns an iterator over the stored Fibre objects."""

        return iter(self.fibres)

    def __len__(self) -> int:
        """Returns the number of fibres."""

        return len(self.fibres)


@dataclass
class Labels:
    """Class holding the label values for one image."""

    name: int
    nuclei: int
    positive: int
    ratio: int
    index: int
    fiber: int


@dataclass
class Lines:
    """Class holding the canvas line elements for one image."""

    half_line: int
    full_line: int
    index_line: int


@dataclass
class Check:
    """Class holding the objects managing the checkboxes in the canvas."""

    box: Checkbutton
    var: BooleanVar
    img:  PhotoImage


@dataclass
class Graphical_element:
    """Class holding all the canvas elements for one image."""

    labels: Labels
    lines: Lines
    rect: int
    button: Button
    check: Check


@dataclass
class Table_entry:
    """Class holding all the information associated with one image."""

    path: Union[Path, str]
    nuclei: Nuclei
    fibres: Fibres
    graph_elt: Optional[Graphical_element] = None

    @property
    def save_version(self):
        """Returns a simpler version of the current class, with no canvas
        object and with the path truncated to only the file name."""

        return Table_entry(path=self.path.name,
                           nuclei=self.nuclei,
                           fibres=self.fibres,
                           graph_elt=None)


@dataclass
class Table_items:
    """Class storing all the Table_entry classes of the opened project.

    It also implements many helper functions for simplifying the code in the
    rest of the project.
    """

    entries: List[Table_entry] = field(default_factory=list)
    current_path: Optional[Path] = None

    def __getitem__(self, item: Path) -> Table_entry:
        """Returns the Table_entry object whose path corresponds to the given
        one."""

        # Searches for the first (hopefully the only) entry with a given path
        for entry in self.entries:
            if entry.path == item:
                return entry

        # In the (unlikely) case when there's no entry for the requested path
        raise KeyError

    def __iter__(self) -> Iterator[Table_entry]:
        """Returns an iterator over the stored Table_entry objects."""

        return iter(self.entries)

    def __bool__(self) -> bool:
        """Returns True if there's at least one stored Table_entry, False
        otherwise."""

        return bool(self.entries)

    def __len__(self) -> int:
        """Returns the number of stored Table_entry objects."""

        return len(self.entries)

    @property
    def file_names(self) -> List[Path]:
        """Returns a list of all the paths of the stored Table_entry
        objects."""

        return [entry.path for entry in self]

    @property
    def current_entry(self) -> Optional[Table_entry]:
        """Returns the Table_entry instance corresponding to the currently
        displayed image."""

        if self.current_path is None:
            return

        return self[self.current_path]

    @property
    def current_index(self) -> Optional[int]:
        """Returns the index of the Table_entry instance corresponding to the
        currently displayed image in the list of files."""

        if self.current_path is None:
            return

        return self.index(self.current_path)

    @property
    def save_version(self):
        """Returns a simpler version of the current class, with no canvas
        object and with the paths of the Table_entry objects truncated to only
        the file name."""

        return Table_items(entries=[entry.save_version for entry
                                    in self.entries],
                           current_path=None)

    def reset(self) -> None:
        """Deletes all the stored Table_entry objects."""

        self.entries = list()
        self.current_path = None

    def append(self, entry: Table_entry) -> None:
        """Adds a Table_entry object to the list of the stored ones."""

        self.entries.append(entry)

    def remove(self, path: Path) -> None:
        """Removes the Table_entry object corresponding to the given path from
        the list of the stored ones."""

        try:
            self.entries.remove(self[path])
        except KeyError:
            raise ValueError(f"No table entry associated with the path {path}")

    def index(self, path: Path) -> int:
        """Returns the position of the Table_entry corresponding to the given
        path in the list of all the stored Table_entry objects."""

        for i, entry in enumerate(self):
            if entry.path == path:
                return i

        raise ValueError(f"No table entry associated with the path {path}")


@dataclass
class Selection_box:
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
    fibre_colour: StringVar = field(
        default_factory=partial(StringVar, value="green", name='fibre_colour'))
    nuclei_colour: StringVar = field(
        default_factory=partial(StringVar, value="blue", name='nuclei_colour'))
    auto_save_time: IntVar = field(
        default_factory=partial(IntVar, value=-1, name='auto_save_time'))
    save_altered_images: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False, name='save_altered'))
    fibre_threshold: IntVar = field(
        default_factory=partial(IntVar, value=25, name='fibre_threshold'))
    nuclei_threshold: IntVar = field(
        default_factory=partial(IntVar, value=25, name='nuclei_threshold'))
    small_objects_threshold: IntVar = field(
        default_factory=partial(IntVar, value=400, name='small_objects'))
    blue_channel_bool: BooleanVar = field(
        default_factory=partial(BooleanVar, value=True, name='blue_channel'))
    green_channel_bool: BooleanVar = field(
        default_factory=partial(BooleanVar, value=True, name='green_channel'))
    red_channel_bool: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False, name='red_channel'))
    show_nuclei: BooleanVar = field(
        default_factory=partial(BooleanVar, value=True, name='show_nuclei'))
    show_fibres: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False, name='show_fibres'))
