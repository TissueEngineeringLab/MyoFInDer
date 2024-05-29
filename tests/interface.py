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
from platform import system
from time import sleep
from threading import Thread
import filecmp
import shutil
from copy import deepcopy

from . import mock_warning_window
from . import mock_filedialog
from . import mock_messagebox


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
        sys.modules['tkinter.messagebox'] = mock_messagebox
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


class Test01Exit(BaseTestInterface):
    """"""

    def testExit(self) -> None:
        """"""

        self._window.safe_destroy()
        with self.assertRaises(TclError):
            self._window.wm_state()
        self._exit = True


class Test02LoadNoImages(BaseTestInterface):
    """"""

    def testLoadNoImages(self) -> None:
        """"""

        mock_filedialog.file_name = None
        self._window._select_images()

        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)
        self.assertEqual(len(self._window._files_table.table_items), 0)


class Test03LoadImages(BaseTestInterface):
    """"""

    def testLoadImages(self) -> None:
        """"""

        mock_filedialog.file_name = [
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


class Test04ClickTable(BaseTestInterface):
    """"""

    def testClickTable(self) -> None:
        """"""

        mock_filedialog.file_name = [
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


class Test05ClickImage(BaseTestInterface):
    """"""

    def testClickImage(self) -> None:
        """"""

        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei), 0)

        self.assertEqual(len(self._window._image_canvas._fibers), 0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.fibers), 0)

        for i in range(1, 11):
            self._window._image_canvas._canvas.event_generate(
                '<ButtonPress-1>', when="now", x=10 * i, y=10 * i)
            self._window._image_canvas._canvas.event_generate(
                '<ButtonRelease-1>',  when="now", x=10 * i, y=10 * i)

        self.assertEqual(len(self._window._image_canvas._nuclei), 10)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         10)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            10)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 0)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 10)

        for i in range(1, 6):
            self._window._image_canvas._canvas.event_generate(
                '<ButtonPress-1>', when="now", x=20 * i, y=20 * i)
            self._window._image_canvas._canvas.event_generate(
                '<ButtonRelease-1>',  when="now", x=20 * i, y=20 * i)

        self.assertEqual(len(self._window._image_canvas._nuclei), 10)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         5)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         5)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            10)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 5)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 5)

        for i in range(1, 6):
            self._window._image_canvas._canvas.event_generate(
                '<ButtonPress-3>', when="now", x=20 * i, y=20 * i)
            self._window._image_canvas._canvas.event_generate(
                '<ButtonRelease-3>',  when="now", x=20 * i, y=20 * i)

        self.assertEqual(len(self._window._image_canvas._nuclei), 5)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         5)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            5)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 0)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 5)

        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-1>', when="now", x=5, y=5)
        self._window._image_canvas._canvas.event_generate(
            '<B1-Motion>', when="now", x=105, y=105)
        self._window._image_canvas._canvas.event_generate(
            '<ButtonRelease-1>', when="now", x=105, y=105)

        self.assertEqual(len(self._window._image_canvas._nuclei), 5)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         5)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            5)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 5)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 0)

        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-3>', when="now", x=5, y=5)
        self._window._image_canvas._canvas.event_generate(
            '<B3-Motion>', when="now", x=105, y=105)
        self._window._image_canvas._canvas.event_generate(
            '<ButtonRelease-3>', when="now", x=105, y=105)

        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei),
            0)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_in_count), 0)
        self.assertEqual((self._window._files_table.table_items.current_entry.
                          nuclei.nuclei_out_count), 0)


