# coding: utf-8

from dataclasses import dataclass, field
from typing import Optional, List
from tkinter.ttk import Button
from functools import partial
from tkinter import StringVar, IntVar, BooleanVar

in_fibre = 'yellow'  # green
out_fibre = 'red'  # 2A7DDE


@dataclass
class Labels:
    name: int
    nuclei: int
    positive: int
    ratio: int
    index: int
    fiber: int


@dataclass
class Lines:
    half_line: int
    full_line: int
    index_line: int


@dataclass
class Table_element:
    labels: Labels
    lines: Lines
    rect: int
    button: Button


@dataclass
class Nucleus:
    x_pos: int
    y_pos: int
    tk_obj: Optional[int]
    color: str

    def __eq__(self, other):
        if not isinstance(other, Nucleus):
            raise NotImplemented("Only two nuclei can be compared together")
        return self.x_pos == other.x_pos and self.y_pos == other.y_pos


@dataclass
class Fibre:
    x_pos: int
    y_pos: int
    h_line: Optional[int]
    v_line: Optional[int]

    def __eq__(self, other):
        if not isinstance(other, Fibre):
            raise NotImplemented("Only two fibres can be compared together")
        return self.x_pos == other.x_pos and self.y_pos == other.y_pos


@dataclass
class Nuclei:
    nuclei: List[Nucleus] = field(default_factory=list)

    _current_index: int = -1

    def append(self, nuc):
        self.nuclei.append(nuc)

    def remove(self, nuc):
        try:
            self.nuclei.remove(nuc)
        except ValueError:
            raise ValueError("No matching nucleus to delete")

    def __iter__(self):
        return self

    def __next__(self):
        try:
            self._current_index += 1
            return self.nuclei[self._current_index]
        except IndexError:
            self._current_index = -1
            raise StopIteration

    @property
    def nuclei_in_count(self):
        return len([nuc for nuc in self.nuclei if nuc.color == in_fibre])

    @property
    def nuclei_out_count(self):
        return len([nuc for nuc in self.nuclei if nuc.color == out_fibre])

    def __len__(self):
        return len(self.nuclei)


@dataclass
class Fibres:
    fibres: List[Fibre] = field(default_factory=list)

    _current_index: int = -1

    def append(self, fib):
        self.fibres.append(fib)

    def remove(self, fib):
        try:
            self.fibres.remove(fib)
        except ValueError:
            raise ValueError("No matching fibre to delete")

    def __iter__(self):
        return self

    def __next__(self):
        try:
            self._current_index += 1
            return self.fibres[self._current_index]
        except IndexError:
            self._current_index = -1
            raise StopIteration

    def __len__(self):
        return len(self.fibres)


@dataclass
class Settings:
    fibre_colour: StringVar = field(
        default_factory=partial(StringVar, value="Green", name='fibre_colour'))
    nuclei_colour: StringVar = field(
        default_factory=partial(StringVar, value="Blue", name='nuclei_colour'))
    auto_save_time: IntVar = field(
        default_factory=partial(IntVar, value=-1, name='auto_save_time'))
    save_altered_images: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False, name='save_altered'))
    do_fibre_counting: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False, name='fibre_count'))
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
