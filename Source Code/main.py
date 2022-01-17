# coding: utf-8

from tkinter import ttk, filedialog, Canvas, Tk, IntVar, \
    Toplevel, Scale, PhotoImage, Menu, StringVar, BooleanVar
from PIL import ImageTk, Image
from os import path, mkdir
from platform import system, release

if system() == "Windows":
  from ctypes import pythonapi, py_object, windll as dll
else:
  from ctypes import pythonapi, py_object, cdll as dll

from table import Table
from imagewindow import Zoom_Advanced
from shutil import rmtree
from webbrowser import open_new

from nucleiFibreSegmentation import deepcell_functie, initialize_mesmer

from threading import get_ident, active_count, Thread
from time import time, sleep
from json import load, dump
from functools import partial
from dataclasses import dataclass, field

# set better resolution
if system() == "Windows" and int(release()) >= 8:
    dll.shcore.SetProcessDpiAwareness(True)


@dataclass
class Settings:
    fibre_colour: StringVar = field(
        default_factory=partial(StringVar, value="Green"))
    nuclei_colour: StringVar = field(
        default_factory=partial(StringVar, value="Blue"))
    auto_save_time: IntVar = field(default_factory=partial(IntVar, value=-1))
    save_altered_images: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False))
    do_fibre_counting: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False))
    n_threads: IntVar = field(default_factory=partial(IntVar, value=3))
    small_objects_threshold: IntVar = field(
        default_factory=partial(IntVar, value=400))
    blue_channel_bool: BooleanVar = field(
        default_factory=partial(BooleanVar, value=True))
    green_channel_bool: BooleanVar = field(
        default_factory=partial(BooleanVar, value=True))
    red_channel_bool: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False))
    show_nuclei: BooleanVar = field(
        default_factory=partial(BooleanVar, value=True))
    show_fibres: BooleanVar = field(
        default_factory=partial(BooleanVar, value=False))


class Warning_window(Toplevel):

    def __init__(self, main_window):
        super().__init__(main_window)

        self._main_window = main_window

        self.resizable(False, False)
        self.grab_set()

        self.title("Hold on!")

        self._set_layout()

    def _set_layout(self):
        ttk.Label(self,
                  text="Are you sure about closing an unsaved project ?"). \
            pack(anchor='n', expand=False, fill='none', side='top',
                 padx=20, pady=20)

        # create the buttons
        ttk.Button(self, text='Save and Close',
                   command=self._main_window.save_button_pressed, width=40). \
            pack(anchor='n', expand=False, fill='none', side='top',
                 padx=20, pady=7)
        ttk.Button(self, text='Close Without Saving',
                   command=self._main_window.destroy, width=40). \
            pack(anchor='n', expand=False, fill='none', side='top',
                 padx=20, pady=7)
        ttk.Button(self, text='Cancel', command=self.destroy, width=40). \
            pack(anchor='n', expand=False, fill='none', side='top',
                 padx=20, pady=7)

        self.update()