class Test06ZoomInOut(BaseTestInterface):
    """"""

    def testZoomInOut(self) -> None:
        """"""

        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        scale_0 = self._window._image_canvas._img_scale
        width_0 = self._window._image_canvas._image.width
        height_0 = self._window._image_canvas._image.height

        self.assertEqual(self._window._image_canvas._can_scale, 1.0)
        self.assertEqual(self._window._image_canvas._current_zoom, 0)

        if system() == "Linux":
            self._window._image_canvas._canvas.event_generate(
                '<4>', when="now", x=5, y=5)
        else:
            self._window._image_canvas._canvas.event_generate(
                '<MouseWheel>', when="now", x=5, y=5, delta=1)

        self.assertAlmostEqual(self._window._image_canvas._img_scale, scale_0 *
                               self._window._image_canvas._delta)
        self.assertEqual(self._window._image_canvas._can_scale,
                         self._window._image_canvas._delta)
        self.assertEqual(self._window._image_canvas._current_zoom, 1)
        self.assertGreater(self._window._image_canvas._canvas.image_tk.width(),
                           width_0)
        self.assertGreater(
            self._window._image_canvas._canvas.image_tk.height(), height_0)

        for _ in range(5):
            if system() == "Linux":
                self._window._image_canvas._canvas.event_generate(
                    '<4>', when="now", x=5, y=5)
            else:
                self._window._image_canvas._canvas.event_generate(
                    '<MouseWheel>', when="now", x=5, y=5, delta=1)

        self.assertAlmostEqual(self._window._image_canvas._img_scale, scale_0 *
                               self._window._image_canvas._delta ** 5)
        self.assertAlmostEqual(self._window._image_canvas._can_scale,
                               self._window._image_canvas._delta ** 5)
        self.assertEqual(self._window._image_canvas._current_zoom, 5)
        self.assertGreater(self._window._image_canvas._canvas.image_tk.width(),
                           width_0)
        self.assertGreater(
            self._window._image_canvas._canvas.image_tk.height(), height_0)

        for _ in range(11):
            if system() == "Linux":
                self._window._image_canvas._canvas.event_generate(
                    '<5>', when="now", x=5, y=5)
            else:
                self._window._image_canvas._canvas.event_generate(
                    '<MouseWheel>', when="now", x=5, y=5, delta=-1)

        self.assertAlmostEqual(self._window._image_canvas._img_scale, scale_0 *
                               self._window._image_canvas._delta ** -5)
        self.assertAlmostEqual(self._window._image_canvas._can_scale,
                               self._window._image_canvas._delta ** -5)
        self.assertEqual(self._window._image_canvas._current_zoom, -5)
        self.assertLess(self._window._image_canvas._canvas.image_tk.width(),
                        width_0)
        self.assertLess(self._window._image_canvas._canvas.image_tk.height(),
                        height_0)


class Test07Drag(BaseTestInterface):
    """"""

    def testDrag(self) -> None:
        """"""

        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        init_x = self._window._image_canvas._canvas.canvasx(0)
        init_y = self._window._image_canvas._canvas.canvasy(0)

        for _ in range(5):
            if system() == "Linux":
                self._window._image_canvas._canvas.event_generate(
                    '<4>', when="now", x=100, y=100)
            else:
                self._window._image_canvas._canvas.event_generate(
                    '<MouseWheel>', when="now", x=100, y=100, delta=1)

        self.assertGreater(self._window._image_canvas._canvas.canvasx(0),
                           init_x)
        self.assertGreater(self._window._image_canvas._canvas.canvasy(0),
                           init_y)
        new_x = self._window._image_canvas._canvas.canvasx(0)
        new_y = self._window._image_canvas._canvas.canvasy(0)

        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-2>', when="now", x=100, y=100)
        self._window._image_canvas._canvas.event_generate(
            '<B2-Motion>', when="now", x=50, y=50)

        self.assertEqual(self._window._image_canvas._canvas.canvasx(0) - new_x,
                         50)
        self.assertEqual(self._window._image_canvas._canvas.canvasy(0) - new_y,
                         50)


