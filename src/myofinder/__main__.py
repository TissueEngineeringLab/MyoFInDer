# coding: utf-8

"""This file contains the executable code that allows to run the MyoFInDer
interface."""

import logging
from sys import stdout, exit
from pathlib import Path
import argparse
from platform import system
from typing import Optional
import os
from tkinter.simpledialog import askstring
from warnings import warn

from . import MainWindow


def main():
    """This is the main method called for running the MyoFInDer application.

    It first parses the command-line arguments, then initializes the logger,
    and finally starts the application window.
    """

    # Parser for parsing the command line arguments of the script
    parser = argparse.ArgumentParser(
        description="Starts MyoFInDer, with optional flags for specifying:\n"
                    "whether to record log messages\n"
                    "whether to run the application in test mode, i.e. stop "
                    "it right after startup\n"
                    "a Deepcell API token to use for running the application\n"
                    "the application folder in which the log messages, "
                    "default parameters, and token should be stored")
    parser.add_argument('-n', '--nolog', action='store_false',
                        help="If provided, the log messages won't be displayed"
                             " and recorded. Otherwise, they are by default.")
    parser.add_argument('-t', '--test', action='store_true',
                        help="If provided, the main window is created but its "
                             "main loop is never started and the window is "
                             "destroyed as soon as it is initialized.")
    parser.add_argument('--token', action='store', nargs=1, type=str,
                        required=False, dest='token',
                        help="If provided, contains the Deepcell API token "
                             "for downloading the AI model from their server")
    parser.add_argument('-f', '--app-folder', action='store', nargs=1,
                        type=Path, required=False, dest='app_folder',
                        help="If provided, should contain the path to the "
                             "folder where to store the log messages and the "
                             "settings file.")
    args = parser.parse_args()

    # Retrieving the command-line arguments
    log: bool = args.nolog
    test: bool = args.test
    token: Optional[str] = args.token[0] if args.token is not None else None
    app_folder: Optional[Path]
    if args.app_folder is None:
        app_folder = None
    else:
        app_folder = args.app_folder[0]

    # Setting the path to the application folder if not already provided
    if app_folder is None:
        if system() in ('Linux', 'Darwin'):
            app_folder = Path.home() / '.MyoFInDer'
        elif system() == 'Windows':
            app_folder = (Path.home() / 'AppData' / 'Local' / 'MyoFInDer')

    # Creating the application folder, if needed
    if app_folder is not None:
        try:
            app_folder.mkdir(parents=True, exist_ok=True)
        except FileNotFoundError:
            app_folder = None

    # True if the token is provided in the command line, via the interface, or
    # as an environment variable
    save_token: bool = token is not None

    # Checking if the token was provided as an environment variable
    value = os.environ.get("DEEPCELL_ACCESS_TOKEN")
    if value is not None:
        token = value
    save_token |= token is not None

    # If the token file is present, try to read the token from it
    if (token is None and
        app_folder is not None
        and (app_folder / 'token.txt').exists()
        and (app_folder / 'token.txt').is_file()):
        try:
            read, *_ = (app_folder / 'token.txt').read_text().splitlines()
            token = read if read else None
        # If the token cannot be read, it can still be input in the interface
        except ValueError:
            warn("A token.txt file was found in the application folder, but "
                 "the provided token cannot be read!", RuntimeWarning)

    # If no token provided, ask for it in a graphical interface
    if token is None:
        warn("A Deepcell API token is needed to use MyoFInDer, please "
             "provide one in the popup window that appears!", RuntimeWarning)
        value = askstring("Enter token", "Please provide a Deepcell API "
                                         "token to use MyoFInDer")
        if value is not None and value:
            token = value

        save_token |= token is not None

    # If still no token given, no choice but to stop the application
    if token is None:
        raise EnvironmentError("No Deepcell API token was provided !\nThis "
                               "token can be written in the token.txt file in "
                               "the application's folder, given as a "
                               "command-line argument using the --token flag, "
                               "or set in the DEEPCELL_ACCESS_TOKEN "
                               "environment variable")
    # Saving the token as an environment variable
    else:
        os.environ.update({"DEEPCELL_ACCESS_TOKEN": token})

    # If the token wasn't read from a file, saving it for next time
    if save_token and token is not None:
        (app_folder / 'token.txt').write_text(token)

    # Setting up the logger
    logger = logging.getLogger("MyoFInDer")
    logger.setLevel(logging.INFO)

    # Setting up the handlers only if logging is enabled
    if log:
        handler_console = logging.StreamHandler(stream=stdout)
        handler_console.setLevel(logging.INFO)

        # Setting up the formatter
        formatter = logging.Formatter('%(asctime)s %(name)-8s %(message)s')
        handler_console.setFormatter(formatter)

        logger.addHandler(handler_console)

        # Setting up the file handler only if a location is provided
        if app_folder is not None:
            handler_file = logging.FileHandler(app_folder / 'logs.txt',
                                               mode='w')
            handler_file.setLevel(logging.INFO)
            handler_file.setFormatter(formatter)
            logger.addHandler(handler_file)

    # Normal workflow
    try:
        logger.log(logging.INFO, "Launching MyoFInDer")
        window = MainWindow(app_folder)
        # Normal operation mode, start the mainloop
        if not test:
            window.mainloop()
        # Test mode, destroy the main window right away
        else:
            window.safe_destroy()
        logger.log(logging.INFO, "MyoFInDer terminated gracefully")

    # Displaying the exception and waiting for the user to close the console
    except (Exception,) as exc:
        logger.exception("MyoFInDer encountered an error while running !",
                         exc_info=exc)
        # Only leave the console on if logging is enabled
        if log:
            print("\n\nPress ENTER to exit ...")
            input()


if __name__ == "__main__":

    exit(main())