class Project_name_window(Toplevel):

    def __init__(self, main_window, new_project):
        super().__init__(main_window)

        self._main_window = main_window
        self._new_project = new_project

        self._warning_var = StringVar(value='')

        self.resizable(False, False)
        self.grab_set()

        if new_project:
            self.title("Creating a New Empty Project")
        else:
            self.title("Saving the Current Project")

        self._set_layout()
        self._check_project_name_entry(self._name_entry.get())

    def _set_layout(self):
        if self._new_project:
            ask_label = ttk.Label(self,
                                  text='Choose a name for your NEW EMPTY '
                                       'Project')
            ask_label.pack(anchor='n', expand=False, fill='none', side='top',
                           padx=20, pady=10)
        else:
            ask_label = ttk.Label(self,
                                  text='Choose a name for your '
                                       'CURRENT Project :')
            ask_label.pack(anchor='n', expand=False, fill='none', side='top',
                           padx=20, pady=10)

        # set the warning label (gives warnings when the name is bad)
        self._warning_var.set('')
        warning_label = ttk.Label(self,
                                  textvariable=self._warning_var,
                                  foreground='red')
        warning_label.pack(anchor='n', expand=False, fill='none', side='top',
                           padx=20, pady=7)
        validate_command = warning_label.register(
            self._check_project_name_entry)

        # set the entry box to input the name
        self._name_entry = ttk.Entry(
            self, validate='key', state='normal',
            width=30,
            validatecommand=(validate_command, '%P'))
        self._name_entry.pack(anchor='n', expand=False, fill='none',
                              side='top', padx=20, pady=7)
        self._name_entry.focus()
        self._name_entry.icursor(len(self._name_entry.get()))

        # save button
        self._folder_name_window_save_button = ttk.Button(
            self, text='Save', width=30,
            command=partial(self._main_window.save_project,
                            self._name_entry.get(), True))
        self._folder_name_window_save_button.pack(
            anchor='n', expand=False, fill='none', side='top', padx=20,
            pady=7)
        self.bind('<Return>', self._enter_pressed)

        self.update()

    def _check_project_name_entry(self, new_entry):

        # check if it is a valid name
        if '/' in new_entry or '.' in new_entry or not new_entry:
            self._folder_name_window_save_button['state'] = 'disabled'
            if len(new_entry) > 0:
                self._warning_var.set('This is not a valid projectname !')
            else:
                self._warning_var.set('')
            return True

        # check if it already exists
        if path.isdir(self._main_window.base_path + 'Projects/' + new_entry):
            self._warning_var.set('This project already exists')
            self._folder_name_window_save_button['state'] = 'disabled'
            return True

        # no warnings
        self._warning_var.set('')
        self._folder_name_window_save_button['state'] = 'enabled'
        return True

    def _enter_pressed(self, *_, **__):

        # if the window exists and the save button is enabled
        if self._folder_name_window_save_button['state'] == 'enabled':
            self._main_window.save_project(self._name_entry.get(), True)


