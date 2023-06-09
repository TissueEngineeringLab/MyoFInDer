# coding: utf-8

from tkinter import messagebox
from pathlib import Path

forbidden_chars = ['/', '\\', '>', '<', ':', '"', '|', '?', '*', '.']
forbidden_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                   'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                   'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']


def check_project_name(path: Path) -> bool:
    """Takes a path where the user wants to save the project as an input, and
    determines whether it is valid. If so, returns True, and False otherwise.

    Args:
        path: The path chosen by the user for saving the project.

    Returns:
        True if the project path is valid and the project can be saved there,
        False otherwise.
    """

    # First, check that there's no forbidden character
    if any(char in forbidden_chars for char in path.name):
        forbidden = ', '.join(set(char for char in path.name
                                  if char in forbidden_chars))
        messagebox.showwarning("Invalid project name",
                               f"The name contains the following forbidden "
                               f"characters :\n{forbidden}")
        return False

    # Then, check that the name is not reserved
    if any(path.name == forbidden for forbidden in forbidden_names):
        messagebox.showwarning("Invalid project name",
                               "This name might be reserved by the OS !\n"
                               "Please choose another one.")
        return False

    # Then, if the name is fine, check that it is not already used
    if path.is_dir() and path.exists() and any(file.suffix == '.pickle'
                                               for file in path.iterdir()):
        messagebox.showwarning("Invalid project name",
                               "This project already exists !\n"
                               "Please choose another one.")
        return False

    return True
