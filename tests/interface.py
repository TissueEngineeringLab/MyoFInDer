# coding: utf-8

from pathlib import Path
from _tkinter import TclError
from PIL import Image
from platform import system
from time import sleep
from threading import Thread
import filecmp
import shutil
from copy import deepcopy

from .util import (BaseTestInterface, BaseTestInterfaceProcessing,
                   mock_warning_window, mock_filedialog)


class Test01Exit(BaseTestInterface):

    def testExit(self) -> None:
        """This test checks that the main window is destroyed as expected after
        a call to safe_destroy()."""

        # Destroying the main window
        self._window.safe_destroy()

        # This call should raise an error as the window shouldn't exist anymore
        with self.assertRaises(TclError):
            self._window.wm_state()

        # Indicating the tearDown() method not to destroy the window
        self._exit = True


class Test02LoadNoImages(BaseTestInterface):

    def testLoadNoImages(self) -> None:
        """This test checks that MyoFInDer successfully handles the situation
        when the user aborts an image selection for loading into the interface.
        """

        # None so that no image is returned by the mock selection window
        mock_filedialog.file_name = None
        self._window._select_images()

        # Checking that no image was loaded in the image canvas and file table
        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)
        self.assertEqual(len(self._window._files_table.table_items), 0)


class Test03LoadImages(BaseTestInterface):

    def testLoadImages(self) -> None:
        """This test checks that MyoFInDer successfully loads several images,
        displays the first one in the image canvas, and displays them all in
        the file table."""

        # The mock selection window returns the paths to three images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that an image is displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')

        # Checking that the images have entries in the files table
        self.assertEqual(len(self._window._files_table.table_items), 3)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (1, 2, 3)])


class Test04ClickTable(BaseTestInterface):

    def testClickTable(self) -> None:
        """This test checks that the currently selected and displayed image is
        updated when the user clicks on another entry of the files table."""

        # The mock selection window returns the paths to three images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that the first image is displayed in the image canvas
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')

        # Generating a click on the third entry of the files table
        (self._window._files_table.table_items.entries[2].graph_elt.
         event_generate('<ButtonPress-1>', when="now"))

        # Checking that the third image is displayed in the image canvas
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_3.jpg')
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_3.jpg')


