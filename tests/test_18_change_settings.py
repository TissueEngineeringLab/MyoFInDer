# coding: utf-8

from copy import deepcopy

from .util import BaseTestInterface


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

        # Modifying the minimum nuclei count setting value
        min_nuc_count = init_settings['minimum_nuclei_count']
        if int(min_nuc_count - 1) > 0:
            self._window._settings_window._count_slider.set(
                int(min_nuc_count - 1))
        else:
            self._window._settings_window._count_slider.set(
                int(min_nuc_count + 1))

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
