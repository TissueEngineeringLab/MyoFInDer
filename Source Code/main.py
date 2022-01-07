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
from validateFileName import is_pathname_valid
from shutil import rmtree
from webbrowser import open_new

from nucleiFibreSegmentation import deepcell_functie, initialize_mesmer

from threading import get_ident, active_count, Thread
from time import time, sleep
from json import load, dump
from functools import partial

default_param = {'fibre_colour_var': "Blue",
                 'previous_fibre_colour_var': "Blue",
                 'nuclei_colour_var': "Blue",
                 'previous_nuclei_colour_var': "Blue",
                 'auto_save_time': -1,
                 'save_altered_images_boolean': 0,
                 'do_fibre_counting': 0,
                 'n_threads': 3,
                 'small_objects_threshold': 400,
                 'recent_projects': [],
                 'blue_channel_bool': True,
                 'green_channel_bool': True,
                 'red_channel_bool': False,
                 'show_nuclei_bool': True,
                 'show_fibres_bool': False}


class splash(Tk):

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


# set better resolution
if system() == "Windows" and int(release()) >= 8:
    dll.shcore.SetProcessDpiAwareness(True)


class main_window(Tk):

    def __init__(self):
        super().__init__()

        self.title("Cellen Tellen - New Project (Unsaved)")
        if system() == "Windows":
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)

        self._base_path = path.abspath('') + "/"

        self._icon = PhotoImage(file=self._base_path + "icon.png")
        self.iconphoto(False, self._icon)

        self._load_settings()
        self._set_menu()
        self._set_layout()
        self._set_bindings()

        self._image_canvas = Zoom_Advanced(self._frm)
        self._nuclei_table = Table(self._aux_frame)
        self._image_canvas.set_table(self._nuclei_table)
        self._nuclei_table.set_image_canvas(self._image_canvas)
        self._save_settings(2)

        self._set_indicators()
        self._set_image_channels()

        self.update()
        self.protocol("WM_DELETE_WINDOW", self._create_warning_window)
        self.mainloop()

    def _load_settings(self):
        if path.isfile(self._base_path + 'general.py'):
            with open(self._base_path + 'general.py', 'r') as param_file:
                param = load(param_file)
        else:
            param = {}

        self._fibre_colour_var = StringVar(
            value=param.pop('fibre_colour_var',
                            default_param['fibre_colour_var']))
        self._previous_fibre_colour_var = StringVar(
            value=param.pop('previous_fibre_colour_var',
                            default_param['previous_fibre_colour_var']))

        self._nuclei_colour_var = StringVar(
            value=param.pop('nuclei_colour_var',
                            default_param['nuclei_colour_var']))
        self._previous_nuclei_colour_var = StringVar(
            value=param.pop('previous_nuclei_colour_var',
                            default_param['previous_nuclei_colour_var']))

        self._auto_save_time = IntVar(
            value=param.pop('auto_save_time', default_param['auto_save_time']))

        self._save_altered_images_boolean = IntVar(
            value=param.pop('save_altered_images_boolean',
                            default_param['save_altered_images_boolean']))

        self._do_fibre_counting = IntVar(
            value=param.pop('do_fibre_counting',
                            default_param['do_fibre_counting']))

        self._n_threads = IntVar(
            value=param.pop('n_threads', default_param['n_threads']))

        self._small_objects_threshold = IntVar(
            value=param.pop('small_objects_threshold',
                            default_param['small_objects_threshold']))

        self._recent_projects = param.pop('recent_projects',
                                          default_param['recent_projects'])

        self._blue_channel_bool = BooleanVar(
            value=param.pop('blue_channel_bool',
                            default_param['blue_channel_bool']))
        self._green_channel_bool = BooleanVar(
            value=param.pop('green_channel_bool',
                            default_param['green_channel_bool']))
        self._red_channel_bool = BooleanVar(
            value=param.pop('red_channel_bool',
                            default_param['red_channel_bool']))
        self._show_nuclei_bool = BooleanVar(
            value=param.pop('show_nuclei_bool',
                            default_param['show_nuclei_bool']))
        self._show_fibres_bool = BooleanVar(
            value=param.pop('show_fibres_bool',
                            default_param['show_fibres_bool']))

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

        self._indicating_nuclei = True

        self._save_settings()

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

        if path.isdir(self._base_path + 'Projects/' + self._auto_save_name):
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
        if path.isdir(self._base_path + 'Projects'):
            loaded = list(self._recent_projects)
            for folder in loaded:
                if path.isdir(self._base_path + 'Projects/' + folder) \
                        and folder != '':
                    self._recent_projects_menu.add_command(
                        label="Load '" + folder + "'",
                        command=partial(self._load_project, folder))
                else:
                    self._recent_projects.remove(folder)
        else:
            mkdir(self._base_path + 'Projects')

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
            offvalue=False, variable=self._blue_channel_bool,
            command=self._set_image_channels)
        self._blue_channel_check_button.pack(anchor="w", side="left", fill='x',
                                             padx=3, pady=5)
        self._green_channel_check_button = ttk.Checkbutton(
            self._tick_frame_1, text="Green Channel", onvalue=True,
            offvalue=False, variable=self._green_channel_bool,
            command=self._set_image_channels)
        self._green_channel_check_button.pack(anchor="w", side="left",
                                              fill='x', padx=3, pady=5)
        self._red_channel_check_button = ttk.Checkbutton(
            self._tick_frame_1, text="Red Channel", onvalue=True,
            offvalue=False, variable=self._red_channel_bool,
            command=self._set_image_channels)
        self._red_channel_check_button.pack(anchor="w", side="left", fill='x',
                                            padx=3, pady=5)

        # indicator selections (which indicators are shown)
        self._indicator = ttk.Label(self._tick_frame_2, text="  Indicators : ")
        self._indicator.pack(anchor="w", side="left", fill='x', padx=3, pady=5)
        self._show_nuclei_check_button = ttk.Checkbutton(
            self._tick_frame_2, text="Nuclei", onvalue=True, offvalue=False,
            variable=self._show_nuclei_bool, command=self._set_indicators)
        self._show_nuclei_check_button.pack(anchor="w", side="left", fill='x',
                                            padx=3, pady=5)
        self._show_fibres_check_button = ttk.Checkbutton(
            self._tick_frame_2, text="Fibres", onvalue=True, offvalue=False,
            variable=self._show_fibres_bool, command=self._set_indicators)
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

    def _set_bindings(self):
        self.bind('<ButtonPress-1>', self._left_click)
        self.bind('<ButtonPress-3>', self._right_click)
        if system() == "Linux":
            self.bind('<4>', self._on_wheel)
            self.bind('<5>', self._on_wheel)
        else:
            self.bind('<MouseWheel>', self._on_wheel)
        self.bind('<Motion>', self._motion)
        self.bind('<Left>', self._on_left_press)
        self.bind('<Right>', self._on_right_press)
        self.bind('<Up>', self._on_up_press)
        self.bind('<Down>', self._on_down_press)
        self.bind('=', self._on_zoom_in_press)
        self.bind('+', self._on_zoom_in_press)
        self.bind('-', self._on_zoom_out_press)
        self.bind('_', self._on_zoom_out_press)

    def _set_autosave_time(self):

        # if a previous timer was set, cancel it
        if self._auto_save_job is not None:
            self.after_cancel(self._auto_save_job)
        self._auto_save_job = None

        # set a new timer if needed
        if self._auto_save_time.get() > 0:
            self._auto_save_job = self.after(self._auto_save_time.get() * 1000,
                                             partial(self._save_project,
                                                     self._auto_save_name))

    def _save_project(self, directory, save_as=False):

        # don't autosave if not needed
        if self._auto_save_time.get() <= 0 and \
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
            if not path.isdir(self._base_path + 'Projects/' + directory):
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
            if self._auto_save_time.get() > 0:  # recall the autosave
                self._set_autosave_time()

        # create the folder
        if not path.isdir(self._base_path + 'Projects/' + directory):
            mkdir(self._base_path + 'Projects/' + directory)

        # create saving popup
        saving_popup = Toplevel(self)
        saving_popup.grab_set()
        saving_popup.title("Saving....")

        scr_width = self.winfo_screenwidth()
        scr_height = self.winfo_screenheight()

        saving_popup.geometry("400x200+" + str(int(scr_width / 2 - 200)) +
                              "+" + str(int(scr_height / 2 - 100)))
        ttk.Label(saving_popup, text="Saving to '" + directory + "' ..."). \
            place(x=200, y=75, anchor='center')
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
        if self._save_altered_images_boolean.get() == 1 or \
                directory == self._auto_save_name:
            self._nuclei_table.save_altered_images(directory)

        # save the data
        self._nuclei_table.save_data(directory)

        # destroy the popup
        saving_popup.destroy()

        # als het nodig is, close
        if self._close:
            self.destroy()

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
        if path.isdir(self._base_path + 'Projects/' + directory) \
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
        self._nuclei_table.load_project(self._base_path + 'Projects/'
                                        + directory)
        self._re_save_images = False

        # if there are images loaded
        if self._nuclei_table.images_available():
            self._process_images_button['state'] = 'enabled'
        else:
            self._process_images_button['state'] = 'disabled'

    def _save_settings(self, setting_index=0):

        settings = [self._fibre_colour_var.get(),
                    self._previous_fibre_colour_var.get(),
                    self._nuclei_colour_var.get(),
                    self._previous_nuclei_colour_var.get(),
                    self._auto_save_time.get(),
                    self._save_altered_images_boolean.get(),
                    self._do_fibre_counting.get(),
                    self._n_threads.get(),
                    self._small_objects_threshold.get(),
                    self._recent_projects,
                    self._blue_channel_bool.get(),
                    self._green_channel_bool.get(),
                    self._red_channel_bool.get(),
                    self._show_nuclei_bool.get(),
                    self._show_fibres_bool.get()]

        settings = {key: setting for key, setting in
                    zip(default_param.keys(), settings)}

        # enable save button if needed
        if setting_index == 3:
            self._save_button['state'] = 'enabled'

        # set the autosave timer
        if setting_index == 2:
            self._set_autosave_time()

        with open(self._base_path + 'general.py', 'w') as param_file:
            dump(settings, param_file)

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
        self._set_unsaved_status()

        # switch off process button
        self._total_images_processed = 0
        self._process_images_button['text'] = 'Stop Processing'
        self._process_images_button.configure(command=self._stop_processing)
        self._processing_label['text'] = "0 of " + str(len(file_names)) + \
                                         " Images Processed"
        self.update()

        # start threading
        n_threads_running = self._n_threads.get()
        if int(self._n_threads.get()) == 0:
            self._process_thread(0, file_names, False,
                                 self._small_objects_threshold.get())
        else:
            for i in range(n_threads_running):
                if i <= len(file_names) - 1:
                    t1 = Thread(target=self._process_thread,
                                args=(i, file_names,
                                      True,
                                      self._small_objects_threshold.get()),
                                daemon=True)
                    t1.start()
                    print(t1)

    def _set_unsaved_status(self):

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
            deepcell_functie(file, self._nuclei_colour_var.get(),
                             self._fibre_colour_var.get(),
                             self._do_fibre_counting.get(),
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
        self._set_unsaved_status()

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
        self._image_canvas.set_channels(self._blue_channel_bool.get(),
                                        self._green_channel_bool.get(),
                                        self._red_channel_bool.get())
        self._save_settings()

    def _set_indicators(self):
        # set the indicators
        self._image_canvas.set_indicators(self._show_nuclei_bool.get(),
                                          self._show_fibres_bool.get())
        self._save_settings()

        # set which indication
        if self._show_fibres_bool.get() and not self._show_nuclei_bool.get():
            self._indicating_nuclei = False
            self._which_indicator_button['text'] = 'Manual : Fibres'
            self._which_indicator_button['state'] = 'disabled'

        if self._show_fibres_bool.get() and self._show_nuclei_bool.get():
            self._which_indicator_button['state'] = 'enabled'

        if not self._show_fibres_bool.get() and self._show_nuclei_bool.get():
            self._indicating_nuclei = True
            self._which_indicator_button['text'] = 'Manual : Nuclei'
            self._which_indicator_button['state'] = 'disabled'

        # pass through the indications to the image canvas
        self._image_canvas.set_which_indication(self._indicating_nuclei)

    def _create_warning_window(self):

        # if unsaved, show the window
        if self._save_button['state'] == 'enabled' and \
                not len(self._nuclei_table.filenames) == 0:
            # create
            warning_window = Toplevel(self)
            warning_window.grab_set()
            scr_width = self.winfo_screenwidth()
            scr_height = self.winfo_screenheight()
            warning_window.geometry(
                "500x200+" + str(int(scr_width / 2 - 250))
                + "+" + str(int(scr_height / 4 - 100)))

            warning_window.title("Hold on!")
            self._close = True

            # create the label
            ttk.Label(warning_window,
                      text="Are you sure about closing an unsaved project?"). \
                place(x=250, y=30, anchor='center')

            # create the buttons
            ttk.Button(warning_window, text='Close Without Saving',
                       command=self.destroy, width=40).place(x=250, y=115,
                                                             anchor='center')
            ttk.Button(warning_window, text='Save and Close',
                       command=self._save_button_pressed, width=40). \
                place(x=250, y=75, anchor='center')
            ttk.Button(warning_window, text='Cancel',
                       command=partial(self._quit_warning_window,
                                       warning_window),
                       width=40).place(x=250, y=155, anchor='center')

        else:
            # if saved, destroy the window
            self.destroy()

    def _quit_warning_window(self, warning_window):
        warning_window.destroy()
        self._close = False

    def _save_button_pressed(self):

        # save as if necessary
        if self._current_project == '':
            self._create_project_name_window()
        else:
            # perform normal save
            self._save_project(self._current_project)

    def _create_project_name_window(self, new_project=False):

        # create the window
        projectname_window = Toplevel(self)
        projectname_window.grab_set()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        projectname_window.geometry("500x200+" +
                                    str(int(screen_width / 2 - 250)) + "+"
                                    + str(int(screen_height / 2 - 100)))
        if new_project:
            projectname_window.title("Creating a New Empty Project")
        else:
            projectname_window.title("Saving the Current Project")

        # set label
        if new_project:
            ask_label = ttk.Label(projectname_window,
                                  text='Choose a name for your NEW EMPTY '
                                       'Project')
            ask_label.place(x=250, y=30, anchor='center')
        else:
            ask_label = ttk.Label(projectname_window,
                                  text='Choose a name for your '
                                       'CURRENT Project')
            ask_label.place(x=250, y=30, anchor='center')

        # set the warning label (gives warnings when the name is bad)
        self._warning_var.set('')
        warning_label = ttk.Label(projectname_window,
                                  textvariable=self._warning_var,
                                  foreground='red')
        warning_label.place(x=250, y=75, anchor='center')
        validate_command = warning_label.register(
            self._check_project_name_entry)

        # set the entry box to input the name
        self._name_entry = ttk.Entry(
            projectname_window, validate='key', state='normal',
            text='Choose a name for your project', width=30,
            validatecommand=(validate_command, '%P'))
        self._name_entry.place(x=250, y=110, anchor='center')
        self._name_entry.focus()
        self._name_entry.icursor(len(self._name_entry.get()))

        # save button
        self._folder_name_window_save_button = ttk.Button(
            projectname_window, text='Save', width=30,
            command=partial(self._save_project, self._name_entry.get(), True))
        self._folder_name_window_save_button.place(x=250, y=150,
                                                   anchor='center')
        projectname_window.bind('<Return>', self._enter_pressed)
        self._check_project_name_entry(self._name_entry.get())

    def _enter_pressed(self, *_, **__):

        # if the window exists and the save button is enabled
        if self._folder_name_window_save_button['state'] == 'enabled':
            self._save_project(self._name_entry.get(), True)

    def _check_project_name_entry(self, new_entry):

        # check if it is a valid name
        if not is_pathname_valid(new_entry) or '/' in new_entry \
                or '.' in new_entry:
            self._folder_name_window_save_button['state'] = 'disabled'
            if len(new_entry) != 0:
                self._warning_var.set('This is not a valid projectname')
            return True

        # check if it already exists
        if path.isdir(self._base_path + 'Projects/' + new_entry):
            self._warning_var.set('This project already exists')
            self._folder_name_window_save_button['state'] = 'disabled'
            return True

        # no warnings
        self._warning_var.set('')
        self._folder_name_window_save_button['state'] = 'enabled'
        return True

    def _change_indications(self):
        if self._indicating_nuclei:
            self._indicating_nuclei = False
            self._which_indicator_button['text'] = 'Manual : Fibres'
        else:
            self._indicating_nuclei = True
            self._which_indicator_button['text'] = 'Manual : Nuclei'
        self._image_canvas.set_which_indication(self._indicating_nuclei)

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
            self._set_unsaved_status()

    def _create_settings_window(self):

        # create the window
        new_window = Toplevel(self)
        new_window.grab_set()  # when you show the popup
        new_window.geometry("500x700+100+100")
        new_window.title("Settings")

        frame = ttk.Frame(new_window, padding="10 10 150 150")
        frame.grid(column=0, row=0, sticky='NESW')

        # nuclei colour
        ttk.Label(frame, text="Nuclei Colour :    ").grid(column=0, row=0,
                                                          sticky='NE')
        nuclei_colour_r1 = ttk.Radiobutton(
            frame, text="Blue Channel", variable=self._nuclei_colour_var,
            value="Blue", command=self._nuclei_colour_sel)
        nuclei_colour_r1.grid(column=1, row=0, sticky='NW')
        nuclei_colour_r2 = ttk.Radiobutton(frame, text="Green Channel",
                                           variable=self._nuclei_colour_var,
                                           value="Green",
                                           command=self._nuclei_colour_sel)
        nuclei_colour_r2.grid(column=1, row=1, sticky='NW')
        nuclei_colour_r3 = ttk.Radiobutton(frame, text="Red Channel",
                                           variable=self._nuclei_colour_var,
                                           value="Red",
                                           command=self._nuclei_colour_sel)
        nuclei_colour_r3.grid(column=1, row=2, sticky='NW')

        # fibre colour
        ttk.Label(frame, text="Fibre Colour :    ").grid(column=0, row=5,
                                                         sticky='NE')
        fibre_colour_r1 = ttk.Radiobutton(frame, text="Blue Channel",
                                          variable=self._fibre_colour_var,
                                          value="Blue",
                                          command=self._nuclei_colour_sel)
        fibre_colour_r1.grid(column=1, row=5, sticky='NW')
        fibre_colour_r2 = ttk.Radiobutton(frame, text="Green Channel",
                                          variable=self._fibre_colour_var,
                                          value="Green",
                                          command=self._nuclei_colour_sel)
        fibre_colour_r2.grid(column=1, row=6, sticky='NW')
        fibre_colour_r3 = ttk.Radiobutton(frame, text="Red Channel",
                                          variable=self._fibre_colour_var,
                                          value="Red",
                                          command=self._nuclei_colour_sel)
        fibre_colour_r3.grid(column=1, row=7, sticky='NW')

        # autosave timer
        ttk.Label(frame, text='Autosave Interval :    ').grid(column=0, row=10,
                                                              sticky='NE')
        ttk.Radiobutton(frame, text="5 Minutes", variable=self._auto_save_time,
                        value=5 * 60,
                        command=partial(self._save_settings, 2)).grid(
            column=1, row=10, sticky='NW')
        ttk.Radiobutton(frame, text="15 Minutes",
                        variable=self._auto_save_time,
                        value=15 * 60,
                        command=partial(self._save_settings, 2)).grid(
            column=1, row=11, sticky='NW')
        ttk.Radiobutton(frame, text="30 Minutes",
                        variable=self._auto_save_time,
                        value=30 * 60,
                        command=partial(self._save_settings, 2)).grid(
            column=1, row=12, sticky='NW')
        ttk.Radiobutton(frame, text="60 Minutes",
                        variable=self._auto_save_time,
                        value=60 * 60,
                        command=partial(self._save_settings, 2)).grid(
            column=1, row=13, sticky='NW')
        ttk.Radiobutton(frame, text="Never",
                        variable=self._auto_save_time, value=-1,
                        command=partial(self._save_settings, 2)).grid(
            column=1, row=14, sticky='NW')

        # save altered images
        ttk.Label(frame, text='Save Altered Images :    ').grid(
            column=0, row=16, sticky='NE')
        ttk.Radiobutton(frame, text="On",
                        variable=self._save_altered_images_boolean,
                        value=1,
                        command=partial(self._save_settings, 3)).grid(
            column=1, row=16, sticky='NW')
        ttk.Radiobutton(frame, text="Off",
                        variable=self._save_altered_images_boolean,
                        value=0,
                        command=partial(self._save_settings, 3)).grid(
            column=1, row=17, sticky='NW')

        # fibre counting
        ttk.Label(frame, text='Count Fibres :    ').grid(column=0, row=19,
                                                         sticky='NE')
        ttk.Radiobutton(frame, text="On",
                        variable=self._do_fibre_counting, value=1,
                        command=partial(self._save_settings, 4)).grid(
            column=1, row=19, sticky='NW')
        ttk.Radiobutton(frame, text="Off",
                        variable=self._do_fibre_counting, value=0,
                        command=partial(self._save_settings, 4)).grid(
            column=1, row=20, sticky='NW')

        # multithreading
        ttk.Label(frame, text='Number of Threads :    ').grid(column=0, row=22,
                                                              sticky='NE')

        self._thread_slider = Scale(frame, from_=0, to=5, orient="horizontal",
                                    label='Off',
                                    command=self._thread_slider_func,
                                    showvalue=False,
                                    length=150)
        self._thread_slider.set(int(self._n_threads.get()))
        self._thread_slider.grid(column=1, row=22, sticky='NW')

        # small objects threshold
        ttk.Label(frame, text='Dead cells size Threshold :    ').grid(
            column=0, row=23, sticky='NE')
        self._small_objects_slider = Scale(
            frame, from_=10, to=1000,
            label=str(int(self._small_objects_threshold.get())),
            orient="horizontal",
            command=self._small_objects_slider_func,
            showvalue=False, length=150)
        self._small_objects_slider.set(
            int(self._small_objects_threshold.get()))
        self._small_objects_slider.grid(column=1, row=23, sticky='NW')

        # set row heights
        frame.grid_rowconfigure(4, minsize=20)
        frame.grid_rowconfigure(9, minsize=20)
        frame.grid_rowconfigure(15, minsize=20)
        frame.grid_rowconfigure(18, minsize=20)
        frame.grid_rowconfigure(23, minsize=20)
        frame.grid_rowconfigure(21, minsize=20)
        frame.grid_columnconfigure(0, minsize=250)

    def _delete_current_project(self):

        if self._current_project != '':
            # delete the project
            rmtree(self._base_path + 'Projects/' + self._current_project)

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
            initialdir=path.normpath(self._base_path + "Projects"),
            title="Choose a Project Folder")

        # load this sh*t
        if (folder != '') and path.isdir(self._base_path + 'Projects/' +
                                         path.basename(folder)):
            self._load_project(path.basename(folder))

    def _thread_slider_func(self, n):
        if int(n) == 0:
            self._thread_slider.configure(label='Off')
        else:
            self._thread_slider.configure(label=str(n))
        self._n_threads.set(int(n))
        self._save_settings()

    def _small_objects_slider_func(self, n):
        self._small_objects_slider.configure(label=str(n))
        self._small_objects_threshold.set(n)
        self._save_settings()

    def _nuclei_colour_sel(self):

        # if the two are the same, reset one
        if self._nuclei_colour_var.get() == self._fibre_colour_var.get():
            if self._previous_nuclei_colour_var.get() != \
                    self._nuclei_colour_var.get():
                self._fibre_colour_var.set(
                    self._previous_nuclei_colour_var.get())
            elif self._previous_fibre_colour_var.get() != \
                    self._fibre_colour_var.get():
                self._nuclei_colour_var.set(
                    self._previous_fibre_colour_var.get())

        # set the previous ones to the current one
        self._previous_nuclei_colour_var.set(self._nuclei_colour_var.get())
        self._previous_fibre_colour_var.set(self._fibre_colour_var.get())

        # save
        self._save_settings()

    def _left_click(self, event):
        self._nuclei_table.left_click(str(event.widget), event.y)
        if self._image_canvas.left_click(str(event.widget), event.x, event.y):
            self._set_unsaved_status()

    # when right-clicking, the position of the cursor is sent to the table and
    # image canvas
    def _right_click(self, event):
        if self._image_canvas.right_click(str(event.widget), event.x, event.y):
            self._set_unsaved_status()

    def _on_wheel(self, event):
        if system() == "Linux":
            self._nuclei_table.onwheel(str(event.widget),
                                       120 if event.num == 4 else -120)
        else:
            self._nuclei_table.onwheel(str(event.widget),
                                       120 * event.delta / abs(event.delta))

    def _motion(self, event):
        if self._nuclei_table is not None:
            self._nuclei_table.motion(str(event.widget), event.y)

    # pass through the key pressing of the arrows to the image canvas to scroll
    # around the image canvas
    def _on_left_press(self, *_, **__):
        self._image_canvas.arrows(0)

    def _on_up_press(self, *_, **__):
        self._image_canvas.arrows(1)

    def _on_right_press(self, *_, **__):
        self._image_canvas.arrows(2)

    def _on_down_press(self, *_, **__):
        self._image_canvas.arrows(3)

    def _on_zoom_in_press(self, event):
        self._image_canvas.zoom(str(event.widget), 120)

    def _on_zoom_out_press(self, event):
        self._image_canvas.zoom(str(event.widget), -120)


if __name__ == "__main__":

    splash()
    main_window()