class Test05ClickImage(BaseTestInterface):

    def testClickImage(self) -> None:
        """This test checks that the nuclei are correctly added, inverted, or
        deleted on the image canvas when left- or right-clicking on it, and
        checks that the files table is updated accordingly."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that the image canvas and file table are empty of nuclei
        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.nuclei), 0)

        # Checking that the image canvas and file table are empty of fibers
        self.assertEqual(len(self._window._image_canvas._fibers), 0)
        self.assertEqual(
            len(self._window._files_table.table_items.current_entry.fibers), 0)

        # Generating 10 left-clicks on the image canvas
        for i in range(1, 11):
            self._window._image_canvas._canvas.event_generate(
                '<ButtonPress-1>', when="now", x=10 * i, y=10 * i)
            self._window._image_canvas._canvas.event_generate(
                '<ButtonRelease-1>',  when="now", x=10 * i, y=10 * i)

        # Checking that the image canvas and the files table have the correct
        # nuclei count
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

        # Generating left-clicks on 5 of the 10 created nuclei
        for i in range(1, 6):
            self._window._image_canvas._canvas.event_generate(
                '<ButtonPress-1>', when="now", x=20 * i, y=20 * i)
            self._window._image_canvas._canvas.event_generate(
                '<ButtonRelease-1>',  when="now", x=20 * i, y=20 * i)

        # Checking that the corresponding nuclei have been inverted on the
        # image canvas and the files table
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

        # Generating right-clicks on 5 of the 10 created nuclei
        for i in range(1, 6):
            self._window._image_canvas._canvas.event_generate(
                '<ButtonPress-3>', when="now", x=20 * i, y=20 * i)
            self._window._image_canvas._canvas.event_generate(
                '<ButtonRelease-3>',  when="now", x=20 * i, y=20 * i)

        # Checking that the corresponding nuclei have been deleted on the
        # image canvas and the files table
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

        # Generating a left click-and-drag over the 5 remaining nuclei
        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-1>', when="now", x=5, y=5)
        self._window._image_canvas._canvas.event_generate(
            '<B1-Motion>', when="now", x=105, y=105)
        self._window._image_canvas._canvas.event_generate(
            '<ButtonRelease-1>', when="now", x=105, y=105)

        # Checking that the corresponding nuclei have been inverted on the
        # image canvas and the files table
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

        # Generating a right click-and-drag over the 5 remaining nuclei
        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-3>', when="now", x=5, y=5)
        self._window._image_canvas._canvas.event_generate(
            '<B3-Motion>', when="now", x=105, y=105)
        self._window._image_canvas._canvas.event_generate(
            '<ButtonRelease-3>', when="now", x=105, y=105)

        # Checking that the corresponding nuclei have been deleted on the
        # image canvas and the files table
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

    def testZoomInOut(self) -> None:
        """This test checks that the image in the image canvas is correctly
        resized when using the mousewheel."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Reading the scale and dimension of the image before any interaction
        scale_0 = self._window._image_canvas._img_scale
        width_0 = self._window._image_canvas._image.width
        height_0 = self._window._image_canvas._image.height

        # Checking that the displayed image is by default not zoomed in or out
        self.assertEqual(self._window._image_canvas._can_scale, 1.0)
        self.assertEqual(self._window._image_canvas._current_zoom, 0)

        # The zoom commands differ on Linux, Windows, and macOS
        # Generating a single zoom-in event with the mousewheel
        if system() == "Linux":
            self._window._image_canvas._canvas.event_generate(
                '<4>', when="now", x=5, y=5)
        else:
            self._window._image_canvas._canvas.event_generate(
                '<MouseWheel>', when="now", x=5, y=5, delta=1)

        # Checking that the zoom was correctly applied in the image canvas
        self.assertAlmostEqual(self._window._image_canvas._img_scale, scale_0 *
                               self._window._image_canvas._delta)
        self.assertEqual(self._window._image_canvas._can_scale,
                         self._window._image_canvas._delta)
        self.assertEqual(self._window._image_canvas._current_zoom, 1)
        self.assertGreater(self._window._image_canvas._canvas.image_tk.width(),
                           width_0)
        self.assertGreater(
            self._window._image_canvas._canvas.image_tk.height(), height_0)

        # Generating five zoom-in events with the mousewheel
        for _ in range(5):
            if system() == "Linux":
                self._window._image_canvas._canvas.event_generate(
                    '<4>', when="now", x=5, y=5)
            else:
                self._window._image_canvas._canvas.event_generate(
                    '<MouseWheel>', when="now", x=5, y=5, delta=1)

        # Checking that the zoom was correctly applied in the image canvas, and
        # that the limit of 5 zoom levels in enforced
        self.assertAlmostEqual(self._window._image_canvas._img_scale, scale_0 *
                               self._window._image_canvas._delta ** 5)
        self.assertAlmostEqual(self._window._image_canvas._can_scale,
                               self._window._image_canvas._delta ** 5)
        self.assertEqual(self._window._image_canvas._current_zoom, 5)
        self.assertGreater(self._window._image_canvas._canvas.image_tk.width(),
                           width_0)
        self.assertGreater(
            self._window._image_canvas._canvas.image_tk.height(), height_0)

        # Generating 11 zoom-out events with the mousewheel
        for _ in range(11):
            if system() == "Linux":
                self._window._image_canvas._canvas.event_generate(
                    '<5>', when="now", x=5, y=5)
            else:
                self._window._image_canvas._canvas.event_generate(
                    '<MouseWheel>', when="now", x=5, y=5, delta=-1)

        # Checking that the zoom was correctly applied in the image canvas, and
        # that the limit of 5 zoom levels in enforced
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

    def testDrag(self) -> None:
        """This test checks that a mousewheel click-and-drag successfully moves
        the image in the image canvas."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Reading the initial coordinates of the upper-left corner of the image
        # on the image canvas
        init_x = self._window._image_canvas._canvas.canvasx(0)
        init_y = self._window._image_canvas._canvas.canvasy(0)

        # The zoom commands differ on Linux, Windows, and macOS
        # Generating five zoom-in events with the mousewheel
        for _ in range(5):
            if system() == "Linux":
                self._window._image_canvas._canvas.event_generate(
                    '<4>', when="now", x=100, y=100)
            else:
                self._window._image_canvas._canvas.event_generate(
                    '<MouseWheel>', when="now", x=100, y=100, delta=1)

        # checking that the coordinates of the upper-left corner of the image
        # in the image canvas have changed
        self.assertGreater(self._window._image_canvas._canvas.canvasx(0),
                           init_x)
        self.assertGreater(self._window._image_canvas._canvas.canvasy(0),
                           init_y)
        # Reading the new coordinates of the upper-left corner of the image on
        # the image canvas
        new_x = self._window._image_canvas._canvas.canvasx(0)
        new_y = self._window._image_canvas._canvas.canvasy(0)

        # Generating a mousewheel click-and-drag event on the image canvas
        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-2>', when="now", x=100, y=100)
        self._window._image_canvas._canvas.event_generate(
            '<B2-Motion>', when="now", x=50, y=50)

        # Checking that the position of the image in the image canvas has been
        # updated with the correct value
        self.assertEqual(self._window._image_canvas._canvas.canvasx(0) - new_x,
                         50)
        self.assertEqual(self._window._image_canvas._canvas.canvasy(0) - new_y,
                         50)


class Test08SetChannels(BaseTestInterface):

    def testSetChannels(self) -> None:
        """This test checks that the checkboxes in the interface can
        successfully show or hide the channels of the displayed image."""

        # The mock selection window returns the path to one image to load
        # The image was modified so that all three channels have a non-zero
        # value in pixel (0, 0)
        mock_filedialog.file_name = [str(Path(__file__).parent / 'data' /
                                         'image_3.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Reading the values of the checkboxes driving the display of the
        # channels
        init_r = self._window.settings.red_channel_bool.get()
        init_g = self._window.settings.green_channel_bool.get()
        init_b = self._window.settings.blue_channel_bool.get()

        # Reading the RGB value of the pixel in position (0, 0)
        r, g, b = (self._window._image_canvas._canvas.image_tk.
                   _PhotoImage__photo.get(0, 0))

        # Checking that the RGB values are consistent with the state of the
        # checkboxes
        self.assertIs(bool(r), init_r)
        self.assertIs(bool(g), init_g)
        self.assertIs(bool(b), init_b)

        # Generating a click on all the checkboxes to invert them
        self._window._red_channel_check_button.invoke()
        self._window._green_channel_check_button.invoke()
        self._window._blue_channel_check_button.invoke()

        # Reading the new RGB value of the pixel in position (0, 0)
        r, g, b = (self._window._image_canvas._canvas.image_tk.
                   _PhotoImage__photo.get(0, 0))

        # Reading the new values of the checkboxes driving the display of the
        # channels
        new_r = self._window.settings.red_channel_bool.get()
        new_g = self._window.settings.green_channel_bool.get()
        new_b = self._window.settings.blue_channel_bool.get()

        # Checking that the state of the checkboxes was successfully inverted
        # by clicking
        self.assertIs(new_r, not init_r)
        self.assertIs(new_g, not init_g)
        self.assertIs(new_b, not init_b)

        # Checking that the RGB values are consistent with the new state of the
        # checkboxes
        self.assertIs(bool(r), new_r)
        self.assertIs(bool(g), new_g)
        self.assertIs(bool(b), new_b)


class Test09DeleteImage(BaseTestInterface):

    def testDeleteImage(self) -> None:
        """This test checks that an image can be successfully deleted from the
        files table and the image canvas by clicking on the delete button of
        the files table."""

        # The mock selection window returns the paths to two images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that the first image is displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')

        # Checking that two images are referenced in the files table
        self.assertEqual(len(self._window._files_table.table_items), 2)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (1, 2)])

        # Generating a delete event on the first image in the files table
        (self._window._files_table.table_items.current_entry.graph_elt.
         close_button.invoke())

        # Checking that the second image is now displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_2.jpg')

        # Checking that only one image is left in the files table
        self.assertEqual(len(self._window._files_table.table_items), 1)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_2.jpg')

        # Generating a delete event on the second image in the files table
        (self._window._files_table.table_items.current_entry.graph_elt.
         close_button.invoke())

        # Checking that no image is displayed in the image canvas
        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)

        # Checking that no image is left in the files table
        self.assertEqual(len(self._window._files_table.table_items), 0)


class Test10DeletePartial(BaseTestInterface):

    def testDeletePartial(self) -> None:
        """This test checks that the partial deletion of images using the
        checkboxes and master delete button in the files table works as
        expected."""

        # The mock selection window returns the paths to three images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Checking that the first image is displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_1.jpg')

        # Checking that three images are referenced in the files table
        self.assertEqual(len(self._window._files_table.table_items), 3)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_1.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (1, 2, 3)])

        # Invoking the master select button to unselect all the images in the
        # files table
        self._window._select_all_button.invoke()
        # Selecting only the first image using its individual select checkbox
        (self._window._files_table.table_items.current_entry.graph_elt.
         check_button.invoke())
        # Invoking the master delete button in the files table
        self._window._delete_all_button.invoke()

        # Checking that the second image is now displayed in the image canvas
        self.assertIsInstance(self._window._image_canvas._image, Image.Image)
        self.assertIsInstance(self._window._image_canvas._image_path, Path)
        self.assertEqual(self._window._image_canvas._image_path.name,
                         'image_2.jpg')

        # Checking that only two images are left in the files table
        self.assertEqual(len(self._window._files_table.table_items), 2)
        self.assertEqual(
            self._window._files_table.table_items.current_entry.path.name,
            'image_2.jpg')
        self.assertCountEqual(
            [item.path.name for item in self._window._files_table.table_items],
            [f'image_{i}.jpg' for i in (2, 3)])

        # Invoking the master delete button in the files table
        self._window._delete_all_button.invoke()

        # Checking that no image is displayed in the image canvas
        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)

        # Checking that no image is left in the files table
        self.assertEqual(len(self._window._files_table.table_items), 0)


class Test11ProcessImages(BaseTestInterfaceProcessing):

    def testProcessImages(self) -> None:
        """This test checks that images can be successfully processed by
        MyoFInDer, and the partial selection checkboxes in the files table also
        work for partial processing."""

        # The mock selection window returns the paths to three images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Checking that the image canvas is empty of nuclei
        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)
        # Checking that the files table is empty of nuclei and fibers
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

        # Invoking the selection checkbox of the last image in the files table
        # to unselect it
        (self._window._files_table.table_items.entries[-1].graph_elt.
         check_button.invoke())
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Thread for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Checking that both positive and negative nuclei have been detected on
        # the image canvas
        self.assertGreater(len(self._window._image_canvas._nuclei), 0)
        self.assertGreater(self._window._image_canvas._nuclei.nuclei_in_count,
                           0)
        self.assertGreater(self._window._image_canvas._nuclei.nuclei_out_count,
                           0)
        # Checking that the two first images have their nuclei and fiber counts
        # updated in the files table
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

        # Checking that the nuclei and fibers count of the last image remained
        # unchanged in the files table
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

    def _stop_processing(self) -> None:
        """This method sets the _stop_event flag while the processing loop is
        running.

        It emulates a click on the "Stop Processing" button in the interface,
        which cannot be achieved in the particular conditions of unit testing.
        """

        sleep(1)
        self._window._stop_event.set()

    def testStopProcessImages(self) -> None:
        """This test checks that the image processing can be successfully
        interrupted by clicking on the "Stop Processing" button after it was
        started."""

        # The mock selection window returns the paths to three images to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / f'image_{i}.jpg')
            for i in (1, 2, 3)]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Instantiating a Thread that will stop the image processing later on
        click_thread = Thread(target=self._stop_processing)

        # Checking that the image canvas is empty of nuclei
        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)
        # Checking that the files table is empty of nuclei and fibers
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

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        click_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Checking that the image canvas is still empty of nuclei due to the
        # processing being interrupted
        self.assertEqual(len(self._window._image_canvas._nuclei), 0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_in_count,
                         0)
        self.assertEqual(self._window._image_canvas._nuclei.nuclei_out_count,
                         0)

        # Checking that the files table is still empty of nuclei and fibers due
        # to the processing being interrupted
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

    def testIndicatorsDisplay(self) -> None:
        """This test checks that the checkboxes driving the display of the
        detected nuclei and fibers are working as expected."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Checking that no Tkinter objects representing nuclei or fibers are
        # present on the image canvas
        self.assertTrue(not any(nuc.tk_obj is not None for nuc
                                in self._window._image_canvas._nuclei))
        self.assertTrue(not any(fib.polygon is not None for fib
                                in self._window._image_canvas._fibers))

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

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

    def testSaveProject(self) -> None:
        """This test checks that the correct files are being created when
        saving a project."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        # The images will be saved to the existing temporary folder created
        # before starting the test
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Checking that all the files that should be saved were indeed created
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

        # Copying all the files that were just saved to a different folder
        shutil.copytree(save_path, save_path / 'copy')

        # Triggering for a second time a save action using the "Save" button
        self._window._save_button.invoke()

        # Checking that the recorded files are still the same as the first ones
        comp = filecmp.cmpfiles(save_path, save_path / 'copy',
                                ('data.pickle', 'settings.pickle',
                                 'save_folder.xlsx',
                                 'Original Images/image_1.jpg'), shallow=False)
        self.assertCountEqual(('data.pickle', 'settings.pickle',
                               'save_folder.xlsx',
                               'Original Images/image_1.jpg'), comp[0])
        self.assertFalse(comp[1] or comp[2])

        # Adding a single nucleus by clicking on the image canvas, so that the
        # project is now different
        self._window._image_canvas._canvas.event_generate(
            '<ButtonPress-1>', when="now", x=10, y=10)
        self._window._image_canvas._canvas.event_generate(
            '<ButtonRelease-1>', when="now", x=10, y=10)
        self._window._show_nuclei_check_button.invoke()

        # Triggering a third save action using the "Save" button
        self._window._save_button.invoke()

        # Checking that some recorded files are now different to the original
        # due to the modification
        comp = filecmp.cmpfiles(save_path, save_path / 'copy',
                                ('data.pickle', 'settings.pickle',
                                 'save_folder.xlsx',
                                 'Original Images/image_1.jpg'), shallow=False)
        self.assertCountEqual(('Original Images/image_1.jpg',), comp[0])
        self.assertCountEqual(('data.pickle', 'save_folder.xlsx',
                               'settings.pickle'), comp[1])
        self.assertFalse(comp[2])


class Test15NewProject(BaseTestInterfaceProcessing):

    def testNewProject(self) -> None:
        """This test checks that creating a new empty project erases all the
        previous modifications."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        # The images will be saved to the existing temporary folder created
        # before starting the test
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Overriding the current changes with a new empty project
        index = self._window._file_menu.index("New Empty Project")
        self._window._file_menu.invoke(index)

        # Checking that the image canvas and the files table are now empty
        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)
        self.assertEqual(len(self._window._files_table.table_items), 0)


