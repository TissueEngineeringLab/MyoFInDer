# coding: utf-8

"""This file contains the executable code that allows to run the MyoFInDer
interface."""

from . import MainWindow
import logging
from sys import stdout, exit
from pathlib import Path
import argparse
from platform import system
from typing import Optional


def main():
    """This is the main method called for running the MyoFInDer application.

    It first parses the command-line arguments, then initializes the logger,
    and finally starts the application window.
    """

    # Parser for parsing the command line arguments of the script
    parser = argparse.ArgumentParser(
        description="Starts MyoFInDer, with optional flags for specifying "
                    "whether to record log messages and whether the module was"
                    " started by the application or independently.")
    parser.add_argument('-n', '--nolog', action='store_false',
                        help="If provided, the log messages won't be displayed"
                             " and recorded. Otherwise, they are by default.")
    parser.add_argument('-t', '--test', action='store_true',
                        help="If provided, the main window is created but its "
                             "main loop is never started and the window is "
                             "destroyed as soon as it is initialized.")
    parser.add_argument('-f', '--app-folder', action='store', nargs=1,
                        type=Path, required=False, dest='app_folder',
                        help="If provided, should contain the path to the "
                             "folder where to store the log messages and the "
                             "settings file.")
    args = parser.parse_args()

    # Retrieving the command-line arguments
    log: bool = args.nolog
    test: bool = args.test
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