class Settings_window(Toplevel):

    def __init__(self, main_window):
        super().__init__(main_window)

        self._main_window = main_window
        self._settings = self._main_window.settings

        self.resizable(False, False)
        self.grab_set()

        self.title("Settings")

        self._set_layout()
        self.update()
        self._center()

    def _set_layout(self):
        frame = ttk.Frame(self, padding="20 20 20 20")
        frame.grid(sticky='NESW')

        # nuclei colour
        ttk.Label(frame, text="Nuclei Colour :").grid(column=0, row=0,
                                                      sticky='NE',
                                                      padx=(0, 10))
        nuclei_colour_r1 = ttk.Radiobutton(
            frame, text="Blue Channel", variable=self._settings.nuclei_colour,
            value="Blue")
        nuclei_colour_r1.grid(column=1, row=0, sticky='NW')
        nuclei_colour_r2 = ttk.Radiobutton(
            frame, text="Green Channel", variable=self._settings.nuclei_colour,
            value="Green")
        nuclei_colour_r2.grid(column=1, row=1, sticky='NW')
        nuclei_colour_r3 = ttk.Radiobutton(
            frame, text="Red Channel", variable=self._settings.nuclei_colour,
            value="Red")
        nuclei_colour_r3.grid(column=1, row=2, sticky='NW')

        # fibre colour
        ttk.Label(frame, text="Fibre Colour :").grid(
            column=0, row=3, sticky='NE', pady=(10, 0), padx=(0, 10))
        fibre_colour_r1 = ttk.Radiobutton(
            frame, text="Blue Channel", variable=self._settings.fibre_colour,
            value="Blue")
        fibre_colour_r1.grid(column=1, row=3, sticky='NW', pady=(10, 0))
        fibre_colour_r2 = ttk.Radiobutton(
            frame, text="Green Channel", variable=self._settings.fibre_colour,
            value="Green")
        fibre_colour_r2.grid(column=1, row=4, sticky='NW')
        fibre_colour_r3 = ttk.Radiobutton(
            frame, text="Red Channel", variable=self._settings.fibre_colour,
            value="Red")
        fibre_colour_r3.grid(column=1, row=5, sticky='NW')

        # autosave timer
        ttk.Label(frame, text='Autosave Interval :').grid(
            column=0, row=6, sticky='NE', pady=(10, 0), padx=(0, 10))
        ttk.Radiobutton(
            frame, text="5 Minutes", variable=self._settings.auto_save_time,
            value=5 * 60).grid(column=1, row=6, sticky='NW', pady=(10, 0))
        ttk.Radiobutton(
            frame, text="15 Minutes", variable=self._settings.auto_save_time,
            value=15 * 60).grid(column=1, row=7, sticky='NW')
        ttk.Radiobutton(
            frame, text="30 Minutes", variable=self._settings.auto_save_time,
            value=30 * 60).grid(column=1, row=8, sticky='NW')
        ttk.Radiobutton(
            frame, text="60 Minutes", variable=self._settings.auto_save_time,
            value=60 * 60).grid(column=1, row=9, sticky='NW')
        ttk.Radiobutton(
            frame, text="Never", variable=self._settings.auto_save_time,
            value=-1).grid(column=1, row=10, sticky='NW')

        # save altered images
        ttk.Label(frame, text='Save Altered Images :').grid(
            column=0, row=11, sticky='NE', pady=(10, 0), padx=(0, 10))
        ttk.Radiobutton(
            frame, text="On", variable=self._settings.save_altered_images,
            value=1).grid(column=1, row=11, sticky='NW', pady=(10, 0))
        ttk.Radiobutton(
            frame, text="Off", variable=self._settings.save_altered_images,
            value=0).grid(column=1, row=12, sticky='NW')

        # fibre counting
        ttk.Label(frame, text='Count Fibres :').grid(
            column=0, row=13, sticky='NE', pady=(10, 0), padx=(0, 10))
        ttk.Radiobutton(
            frame, text="On", variable=self._settings.do_fibre_counting,
            value=1).grid(column=1, row=13, sticky='NW', pady=(10, 0))
        ttk.Radiobutton(
            frame, text="Off", variable=self._settings.do_fibre_counting,
            value=0).grid(column=1, row=14, sticky='NW')

        # multithreading
        ttk.Label(frame, text='Number of Threads :').grid(
            column=0, row=15, sticky='E', pady=(10, 0), padx=(0, 10))

        thread_slider_frame = ttk.Frame(frame)

        ttk.Label(thread_slider_frame, textvariable=self._settings.n_threads,
                  width=3).\
            pack(side='left', anchor='w', fill='none', expand=False,
                 padx=(0, 20))

        Scale(thread_slider_frame, from_=0, to=5, orient="horizontal",
              variable=self._settings.n_threads, showvalue=False, length=150,
              tickinterval=1).\
            pack(side='left', anchor='w', fill='none', expand=False)

        thread_slider_frame.grid(column=1, row=15, sticky='NW', pady=(10, 0))

        # small objects threshold
        ttk.Label(frame, text='Dead cells size Threshold :').grid(
            column=0, row=16, sticky='E', pady=(10, 0), padx=(0, 10))

        threshold_slider_frame = ttk.Frame(frame)

        ttk.Label(threshold_slider_frame,
                  textvariable=self._settings.small_objects_threshold,
                  width=3). \
            pack(side='left', anchor='w', fill='none', expand=False,
                 padx=(0, 20))

        Scale(threshold_slider_frame, from_=10, to=1000,
              variable=self._settings.small_objects_threshold,
              orient="horizontal", length=150, showvalue=False,
              tickinterval=300). \
            pack(side='left', anchor='w', fill='none', expand=False)

        threshold_slider_frame.grid(column=1, row=16, sticky='NW',
                                    pady=(10, 0))

    def _center(self):
        scr_width = self.winfo_screenwidth()
        scr_height = self.winfo_screenheight()
        height = self.winfo_height()
        width = self.winfo_width()

        self.geometry('+%d+%d' % ((scr_width - width) / 2,
                                  (scr_height - height) / 2))


