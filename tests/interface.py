# coding: utf-8

from __future__ import annotations
import sys
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Optional
import logging
from _tkinter import TclError
from PIL import Image
from time import sleep

from . import mock_warning_window
from . import mock_filedialog


class BaseTestInterface(unittest.TestCase):
    """"""

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self._dir: Optional[TemporaryDirectory] = None
        self._logger: Optional[logging.Logger] = None
        self._exit: bool = False

    def setUp(self) -> None:
        """"""

        sys.modules['tkinter.filedialog'] = mock_filedialog
        sys.modules['myofinder.tools.warning_window'] = mock_warning_window
        from myofinder import MainWindow

        self._logger = logging.getLogger("MyoFInDer")
        self._exit = False

        self._dir = TemporaryDirectory()
        self._dir.__enter__()
        self._window = MainWindow(Path(self._dir.name))

    def tearDown(self) -> None:
        """"""

        if not self._exit:
            self._window.safe_destroy()

        if self._dir is not None:
            self._dir.__exit__(None, None, None)
            self._dir.cleanup()


class Test1Exit(BaseTestInterface):
    """"""

    def testExit(self) -> None:
        """"""

        self._window.safe_destroy()
        with self.assertRaises(TclError):
            self._window.wm_state()
        self._exit = True


class Test2LoadNoImages(BaseTestInterface):
    """"""

    def testLoadNoImages(self) -> None:
        """"""

        mock_filedialog.return_value = None
        self._window._select_images()

        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)
        self.assertEqual(len(self._window._files_table.table_items), 0)


class Test3LoadImages(BaseTestInterface):
    """"""

    def testLoadImages(self) -> None:
        """"""

        mock_filedialog.return_value = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in range(1, 4)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')

        self.assertEqual(len(self._window._files_table.table_items), 3)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in range(1, 4)])


class Test4ClickTable(BaseTestInterface):
    """"""

    def testClickTable(self) -> None:
        """"""

        mock_filedialog.return_value = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in range(1, 4)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')

        (self._window._files_table.table_items.entries[2].graph_elt.
         event_generate('<ButtonPress-1>', when="now"))

        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_3.jpg')
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_3.jpg')
