# coding: utf-8

from tkinter import ttk, filedialog, Tk, IntVar, PhotoImage, Menu, StringVar, \
    messagebox
from platform import system, release
from shutil import rmtree
from webbrowser import open_new
from threading import Thread, Event
from queue import Empty, Queue
from time import sleep
from pickle import load, dump
from functools import partial, wraps
from pathlib import Path
from typing import Callable, NoReturn, Optional

from .tools import Settings
from .tools import Save_popup
from .tools import Warning_window
from .tools import Project_name_window
from .tools import Settings_window
from .tools import Splash_window
from .files_table import Files_table
from .image_canvas import Image_canvas

# Sets a better resolution on recent Windows platforms
if system() == "Windows" and int(release()) >= 8:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(True)

# Todo:
#   Set up unit tests
#   Improve software distribution
#   Add a nuclei threshold
#   Configure CTRL+S


def _save_before_closing(func: Callable) -> Callable:
    """Decorator for warning the user when an action that may cause unwanted
    data loss is triggered.

    The user will then be proposed to save the work, continue anyway, or abort.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):

        # The warning window will return False if the operation shouldn't be
        # carried on
        if self._create_warning_window():
            func(self, *args, **kwargs)
    return wrapper


class Main_window(Tk):
    """The main window of the Cellen Tellen software.

    It manages all the buttons, menus, events, and the secondary windows.
    """

    def __init__(self) -> None:
        """Creates the splash window, then the main window, sets the layout and
        the callbacks."""

        # Sets the different paths used in the project
        self.base_path = Path(__file__).parent
        if Path(__file__).name.endswith(".pyc"):
            self.base_path = self.base_path.parent
        self.projects_path = self.base_path.parent / 'Projects'
        self._settings_path = self.base_path / 'settings'

        # Generates a splash window while waiting for the modules to load
        splash = Splash_window(self)
        splash.resize_image()
        self._segmentation = splash.display()
        splash.destroy()

        # Initializes the main window
        super().__init__()
        self.title("Cellen Tellen - New Project (Unsaved)")
        if system() == "Windows":
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)

        # Sets the application icon
        icon = PhotoImage(file=self.base_path / 'app_images' /
                          "project_icon.png")
        self.iconphoto(False, icon)  # Without it the icon is buggy in Windows
        self.iconphoto(True, icon)

        # Sets the settings, variables, callbacks, menus and layout
        self._load_settings()
        self._set_variables()
        self._set_traces()
        self._set_menu()
        self._set_layout()

        # Sets the image canvas and the files table
        self._image_canvas = Image_canvas(self._frm, self)
        self._files_table = Files_table(self._aux_frame, self.projects_path)
        self._image_canvas.nuclei_table = self._files_table
        self._files_table.image_canvas = self._image_canvas

        self._save_settings(autosave_time=True)

        # Finishes the initialization and starts the event loop
        self.update()
        self.protocol("WM_DELETE_WINDOW", self._safe_destroy)
        self.mainloop()

    def set_unsaved_status(self) -> NoReturn:
        """Sets the title and save button when a project is modified."""

        if self._current_project is not None:
            self.title("Cellen Tellen - Project '" + self._current_project.name
                       + "' (Unsaved)")
            self._save_button['state'] = 'enabled'
            self._save_button['text'] = 'Save'
        else:
            self.title("Cellen Tellen - New Project (Unsaved)")
            self._save_button['state'] = 'enabled'
            self._save_button['text'] = 'Save As'

    def _load_settings(self) -> NoReturn:
        """Loads the settings from the settings file if any, otherwise sets
        them to default."""

        # Gets the settings from the settings.pickle file
        if (self._settings_path / 'settings.pickle').is_file():
            with open(self._settings_path /
                      'settings.pickle', 'rb') as param_file:
                settings = load(param_file)
        else:
            settings = {}

        # Creates a Settings instance and sets the values
        self.settings = Settings()  # The default values are preset in Settings
        for key, value in settings.items():
            getattr(self.settings, key).set(value)

        # Gets the recent projects from the recent_projects.pickle file
        if (self._settings_path / 'recent_projects.pickle').is_file():
            with open(self._settings_path /
                      'recent_projects.pickle', 'rb') as recent_projects:
                recent = load(recent_projects)

            # Only the names are stored, the path must be completed
            # Here we also make sure that the projects are valid
            self._recent_projects = [
                self.projects_path / proj for proj in recent['recent_projects']
                if proj
                and (self.projects_path / proj).is_dir()
                and (self.projects_path / proj / 'data.pickle').is_file()]
            self._recent_projects = list(dict.fromkeys(self._recent_projects))
        else:
            self._recent_projects = []

        # Finally, saving the recent projects and the settings
        self._save_settings()

    def _set_traces(self) -> NoReturn:
        """Sets the callbacks triggered upon modification of the settings."""

        # Making sure there's no conflict between the nuclei and fibres colors
        self.settings.fibre_colour.trace_add("write", self._nuclei_colour_sel)
        self.settings.nuclei_colour.trace_add("write", self._nuclei_colour_sel)

        # Simply saving the settings upon modification
        self.settings.auto_save_time.trace_add("write",
                                               self._save_settings_callback)
        self.settings.save_altered_images.trace_add(
            "write", self._save_settings_callback)
        self.settings.fibre_threshold.trace_add("write",
                                                self._save_settings_callback)
        self.settings.small_objects_threshold.trace_add(
            "write", self._save_settings_callback)

        # Updates the display when an image has been processed
        self._processed_images_count.trace_add("write",
                                               self._update_processed_images)

    def _set_variables(self) -> NoReturn:
        """Sets the different variables used in the class."""

        # Variables used when there's a conflict in the choice of colors for
        # the fibres and nuclei
        self._previous_nuclei_colour = StringVar(
            value=self.settings.nuclei_colour.get())
        self._previous_fibre_colour = StringVar(
            value=self.settings.fibre_colour.get())

        # Variables managing the processing thread
        self._processed_images_count = IntVar(value=0)
        self._img_to_process_count = 0
        self._stop_thread = False
        self._stop_event = Event()
        self._stop_event.set()
        self._queue = Queue(maxsize=0)
        self._thread = Thread(target=self._process_thread)
        self._thread.start()

        # Variables managing the automatic save
        self._auto_save_path = self.projects_path / 'AUTOSAVE'
        self._auto_save_job = None

        self._max_recent_projects = 20  # Maximum number of recent projects
        self._current_project = None  # Path to the current project

    def _set_menu(self) -> NoReturn:
        """Sets the menu bar."""

        # Sets the overall menu bar
        self._menu_bar = Menu(self)
        self.config(menu=self._menu_bar)
        self._menu_bar.config(font=("TKDefaultFont", 12))

        # Sets the file menu
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

        # Sets the settings menu
        self._settings_menu = Menu(self._menu_bar, tearoff=0)
        self._settings_menu.add_command(
            label="Settings", command=partial(Settings_window, self))
        self._menu_bar.add_cascade(label="Settings", menu=self._settings_menu)

        # Sets the help menu
        self._help_menu = Menu(self._menu_bar, tearoff=0)
        self._help_menu.add_command(label="Help", command=self._open_github)
        self._menu_bar.add_cascade(label="Help", menu=self._help_menu)

        # Sets the quit menu
        self._quit_menu = Menu(self._menu_bar, tearoff=0)
        self._quit_menu.add_command(label="Quit", command=self._safe_destroy)
        self._menu_bar.add_cascade(label="Quit", menu=self._quit_menu)

        # Disables the recent project menu if there's no recent project
        if not self._recent_projects:
            self._file_menu.entryconfig("Recent Projects", state='disabled')
            return

        # associate commands with the recent projects items
        for path in self._recent_projects:
            self._recent_projects_menu.add_command(
                label="Load '" + path.name + "'",
                command=partial(self._safe_load, path))

    def _set_layout(self) -> NoReturn:
        """Sets the overall layout of the window."""

        # The main frame of the window
        self._frm = ttk.Frame()
        self._frm.pack(fill='both', expand=True)

        # The frame containing the files table, the buttons and the checkboxes
        self._aux_frame = ttk.Frame(self._frm)
        self._aux_frame.pack(expand=False, fill="both",
                             anchor="e", side='right')

        # The row of buttons
        self._button_frame = ttk.Frame(self._aux_frame)
        self._button_frame.pack(expand=False, fill="x", anchor='n', side='top')

        # The first row of checkboxes
        self._tick_frame_1 = ttk.Frame(self._aux_frame)
        self._tick_frame_1.pack(expand=False, fill="x", anchor='n', side='top')

        # The second row of checkboxes
        self._tick_frame_2 = ttk.Frame(self._aux_frame)
        self._tick_frame_2.pack(expand=False, fill="x", anchor='n', side='top')

        # Creating the buttons
        self._load_button = ttk.Button(self._button_frame, text="Load Images",
                                       command=self._select_images)
        self._load_button.pack(fill="x", anchor="w", side='left', padx=10,
                               pady=5, expand=True)
        self._button_style = ttk.Style()
        self._process_images_button = ttk.Button(self._button_frame,
                                                 text="Process Images",
                                                 command=self._process_images,
                                                 state='disabled')
        self._process_images_button.pack(fill="x", anchor="w", side='left',
                                         padx=10, pady=5, expand=True)
        self._save_button = ttk.Button(self._button_frame, text='Save As',
                                       command=self._save_button_pressed,
                                       state='enabled')
        self._save_button.pack(fill="x", anchor="w", side='left', padx=10,
                               pady=5, expand=True)

        # Creating the checkboxes of the first row
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

        # Creating the checkboxes of the second row
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

        # Label displaying info during image processing
        self._processing_label = ttk.Label(self._aux_frame, text="")
        self._processing_label.pack(anchor="n", side="top", fill='x', padx=3,
                                    pady=5)

    def _save_settings_callback(self, name: str, _, __) -> NoReturn:
        """Saves the settings upon modification of one of them.

        Some settings require a slightly different saving strategy.

        Args:
            name: The name of the setting that was modified.
        """

        if name == 'auto_save_time':
            self._save_settings(autosave_time=True)
        elif name == 'save_altered':
            self._save_settings(enable_save=True)
        else:
            self._save_settings()

    def _save_settings(self,
                       autosave_time: bool = False,
                       enable_save: bool = False) -> NoReturn:
        """Saves the settings and recent projects to .pickle files.

        Args:
            autosave_time: If True, sets the autosave time before saving.
            enable_save: If True, enables the save button
        """

        # Enables the save button if needed
        if enable_save:
            self._save_button['state'] = 'enabled'

        # Set the autosave timer
        if autosave_time:
            self._set_autosave_time()

        # Saving the settings
        settings = {key: value.get() for key, value in
                    self.settings.__dict__.items()}

        if not self._settings_path.is_dir():
            Path.mkdir(self._settings_path)

        with open(self._settings_path /
                  'settings.pickle', 'wb+') as param_file:
            dump(settings, param_file, protocol=4)

        # Saving the recent projects
        with open(self._settings_path /
                  'recent_projects.pickle', 'wb+') as recent_projects_file:
            dump({'recent_projects': [str(path.name) for path in
                                      self._recent_projects]},
                 recent_projects_file, protocol=4)

    def _delete_current_project(self) -> NoReturn:
        """Deletes the current project and all the associated files."""

        if self._current_project is None:
            return

        # Security to prevent unwanted data loss
        ret = messagebox.askyesno('Hold on !',
                                  "Do you really want to delete the current "
                                  "project ?\nThis operation can't be undone.")

        if ret:
            # Simply deletes all the project files
            rmtree(self._current_project)

            # Removes the project from the recent projects
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

            # Creates a new empty project
            self._create_empty_project()

    def _create_empty_project(self) -> NoReturn:
        """Creates a new empty project."""

        # Resets the entire window
        self._files_table.reset()
        self._image_canvas.reset()

        # Sets the buttons and the menu
        self._save_button['state'] = 'enabled'
        self._save_button['text'] = 'Save As'
        self._process_images_button['state'] = 'disabled'
        self._file_menu.entryconfig(self._file_menu.index("Delete Current "
                                                          "Project"),
                                    state="disabled")

        # Sets the title
        self.title("Cellen Tellen - New Project (Unsaved)")
        self._current_project = None

    def _save_project(self, directory: Optional[Path] = None) -> None:
        """Saves a project, its images and the associated data.

        Args:
            directory: The path to the folder where the project should be
                saved.
        """

        # A call without a directory means an autosave
        if directory is None:
            if self.settings.auto_save_time.get() > 0:
                directory = self._auto_save_path
            else:
                return

        # Setting the save button, the project title and the menu entries
        if directory != self._auto_save_path:
            self._set_title_and_button(directory)
            self._add_to_recent_projects(directory)

        # Starting the next autosave job, as the current one ends now
        else:
            self._file_menu.entryconfig("Load Automatic Save", state='normal')
            if self.settings.auto_save_time.get() > 0:
                self._set_autosave_time()

        # Creating the folder if needed
        if not directory.is_dir():
            Path.mkdir(directory, parents=True)

        # Displays a popup indicating the project is being saved
        saving_popup = Save_popup(self, directory)
        sleep(1)

        # Actually saving the project
        save_altered = self.settings.save_altered_images.get() or \
            directory == self._auto_save_path
        self._files_table.save_project(directory, save_altered)

        saving_popup.destroy()

    def _load_project(self, directory: Optional[Path] = None) -> None:
        """Loads a project, its images and its data.

        Args:
            directory: The path to the directory containing the project to
                load.
        """

        # Choose the folder in a dialog window if it wasn't specified
        if directory is None:
            folder = filedialog.askdirectory(
                initialdir=self.projects_path,
                mustexist=True,
                title="Choose a Project Folder")

            if not folder:
                return

            directory = Path(folder)

        # Checking that a valid project was selected
        if not directory.is_dir() or not (directory / 'data.pickle').is_file()\
                or not directory.parent == self.projects_path:
            messagebox.showerror("Error while loading",
                                 "This isn't a valid Cellen-tellen project !")
            return

        # Setting the save button, the project title and the menu entries
        self._set_title_and_button(directory)
        if directory != self._auto_save_path:
            self._add_to_recent_projects(directory)

        # Actually loading the project
        self._files_table.load_project(directory)

        # Enabling the process images button
        if self._files_table.filenames:
            self._process_images_button['state'] = 'enabled'
        else:
            self._process_images_button['state'] = 'disabled'

    def _set_title_and_button(self, directory: Path) -> NoReturn:
        """Sets the project title and the save button when loading or saving
        a project.

        Args:
            directory: The path to the directory where the project is saved.
        """

        # Sets the save button
        self._save_button['state'] = 'disabled'
        self._save_button['text'] = 'Save'

        # Sets the menu
        self._file_menu.entryconfig(
            self._file_menu.index("Delete Current Project"), state="normal")

        # Sets the project name
        self._current_project = directory
        self.title("Cellen Tellen - Project '" + directory.name + "'")

    def _add_to_recent_projects(self, directory: Path) -> NoReturn:
        """Sets the recent project menu entry when loading or saving a project.

        Args:
            directory: The path to the directory where the project is saved.
        """

        # First, remove the project from the recent projects
        if directory in self._recent_projects:
            index = self._recent_projects.index(directory)
            self._recent_projects_menu.delete(index)
            self._recent_projects.remove(directory)

        # Then insert it again, likely in another position
        self._recent_projects_menu.insert_command(
            index=0, label="Load '" + directory.name + "'",
            command=partial(self._safe_load, directory))
        self._recent_projects.insert(0, directory)
        self._file_menu.entryconfig("Recent Projects", state='normal')

        # Remove the last project if there are too many
        if len(self._recent_projects) > self._max_recent_projects:
            self._recent_projects_menu.delete(
                self._recent_projects_menu.index("end"))
            self._recent_projects.pop()

        self._save_settings()

    def _create_warning_window(self) -> bool:
        """Creates a warning window in case the user triggers an action that
        might cause unwanted data loss.

        Also manages the situation when the user tries to exit the program
        while images are being processed.
        """

        # Case when the user tries to exit while computations are running
        if not self._queue.empty():
            ret = messagebox.askyesno(
                'Hold on !',
                "The program is still computing !\n"
                "It is safer to wait for the computation to end.\n"
                "Quit anyway ?\n"
                "(resources may take some time to be released even after "
                "exiting)")

            # Trying to stop the computation if requested
            if ret:
                self._stop_thread = True

            return ret

        # If the project is unsaved, propose to save it
        if self._save_button['state'] == 'enabled' and \
                self._files_table.filenames:

            # Creating the warning window and waiting for the user to choose
            return_var = IntVar()
            warning_window = Warning_window(self, return_var)
            self.wait_variable(return_var)

            # Handling the different possible answers from the user
            ret = return_var.get()
            # The user wants to save and proceed
            if ret == 2:
                warning_window.destroy()
                return self._save_button_pressed()
            # the user wants to proceed without saving
            elif ret == 1:
                warning_window.destroy()
                return True
            # The user cancelled its action
            else:
                return False

        return True

    def _save_button_pressed(self, force_save_as: bool = False) -> bool:
        """Method called when a save action is triggered by the user.

        It may or may not lead to an actual save.

        Args:
            force_save_as: If True, saves the project as a new one even if it
                already has a folder.
        """

        # Asks for a new project name if needed
        if force_save_as or self._current_project is None:
            # Creating a project name window and waiting for the user to choose
            return_var = IntVar()
            name_window = Project_name_window(self, return_var)
            self.wait_variable(return_var)
            ret = return_var.get()
            # A name was given
            if ret:
                name = name_window.return_name()
                name_window.destroy()
                self._save_project(self.projects_path / name)
                return True
            # No name was given
            else:
                return False

        # Perform a normal save otherwise
        else:
            self._save_project(self._current_project)
            return True

    @_save_before_closing
    def _safe_destroy(self) -> None:
        """Stops the computation thread, closes the main window, and displays
        a warning if there's unsaved data."""

        self._stop_thread = True
        sleep(0.5)
        self._thread.join(timeout=1)

        self.destroy()

    @_save_before_closing
    def _safe_empty_project(self) -> None:
        """Creates an empy project, and displays a warning if there's unsaved
        data."""

        self._create_empty_project()

    @_save_before_closing
    def _safe_load(self, path: Optional[Path] = None) -> None:
        """Loads an existing project, and displays a warning if there's unsaved
        data.

        Args:
            path: The path to the project to load.
        """

        self._load_project(path)

    def _disable_buttons(self) -> NoReturn:
        """Disables most of the buttons and menu entries when computing."""

        # Disabling the buttons
        self._load_button['state'] = "disabled"
        self._save_button['state'] = "disabled"

        # Disabling the menu entries
        self._file_menu.entryconfig("Load Automatic Save", state='disabled')
        self._file_menu.entryconfig("Recent Projects", state='disabled')
        self._file_menu.entryconfig("Delete Current Project", state="disabled")
        self._file_menu.entryconfig("Save Project As", state="disabled")
        self._file_menu.entryconfig("New Empty Project", state="disabled")
        self._file_menu.entryconfig("Load From Explorer", state="disabled")

        # Disables the file table close buttons
        self._files_table.enable_close_buttons(False)

    def _enable_buttons(self) -> NoReturn:
        """Re-enables the buttons and menu entries once processing is over."""

        # Re-enabling buttons
        self._load_button['state'] = "enabled"
        self.set_unsaved_status()
        self._set_indicators()

        # Re-enabling menu entries
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

        # Re-enabling the file table close buttons
        self._files_table.enable_close_buttons(True)

    def _stop_processing(self, force: bool = True) -> None:
        """Empties the queue of images waiting for processing, and waits for
        the already started computation to end.

        This method is called when the user clicks on the Stop Processing
        button of the GUI. It is also called regularly by the processing thread
        so that the GUI gets back to normal operation mode once the last image
        has been processed.

        Args:
            force: If False, means that this method is called from the
                processing thread and won't have any effect unless the last
                image was just computed. If True, it is called by the user and
                will have effect.
        """

        # If called from the thread and there are images left to process, abort
        if not force and not self._queue.empty():
            return

        # If called from the thread but GUI already back to normal, abort
        if not force and self._stop_event.is_set():
            return

        # Sends a stop signal to the processing thread
        self._stop_event.set()

        # Wait for the job queue to be empty and then resets the GUI
        if force:
            self._processing_label['text'] = "Stopping"
            self._process_images_button["state"] = 'disabled'
            i = 1
            while not self._queue.empty():
                self.update()
                # Indicating the user how many processes are left
                self._processing_label[
                    'text'] = f"Stopping {'.' * (i % 4)}{' ' * (4 - i % 4)}" \
                              f"(waiting for the current computation to " \
                              f"finish)"
                i += 1
                sleep(0.5)

        # Cleaning up the buttons and variables related to processing
        self._processed_images_count.set(0)
        self._img_to_process_count = 0
        self._process_images_button["state"] = 'enabled'
        self._process_images_button['text'] = "Process Images"
        self._process_images_button.configure(command=self._process_images)
        self._processing_label['text'] = ""

        # Putting the interface back into normal operation state
        self._enable_buttons()
        self.set_unsaved_status()

    def _process_images(self) -> NoReturn:
        """Prepares the interface and then sends to images to process to the
        processing thread."""

        # Getting the names of the images to process
        file_names = self._files_table.filenames

        # Setting the buttons and variables related to processing
        self._processed_images_count.set(0)
        self._img_to_process_count = len(file_names)
        self._process_images_button['text'] = 'Stop Processing'
        self._process_images_button.configure(command=self._stop_processing)
        self._processing_label['text'] = f"0 of {len(file_names)} Images " \
                                         f"Processed "

        # Disabling most of the buttons and menu entries
        self._disable_buttons()
        self.update()

        # Sending the jobs to the processing thread
        self._stop_event.clear()
        for file in file_names:
            self._queue.put_nowait(
                (file,
                 self.settings.nuclei_colour.get(),
                 self.settings.fibre_colour.get(),
                 self.settings.fibre_threshold.get(),
                 self.settings.small_objects_threshold.get()))

    def _process_thread(self) -> None:
        """"""

        # Looping forever until the stop_thread flag is raised
        while not self._stop_thread:

            # If the stop_event is set, we just have to discard all the jobs
            if self._stop_event.is_set():
                while not self._queue.empty():
                    try:
                        self._queue.get_nowait()
                    except Empty:
                        pass

                sleep(1)

            # Case when there are jobs to handle
            elif not self._queue.empty():
                # Acquiring the next job in the queue
                try:
                    path, nuclei_color, fibre_color, fibre_threshold, \
                        small_objects_threshold = self._queue.get_nowait()
                except Empty:
                    sleep(1)
                    continue

                # Not processing if the user wants to stop the computation
                if self._stop_event.is_set():
                    continue

                try:
                    # Now processing the image
                    file, nuclei_out, nuclei_in, fibre_contours, area = \
                        self._segmentation(path,
                                           nuclei_color,
                                           fibre_color,
                                           fibre_threshold,
                                           small_objects_threshold)

                    # Not updating if the user wants to stop the computation
                    if self._stop_event.is_set():
                        continue

                    # Updating the image data with the result of the processing
                    self._files_table.input_processed_data(nuclei_out,
                                                           nuclei_in,
                                                           fibre_contours,
                                                           area, file)

                    # Updating the processed images count
                    self._processed_images_count.set(
                        self._processed_images_count.get() + 1)

                # Displaying any error in an error window
                except (Exception,) as exc:
                    messagebox.showerror("Error !",
                                         f"An error occurred while processing "
                                         f"the images !\nError : {exc}")

            # To lazily get the GUI back to normal once all the jobs are
            # completed
            else:
                self._stop_processing(force=False)
                sleep(1)

    def _update_processed_images(self, _, __, ___) -> NoReturn:
        """Updates the display of the processed images count."""

        processed = self._processed_images_count.get()
        if processed:
            self._processing_label['text'] = f"{processed} of " \
                                             f"{self._img_to_process_count} " \
                                             f"Images Processed"

    def _select_images(self) -> NoReturn:
        """Opens a dialog window for selecting the images to load, then adds
        them in the files table."""

        # Getting the file names
        file_names = filedialog.askopenfilenames(
            filetypes=[('Image Files', ('.tif', '.png', '.jpg', '.jpeg',
                                        '.bmp', '.hdr'))],
            parent=self, title='Please select a directory')

        if file_names:
            file_names = [Path(path) for path in file_names]

            # Enables the process images button
            self._process_images_button["state"] = 'enabled'

            # Adds the images to the table
            self._files_table.add_images(file_names)
            self.set_unsaved_status()

    def _set_autosave_time(self) -> NoReturn:
        """Schedules a save job according to the selected autosave time."""

        # Cancels any previous autosave job
        if self._auto_save_job is not None:
            self.after_cancel(self._auto_save_job)
        self._auto_save_job = None

        # Schedule a new autosave job
        if self.settings.auto_save_time.get() > 0:
            self._auto_save_job = self.after(self.settings.auto_save_time.get()
                                             * 1000, self._save_project)

    def _set_image_channels(self) -> NoReturn:
        """Redraws the current image with the selected channels."""

        self._image_canvas.show_image()
        self._save_settings()

    def _set_indicators(self) -> NoReturn:
        """Updates the display of fibres and nuclei according to the user
        selection."""
        
        # Updating the display
        self._image_canvas.set_indicators()
        self._save_settings()

    def _nuclei_colour_sel(self, _, __, ___) -> NoReturn:
        """Ensures there's no conflict in the chosen image channels for fibres
        and nuclei."""

        # Sets one of the channels back to its previous value in case of
        # conflict
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

        # Sets the previous values variables
        self._previous_nuclei_colour.set(self.settings.nuclei_colour.get())
        self._previous_fibre_colour.set(self.settings.fibre_colour.get())

        # Finally, save and redraw the nuclei and fibers
        self._save_settings()
        self._image_canvas.set_indicators()

    @staticmethod
    def _open_github() -> NoReturn:
        """Opens the project repository in a browser."""

        open_new("https://github.com/WeisLeDocto/Cellen-Tellen")
