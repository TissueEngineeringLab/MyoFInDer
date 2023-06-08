# coding: utf-8

"""Executable file for running the application"""

from . import Main_window
import logging
from sys import stdout
from pathlib import Path
import argparse


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
    parser.add_argument('-l', '--log', action='store_true',
                        help="If provided, the log messages will be displayed "
                             "and recorded. Otherwise, they will be ignored.")
    args = parser.parse_args()

    # Retrieving the command-line arguments
    from_app = args.app
    log = args.log

    base_path = Path(__file__).parent
    if Path(__file__).name.endswith(".pyc"):
        base_path = base_path.parent

    # Setting up the logger
    logger = logging.getLogger("Cellen-Tellen")
    logger.setLevel(logging.INFO)

    # Setting up the handlers
    handler_console = logging.StreamHandler(stream=stdout)
    handler_console.setLevel(logging.INFO)

    handler_file = logging.FileHandler(base_path / 'logs.txt', mode='w')
    handler_file.setLevel(logging.INFO)

    # Setting up the formatter
    formatter = logging.Formatter('%(asctime)s %(name)-8s %(message)s')
    handler_console.setFormatter(formatter)
    handler_file.setFormatter(formatter)

    logger.addHandler(handler_console)
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
        print("\n\nPress ENTER to exit ...")
        input()