class Test16LoadProject(BaseTestInterfaceProcessing):

    def testLoadProject(self) -> None:
        """This test checks that the settings and image data can successfully
        be loaded from a previously saved project without altering the
        information."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        # The images will be saved to the existing temporary folder created
        # before starting the test
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        mock_filedialog.load_directory = mock_filedialog.save_folder
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Copying the current parameters and image data to later compare it
        settings = deepcopy(self._window.settings.get_all())
        table = deepcopy(self._window._files_table.table_items.save_version)

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Overriding the current changes with a new empty project
        index = self._window._file_menu.index("New Empty Project")
        self._window._file_menu.invoke(index)

        # Re-loading the data that was just saved and erased
        index = self._window._file_menu.index("Load From Explorer")
        self._window._file_menu.invoke(index)

        # Checking that the loaded data matches the one copied earlier
        self.assertEqual(settings, self._window.settings.get_all())
        self.assertEqual(table,
                         self._window._files_table.table_items.save_version)


class Test17DeleteProject(BaseTestInterfaceProcessing):

    def testDeleteProject(self) -> None:
        """This test checks that deleting the current project successfully
        removes all the recorded files and resets the image canvas and the
        files table."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        # The images will be saved to the existing temporary folder created
        # before starting the test
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Checking quickly that the project was saved as expected
        self.assertTrue((Path(self._dir.name) / 'save_folder').exists())

        # Deleting the current project and flushing the interface
        index = self._window._file_menu.index("Delete Current Project")
        self._window._file_menu.invoke(index)

        # Checking that the image canvas and the files table are now empty
        self.assertIsNone(self._window._image_canvas._image)
        self.assertIsNone(self._window._image_canvas._image_path)
        self.assertEqual(len(self._window._files_table.table_items), 0)

        # Checking that all the recorded files were now deleted
        self.assertFalse((Path(self._dir.name) / 'save_folder').exists())


