# coding: utf-8

"""Executable file for running the application"""

from . import Main_window
import logging
from sys import stdout
from pathlib import Path
import argparse
from platform import system


if __name__ == "__main__":

    # Parser for parsing the command line arguments of the script
    parser = argparse.ArgumentParser(
        description="Starts MyoFInDer, with optional flags for specifying "
                    "whether to record log messages and whether the module was"
                    " started by the application or independently.")
    parser.add_argument('-n', '--nolog', action='store_false',
                        help="If provided, the log messages won't be displayed"
                             " and recorded. Otherwise, they are by default.")
    args = parser.parse_args()

    # Retrieving the command-line argument
    log = args.nolog

    # Setting the path to the application folder
    if system() in ('Linux', 'Darwin'):
        app_folder = Path.home() / '.MyoFInDer'
    elif system() == 'Windows':
        app_folder = (Path.home() / 'AppData' / 'Local' / 'MyoFInDer')
    else:
        app_folder = None

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
        window = Main_window(app_folder)
        window.mainloop()
        logger.log(logging.INFO, "MyoFInDer terminated gracefully")

    # Displaying the exception and waiting for the user to close the console
    except (Exception,) as exc:
        logger.exception("MyoFInDer encountered an error while running !",
                         exc_info=exc)
        # Only leave the console on if logging is enabled
        if log:
            print("\n\nPress ENTER to exit ...")
            input()