class Test08SetChannels(BaseTestInterface):
    """"""

    def testSetChannels(self) -> None:
        """"""

        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_3.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        init_r = self._window.settings.red_channel_bool.get()
        init_g = self._window.settings.green_channel_bool.get()
        init_b = self._window.settings.blue_channel_bool.get()

        r, g, b = (self._window._image_canvas._canvas.image_tk.
                   _PhotoImage__photo.get(0, 0))

        self.assertIs(bool(r), init_r)
        self.assertIs(bool(g), init_g)
        self.assertIs(bool(b), init_b)

        self._window._red_channel_check_button.invoke()
        self._window._green_channel_check_button.invoke()
        self._window._blue_channel_check_button.invoke()

        r, g, b = (self._window._image_canvas._canvas.image_tk.
                   _PhotoImage__photo.get(0, 0))

        new_r = self._window.settings.red_channel_bool.get()
        new_g = self._window.settings.green_channel_bool.get()
        new_b = self._window.settings.blue_channel_bool.get()

        self.assertIs(new_r, not init_r)
        self.assertIs(new_g, not init_g)
        self.assertIs(new_b, not init_b)

        self.assertIs(bool(r), new_r)
        self.assertIs(bool(g), new_g)
        self.assertIs(bool(b), new_b)


class Test09DeleteImage(BaseTestInterface):
    """"""

    def testDeleteImage(self) -> None:
        """"""

        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')

        self.assertEqual(len(self._window._files_table.table_items), 2)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (1, 2)])

        (self._window._files_table.table_items.current_entry.graph_elt.
         close_button.invoke())

        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_2.jpg')

        self.assertEqual(len(self._window._files_table.table_items), 1)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_2.jpg')

        (self._window._files_table.table_items.current_entry.graph_elt.
         close_button.invoke())

        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)

        self.assertEqual(len(self._window._files_table.table_items), 0)


class Test10DeletePartial(BaseTestInterface):
    """"""

    def testDeletePartial(self) -> None:
        """"""

        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
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
            [f'image_{i}.jpg' for i in (1, 2, 3)])

        self._window._select_all_button.invoke()
        (self._window._files_table.table_items.current_entry.graph_elt.
         check_button.invoke())
        self._window._delete_all_button.invoke()

        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_2.jpg')

        self.assertEqual(len(self._window._files_table.table_items), 2)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_2.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (2, 3)])

        self._window._delete_all_button.invoke()

        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)

        self.assertEqual(len(self._window._files_table.table_items), 0)


class BaseTestInterfaceProcessing(BaseTestInterface):
    """"""

    def _stop_thread(self):
        """"""

        sleep(5)
        while not self._window._queue.empty():
            sleep(1)
        self._window._stop_thread = True


class Test11ProcessImages(BaseTestInterfaceProcessing):
    """"""

    def testProcessImages(self) -> None:
        """"""

        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        self._window._stop_thread = True
        sleep(2)
        stop_thread = Thread(target=self._stop_thread)

        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)
        for i in range(3):
            self.assertEqual(
                len(self._window._files_table.table_items.entries[i].nuclei),
                0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              nuclei.nuclei_in_count), 0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              nuclei.nuclei_out_count), 0)
            self.assertEqual(
                len(self._window._files_table.table_items.entries[i].fibers),
                0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              fibers.area), 0)

        (self._window._files_table.table_items.entries[-1].graph_elt.
         check_button.invoke())
        self._window._process_images_button.invoke()

        self._window._stop_thread = False
        stop_thread.start()
        self._window._process_thread()
        self._window.update()

        self.assertGreater(len(self._window._image_canvas._nuclei), 0)
        self.assertGreater(self._window._image_canvas._nuclei.nuclei_in_count,
                           0)
        self.assertGreater(self._window._image_canvas._nuclei.nuclei_out_count,
                           0)
        for i in range(2):
            self.assertGreater(
                len(self._window._files_table.table_items.entries[i].nuclei),
                0)
            self.assertGreater((self._window._files_table.table_items.
                                entries[i].nuclei.nuclei_in_count), 0)
            self.assertGreater((self._window._files_table.table_items.
                                entries[i].nuclei.nuclei_out_count), 0)
            self.assertGreater(
                len(self._window._files_table.table_items.entries[i].fibers),
                0)
            self.assertGreater((self._window._files_table.table_items.
                                entries[i].fibers.area), 0)

        self.assertEqual(
            len(self._window._files_table.table_items.entries[2].nuclei),
            0)
        self.assertEqual((self._window._files_table.table_items.entries[2].
                          nuclei.nuclei_in_count), 0)
        self.assertEqual((self._window._files_table.table_items.entries[2].
                          nuclei.nuclei_out_count), 0)
        self.assertEqual(
            len(self._window._files_table.table_items.entries[2].fibers),
            0)
        self.assertEqual((self._window._files_table.table_items.entries[2].
                          fibers.area), 0)


