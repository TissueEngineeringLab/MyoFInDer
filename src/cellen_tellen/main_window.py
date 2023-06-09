# coding: utf-8

from tkinter import ttk, filedialog, Tk, IntVar, PhotoImage, Menu, StringVar, \
    messagebox, Checkbutton, BooleanVar
from platform import system, release
from shutil import rmtree
from webbrowser import open_new
from threading import Thread, Event
from queue import Empty, Queue
from time import sleep
from pickle import load, dump
from functools import partial, wraps
from pathlib import Path
from typing import Callable, Optional
import logging

from .tools import Settings
from .tools import Save_popup
from .tools import Warning_window
from .tools import Settings_window
from .tools import Splash_window
from .tools import check_project_name
from .files_table import Files_table
from .image_canvas import Image_canvas

# Sets a better resolution on recent Windows platforms
if system() == "Windows" and int(release()) >= 8:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(True)

# Todo:
#   Set up unit tests


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

        # Setting the logger
        self._logger = logging.getLogger("Cellen-Tellen.MainWindow")

        # Sets the different paths used in the project
        self.base_path = Path(__file__).parent
        if Path(__file__).name.endswith(".pyc"):
            self.base_path = self.base_path.parent
        self.log(f"Base path for the project: {str(self.base_path)}")
        self.projects_path = self.base_path.parent / 'Projects'
        self._settings_path = self.base_path / 'settings'

        # Generates a splash window while waiting for the modules to load
        self.log("Creating the splash window")
        splash = Splash_window()
        self.log("Centering the splash window")
        splash.resize_image()
        self.log("Displaying the splash window")
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
        self.log("Setting the application icon")
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
        self.log("Creating the image canvas")
        self._image_canvas = Image_canvas(self._frm, self)
        self.log("Creating the files table")
        self._files_table = Files_table(self._aux_frame,
                                        self.projects_path,
                                        self)
        self._image_canvas.nuclei_table = self._files_table
        self._files_table.image_canvas = self._image_canvas

        self._save_settings()

        # Finishes the initialization and starts the event loop
        self.update()
        self.log("Setting the main windows's bindings and protocols")
        self.bind_all('<Control-s>', self._save_button_pressed)
        self.protocol("WM_DELETE_WINDOW", self._safe_destroy)

    def set_unsaved_status(self) -> None:
        """Sets the title and save button when a project is modified."""

        self.log("Setting the unsaved status")

        if self._current_project is not None:
            self.title(f"Cellen Tellen - Project "
                       f"'{self._current_project.name}' (Unsaved)")
            self._save_button['state'] = 'enabled'
            self._save_button['text'] = 'Save'
        else:
            self.title("Cellen Tellen - New Project (Unsaved)")
            self._save_button['state'] = 'enabled'
            self._save_button['text'] = 'Save As'

    def update_master_check(self) -> None:
        """Updates the master checkbox according to the states of the
        checkboxes of all the files menu entries."""

        self._master_check_var.set(self._files_table.all_checked)

    def log(self, msg: str) -> None:
        """Wrapper for reducing the verbosity of logging."""

        # For some reason the processing adds a handler to the root logger
        root = self._logger.parent.parent
        while root.hasHandlers():
            root.removeHandler(root.handlers[0])

        self._logger.log(logging.INFO, msg)

    def _load_settings(self) -> None:
        """Loads the settings from the settings file if any, otherwise sets
        them to default."""

        # Gets the settings from the settings.pickle file
        settings_file = self._settings_path / 'settings.pickle'
        if settings_file.is_file():
            self.log(f"Loading the settings file from {settings_file}")
            with open(settings_file, 'rb') as param_file:
                settings = load(param_file)
        else:
            self.log("No setting file detected, loading the default settings")
            settings = dict()

        # Creates a Settings instance and sets the values
        self.settings = Settings()  # The default values are preset in Settings
        self.settings.update(settings)
        self.log(f"Settings values: {str(self.settings)}")

        # Gets the recent projects from the recent_projects.pickle file
        projects_file = self._settings_path / 'recent_projects.pickle'
        if projects_file.is_file():
            self.log(f"Loading the recent projects file from {projects_file}")
            with open(projects_file, 'rb') as recent_projects:
                recent = load(recent_projects)

            # Only the names are stored, the path must be completed
            # Here we also make sure that the projects are valid
            self._recent_projects = [
                self.projects_path / proj for proj in recent['recent_projects']
                if proj
                and (self.projects_path / proj).is_dir()
                and (self.projects_path / proj / 'data.pickle').is_file()]
            self._recent_projects = list(dict.fromkeys(self._recent_projects))
            self.log(f"Recent projects: "
                     f"{', '.join(map(str, self._recent_projects))}")
        else:
            self.log("No recent projects file detected")
            self._recent_projects = []

        # Finally, saving the recent projects and the settings
        self._save_settings()

    def _set_traces(self) -> None:
        """Sets the callbacks triggered upon modification of the settings."""

        self.log("Setting the main windows's traces")

        # Making sure there's no conflict between the nuclei and fibres colors
        self.settings.fibre_colour.trace_add("write", self._nuclei_colour_sel)
        self.settings.nuclei_colour.trace_add("write", self._nuclei_colour_sel)

        # Simply saving the settings upon modification
        self.settings.save_altered_images.trace_add(
            "write", self._save_settings_callback)
        self.settings.fibre_threshold.trace_add("write",
                                                self._save_settings_callback)
        self.settings.nuclei_threshold.trace_add("write",
                                                 self._save_settings_callback)
        self.settings.small_objects_threshold.trace_add(
            "write", self._save_settings_callback)

        # Updates the display when an image has been processed
        self._processed_images_count.trace_add("write",
                                               self._update_processed_images)

    def _set_variables(self) -> None:
        """Sets the different variables used in the class."""

        self.log("Setting the main windows's variables")

        # Variables used when there's a conflict in the choice of colors for
        # the fibres and nuclei
        self._previous_nuclei_colour = StringVar(
            value=self.settings.nuclei_colour.get())
        self._previous_fibre_colour = StringVar(
            value=self.settings.fibre_colour.get())

        # The variables associated with the master checkbox
        self._master_check_var = BooleanVar(value=True)

        # Variables managing the processing thread
        self._processed_images_count = IntVar(value=0)
        self._img_to_process_count = 0
        self._stop_thread = False
        self._stop_event = Event()
        self._stop_event.set()
        self._queue = Queue(maxsize=0)
        self._thread = Thread(target=self._process_thread)
        self._thread.start()

        self._max_recent_projects = 20  # Maximum number of recent projects
        self._current_project = None  # Path to the current project

    def _set_menu(self) -> None:
        """Sets the menu bar."""

        self.log("Setting the main windows's menu bar")

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
                label=f"Load '{path.name}'",
                command=partial(self._safe_load, path))

    def _set_layout(self) -> None:
        """Sets the overall layout of the window."""

        self.log("Setting the main windows's layout")

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

        self._text_button_frame = ttk.Frame(self._aux_frame)
        self._text_button_frame.pack(anchor="n", side="top", fill='x', padx=3,
                                     pady=5)

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
        self._processing_label = ttk.Label(self._text_button_frame, text="")
        self._processing_label.pack(anchor="w", side="left", fill='x',
                                    padx=(9, 0))

        self._delete_all_button = ttk.Button(self._text_button_frame,
                                             text='X', width=2,
                                             command=self._delete_many_files)
        self._delete_all_button.pack(anchor="e", side="right", fill='none',
                                     padx=(0, 15))

        self._check_img = PhotoImage(width=1, height=1)
        self._select_all_button = Checkbutton(self._text_button_frame,
                                              image=self._check_img,
                                              width=6, height=24,
                                              command=self._invert_checkboxes,
                                              variable=self._master_check_var)
        self._select_all_button.pack(anchor="e", side="right", fill='none')

    def _save_settings_callback(self, name: str, _, __) -> None:
        """Saves the settings upon modification of one of them.

        Some settings require a slightly different saving strategy.

        Args:
            name: The name of the setting that was modified.
        """

        if name == 'save_altered':
            self._save_settings(enable_save=True)
        else:
            self._save_settings()

    def _save_settings(self,
                       enable_save: bool = False) -> None:
        """Saves the settings and recent projects to .pickle files.

        Args:
            enable_save: If True, enables the save button
        """

        # Enables the save button if needed
        if enable_save:
            self._save_button['state'] = 'enabled'

        # Saving the settings
        settings = {key: value.get() for key, value
                    in vars(self.settings).items()}
        self.log(f"Settings values: {str(self.settings)}")

        if not self._settings_path.is_dir():
            self.log(f"Created the Settings folder at: {self._settings_path}")
            Path.mkdir(self._settings_path)

        settings_file = self._settings_path / 'settings.pickle'
        with open(settings_file, 'wb+') as param_file:
            dump(settings, param_file, protocol=4)
            self.log(f"Saved the settings at: {settings_file}")

        # Saving the recent projects
        projects_file = self._settings_path / 'recent_projects.pickle'
        with open(projects_file, 'wb+') as recent_projects_file:
            dump({'recent_projects': [str(path.name) for path in
                                      self._recent_projects]},
                 recent_projects_file, protocol=4)
            self.log(f"Saved the recent projects at: {projects_file}")

    def _delete_current_project(self) -> None:
        """Deletes the current project and all the associated files."""

        self.log("User requested deletion of the current project")

        if self._current_project is None:
            self.log("No current project to delete")
            return

        # Security to prevent unwanted data loss
        ret = messagebox.askyesno('Hold on !',
                                  "Do you really want to delete the current "
                                  "project ?\nThis operation can't be undone.")

        if ret:
            self.log("User approved deletion of current project")

            # Simply deletes all the project files
            rmtree(self._current_project)
            self.log("Deleted the files of the current project")

            # Removes the project from the recent projects
            index = self._recent_projects.index(self._current_project)
            self._recent_projects_menu.delete(index)
            self._recent_projects.remove(self._current_project)
            self.log("Removed current project from the recent projects")

            if not self._recent_projects:
                self._file_menu.entryconfig("Recent Projects",
                                            state='disabled')
            self._save_settings()

            # Creates a new empty project
            self._create_empty_project()

        else:
            self.log("User aborted deletion of current project")

    def _create_empty_project(self) -> None:
        """Creates a new empty project."""

        self.log("Creating an empty project")

        # Resets the entire window
        self._files_table.table_items.reset()
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

    def _save_project(self, directory: Path) -> None:
        """Saves a project, its images and the associated data.

        Args:
            directory: The path to the folder where the project should be
                saved.
        """

        # Setting the save button, the project title and the menu entries
        self._set_title_and_button(directory)
        self._add_to_recent_projects(directory)

        # Creating the folder if needed
        if not directory.is_dir():
            self.log(f"Creating the directory where to save the "
                     f"project at {directory}")
            Path.mkdir(directory, parents=True)

        # Displays a popup indicating the project is being saved
        saving_popup = Save_popup(self, directory)
        sleep(1)

        # Actually saving the project
        save_altered = self.settings.save_altered_images.get()
        self._files_table.save_project(directory, save_altered)
        self.log(f"Project saved at {directory}")

        saving_popup.destroy()

    def _load_project(self, directory: Optional[Path] = None) -> None:
        """Loads a project, its images and its data.

        Args:
            directory: The path to the directory containing the project to
                load.
        """

        if directory is not None:
            self.log(f"Project loading requested by the user at {directory}")
        else:
            self.log("Project loading requested by the user")

        # Choose the folder in a dialog window if it wasn't specified
        if directory is None:
            folder = filedialog.askdirectory(
                initialdir=self.projects_path,
                mustexist=True,
                title="Choose a Project Folder")

            if not folder:
                self.log("Project loading aborted bu the user")
                return

            directory = Path(folder)
            self.log(f"User requested to load project {directory}")

        # Checking that a valid project was selected
        if not directory.is_dir() or not (directory / 'data.pickle').is_file()\
                or not directory.parent == self.projects_path:
            messagebox.showerror("Error while loading",
                                 "This isn't a valid Cellen-tellen project !")
            self.log("The selected directory is not valid for loading into "
                     "Cellen-Tellen")
            return

        # Setting the save button, the project title and the menu entries
        self._set_title_and_button(directory)
        self._add_to_recent_projects(directory)

        # Actually loading the project
        self.log(f"Loading the project {directory}")
        self._files_table.load_project(directory)

        # Enabling the process images button
        if self._files_table.table_items:
            self._process_images_button['state'] = 'enabled'
        else:
            self._process_images_button['state'] = 'disabled'

    def _set_title_and_button(self, directory: Path) -> None:
        """Sets the project title and the save button when loading or saving
        a project.

        Args:
            directory: The path to the directory where the project is saved.
        """

        self.log("Setting the title and buttons of the main window")

        # Sets the save button
        self._save_button['state'] = 'disabled'
        self._save_button['text'] = 'Save'

        # Sets the menu
        self._file_menu.entryconfig(
            self._file_menu.index("Delete Current Project"), state="normal")

        # Sets the project name
        self._current_project = directory
        self.title(f"Cellen Tellen - Project '{directory.name}'")

    def _add_to_recent_projects(self, directory: Path) -> None:
        """Sets the recent project menu entry when loading or saving a project.

        Args:
            directory: The path to the directory where the project is saved.
        """

        self.log(f"Adding {directory} to the recent projects")

        # First, remove the project from the recent projects
        if directory in self._recent_projects:
            index = self._recent_projects.index(directory)
            self._recent_projects_menu.delete(index)
            self._recent_projects.remove(directory)

        # Then insert it again, likely in another position
        self._recent_projects_menu.insert_command(
            index=0, label=f"Load '{directory.name}'",
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

        self.log("Checking if it is necessary to create a warning window")

        # Case when the user tries to exit while computations are running
        if not self._queue.empty():
            self.log("Processing queue not empty")
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
                self.log("User requested the computation to stop")
            else:
                self.log("User canceled the action")

            return ret

        # If the project is unsaved, propose to save it
        if self._save_button['state'] == 'enabled' and \
                self._files_table.table_items:

            self.log("The project is unsaved")

            # Creating the warning window and waiting for the user to choose
            return_var = IntVar()
            warning_window = Warning_window(self, return_var)
            self.wait_variable(return_var)

            # Handling the different possible answers from the user
            ret = return_var.get()
            # The user wants to save and proceed
            if ret == 2:
                self.log("User requested to save the project and proceed")
                warning_window.destroy()
                return self._save_button_pressed()
            # the user wants to proceed without saving
            elif ret == 1:
                warning_window.destroy()
                self.log("User requested to proceed anyway without saving")
                return True
            # The user cancelled its action
            else:
                self.log("User requested to cancel the action")
                return False

        self.log("No warning window required")
        return True

    def _save_button_pressed(self, _: Optional[Event] = None,
                             force_save_as: bool = False) -> bool:
        """Method called when a save action is triggered by the user or when
        CTRL+S is hit.

        It may or may not lead to an actual save.

        Args:
            force_save_as: If True, saves the project as a new one even if it
                already has a folder.
        """

        self.log("The user requested to save the current project")

        # Asks for a new project name if needed
        if force_save_as or self._current_project is None:
            save = False
            path = None

            # Letting the user choose a path for saving the project
            while not save:
                # Ask for a project name and location
                path = filedialog.asksaveasfilename(
                    confirmoverwrite=False, defaultextension=None,
                    initialdir=Path.cwd(), title='Saving Current Project')
                # The user can exit by pressing the cancel button
                if not path:
                    self.log("The user aborted the save action")
                    return False
                # Checking the validity of the chosen path
                path = Path(path)
                save = check_project_name(path)

            self.log(f"Saving the project to {path}")
            self._save_project(path)
            return True

        # Perform a normal save otherwise
        else:
            self.log(f"Saving the project to {self._current_project}")
            self._save_project(self._current_project)
            return True

    @_save_before_closing
    def _safe_destroy(self) -> None:
        """Stops the computation thread, closes the main window, and displays
        a warning if there's unsaved data."""

        self.log("Requesting the processing thread to finish")
        self._stop_thread = True
        sleep(0.5)
        self.log("Waiting for the processing thread to finish")
        self._thread.join(timeout=1)

        if self._thread.is_alive():
            self.log("ERROR! The processing thread is still alive !")
        else:
            self.log("The processing thread terminated as excepted")

        self.log("Destroying the main window")
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

    def _disable_buttons(self) -> None:
        """Disables most of the buttons and menu entries when computing."""

        self.log("Disabling the buttons")

        # Disabling the buttons
        self._load_button['state'] = "disabled"
        self._save_button['state'] = "disabled"
        self._select_all_button['state'] = 'disabled'
        self._delete_all_button['state'] = 'disabled'

        # Disabling the menu entries
        self._file_menu.entryconfig("Recent Projects", state='disabled')
        self._file_menu.entryconfig("Delete Current Project", state="disabled")
        self._file_menu.entryconfig("Save Project As", state="disabled")
        self._file_menu.entryconfig("New Empty Project", state="disabled")
        self._file_menu.entryconfig("Load From Explorer", state="disabled")

        # Disables the file table close buttons
        self._files_table.enable_buttons(False)

    def _enable_buttons(self) -> None:
        """Re-enables the buttons and menu entries once processing is over."""

        self.log("Enabling the buttons")

        # Re-enabling buttons
        self._load_button['state'] = "enabled"
        self._select_all_button['state'] = 'normal'
        self._delete_all_button['state'] = 'enabled'
        self.set_unsaved_status()
        self._set_indicators()

        # Re-enabling menu entries
        if self._recent_projects:
            self._file_menu.entryconfig("Recent Projects", state='normal')
        if self._current_project is not None:
            self._file_menu.entryconfig("Delete Current Project",
                                        state='normal')
        self._file_menu.entryconfig("Save Project As", state="normal")
        self._file_menu.entryconfig("New Empty Project", state="normal")
        self._file_menu.entryconfig("Load From Explorer", state="normal")

        # Re-enabling the file table close buttons
        self._files_table.enable_buttons(True)

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
        self.log("End of processing requested, setting the stop event")
        self._stop_event.set()

        # Wait for the job queue to be empty and then resets the GUI
        if force:
            self._processing_label['text'] = "Stopping"
            self._process_images_button["state"] = 'disabled'
            i = 1
            while not self._queue.empty():
                self.log("Processing queue not empty, waiting for the thread "
                         "to stop processing")
                self.update()
                # Indicating the user how many processes are left
                self._processing_label[
                    'text'] = f"Stopping {'.' * (i % 4)}{' ' * (4 - i % 4)}" \
                              f"(waiting for the current computation to " \
                              f"finish)"
                i += 1
                sleep(0.5)

        # Cleaning up the buttons and variables related to processing
        self.log("Cleaning up the processing-related objects")
        self._processed_images_count.set(0)
        self._img_to_process_count = 0
        self._process_images_button["state"] = 'enabled'
        self._process_images_button['text'] = "Process Images"
        self._process_images_button.configure(command=self._process_images)
        self._processing_label['text'] = ""

        # Putting the interface back into normal operation state
        self._enable_buttons()
        self.set_unsaved_status()

    def _process_images(self) -> None:
        """Prepares the interface and then sends to images to process to the
        processing thread."""

        self.log("User requested the images to be processed")

        # Getting the names of the images to process
        file_names = self._files_table.checked_files

        # If all checkboxes are unchecked, do nothing
        if not file_names:
            self.log("No images to process, aborting")
            return

        self.log(f"Processing the images: {', '.join(map(str, file_names))}")

        # Setting the buttons and variables related to processing
        self.log("Setting up the processing-related objects")
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
        self.log("Sending the jobs to the processing thread")
        for file in file_names:
            self._queue.put_nowait(
                (file,
                 self.settings.nuclei_colour.get(),
                 self.settings.fibre_colour.get(),
                 self.settings.fibre_threshold.get(),
                 self.settings.nuclei_threshold.get(),
                 self.settings.small_objects_threshold.get()))

    def _process_thread(self) -> None:
        """Main loop of the thread in charge of processing the images.

        Discards all the received jobs when the stop event is set.
        Otherwise, handles sequentially all the received jobs until the job
        queue is exhausted or until told to stop.
        Also periodically calls stop_processing so that the interface is rest
        after the last job in the queue was handled.
        """

        self.log("Starting the processing thread")

        # Looping forever until the stop_thread flag is raised
        while not self._stop_thread:

            # If the stop_event is set, we just have to discard all the jobs
            if self._stop_event.is_set():
                while not self._queue.empty():
                    self.log("Emptying the processing queue after the stop "
                             "event was set")
                    try:
                        self._queue.get_nowait()
                    except Empty:
                        pass

                sleep(1)

            # Case when there are jobs to handle
            elif not self._queue.empty():
                # Acquiring the next job in the queue
                try:
                    job = self._queue.get_nowait()
                    path, nuclei_color, fibre_color, fibre_threshold, \
                        nuclei_threshold, small_objects_threshold = job
                    self.log(f"Processing thread received job: "
                             f"{', '.join(map(str, job))}")
                except Empty:
                    sleep(1)
                    continue

                # Not processing if the user wants to stop the computation
                if self._stop_event.is_set():
                    self.log("Stop event was set, aborting processing")
                    continue

                try:
                    # Now processing the image
                    file, nuclei_out, nuclei_in, fibre_contours, area = \
                        self._segmentation(path,
                                           nuclei_color,
                                           fibre_color,
                                           fibre_threshold,
                                           nuclei_threshold,
                                           small_objects_threshold)
                    self.log(f"Segmentation returned file: {file}, "
                             f"nuclei out: {len(nuclei_out)}, "
                             f"nuclei in: {len(nuclei_in)}, "
                             f"fibre contours: {len(fibre_contours)}, "
                             f"area: {area}")

                    # Not updating if the user wants to stop the computation
                    if self._stop_event.is_set():
                        continue

                    # Updating the image data with the result of the processing
                    self.log("Passing precessed data to the files table")
                    self._files_table.input_processed_data(nuclei_out,
                                                           nuclei_in,
                                                           fibre_contours,
                                                           area, file)

                # Displaying any error in an error window
                except (Exception,) as exc:
                    messagebox.showerror("Error !",
                                         f"An error occurred while processing "
                                         f"the images !\nError : {exc}")
                    self._logger.exception("Exception caught wile processing "
                                           "image", exc_info=exc)

                # Updating the processed images count
                finally:
                    self._processed_images_count.set(
                        self._processed_images_count.get() + 1)

            # To lazily get the GUI back to normal once all the jobs are
            # completed
            else:
                self.log("Processing queue empty, requesting to stop the "
                         "processing")
                self._stop_processing(force=False)
                sleep(1)

        self.log("Processing thread finished")

    def _update_processed_images(self, _, __, ___) -> None:
        """Updates the display of the processed images count."""

        processed = self._processed_images_count.get()
        if processed:
            self._processing_label['text'] = f"{processed} of " \
                                             f"{self._img_to_process_count} " \
                                             f"Images Processed"

    def _select_images(self) -> None:
        """Opens a dialog window for selecting the images to load, then adds
        them in the files table."""

        self.log("Load button clicked by the user")

        # Getting the file names
        file_names = filedialog.askopenfilenames(
            filetypes=[('Image Files', ('.tif', '.png', '.jpg', '.jpeg',
                                        '.bmp', '.hdr'))],
            parent=self, title='Please select a directory')

        if file_names:
            file_names = [Path(path) for path in file_names]
            self.log(f"User requested to load the images: "
                     f"{', '.join(map(str, file_names))}")

            # Enables the process images button
            self._process_images_button["state"] = 'enabled'

            # Adds the images to the table
            self._files_table.add_images(file_names)
            self.set_unsaved_status()

        else:
            self.log("No files selected by the user, aborting")

    def _set_image_channels(self) -> None:
        """Redraws the current image with the selected channels."""

        self.log("Setting the image channels to display")
        self._image_canvas.show_image()
        self._save_settings()

    def _set_indicators(self) -> None:
        """Updates the display of fibres and nuclei according to the user
        selection."""
        
        # Updating the display
        self.log("Setting the image indicators to display")
        self._image_canvas.set_indicators()
        self._save_settings()

    def _nuclei_colour_sel(self, _, __, ___) -> None:
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

    def _invert_checkboxes(self) -> None:
        """Called when clicking on the master checkbox.

        If all the boxes are checked, unchecks them all, otherwise checks them
        all.
        """

        self.log("Inverting all the checkboxes")

        if self._files_table.all_checked:
            for item in self._files_table.table_items:
                item.graph_elt.button_var.set(False)
        else:
            for item in self._files_table.table_items:
                item.graph_elt.button_var.set(True)

    def _delete_many_files(self) -> None:
        """Called when hitting the master delete button.

        Deletes all the files in the files table whose checkboxes are checked.
        """

        self.log("Delete all button clicked by the user")

        # Getting the list of files to delete, and checking it's not empty
        to_delete = self._files_table.checked_files
        if not to_delete:
            self.log("No file to delete, aborting")
            return

        # Actually deleting the files
        self.log(f"Deleting the files: {', '.join(map(str, to_delete))}")
        self._files_table.delete_image(tuple(to_delete))

    def _open_github(self) -> None:
        """Opens the project repository in a browser."""

        self.log("Opening the online documentation")
        open_new("https://github.com/WeisLeDocto/Cellen-Tellen")