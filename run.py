# coding: utf-8

"""Executable file for running the application"""

from cellen_tellen import Main_window
import logging
from sys import stdout
from pathlib import Path


if __name__ == "__main__":

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