class Splash(Tk):

    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.grab_set()

        self._image = Image.open("movedim.png")
        self._resize_image()
        self._display()

        self.destroy()

    def _resize_image(self):
        size_factor = 0.35

        scr_width = self.winfo_screenwidth()
        scr_height = self.winfo_screenheight()
        img_ratio = self._image.width / self._image.height
        scr_ratio = scr_width / scr_height

        if img_ratio > scr_ratio:
            self._image = self._image.resize(
                (int(scr_width * size_factor),
                 int(scr_width * size_factor / img_ratio)),
                Image.ANTIALIAS)
            self.geometry('%dx%d+%d+%d' % (
                int(scr_width * size_factor),
                int(scr_width * size_factor / img_ratio),
                scr_width * (1 - size_factor) / 2,
                (scr_height - int(scr_width * size_factor / img_ratio)) / 2))

        else:
            self._image = self._image.resize(
                (int(scr_height * size_factor * img_ratio),
                 int(scr_height * size_factor)),
                Image.ANTIALIAS)
            self.geometry('%dx%d+%d+%d' % (
                int(scr_height * size_factor * img_ratio),
                int(scr_height * size_factor),
                (scr_width - int(scr_height * size_factor * img_ratio)) / 2,
                scr_height * (1 - size_factor) / 2))

    def _display(self):
        image_tk = ImageTk.PhotoImage(self._image)
        self._canvas = Canvas(self, bg="brown")
        self._canvas.create_image(0, 0, image=image_tk, anchor="nw")
        self._canvas.create_text(
            20, int(0.70 * self._image.height),
            anchor='w',
            text="Cellen Tellen - A P&O project by Quentin De Rore, Ibrahim El"
                 " Kaddouri, Emiel Vanspranghels and Henri Vermeersch, "
                 "assisted by Desmond Kabus, Rebecca Wüst and Maria Olenic",
            fill="white",
            font='Helvetica 7 bold',
            width=self._image.width - 40)

        self._loading_label = self._canvas.create_text(
            20, int(0.9 * self._image.height),
            anchor="w",
            text='Importing dependencies...',
            fill="white",
            font='Helvetica 7 bold',
            width=self._image.width - 40)

        self._canvas.pack(fill="both", expand=True)
        self.update()

        sleep(1)

        self._canvas.itemconfig(self._loading_label,
                                text="Initialising Mesmer...")
        self.update()
        initialize_mesmer()

        self._canvas.itemconfig(self._loading_label,
                                text="Starting program...")
        self.update()

        sleep(1)