class Test18ChangeSettings(BaseTestInterface):

    def testChangeSettings(self) -> None:
        """This test checks that interacting with the settings-related
        graphical objects does change the internal variables storing the
        settings values."""

        # Copying the initial state of the settings for later comparing it
        init_settings = deepcopy(self._window.settings.get_all())

        # Checking that no settings window was created so far
        self.assertIsNone(self._window._settings_window)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Checking that the settings window was now created
        self.assertIsNotNone(self._window._settings_window)

        # Modifying the nuclei colour setting value
        if init_settings['nuclei_colour'] == 'blue':
            self._window._settings_window._nuclei_colour_r2.invoke()
        elif init_settings['nuclei_colour'] == 'green':
            self._window._settings_window._nuclei_colour_r3.invoke()
        elif init_settings['nuclei_colour'] == 'red':
            self._window._settings_window._nuclei_colour_r1.invoke()

        # Modifying the fiber colour setting value
        if init_settings['fiber_colour'] == 'blue':
            self._window._settings_window._fiber_colour_r2.invoke()
        elif init_settings['fiber_colour'] == 'green':
            self._window._settings_window._fiber_colour_r3.invoke()
        elif init_settings['fiber_colour'] == 'red':
            self._window._settings_window._fiber_colour_r1.invoke()

        # Modifying the save overlay setting value
        if init_settings['save_overlay']:
            self._window._settings_window._overlay_off_button.invoke()
        else:
            self._window._settings_window._overlay_on_button.invoke()

        # Modifying the minimum fiber intensity setting value
        min_fib_int = init_settings['minimum_fiber_intensity']
        if int(min_fib_int - 1) > 0:
            self._window._settings_window._min_fib_int_slider.set(
                int(min_fib_int - 1))
        else:
            self._window._settings_window._min_fib_int_slider.set(
                int(min_fib_int + 1))

        # Modifying the maximum fiber intensity setting value
        max_fib_int = init_settings['maximum_fiber_intensity']
        if int(max_fib_int + 1) < 255:
            self._window._settings_window._max_fib_int_slider.set(
                int(max_fib_int + 1))
        else:
            self._window._settings_window._max_fib_int_slider.set(
                int(max_fib_int - 1))

        # Modifying the minimum nucleus intensity setting value
        min_nuc_int = init_settings['minimum_nucleus_intensity']
        if int(min_nuc_int - 1) > 0:
            self._window._settings_window._min_nuc_int_slider.set(
                int(min_nuc_int - 1))
        else:
            self._window._settings_window._min_nuc_int_slider.set(
                int(min_nuc_int + 1))

        # Modifying the maximum nucleus intensity setting value
        max_nuc_int = init_settings['maximum_nucleus_intensity']
        if int(max_nuc_int + 1) < 255:
            self._window._settings_window._max_nuc_int_slider.set(
                int(max_nuc_int + 1))
        else:
            self._window._settings_window._max_nuc_int_slider.set(
                int(max_nuc_int - 1))

        # Modifying the minimum nucleus diameter setting value
        min_nuc_diam = init_settings['minimum_nuc_diameter']
        if int(min_nuc_diam - 1) > 0:
            self._window._settings_window._min_nuc_diam_slider.set(
                int(min_nuc_diam - 1))
        else:
            self._window._settings_window._min_nuc_diam_slider.set(
                int(min_nuc_diam + 1))

        # Modifying the channels display settings values
        self._window._red_channel_check_button.invoke()
        self._window._green_channel_check_button.invoke()
        self._window._blue_channel_check_button.invoke()

        # Modifying the results display settings values
        self._window._show_nuclei_check_button.invoke()
        self._window._show_fibers_check_button.invoke()

        # Closing the settings window and checking that it was destroyed
        self._window._settings_window.destroy()
        self.assertIsNone(self._window._settings_window)

        # Checking that the same settings are still available
        self.assertTrue(all(key in init_settings for key
                            in self._window.settings.get_all()))

        # Checking that no setting value was left unchanged
        self.assertFalse(any(val_1 == val_2 for (_, val_1), (_, val_2)
                             in zip(init_settings.items(),
                                    self._window.settings.get_all().items())))


