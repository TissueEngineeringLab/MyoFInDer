# coding: utf-8

from dataclasses import dataclass, field
from typing import Optional, List, Any, NoReturn, Tuple
from tkinter.ttk import Button
from functools import partial
from tkinter import StringVar, IntVar, BooleanVar


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
class Table_element:
    """Class holding all the canvas elements for one image."""

    labels: Labels
    lines: Lines
    rect: int
    button: Button


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

    _current_index: int = -1

    def append(self, nuc: Nucleus) -> NoReturn:
        """Adds a nucleus to the list of nuclei."""

        self.nuclei.append(nuc)

    def remove(self, nuc: Nucleus) -> NoReturn:
        """Removes a given nucleus from the list of nuclei."""

        try:
            self.nuclei.remove(nuc)
        except ValueError:
            raise ValueError("No matching nucleus to delete")

    def __iter__(self):
        return self

    def __next__(self) -> Nucleus:
        """Iterates through the nuclei until there's no nucleus left."""

        try:
            self._current_index += 1
            return self.nuclei[self._current_index]
        except IndexError:
            self._current_index = -1
            raise StopIteration

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

    _current_index: int = -1

    def append(self, fib: Fibre) -> NoReturn:
        """Adds a fiber to the list of fibres."""

        self.fibres.append(fib)

    def remove(self, fib: Fibre) -> NoReturn:
        """Removes a given fiber from the list of fibres."""

        try:
            self.fibres.remove(fib)
        except ValueError:
            raise ValueError("No matching fibre to delete")

    def __iter__(self):
        return self

    def __next__(self):
        """Iterates through the fibres until there's no fibre left."""

        try:
            self._current_index += 1
            return self.fibres[self._current_index]
        except IndexError:
            self._current_index = -1
            raise StopIteration

    def __len__(self) -> int:
        """Returns the number of fibres."""

        return len(self.fibres)


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
    n_threads: IntVar = field(
        default_factory=partial(IntVar, value=3, name='n_threads'))
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