class Main_window(Tk):

    def __init__(self):
        super().__init__()

        self.title("Cellen Tellen - New Project (Unsaved)")
        if system() == "Windows":
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)

        self.base_path = path.abspath('') + "/"

        icon = PhotoImage(file=self.base_path + "icon.png")
        self.iconphoto(True, icon)

        self._load_settings()
        self._set_variables()
        self._set_menu()
        self._set_layout()

        self._image_canvas = Zoom_Advanced(self._frm, self)
        self._nuclei_table = Table(self._aux_frame)
        self._image_canvas.set_table(self._nuclei_table)
        self._nuclei_table.set_image_canvas(self._image_canvas)
        self._save_settings(2)

        self.update()
        self.protocol("WM_DELETE_WINDOW", self._create_warning_window)
        self.mainloop()

    def _load_settings(self):
        if path.isfile(self.base_path + 'settings.py'):
            with open(self.base_path + 'settings.py', 'r') as param_file:
                settings = load(param_file)
        else:
            settings = {}

        self.settings = Settings()
        for key, value in settings.items():
            getattr(self.settings, key).set(value)

        if path.isfile(self.base_path + 'recent_projects.py'):
            with open(self.base_path +
                      'recent_projects.py', 'r') as recent_projects:
                recent = load(recent_projects)
            self._recent_projects = recent['recent_projects']
        else:
            self._recent_projects = []

        self._save_settings()

    def _set_variables(self):

        self.settings.fibre_colour.trace_add("write", self._nuclei_colour_sel)
        self.settings.nuclei_colour.trace_add("write", self._nuclei_colour_sel)
        self.settings.auto_save_time.trace_add("write",
                                               self._save_settings_time)
        self.settings.save_altered_images.trace_add("write",
                                                    self._save_settings_images)
        self.settings.do_fibre_counting.trace_add("write",
                                                  self._save_settings_callback)
        self.settings.small_objects_threshold.trace_add(
            "write", self._save_settings_callback)
        self.settings.n_threads.trace_add("write",
                                          self._save_settings_callback)

        self._previous_nuclei_colour = StringVar(
            value=self.settings.nuclei_colour.get())
        self._previous_fibre_colour = StringVar(
            value=self.settings.fibre_colour.get())

        self.draw_nuclei = BooleanVar(value=True)

        # threads
        self._current_threads = []
        self._total_images_processed = 0
        self._thread_slider = None
        self._n_threads_running = 0

        self._small_objects_slider = None

        # automatic save
        self._auto_save_name = 'AUTOSAVE'
        self._re_save_images = False
        self._auto_save_job = None

        self._max_recent_projects = 20

        # set the warning var for folder name input
        self._warning_var = StringVar(value='')
        self._name_entry = None
        self._folder_name_window_save_button = None
        self._current_project = ''

    def _set_menu(self):
        self._menu_bar = Menu(self)
        self.config(menu=self._menu_bar)
        self._menu_bar.config(font=("TKDefaultFont", 12))

        self._file_menu = Menu(self._menu_bar, tearoff=0)
        self._file_menu.add_command(label="New Empty Project",
                                    command=self._create_empty_project)
        self._file_menu.add_command(label="Save Project As",
                                    command=self._create_project_name_window)
        self._file_menu.add_command(label="Delete Current Project",
                                    command=self._delete_current_project)
        self._file_menu.entryconfig(
            self._file_menu.index("Delete Current Project"), state="disabled")
        self._file_menu.add_command(label="Load From Explorer",
                                    command=self._load_project_from_explorer)
        self._file_menu.add_separator()

        self._file_menu.add_command(label='Load Automatic Save',
                                    state='disabled',
                                    command=partial(self._load_project,
                                                    self._auto_save_name))

        if path.isdir(self.base_path + 'Projects/' + self._auto_save_name):
            self._file_menu.entryconfig("Load Automatic Save", state='normal')
        self._file_menu.add_separator()

        self._recent_projects_menu = Menu(self._file_menu, tearoff=0)
        self._file_menu.add_cascade(label="Recent Projects",
                                    menu=self._recent_projects_menu)

        self._menu_bar.add_cascade(label="File", menu=self._file_menu)

        self._settings_menu = Menu(self._menu_bar, tearoff=0)
        self._settings_menu.add_command(
            label="Settings", command=self._create_settings_window)
        self._menu_bar.add_cascade(label="Settings", menu=self._settings_menu)

        self._help_menu = Menu(self._menu_bar, tearoff=0)
        self._help_menu.add_command(label="Help", command=self._open_github)
        self._menu_bar.add_cascade(label="Help", menu=self._help_menu)

        self._quit_menu = Menu(self._menu_bar, tearoff=0)
        self._quit_menu.add_command(label="Quit", command=self.destroy)
        self._menu_bar.add_cascade(label="Quit", menu=self._quit_menu)

        self._set_recent_projects()

    def _set_recent_projects(self):
        # load the list of recent projects if these projects exist
        if path.isdir(self.base_path + 'Projects'):
            loaded = list(self._recent_projects)
            for folder in loaded:
                if path.isdir(self.base_path + 'Projects/' + folder) \
                        and folder != '':
                    self._recent_projects_menu.add_command(
                        label="Load '" + folder + "'",
                        command=partial(self._load_project, folder))
                else:
                    self._recent_projects.remove(folder)
        else:
            mkdir(self.base_path + 'Projects')

        if len(self._recent_projects) == 0:
            self._file_menu.entryconfig("Recent Projects", state='disabled')

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
        self._button_style.configure('my.TButton', font=('TKDefaultFont', 11))
        self._process_images_button = ttk.Button(self._button_frame,
                                                 text="Process Images",
                                                 command=self._process_images,
                                                 style='my.TButton',
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
                                       command=self.save_button_pressed,
                                       state='enabled')
        self._save_button.pack(fill="x", anchor="w", side='left', padx=3,
                               pady=5)

        # set indicators
        self._which_indicator_button = ttk.Button(
            self._button_frame, text='Manual : Nuclei',
            command=self._change_indications, state='enabled')
        self._which_indicator_button.pack(fill="x", anchor="w", side='left',
                                          padx=3, pady=5)

    def _set_autosave_time(self):

        # if a previous timer was set, cancel it
        if self._auto_save_job is not None:
            self.after_cancel(self._auto_save_job)
        self._auto_save_job = None

        # set a new timer if needed
        if self.settings.auto_save_time.get() > 0:
            self._auto_save_job = self.after(self.settings.auto_save_time.get()
                                             * 1000, self.save_project)

    def save_project(self, directory=None, save_as=False):

        if directory is None:
            directory = self._auto_save_name

        # don't autosave if not needed
        if self.settings.auto_save_time.get() <= 0 and \
                directory == self._auto_save_name:
            return

        if save_as:
            self._re_save_images = True

        if directory != self._auto_save_name:
            # destroy the save as window if it exists
            if self._folder_name_window_save_button is not None:
                self._folder_name_window_save_button.master.destroy()

            # set the save button
            self._save_button['state'] = 'disabled'
            self._save_button['text'] = 'Save'
            self._file_menu.entryconfig(
                self._file_menu.index("Delete Current Project"),
                state="normal")

            # change the current project name
            self._current_project = directory
            self.title("Cellen Tellen - Project '" +
                       self._current_project + "'")

            # do the recent projects sh*t
            if not path.isdir(self.base_path + 'Projects/' + directory):
                self._recent_projects_menu.insert_command(
                    index=0, label="Load '" + directory + "'",
                    command=partial(self._load_project, directory))
                self._recent_projects.insert(0, directory)
                self._file_menu.entryconfig("Recent Projects", state='normal')
                if len(self._recent_projects) > self._max_recent_projects:
                    # remove the last
                    self._recent_projects_menu.delete(
                        "Load '" + self._recent_projects[-1] +
                        "'")
                    self._recent_projects.pop(len(self._recent_projects) - 1)

                self._save_settings()

        else:
            # set the automatic save entry
            self._file_menu.entryconfig("Load Automatic Save", state='normal')
            if self.settings.auto_save_time.get() > 0:  # recall the autosave
                self._set_autosave_time()

        # create the folder
        if not path.isdir(self.base_path + 'Projects/' + directory):
            mkdir(self.base_path + 'Projects/' + directory)

        # create saving popup
        saving_popup = Toplevel(self)
        saving_popup.grab_set()
        saving_popup.title("Saving....")

        ttk.Label(saving_popup, text="Saving to '" + directory + "' ..."). \
            pack(anchor='center', expand=False, fill='none')
        saving_popup.update()
        self.update()
        saving_popup.update()

        # save the table
        self._nuclei_table.save_table(directory)

        # save the originals
        if self._re_save_images or directory == self._auto_save_name:
            self._nuclei_table.save_originals(directory)
        self._re_save_images = False

        # save the altered images
        if self.settings.save_altered_images.get() == 1 or \
                directory == self._auto_save_name:
            self._nuclei_table.save_altered_images(directory)

        # save the data
        self._nuclei_table.save_data(directory)

        # destroy the popup
        saving_popup.destroy()

    def _load_project(self, directory):

        # stop processing
        self._stop_processing()

        # set the window title
        self.title("Cellen Tellen - Project '" + directory + "'")
        self._current_project = directory

        # set the save button
        self._save_button['state'] = 'disabled'
        self._save_button['text'] = 'Save'
        self._file_menu.entryconfig(
            self._file_menu.index("Delete Current Project"), state="normal")

        # do the recent projects sh*t
        if path.isdir(self.base_path + 'Projects/' + directory) \
                and directory != self._auto_save_name:
            # remove it first
            if directory in self._recent_projects:
                self._recent_projects_menu.delete("Load '" + directory + "'")
                self._recent_projects.remove(directory)

            self._recent_projects_menu.insert_command(
                index=0, label="Load '" + directory + "'",
                command=partial(self._load_project, directory))
            self._recent_projects.insert(0, directory)
            self._file_menu.entryconfig("Recent Projects", state='normal')
            if len(self._recent_projects) > self._max_recent_projects:
                # remove the last
                self._recent_projects_menu.delete(
                    "Load '" + self._recent_projects[-1] + "'")
                self._recent_projects.pop(len(self._recent_projects) - 1)

            self._save_settings()

        # load the project
        self._nuclei_table.load_project(self.base_path + 'Projects/'
                                        + directory)
        self._re_save_images = False

        # if there are images loaded
        if self._nuclei_table.filenames:
            self._process_images_button['state'] = 'enabled'
        else:
            self._process_images_button['state'] = 'disabled'

    def _save_settings_time(self, _, __, ___):
        self._save_settings(setting_index=2)

    def _save_settings_images(self, _, __, ___):
        self._save_settings(setting_index=3)

    def _save_settings_callback(self, _, __, ___):
        self._save_settings()

    def _save_settings(self, setting_index=0):

        # enable save button if needed
        if setting_index == 3:
            self._save_button['state'] = 'enabled'

        # set the autosave timer
        if setting_index == 2:
            self._set_autosave_time()

        settings = {key: value.get() for key, value in
                    self.settings.__dict__.items()}

        with open(self.base_path + 'settings.py', 'w') as param_file:
            dump(settings, param_file)

        with open(self.base_path +
                  'recent_projects.py', 'w') as recent_projects:
            dump({'recent_projects': self._recent_projects}, recent_projects)

    def _stop_processing(self):

        # end the threads
        for thread in self._current_threads:
            res = pythonapi.PyThreadState_SetAsyncExc(thread,
                                                      py_object(SystemExit))
            if res > 1:
                pythonapi.PyThreadState_SetAsyncExc(thread, 0)
                print('Exception raise failure')

        print("Still running threads (should be 1) :", active_count())

        # empty threads
        self._current_threads = []
        self._total_images_processed = 0
        self._process_images_button['text'] = "Process Images"
        self._process_images_button.configure(command=self._process_images)
        self._processing_label['text'] = ""

    def _process_images(self):

        # stop vorige threads
        self._stop_processing()

        # get the file_names
        file_names = self._nuclei_table.filenames
        self.set_unsaved_status()

        # switch off process button
        self._total_images_processed = 0
        self._process_images_button['text'] = 'Stop Processing'
        self._process_images_button.configure(command=self._stop_processing)
        self._processing_label['text'] = "0 of " + str(len(file_names)) + \
                                         " Images Processed"
        self.update()

        # start threading
        n_threads_running = self.settings.n_threads.get()
        if int(self.settings.n_threads.get()) == 0:
            self._process_thread(0, file_names, False,
                                 self.settings.small_objects_threshold.get())
        else:
            for i in range(n_threads_running):
                if i <= len(file_names) - 1:
                    t1 = Thread(target=self._process_thread,
                                args=(i, file_names,
                                      True,
                                      self.settings.small_objects_threshold.
                                      get()),
                                daemon=True)
                    t1.start()
                    print(t1)

    def set_unsaved_status(self):

        # set the unsaved status
        if self._current_project != '':
            self.title("Cellen Tellen - Project '" + self._current_project +
                       "' (Unsaved)")
            self._save_button['state'] = 'enabled'
            self._save_button['text'] = 'Save'

    def _process_thread(self, index, file_names, is_thread,
                        small_objects_thresh):

        # add the thread
        if is_thread:
            id_ = get_ident()
            if id_ not in self._current_threads:
                self._current_threads.append(id_)

        file = file_names[index]

        start = time()

        # get result
        nuclei, nuclei_in_fibre, fibre_positions, image_width, image_height = \
            deepcell_functie(file, self.settings.nuclei_colour.get(),
                             self.settings.fibre_colour.get(),
                             self.settings.do_fibre_counting.get(),
                             small_objects_thresh)

        end1 = time()

        # convert image coordinates to relative between 0 and 1
        for nucleus in nuclei:
            nucleus[0] = float(nucleus[0]) / float(image_width)
            nucleus[1] = float(nucleus[1]) / float(image_height)
        for nucleus in nuclei_in_fibre:
            nucleus[0] = float(nucleus[0]) / float(image_width)
            nucleus[1] = float(nucleus[1]) / float(image_height)
        for pos in fibre_positions:
            pos[0] = float(pos[0]) / float(image_width)
            pos[1] = float(pos[1]) / float(image_height)

        print("file : ", end1 - start)

        # send the output to the table
        self._nuclei_table.input_processed_data(nuclei, nuclei_in_fibre,
                                                fibre_positions,
                                                index)

        # close if necessary
        self._update_processed_images(file_names)
        self.set_unsaved_status()

        if is_thread:
            if index >= len(file_names) - self._n_threads_running:
                # close the threshold
                self._thread_exited(get_ident())
            else:
                # keep on processing more images
                self._process_thread(index + self._n_threads_running,
                                     file_names, True, small_objects_thresh)
        else:
            if index + 1 < len(file_names):
                # keep on processing more images
                self._process_thread(index + 1, file_names, False,
                                     small_objects_thresh)
            else:
                # all images are done
                self._stop_processing()

    def _update_processed_images(self, file_names):

        # change the label
        self._total_images_processed += 1
        self._processing_label['text'] = str(self._total_images_processed) + \
            " of " + str(len(file_names)) + " Images Processed"

    def _thread_exited(self, id_):
        self._current_threads.remove(id_)
        if len(self._current_threads) == 0:
            self._stop_processing()

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

    def _create_warning_window(self):

        # if unsaved, show the window
        if self._save_button['state'] == 'enabled' and \
                self._nuclei_table.filenames:
            # create
            Warning_window(self)

        else:
            # if saved, destroy the window
            self.destroy()

    def save_button_pressed(self):

        # save as if necessary
        if self._current_project == '':
            self._create_project_name_window()
        else:
            # perform normal save
            self.save_project(self._current_project)

    def _create_project_name_window(self, new_project=False):

        # create the window
        Project_name_window(self, new_project)

    def _change_indications(self):
        if self.draw_nuclei.get():
            self.draw_nuclei.set(False)
            self._which_indicator_button['text'] = 'Manual : Fibres'
        else:
            self.draw_nuclei.set(True)
            self._which_indicator_button['text'] = 'Manual : Nuclei'

    @staticmethod
    def _open_github():
        open_new("https://github.com/Quentinderore2/Cellen-Tellen")

    def _create_empty_project(self):

        # reset everything
        self._stop_processing()
        self._nuclei_table.reset()
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
        self._current_project = ''

        # call for project name
        self._create_project_name_window(True)

    def _select_images(self):

        # get the filenames with a dialog box
        file_names = filedialog.askopenfilenames(
            filetypes=[('Image Files', ('.tif', '.png', '.jpg', '.jpeg',
                                        '.bmp', '.hdr'))],
            parent=self, title='Please select a directory')

        if len(file_names) != 0:
            # stop processing
            self._stop_processing()

            # enable the process image buttons
            self._process_images_button["state"] = 'enabled'

            # add them to the table
            self._re_save_images = True
            self._nuclei_table.add_images(file_names)
            self.set_unsaved_status()

    def _create_settings_window(self):

        # create the window
        Settings_window(self)

    def _delete_current_project(self):

        if self._current_project != '':
            # delete the project
            rmtree(self.base_path + 'Projects/' + self._current_project)

            # remove the load button
            self._recent_projects_menu.delete(
                self._recent_projects_menu.index("Load '" +
                                                 self._current_project + "'"))
            self._recent_projects.remove(self._current_project)
            if len(self._recent_projects) == 0:
                self._file_menu.entryconfig("Recent Projects",
                                            state='disabled')
            self._save_settings()

            # create empty project
            self._create_empty_project()

            if self._current_project == self._auto_save_name:
                self._file_menu.entryconfig("Load Automatic Save",
                                            state='disabled')

    def _load_project_from_explorer(self):

        # ask a folder
        folder = filedialog.askdirectory(
            initialdir=path.normpath(self.base_path + "Projects"),
            title="Choose a Project Folder")

        # load this sh*t
        if (folder != '') and path.isdir(self.base_path + 'Projects/' +
                                         path.basename(folder)):
            self._load_project(path.basename(folder))

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


if __name__ == "__main__":

    Splash()
    Main_window()