class Test12StopProcessImages(BaseTestInterfaceProcessing):
    """"""

    def _stop_processing(self):
        """"""

        sleep(1)
        self._window._stop_event.set()

    def testStopProcessImages(self) -> None:
        """"""

        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        self._window._stop_thread = True
        sleep(2)
        stop_thread = Thread(target=self._stop_thread)
        click_thread = Thread(target=self._stop_processing)

        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)
        for i in range(3):
            self.assertEqual(
                len(self._window._files_table.table_items.entries[i].nuclei),
                0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              nuclei.nuclei_in_count), 0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              nuclei.nuclei_out_count), 0)
            self.assertEqual(
                len(self._window._files_table.table_items.entries[i].fibers),
                0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              fibers.area), 0)

        self._window._process_images_button.invoke()

        self._window._stop_thread = False
        stop_thread.start()
        click_thread.start()
        self._window._process_thread()
        self._window.update()

        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)

        for i in range(3):
            self.assertEqual(
                len(self._window._files_table.table_items.entries[i].nuclei),
                0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              nuclei.nuclei_in_count), 0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              nuclei.nuclei_out_count), 0)
            self.assertEqual(
                len(self._window._files_table.table_items.entries[i].fibers),
                0)
            self.assertEqual((self._window._files_table.table_items.entries[i].
                              fibers.area), 0)


class Test13IndicatorsDisplay(BaseTestInterfaceProcessing):
    """"""

    def testIndicatorsDisplay(self) -> None:
        """"""

        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        self._window._stop_thread = True
        sleep(2)
        stop_thread = Thread(target=self._stop_thread)

        self.assertTrue(not any(nuc.tk_obj is not None for nuc
                                in self._window._image_canvas._nuclei))
        self.assertTrue(not any(fib.polygon is not None for fib
                                in self._window._image_canvas._fibers))

        self._window._process_images_button.invoke()

        self._window._stop_thread = False
        stop_thread.start()
        self._window._process_thread()
        self._window.update()

        display_nuc = self._window.settings.show_nuclei.get()
        display_fib = self._window.settings.show_fibers.get()

        if display_nuc:
            self.assertTrue(all(nuc.tk_obj is not None for nuc
                                in self._window._image_canvas._nuclei))
        else:
            self.assertTrue(not any(nuc.tk_obj is not None for nuc
                                    in self._window._image_canvas._nuclei))
        if display_fib:
            self.assertTrue(all(fib.polygon is not None for fib
                                in self._window._image_canvas._fibers))
        else:
            self.assertTrue(not any(fib.polygon is not None for fib
                                    in self._window._image_canvas._fibers))

        self._window._show_nuclei_check_button.invoke()
        self._window._show_fibers_check_button.invoke()

        if display_nuc:
            self.assertTrue(not any(nuc.tk_obj is not None for nuc
                                    in self._window._image_canvas._nuclei))
        else:
            self.assertTrue(all(nuc.tk_obj is not None for nuc
                                in self._window._image_canvas._nuclei))
        if display_fib:
            self.assertTrue(not any(fib.polygon is not None for fib
                                    in self._window._image_canvas._fibers))
        else:
            self.assertTrue(all(fib.polygon is not None for fib
                                in self._window._image_canvas._fibers))


