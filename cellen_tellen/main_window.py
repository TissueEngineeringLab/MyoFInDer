# coding: utf-8

from tkinter import ttk, filedialog, Tk, IntVar, PhotoImage, Menu, StringVar, \
    BooleanVar, messagebox
from platform import system, release
from shutil import rmtree
from webbrowser import open_new
from threading import Thread, BoundedSemaphore, active_count, Event
from time import sleep
from pickle import load, dump
from functools import partial, wraps
from pathlib import Path

from .tools import Settings
from .tools import Save_popup
from .tools import Warning_window
from .tools import Project_name_window
from .tools import Settings_window
from .tools import Splash_window
from .files_table import Files_table
from .image_canvas import Image_canvas

if system() == "Windows":
  from ctypes import windll

# set better resolution
if system() == "Windows" and int(release()) >= 8:
    windll.shcore.SetProcessDpiAwareness(True)


def _save_before_closing(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._create_warning_window():
            func(self, *args, **kwargs)
    return wrapper


class Main_window(Tk):

    def __init__(self):

        self.base_path = Path(__file__).parent
        if Path(__file__).name.endswith(".pyc"):
            self.base_path = self.base_path.parent
        self.projects_path = self.base_path.parent / 'Projects'
        self._settings_path = self.base_path / 'settings'

        splash = Splash_window(self)
        splash.resize_image()
        self._segmentation = splash.display()

        splash.destroy()

        super().__init__()

        self.title("Cellen Tellen - New Project (Unsaved)")
        if system() == "Windows":
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)

        icon = PhotoImage(file=self.base_path / 'app_images' /
                          "project_icon.png")
        self.iconphoto(True, icon)

        self._load_settings()
        self._set_variables()
        self._set_traces()
        self._set_menu()
        self._set_layout()

        self._image_canvas = Image_canvas(self._frm, self)
        self._files_table = Files_table(self._aux_frame, self.projects_path)
        self._image_canvas.set_table(self._files_table)
        self._files_table.set_image_canvas(self._image_canvas)
        self._save_settings(autosave_time=True)

        self.update()
        self.protocol("WM_DELETE_WINDOW", self._safe_destroy)
        self.mainloop()

    def set_unsaved_status(self):

        # set the unsaved status
        if self._current_project is not None:
            self.title("Cellen Tellen - Project '" + self._current_project.name
                       + "' (Unsaved)")
            self._save_button['state'] = 'enabled'
            self._save_button['text'] = 'Save'
        else:
            self.title("Cellen Tellen - New Project (Unsaved)")
            self._save_button['state'] = 'enabled'
            self._save_button['text'] = 'Save As'

    def _load_settings(self):
        if (self._settings_path / 'settings.pickle').is_file():
            with open(self._settings_path /
                      'settings.pickle', 'rb') as param_file:
                settings = load(param_file)
        else:
            settings = {}

        self.settings = Settings()
        for key, value in settings.items():
            getattr(self.settings, key).set(value)

        if (self._settings_path / 'recent_projects.pickle').is_file():
            with open(self._settings_path /
                      'recent_projects.pickle', 'rb') as recent_projects:
                recent = load(recent_projects)

            self._recent_projects = [
                self.projects_path / proj for proj in recent['recent_projects']
                if proj
                and (self.projects_path / proj).is_dir()
                and (self.projects_path / proj / 'data.pickle').is_file()]
            self._recent_projects = list(dict.fromkeys(self._recent_projects))
        else:
            self._recent_projects = []

        self._save_settings()

    def _set_traces(self):
        self.settings.fibre_colour.trace_add("write", self._nuclei_colour_sel)
        self.settings.nuclei_colour.trace_add("write", self._nuclei_colour_sel)
        self.settings.auto_save_time.trace_add("write",
                                               self._save_settings_callback)
        self.settings.save_altered_images.trace_add(
            "write", self._save_settings_callback)
        self.settings.do_fibre_counting.trace_add("write",
                                                  self._save_settings_callback)
        self.settings.small_objects_threshold.trace_add(
            "write", self._save_settings_callback)
        self.settings.n_threads.trace_add("write",
                                          self._save_settings_callback)

        self._processed_images_count.trace_add("write",
                                               self._update_processed_images)

    def _set_variables(self):

        self._previous_nuclei_colour = StringVar(
            value=self.settings.nuclei_colour.get())
        self._previous_fibre_colour = StringVar(
            value=self.settings.fibre_colour.get())

        self.draw_nuclei = BooleanVar(value=True)

        # threads
        self._processed_images_count = IntVar(value=0)
        self._img_to_process_count = 0
        self._stop_event = Event()
        self._thread_slider = None
        self._n_threads_running = 0

        self._small_objects_slider = None

        # automatic save
        self._auto_save_path = self.projects_path / 'AUTOSAVE'
        self._auto_save_job = None

        self._max_recent_projects = 20

        # set the warning var for folder name input
        self._warning_var = StringVar(value='')
        self._name_entry = None
        self._current_project = None

    def _set_menu(self):
        self._menu_bar = Menu(self)
        self.config(menu=self._menu_bar)
        self._menu_bar.config(font=("TKDefaultFont", 12))

        self._file_menu = Menu(self._menu_bar, tearoff=0)
        self._file_menu.add_command(label="New Empty Project",
                                    command=self._safe_empty_project)
        self._file_menu.add_command(label="Save Project As",
                                    command=partial(self._save_button_pressed,
                                                    force_save_as=True))
        self._file_menu.add_command(label="Delete Current Project",
                                    command=self._delete_current_project)
        self._file_menu.entryconfig(
            self._file_menu.index("Delete Current Project"), state="disabled")
        self._file_menu.add_command(
            label="Load From Explorer",
            command=self._safe_load)
        self._file_menu.add_separator()

        self._file_menu.add_command(label='Load Automatic Save',
                                    state='disabled',
                                    command=partial(self._safe_load,
                                                    self._auto_save_path))

        if self._auto_save_path.is_dir():
            self._file_menu.entryconfig("Load Automatic Save", state='normal')
        self._file_menu.add_separator()

        self._recent_projects_menu = Menu(self._file_menu, tearoff=0)
        self._file_menu.add_cascade(label="Recent Projects",
                                    menu=self._recent_projects_menu)

        self._menu_bar.add_cascade(label="File", menu=self._file_menu)

        self._settings_menu = Menu(self._menu_bar, tearoff=0)
        self._settings_menu.add_command(
            label="Settings", command=partial(Settings_window, self))
        self._menu_bar.add_cascade(label="Settings", menu=self._settings_menu)

        self._help_menu = Menu(self._menu_bar, tearoff=0)
        self._help_menu.add_command(label="Help", command=self._open_github)
        self._menu_bar.add_cascade(label="Help", menu=self._help_menu)

        self._quit_menu = Menu(self._menu_bar, tearoff=0)
        self._quit_menu.add_command(label="Quit", command=self._safe_destroy)
        self._menu_bar.add_cascade(label="Quit", menu=self._quit_menu)

        if not self._recent_projects:
            self._file_menu.entryconfig("Recent Projects", state='disabled')
            return

        for path in self._recent_projects:
            self._recent_projects_menu.add_command(
                label="Load '" + path.name + "'",
                command=partial(self._safe_load, path))

    def _set_layout(self):
        self._frm = ttk.Frame()
        self._frm.pack(fill='both', expand=True)

        self._aux_frame = ttk.Frame(self._frm)
        self._aux_frame.pack(expand=False, fill="both",
                             anchor="e", side='right')

        self._button_frame = ttk.Frame(self._aux_frame)
        self._button_frame.pack(expand=False, fill="x", anchor='n', side='top')

        self._tick_frame_1 = ttk.Frame(self._aux_frame)
        self._tick_frame_1.pack(expand=False, fill="x", anchor='n', side='top')

        self._tick_frame_2 = ttk.Frame(self._aux_frame)
        self._tick_frame_2.pack(expand=False, fill="x", anchor='n', side='top')

        self._load_button = ttk.Button(self._button_frame, text="Load Images",
                                       command=self._select_images)
        self._load_button.pack(fill="x", anchor="w", side='left', padx=3,
                               pady=5)
        self._button_style = ttk.Style()
        self._process_images_button = ttk.Button(self._button_frame,
                                                 text="Process Images",
                                                 command=self._process_images,
                                                 state='disabled')
        self._process_images_button.pack(fill="x", anchor="w", side='left',
                                         padx=3, pady=5)

        # image channel selection (which colour channels are displayed)
        self._channels = ttk.Label(self._tick_frame_1, text="  Channels :   ")
        self._channels.pack(anchor="w", side="left", fill='x', padx=3, pady=5)
        self._blue_channel_check_button = ttk.Checkbutton(
            self._tick_frame_1, text="Blue Channel", onvalue=True,
            offvalue=False, variable=self.settings.blue_channel_bool,
            command=self._set_image_channels)
        self._blue_channel_check_button.pack(anchor="w", side="left", fill='x',
                                             padx=3, pady=5)
        self._green_channel_check_button = ttk.Checkbutton(
            self._tick_frame_1, text="Green Channel", onvalue=True,
            offvalue=False, variable=self.settings.green_channel_bool,
            command=self._set_image_channels)
        self._green_channel_check_button.pack(anchor="w", side="left",
                                              fill='x', padx=3, pady=5)
        self._red_channel_check_button = ttk.Checkbutton(
            self._tick_frame_1, text="Red Channel", onvalue=True,
            offvalue=False, variable=self.settings.red_channel_bool,
            command=self._set_image_channels)
        self._red_channel_check_button.pack(anchor="w", side="left", fill='x',
                                            padx=3, pady=5)

        # indicator selections (which indicators are shown)
        self._indicator = ttk.Label(self._tick_frame_2, text="  Indicators : ")
        self._indicator.pack(anchor="w", side="left", fill='x', padx=3, pady=5)
        self._show_nuclei_check_button = ttk.Checkbutton(
            self._tick_frame_2, text="Nuclei", onvalue=True, offvalue=False,
            variable=self.settings.show_nuclei, command=self._set_indicators)
        self._show_nuclei_check_button.pack(anchor="w", side="left", fill='x',
                                            padx=3, pady=5)
        self._show_fibres_check_button = ttk.Checkbutton(
            self._tick_frame_2, text="Fibres", onvalue=True, offvalue=False,
            variable=self.settings.show_fibres, command=self._set_indicators)
        self._show_fibres_check_button.pack(anchor="w", side="left", fill='x',
                                            padx=3, pady=5)

        self._processing_label = ttk.Label(self._aux_frame, text="")
        self._processing_label.pack(anchor="n", side="top", fill='x', padx=3,
                                    pady=5)

        # save altered images and table
        self._save_button = ttk.Button(self._button_frame, text='Save As',
                                       command=self._save_button_pressed,
                                       state='enabled')
        self._save_button.pack(fill="x", anchor="w", side='left', padx=3,
                               pady=5)

        # set indicators
        self._which_indicator_button = ttk.Button(
            self._button_frame, text='Manual : Nuclei',
            command=self._change_indications, state='enabled')
        self._which_indicator_button.pack(fill="x", anchor="w", side='left',
                                          padx=3, pady=5)

    def _save_settings_callback(self, name, _, __):
        if name == 'auto_save_time':
            self._save_settings(autosave_time=True)
        elif name == 'save_altered':
            self._save_settings(enable_save=True)
        else:
            self._save_settings()

    def _save_settings(self, autosave_time=False, enable_save=False):

        # enable save button if needed
        if enable_save:
            self._save_button['state'] = 'enabled'

        # set the autosave timer
        if autosave_time:
            self._set_autosave_time()

        settings = {key: value.get() for key, value in
                    self.settings.__dict__.items()}

        if not self._settings_path.is_dir():
            Path.mkdir(self._settings_path)

        with open(self._settings_path /
                  'settings.pickle', 'wb+') as param_file:
            dump(settings, param_file, protocol=4)

        with open(self._settings_path /
                  'recent_projects.pickle', 'wb+') as recent_projects_file:
            dump({'recent_projects': [str(path.name) for path in
                                      self._recent_projects]},
                 recent_projects_file, protocol=4)

    def _delete_current_project(self):

        if self._current_project is None:
            return

        ret = messagebox.askyesno('Hold on !',
                                  "Do you really want to delete the current "
                                  "project ?\nThis operation can't be undone.")

        if ret:
            # delete the project
            rmtree(self._current_project)

            # remove the load button
            index = self._recent_projects.index(self._current_project)
            self._recent_projects_menu.delete(index)
            self._recent_projects.remove(self._current_project)

            if not self._recent_projects:
                self._file_menu.entryconfig("Recent Projects",
                                            state='disabled')
            self._save_settings()

            if self._current_project == self._auto_save_path:
                self._file_menu.entryconfig("Load Automatic Save",
                                            state='disabled')

            # create empty project
            self._create_empty_project()

    def _create_empty_project(self):

        # reset everything
        self._files_table.reset()
        self._image_canvas.reset()

        # set the save button
        self._save_button['state'] = 'enabled'
        self._save_button['text'] = 'Save As'
        self._process_images_button['state'] = 'disabled'
        self._file_menu.entryconfig(self._file_menu.index("Delete Current "
                                                          "Project"),
                                    state="disabled")

        # set window title
        self.title("Cellen Tellen - New Project (Unsaved)")
        self._current_project = None

    def _save_project(self, directory: Path = None):

        if directory is None:
            if self.settings.auto_save_time.get() > 0:
                directory = self._auto_save_path
            else:
                return

        if directory != self._auto_save_path:

            self._set_title_and_button(directory)

            # do the recent projects sh*t
            self._add_to_recent_projects(directory)

        else:
            # set the automatic save entry
            self._file_menu.entryconfig("Load Automatic Save", state='normal')
            if self.settings.auto_save_time.get() > 0:  # recall the autosave
                self._set_autosave_time()

        # create the folder
        if not directory.is_dir():
            Path.mkdir(directory, parents=True)

        # create saving popup
        saving_popup = Save_popup(self, directory)
        sleep(1)

        save_altered = self.settings.save_altered_images.get() or \
            directory == self._auto_save_path
        self._files_table.save_project(directory, save_altered)

        # destroy the popup
        saving_popup.destroy()

    def _load_project(self, directory: Path = None):

        if directory is None:
            # ask a folder
            folder = filedialog.askdirectory(
                initialdir=self.projects_path,
                mustexist=True,
                title="Choose a Project Folder")

            if not folder:
                return

            directory = Path(folder)

        if not directory.is_dir() or not (directory / 'data.pickle').is_file()\
                or not directory.parent == self.projects_path:
            messagebox.showerror("Error while loading",
                                 "This isn't a valid Cellen-tellen project !")
            return

        # set the save button
        self._set_title_and_button(directory)

        # do the recent projects sh*t
        if directory != self._auto_save_path:

            self._add_to_recent_projects(directory)

        # load the project
        self._files_table.load_project(directory)

        # if there are images loaded
        if self._files_table.filenames:
            self._process_images_button['state'] = 'enabled'
        else:
            self._process_images_button['state'] = 'disabled'

    def _set_title_and_button(self, directory):
        # set the save button
        self._save_button['state'] = 'disabled'
        self._save_button['text'] = 'Save'
        self._file_menu.entryconfig(
            self._file_menu.index("Delete Current Project"), state="normal")

        # change the current project name
        self._current_project = directory
        self.title("Cellen Tellen - Project '" + directory.name + "'")

    def _add_to_recent_projects(self, directory):

        if directory in self._recent_projects:
            index = self._recent_projects.index(directory)
            self._recent_projects_menu.delete(index)
            self._recent_projects.remove(directory)

        self._recent_projects_menu.insert_command(
            index=0, label="Load '" + directory.name + "'",
            command=partial(self._safe_load, directory))
        self._recent_projects.insert(0, directory)
        self._file_menu.entryconfig("Recent Projects", state='normal')

        if len(self._recent_projects) > self._max_recent_projects:
            # remove the last
            self._recent_projects_menu.delete(
                self._recent_projects_menu.index("end"))
            self._recent_projects.pop()

        self._save_settings()

    def _create_warning_window(self):

        if active_count() > 1:
            ret = messagebox.askyesno(
                'Hold on !',
                "The program is still computing !\n"
                "It is safer to wait for the computation to end.\n"
                "Quit anyway ?\n"
                "(resources may take some time to be released even after "
                "exiting)")

            if ret:
                self._stop_event.set()
            if active_count() > 1:
                return bool(ret)
            else:
                messagebox.showinfo('Update', "Looks like the computation is "
                                              "actually over now !")

        # if unsaved, show the window
        if self._save_button['state'] == 'enabled' and \
                self._files_table.filenames:

            # create
            return_var = IntVar()
            warning_window = Warning_window(self, return_var)
            self.wait_variable(return_var)
            ret = return_var.get()
            if ret == 2:
                warning_window.destroy()
                return self._save_button_pressed()
            elif ret == 1:
                warning_window.destroy()
                return True
            else:
                return False

        return True

    def _save_button_pressed(self, force_save_as=False):

        # save as if necessary
        if force_save_as or self._current_project is None:
            return_var = IntVar()
            name_window = Project_name_window(self, return_var)
            self.wait_variable(return_var)
            ret = return_var.get()
            if ret:
                name = name_window.return_name()
                name_window.destroy()
                self._save_project(self.projects_path / name)
                return True
            else:
                return False

        else:
            # perform normal save
            self._save_project(self._current_project)
            return True

    @_save_before_closing
    def _safe_destroy(self):
        self.destroy()

    @_save_before_closing
    def _safe_empty_project(self):
        self._create_empty_project()

    @_save_before_closing
    def _safe_load(self, path: Path = None):
        self._load_project(path)

    def _disable_buttons(self):

        self._load_button['state'] = "disabled"
        self._save_button['state'] = "disabled"
        self._which_indicator_button['state'] = 'disabled'

        self._file_menu.entryconfig("Load Automatic Save", state='disabled')
        self._file_menu.entryconfig("Recent Projects", state='disabled')
        self._file_menu.entryconfig("Delete Current Project", state="disabled")
        self._file_menu.entryconfig("Save Project As", state="disabled")
        self._file_menu.entryconfig("New Empty Project", state="disabled")
        self._file_menu.entryconfig("Load From Explorer", state="disabled")

        self._files_table.enable_close_buttons(False)

    def _enable_buttons(self):

        self._load_button['state'] = "enabled"
        self.set_unsaved_status()
        self._set_indicators()

        if self._auto_save_path.is_dir():
            self._file_menu.entryconfig("Load Automatic Save", state='normal')
        if self._recent_projects:
            self._file_menu.entryconfig("Recent Projects", state='normal')
        if self._current_project is not None:
            self._file_menu.entryconfig("Delete Current Project",
                                        state='normal')
        self._file_menu.entryconfig("Save Project As", state="normal")
        self._file_menu.entryconfig("New Empty Project", state="normal")
        self._file_menu.entryconfig("Load From Explorer", state="normal")

        self._files_table.enable_close_buttons(True)

    def _stop_processing(self, force=True):

        if not force and (active_count() > 2 or self._stop_event.is_set()):
            return

        # empty threads
        self._stop_event.set()
        if force:
            self._processing_label['text'] = "Stopping"
            i = 1
            while active_count() > 1:
                self.update()
                self._processing_label[
                    'text'] = "Stopping" + '.' * (i % 4) + ' ' * (4 - i % 4) \
                              + f"(waiting for {active_count() - 1} " \
                                f"thread(s) to finish)"
                i += 1
                sleep(1)

        self._processed_images_count.set(0)
        self._img_to_process_count = 0
        self._process_images_button["state"] = 'enabled'
        self._process_images_button['text'] = "Process Images"
        self._process_images_button.configure(command=self._process_images)
        self._processing_label['text'] = ""

        self._enable_buttons()
        self.set_unsaved_status()

    def _process_images(self):

        # get the file_names
        file_names = self._files_table.filenames

        # switch off process button
        self._processed_images_count.set(0)
        self._img_to_process_count = len(file_names)
        self._process_images_button['text'] = 'Stop Processing'
        self._process_images_button.configure(command=self._stop_processing)
        self._processing_label['text'] = "0 of " + str(len(file_names)) + \
                                         " Images Processed"

        self._disable_buttons()

        self.update()

        # start threading
        self._stop_event.clear()
        semaphore = BoundedSemaphore(value=self.settings.n_threads.get())
        for file in file_names:
            Thread(target=self._process_thread,
                   args=(file, semaphore, self._stop_event)).start()

    def _process_thread(self, file: Path, semaphore: BoundedSemaphore,
                        stop_event: Event):

        if stop_event.is_set():
            return

        with semaphore:
            # get result
            nuclei_out, nuclei_in, fibre_positions = \
                self._segmentation(file, self.settings.nuclei_colour.get(),
                                   self.settings.fibre_colour.get(),
                                   self.settings.do_fibre_counting.get(),
                                   self.settings.small_objects_threshold.get())

            if stop_event.is_set():
                return

            # send the output to the table
            self._files_table.input_processed_data(nuclei_out, nuclei_in,
                                                   fibre_positions, file)

            # close if necessary
            self._processed_images_count.set(
                self._processed_images_count.get() + 1)

        if stop_event.is_set():
            return

        self._stop_processing(force=False)

    def _update_processed_images(self, _, __, ___):
        # change the label
        processed = self._processed_images_count.get()
        if processed:
            self._processing_label['text'] = str(processed) + \
                " of " + str(self._img_to_process_count) + " Images Processed"

    def _select_images(self):

        # get the filenames with a dialog box
        file_names = filedialog.askopenfilenames(
            filetypes=[('Image Files', ('.tif', '.png', '.jpg', '.jpeg',
                                        '.bmp', '.hdr'))],
            parent=self, title='Please select a directory')

        if file_names:
            file_names = [Path(path) for path in file_names]

            # enable the process image buttons
            self._process_images_button["state"] = 'enabled'

            # add them to the table
            self._files_table.add_images(file_names)
            self.set_unsaved_status()

    def _set_autosave_time(self):

        # if a previous timer was set, cancel it
        if self._auto_save_job is not None:
            self.after_cancel(self._auto_save_job)
        self._auto_save_job = None

        # set a new timer if needed
        if self.settings.auto_save_time.get() > 0:
            self._auto_save_job = self.after(self.settings.auto_save_time.get()
                                             * 1000, self._save_project)

    def _set_image_channels(self):
        self._image_canvas.set_channels()
        self._save_settings()

    def _set_indicators(self):
        
        show_nuclei = self.settings.show_nuclei.get()
        show_fibres = self.settings.show_fibres.get()
        
        # set the indicators
        self._image_canvas.set_indicators()
        self._save_settings()

        # set which indication
        if show_fibres and not show_nuclei:
            self.draw_nuclei.set(False)
            self._which_indicator_button['text'] = 'Manual : Fibres'
            self._which_indicator_button['state'] = 'disabled'

        elif show_fibres and show_nuclei:
            self._which_indicator_button['state'] = 'enabled'

        if not show_fibres and show_nuclei:
            self.draw_nuclei.set(True)
            self._which_indicator_button['text'] = 'Manual : Nuclei'
            self._which_indicator_button['state'] = 'disabled'

    def _change_indications(self):
        if self.draw_nuclei.get():
            self.draw_nuclei.set(False)
            self._which_indicator_button['text'] = 'Manual : Fibres'
        else:
            self.draw_nuclei.set(True)
            self._which_indicator_button['text'] = 'Manual : Nuclei'

    def _nuclei_colour_sel(self, _, __, ___):

        # if the two are the same, reset one
        if self.settings.nuclei_colour.get() == \
                self.settings.fibre_colour.get():
            if self._previous_nuclei_colour.get() != \
                    self.settings.nuclei_colour.get():
                self.settings.fibre_colour.set(
                    self._previous_nuclei_colour.get())
            elif self._previous_fibre_colour.get() != \
                    self.settings.fibre_colour.get():
                self.settings.nuclei_colour.set(
                    self._previous_fibre_colour.get())

        # set the previous ones to the current one
        self._previous_nuclei_colour.set(self.settings.nuclei_colour.get())
        self._previous_fibre_colour.set(self.settings.fibre_colour.get())

        # save
        self._save_settings()

    @staticmethod
    def _open_github():
        open_new("https://github.com/Quentinderore2/Cellen-Tellen")
