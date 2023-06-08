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
        description="Starts Cellen-Tellen, with optional flags for specifying "
                    "whether to record log messages and whether the module was"
                    " started by the application or independently.")
    parser.add_argument('-a', '--app', action='store_true',
                        help="If provided, indicates the module that it was "
                             "started from an application. It consequently "
                             "enables or disables some features.")
    parser.add_argument('-n', '--nolog', action='store_false',
                        help="If provided, the log messages won't be displayed"
                             " and recorded. Otherwise, they are by default.")
    args = parser.parse_args()

    # Retrieving the command-line arguments
    from_app = args.app
    log = args.nolog

    # If started from an app, sets the base path for saving log messages,
    # settings and the location of the recent projects
    if from_app:
        log_dir = Path.cwd()
    else:
        if system() in ('Linux', 'Darwin'):
            log_dir = Path('/tmp/Cellen-Tellen')
        elif system() == 'Windows':
            log_dir = (Path.home() / 'AppData' / 'Local' / 'Temp'
                       / 'Cellen-Tellen')
        else:
            log_dir = None

    # Creating the folder for logging, if needed
    if log_dir is not None:
        try:
            log_dir.mkdir(parents=False, exist_ok=True)
        except FileNotFoundError:
            log_dir = None

    # Setting up the logger
    logger = logging.getLogger("Cellen-Tellen")
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
        if log_dir is not None:
            handler_file = logging.FileHandler(log_dir / 'logs.txt', mode='w')
            handler_file.setLevel(logging.INFO)
            handler_file.setFormatter(formatter)
            logger.addHandler(handler_file)

    # Normal workflow
    try:
        logger.log(logging.INFO, "Launching Cellen-Tellen")
        window = Main_window()
        window.mainloop()
        logger.log(logging.INFO, "Cellen-Tellen terminated gracefully")

    # Displaying the exception and waiting for the user to close the console
    except (Exception,) as exc:
        logger.exception("Cellen-Tellen encountered an error while running !",
                         exc_info=exc)
        # Only leave the console on if logging is enabled
        if log:
            print("\n\nPress ENTER to exit ...")
            input()