class Test14SaveProject(BaseTestInterfaceProcessing):
    """"""

    def testSaveProject(self) -> None:
        """"""

        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        self._window._select_images()

        self._window._stop_thread = True
        sleep(2)
        stop_thread = Thread(target=self._stop_thread)

        self._window._process_images_button.invoke()

        self._window._stop_thread = False
        stop_thread.start()
        self._window._process_thread()
        self._window.update()

        self._window._save_button.invoke()

        save_path = Path(mock_filedialog.save_folder)
        self.assertTrue(save_path.exists())
        self.assertTrue(save_path.is_dir())
        self.assertTrue((save_path / 'settings.pickle').exists())
        self.assertTrue((save_path / 'save_folder.xlsx').exists())
        self.assertTrue((save_path / 'data.pickle').exists())
        self.assertTrue((save_path / 'Original Images').exists())
        self.assertTrue((save_path / 'Original Images').is_dir())
        self.assertGreater(len(tuple((save_path /
                                      'Original Images').iterdir())), 0)

        shutil.copytree(save_path, save_path / 'copy')

        self._window._save_button.invoke()

        comp = filecmp.cmpfiles(save_path, save_path / 'copy',
                                ('data.pickle', 'settings.pickle',
                                 'save_folder.xlsx',
                                 'Original Images/image_1.jpg'), shallow=False)
        self.assertCountEqual(('data.pickle', 'settings.pickle',
                               'save_folder.xlsx',
                               'Original Images/image_1.jpg'), comp[0])
        self.assertFalse(comp[1] or comp[2])

        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-1>', when="now", x=10, y=10)
        self._window._image_canvas._canvas.event_generate(
            '<ButtonRelease-1>', when="now", x=10, y=10)
        self._window._show_nuclei_check_button.invoke()

        self._window._save_button.invoke()

        comp = filecmp.cmpfiles(save_path, save_path / 'copy',
                                ('data.pickle', 'settings.pickle',
                                 'save_folder.xlsx',
                                 'Original Images/image_1.jpg'), shallow=False)
        self.assertCountEqual(('Original Images/image_1.jpg',), comp[0])
        self.assertCountEqual(('data.pickle', 'save_folder.xlsx',
                               'settings.pickle'), comp[1])
        self.assertFalse(comp[2])


class Test15NewProject(BaseTestInterfaceProcessing):
    """"""

    def testNewProject(self) -> None:
        """"""

        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        self._window._select_images()

        self._window._stop_thread = True
        sleep(2)
        stop_thread = Thread(target=self._stop_thread)

        self._window._process_images_button.invoke()

        self._window._stop_thread = False
        stop_thread.start()
        self._window._process_thread()
        self._window.update()

        self._window._save_button.invoke()

        index = self._window._file_menu.index("New Empty Project")
        self._window._file_menu.invoke(index)

        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)
        self.assertEqual(len(self._window._files_table.table_items), 0)


class Test16LoadProject(BaseTestInterfaceProcessing):
    """"""

    def testLoadProject(self) -> None:
        """"""

        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        mock_filedialog.load_directory = mock_filedialog.save_folder
        self._window._select_images()

        self._window._stop_thread = True
        sleep(2)
        stop_thread = Thread(target=self._stop_thread)

        self._window._process_images_button.invoke()

        self._window._stop_thread = False
        stop_thread.start()
        self._window._process_thread()
        self._window.update()

        settings = deepcopy(self._window.settings.get_all())
        table = deepcopy(self._window._files_table.table_items.save_version)

        self._window._save_button.invoke()

        index = self._window._file_menu.index("New Empty Project")
        self._window._file_menu.invoke(index)

        index = self._window._file_menu.index("Load From Explorer")
        self._window._file_menu.invoke(index)

        self.assertEqual(settings, self._window.settings.get_all())
        self.assertEqual(table,
                         self._window._files_table.table_items.save_version)
