# coding: utf-8

"""Executable file for running the application"""

from cellen_tellen import Main_window
import logging
from sys import stdout

if __name__ == "__main__":

    logger = logging.getLogger("Cellen-Tellen")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(stream=stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)-8s '
                                  '%(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    try:
        Main_window()
    except (Exception,) as exc:
        logger.exception("Cellen-Tellen encountered an error while running !",
                         exc_info=exc)
        print("\n\nPress ENTER to exit ...")
        input()
