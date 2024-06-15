# coding: utf-8

from typing import Iterable, Optional

file_name: Optional[Iterable[str]] = None
save_folder: Optional[str] = None
load_directory: Optional[str] = None


def askopenfilenames(*_, **__) -> Optional[Iterable[str]]:
    """Mocks a call to tkinter.filedialog.askopenfilenames().

    Normally returns paths to files selected by the user in a file browser
    interface.
    """

    return file_name


def asksaveasfilename(*_, **__) -> Optional[str]:
    """Mocks a call to tkinter.filedialog.asksaveasfilename().

    Normally returns the name of a file selected by the user in a file browser
    interface.
    """

    return save_folder


def askdirectory(*_, **__) -> Optional[str]:
    """Mocks a call to tkinter.filedialog.askdirectory().

    Normally returns the name of a directory selected by the user in a file
    browser interface.
    """

    return load_directory