class Test19ProcessVarySettings(BaseTestInterfaceProcessing):

    def testProcessVarySettings(self) -> None:
        """This test checks that the output of the processing is influenced as
        expected by the value of some settings."""

        # Copying the initial state of the settings for later restoring it
        init_settings = deepcopy(self._window.settings.get_all())

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        # The images will be saved to the existing temporary folder created
        # before starting the test
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Recording the result of the first computation for later comparing it
        nuc = len(self._window._files_table.table_items.entries[0].nuclei)
        nuc_in = (self._window._files_table.table_items.entries[0].
                  nuclei.nuclei_in_count)
        nuc_out = (self._window._files_table.table_items.entries[0].
                   nuclei.nuclei_out_count)
        fib = len(self._window._files_table.table_items.entries[0].fibers)
        area = self._window._files_table.table_items.entries[0].fibers.area

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the minimum fiber intensity setting to the maximum
        self._window._settings_window._min_fib_int_slider.set(
            self._window._settings_window._min_fib_int_slider.cget('to'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertNotEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertNotEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the maximum fiber intensity setting to the minimum
        self._window._settings_window._max_fib_int_slider.set(
            self._window._settings_window._max_fib_int_slider.cget('from'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertNotEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertNotEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the minimum nucleus intensity setting to the maximum
        self._window._settings_window._min_nuc_int_slider.set(
            self._window._settings_window._min_nuc_int_slider.cget('to'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertNotEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the maximum nucleus intensity setting to the minimum
        self._window._settings_window._max_nuc_int_slider.set(
            self._window._settings_window._max_nuc_int_slider.cget('from'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertNotEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)

        # Restoring the initial state of the settings
        self._window.settings.update(init_settings)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)

        # Setting the minimum nucleus diameter setting to the maximum
        self._window._settings_window._min_nuc_diam_slider.set(
            self._window._settings_window._min_nuc_diam_slider.cget('to'))

        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the correct computation output changed and the correct
        # ones were preserved
        self.assertNotEqual(
            nuc, len(self._window._files_table.table_items.entries[0].nuclei))
        self.assertNotEqual(
            nuc_in, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_in_count)
        self.assertNotEqual(
            nuc_out, self._window._files_table.table_items.entries[0].
            nuclei.nuclei_out_count)
        self.assertEqual(
            fib, len(self._window._files_table.table_items.entries[0].fibers))
        self.assertEqual(
            area, self._window._files_table.table_items.entries[0].fibers.area)


class Test20SaveVarySettings(BaseTestInterfaceProcessing):

    def testSaveVarySettings(self) -> None:
        """This test checks that the project recording process is influenced as
        expected by the value of some settings."""

        # The mock selection window returns the path to one image to load
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        # The images will be saved to the existing temporary folder created
        # before starting the test
        mock_filedialog.save_folder = str(Path(self._dir.name) / 'save_folder')
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Starting the processing loop in the main Thread rather than in a
        # separate one
        self._window._process_thread()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Disabling the recording of overlay images
        self._window._settings_window._overlay_off_button.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Checking that the project was recorded but not the overlay images
        save_path = Path(mock_filedialog.save_folder)
        self.assertTrue(save_path.exists())
        self.assertFalse((save_path / 'Overlay Images').exists())

        # Deleting the current project and flushing the interface
        index = self._window._file_menu.index("Delete Current Project")
        self._window._file_menu.invoke(index)

        # Re-loading the same image in the interface as previously
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Enabling the recording of overlay images
        self._window._settings_window._overlay_on_button.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Triggering a save action using the "Save" button
        self._window._save_button.invoke()

        # Checking that the project was recorded along with the overlay images
        self.assertTrue(save_path.exists())
        self.assertTrue((save_path / 'Overlay Images' /
                         'image_1.jpg').exists())


class Test21ProcessVaryChannels(BaseTestInterfaceProcessing):

    def testProcessVaryChannels(self) -> None:
        """This test checks that the image processing gives a similar output
        with all the possible combinations of channels colors.

        To this end, a same image was duplicated but with its colors shuffled
        across all the possible channel combinations.
        """

        # The mock selection window returns the path to one image to load
        # The nuclei are on the blue channel, the fibers on the green channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_1.jpg')]
        mock_warning_window.WarningWindow.value = 1
        self._window._select_images()

        # Stopping the regular processing Thread
        self._window._stop_thread = True
        sleep(2)
        # Instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to blue, the fibers channel to green
        self._window._settings_window._nuclei_colour_r1.invoke()
        self._window._settings_window._fiber_colour_r2.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()

        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Reading the processing output to later compare it with other runs
        nuc = len(self._window._files_table.table_items.entries[0].nuclei)
        nuc_in = (self._window._files_table.table_items.entries[0].
                  nuclei.nuclei_in_count)
        nuc_out = (self._window._files_table.table_items.entries[0].
                   nuclei.nuclei_out_count)
        fib = len(self._window._files_table.table_items.entries[0].fibers)
        area = self._window._files_table.table_items.entries[0].fibers.area

        # Making sure that some nuclei and some fibers were detected
        self.assertGreater(nuc, 0)
        self.assertGreater(nuc_in, 0)
        self.assertGreater(nuc_out, 0)
        self.assertGreater(fib, 0)
        self.assertGreater(area, 0)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the green channel, the fibers on the blue channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_4.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to green, the fibers channel to blue
        self._window._settings_window._nuclei_colour_r2.invoke()
        self._window._settings_window._fiber_colour_r1.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 5)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 5)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 5)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the blue channel, the fibers on the red channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_5.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to blue, the fibers channel to red
        self._window._settings_window._nuclei_colour_r1.invoke()
        self._window._settings_window._fiber_colour_r3.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 5)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 5)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 5)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the green channel, the fibers on the red channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_6.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to green, the fibers channel to red
        self._window._settings_window._nuclei_colour_r2.invoke()
        self._window._settings_window._fiber_colour_r3.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 5)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 5)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 5)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the red channel, the fibers on the blue channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_7.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to red, the fibers channel to blue
        self._window._settings_window._nuclei_colour_r3.invoke()
        self._window._settings_window._fiber_colour_r1.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 5)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 5)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 5)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)

        # Removing the existing image from the image canvas and the files table
        self._window._delete_all_button.invoke()

        # The nuclei are on the red channel, the fibers on the green channel
        mock_filedialog.file_name = [
            str(Path(__file__).parent / 'data' / 'image_8.jpg')]
        self._window._select_images()

        # Invoking the creation of a settings window
        index = self._window._settings_menu.index("Settings")
        self._window._settings_menu.invoke(index)
        # Setting the nuclei channel to red, the fibers channel to green
        self._window._settings_window._nuclei_colour_r3.invoke()
        self._window._settings_window._fiber_colour_r2.invoke()
        # Closing the settings window
        self._window._settings_window.destroy()

        # Re-instantiating a Thread that will stop the processing loop later on
        stop_thread = Thread(target=self._stop_thread)
        # Invoking the button for starting the image processing
        self._window._process_images_button.invoke()
        # Starting the Threads for later stopping the processing loop
        self._window._stop_thread = False
        stop_thread.start()
        # Re-starting the processing loop in the main Thread
        self._window._process_thread()

        # Checking that the output of the processing is reasonably close to the
        # one with the regular colors
        self.assertLessEqual(
            abs(nuc - len(self._window._files_table.table_items.
                          entries[0].nuclei)), 5)
        self.assertLessEqual(
            abs(nuc_in - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_in_count), 5)
        self.assertLessEqual(
            abs(nuc_out - self._window._files_table.table_items.entries[0].
                nuclei.nuclei_out_count), 5)
        self.assertLessEqual(
            abs(fib - len(self._window._files_table.table_items.
                          entries[0].fibers)), 3)
        self.assertLessEqual(
            abs(area - self._window._files_table.table_items.entries[0].
                fibers.area), 0.05)
