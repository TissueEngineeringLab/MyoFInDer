# coding: utf-8

"""Executable file for running the application"""

from cellen_tellen import Main_window
import logging
from sys import stdout


if __name__ == "__main__":

    # Setting up the logger
    logger = logging.getLogger("Cellen-Tellen")
    logger.setLevel(logging.INFO)

    # Setting up the handlers
    handler = logging.StreamHandler(stream=stdout)
    handler.setLevel(logging.INFO)

    # Setting up the formatter
    formatter = logging.Formatter('%(asctime)s %(name)-8s %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Normal workflow
    try:
        logger.log(logging.INFO, "Launching Cellen-Tellen")
        Main_window()
        logger.log(logging.INFO, "Cellen-Tellen terminated gracefully")

    # Displaying the exception and waiting for the user to close the console
    except (Exception,) as exc:
        logger.exception("Cellen-Tellen encountered an error while running !",
                         exc_info=exc)
        print("\n\nPress ENTER to exit ...")
        input()
