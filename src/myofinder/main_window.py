# coding: utf-8

from tkinter import ttk, filedialog, Tk, IntVar, PhotoImage, Menu, StringVar, \
    messagebox, Checkbutton, BooleanVar
from platform import system
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
import importlib.resources as resources

from .tools import Settings
from .tools import SavePopup
from .tools import WarningWindow
from .tools import SettingsWindow
from .tools import SplashWindow
from .tools import check_project_name
from .files_table import FilesTable
from .image_canvas import ImageCanvas

# Sets a better resolution on recent Windows platforms
if system() == "Windows":
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(True)


def _save_before_closing(func: Callable) -> Callable:
    """Decorator for warning the user when an action that may cause unwanted
    data loss is triggered.

    The user will then be proposed to save the work, continue anyway, or abort.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """The warning window will return False if the operation shouldn't be
        carried on"""

        if self._create_warning_window():
            func(self, *args, **kwargs)
    return wrapper


class MainWindow(Tk):
    """The main window of the MyoFInDer software.

    It manages all the buttons, menus, events, and the secondary windows.
    """

    def __init__(self, app_folder: Optional[Path]) -> None:
        """Creates the splash window, then the main window, sets the layout and
        the callbacks.

        Args:
            app_folder: The Path to the application folder.
        """

        # Setting the logger
        self._logger = logging.getLogger("MyoFInDer.MainWindow")

        # Generates a splash window while waiting for the modules to load
        self.log("Creating the splash window")
        splash = SplashWindow()
        self.log("Centering the splash window")
        splash.resize_image()
        self.log("Displaying the splash window")
        self._segmentation = splash.display()
        splash.destroy()

        # Initializes the main window
        super().__init__()
        self.title("MyoFInDer - New Project (Unsaved)")
        if system() in ("Windows", "Darwin"):
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)
        self.app_folder = app_folder

        # Sets the application icon
        self.log("Setting the application icon")
        ref = resources.files('myofinder') / 'app_images' / 'project_icon.png'
        with resources.as_file(ref) as path:
            icon = PhotoImage(file=str(path))
        self.iconphoto(False, icon)  # Without it the icon is buggy in Windows
        self.iconphoto(True, icon)

        # Sets the settings, variables, callbacks, menus and layout
        self._set_variables()
        self._set_traces()
        self._set_menu()
        self._set_layout()

        # Sets the image canvas and the files table
        self.log("Creating the image canvas")
        self._image_canvas = ImageCanvas(self._frm, self)
        self.log("Creating the files table")
        self._files_table = FilesTable(self._aux_frame, self)
        self._image_canvas.nuclei_table = self._files_table
        self._files_table.image_canvas = self._image_canvas

        # Loading the previous setting if applicable
        if self.app_folder is not None:
            if (self.app_folder / 'settings.pickle').exists():
                self._load_settings(self.app_folder)

        # Finishes the initialization and starts the event loop
        self.update()
        self.log("Setting the main windows's bindings and protocols")
        self.bind_all('<Control-s>', self._save_button_pressed)
        self.protocol("WM_DELETE_WINDOW", self.safe_destroy)

    def set_unsaved_status(self) -> None:
        """Sets the title and save button when a project is modified."""

        self.log("Setting the unsaved status")

        if self._current_project is not None:
            self.title(f"MyoFInDer - Project "
                       f"'{self._current_project.name}' (Unsaved)")
            self._save_button['state'] = 'enabled'
            self._save_button['text'] = 'Save'
        else:
            self.title("MyoFInDer - New Project (Unsaved)")
            self._save_button['state'] = 'enabled'
            self._save_button['text'] = 'Save As'

    def save_settings(self, project_path: Path) -> None:
        """Saves the settings to a settings.pickle file.

        Args:
            project_path: The Path where the project will be saved.
        """

        # Saving the settings
        self.log(f"Settings values: {str(self.settings)}")
        settings_file = project_path / 'settings.pickle'
        with open(settings_file, 'wb+') as param_file:
            dump(self.settings.get_all(), param_file, protocol=4)
            self.log(f"Saved the settings at: {settings_file}")

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

    @_save_before_closing
    def safe_destroy(self) -> None:
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

    def _set_variables(self) -> None:
        """Sets the different variables used in the class."""

        self.log("Setting the main windows's variables")

        self.settings = Settings()
        self._settings_window: Optional[SettingsWindow] = None

        # Variables used when there's a conflict in the choice of colors for
        # the fibers and nuclei
        self._previous_nuclei_colour = StringVar(
            value=self.settings.nuclei_colour.get())
        self._previous_fiber_colour = StringVar(
            value=self.settings.fiber_colour.get())

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

        self._current_project: Optional[Path] = None  # Path to current project

    def _set_traces(self) -> None:
        """Sets the callbacks triggered upon modification of the settings."""

        self.log("Setting the main windows's traces")

        # Making sure there's no conflict between the nuclei and fibers colors
        self.settings.fiber_colour.trace_add("write", self._nuclei_colour_sel)
        self.settings.nuclei_colour.trace_add("write", self._nuclei_colour_sel)

        # Some settings should enable the save button when modified
        self.settings.save_overlay.trace_add(
            "write", self._enable_save_button)
        self.settings.minimum_fiber_intensity.trace_add(
            "write", self._enable_save_button)
        self.settings.maximum_fiber_intensity.trace_add(
            "write", self._enable_save_button)
        self.settings.minimum_nucleus_intensity.trace_add(
            "write", self._enable_save_button)
        self.settings.maximum_nucleus_intensity.trace_add(
            "write", self._enable_save_button)
        self.settings.minimum_nuc_diameter.trace_add(
            "write", self._enable_save_button)
        self.settings.minimum_nuclei_count.trace_add(
            "write", self._enable_save_button)

        # Updates the display when an image has been processed
        self._processed_images_count.trace_add("write",
                                               self._update_processed_images)

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

        self._menu_bar.add_cascade(label="File", menu=self._file_menu)

        # Sets the settings menu
        self._settings_menu = Menu(self._menu_bar, tearoff=0)
        self._settings_menu.add_command(
            label="Settings", command=self._open_settings_window)
        self._menu_bar.add_cascade(label="Settings", menu=self._settings_menu)

        # Sets the help menu
        self._help_menu = Menu(self._menu_bar, tearoff=0)
        self._help_menu.add_command(label="Help", command=self._open_github)
        self._menu_bar.add_cascade(label="Help", menu=self._help_menu)

        # Sets the quit menu
        self._quit_menu = Menu(self._menu_bar, tearoff=0)
        self._quit_menu.add_command(label="Quit", command=self.safe_destroy)
        self._menu_bar.add_cascade(label="Quit", menu=self._quit_menu)

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
            self._tick_frame_1, text="Blue", onvalue=True, offvalue=False,
            variable=self.settings.blue_channel_bool,
            command=self._set_image_channels)
        self._blue_channel_check_button.pack(anchor="w", side="left", fill='x',
                                             padx=5, pady=5)
        self._green_channel_check_button = ttk.Checkbutton(
            self._tick_frame_1, text="Green", onvalue=True, offvalue=False,
            variable=self.settings.green_channel_bool,
            command=self._set_image_channels)
        self._green_channel_check_button.pack(anchor="w", side="left",
                                              fill='x', padx=5, pady=5)
        self._red_channel_check_button = ttk.Checkbutton(
            self._tick_frame_1, text="Red", onvalue=True, offvalue=False,
            variable=self.settings.red_channel_bool,
            command=self._set_image_channels)
        self._red_channel_check_button.pack(anchor="w", side="left", fill='x',
                                            padx=5, pady=5)

        # Creating the checkboxes of the second row
        self._indicator = ttk.Label(self._tick_frame_2, text="  Indicators : ")
        self._indicator.pack(anchor="w", side="left", fill='x', padx=3, pady=5)
        self._show_nuclei_check_button = ttk.Checkbutton(
            self._tick_frame_2, text="Nuclei", onvalue=True, offvalue=False,
            variable=self.settings.show_nuclei, command=self._set_indicators)
        self._show_nuclei_check_button.pack(anchor="w", side="left", fill='x',
                                            padx=3, pady=5)
        self._show_fibers_check_button = ttk.Checkbutton(
            self._tick_frame_2, text="Fibers", onvalue=True, offvalue=False,
            variable=self.settings.show_fibers, command=self._set_indicators)
        self._show_fibers_check_button.pack(anchor="w", side="left", fill='x',
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

    def _enable_save_button(self, _, __, ___) -> None:
        """Some settings should enable the save button when modified."""

        self._save_button['state'] = 'enabled'

    def _open_settings_window(self) -> None:
        """Opens the window where users can adjust the settings."""

        self._settings_window = SettingsWindow(self)

    def _load_settings(self, project_path: Path) -> None:
        """Loads the settings from the settings file if any is present.

        Args:
            project_path: The Path where the project is saved.
        """

        # Gets the settings from the settings.pickle file
        settings_file = project_path / 'settings.pickle'
        if settings_file.is_file() and settings_file.exists():
            self.log(f"Loading the settings file from {settings_file}")
            with open(settings_file, 'rb') as param_file:
                settings = load(param_file)
        else:
            self.log("No setting file detected, loading the default settings")
            settings = dict()

        # Creates a Settings instance and sets the values
        self.settings.update(settings)
        self.log(f"Settings values: {str(self.settings)}")

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
        self.title("MyoFInDer - New Project (Unsaved)")
        self._current_project = None

    def _save_project(self, directory: Path) -> None:
        """Saves a project, its images and the associated data.

        Args:
            directory: The path to the folder where the project should be
                saved.
        """

        # Creating the folder if needed
        try:
            if not (directory.is_dir() and directory.exists()):
                self.log(f"Creating the directory where to save the "
                         f"project at {directory}")
                Path.mkdir(directory, parents=True)

        # If an exception is raised, catching and displaying it
        except (Exception,) as exc:
            self._logger.exception(
                f"Exception caught while creating the directory where to "
                f"save the project !", exc_info=exc)
            messagebox.showerror("Error !", "Could not create the folder "
                                            "where to save the project !")
            return

        saving_popup: Optional[SavePopup] = None
        try:
            # Displays a popup indicating the project is being saved
            saving_popup = SavePopup(self, directory)
            sleep(1)

            # Actually saving the project
            self.save_settings(directory)
            self._files_table.save_project(directory,
                                           self.settings.save_overlay.get())

            # Checking that all the mandatory files were created as expected
            if ((directory / 'settings.pickle').exists() and
                (directory / f"{directory.name}.xlsx").exists() and
                (directory / 'data.pickle').exists() and
                (directory / 'Original Images').exists() and
                len(tuple((directory / 'Original Images').iterdir()))):

                # Setting the save button, the project title and the menu entry
                self._set_title_and_button(directory)
                self.log(f"Project saved at {directory}")

            else:
                messagebox.showerror("Error !", "Could not save the project !")

        # If an exception is raised, catching it and displaying
        except (Exception,) as exc:
            self._logger.exception(
                f"Exception caught while saving the project !", exc_info=exc)
            messagebox.showerror("Error !", "Could not save the project !")

        # Delete the save popup if it was ever created
        finally:
            if saving_popup is not None:
                saving_popup.destroy()

    def _load_project(self) -> None:
        """Loads a project, its images and its data."""

        self.log("Project loading requested by the user")

        # Choose the folder in a dialog window
        directory = filedialog.askdirectory(
            initialdir=Path.cwd(),
            mustexist=True,
            title="Choose a Project Folder")

        if not directory:
            self.log("Project loading aborted bu the user")
            return

        directory = Path(directory)
        self.log(f"User requested to load project {directory}")

        # Checking that a valid project was selected
        if not (directory.is_dir() and directory.exists() and
                (directory / 'data.pickle').is_file() and
                (directory / 'data.pickle').exists()):
            messagebox.showerror("Error while loading",
                                 "This isn't a valid MyoFInDer project !")
            self.log("The selected directory is not valid for loading into "
                     "MyoFInDer")
            return

        # Setting the save button, the project title and the menu entries
        self._set_title_and_button(directory)

        # Actually loading the project
        self.log(f"Loading the project {directory}")
        self._load_settings(directory)
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
        self.title(f"MyoFInDer - Project '{directory.name}'")

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
            warning_window = WarningWindow(self, return_var)
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

    def _save_button_pressed(self,
                             _: Optional[Event] = None,
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
    def _safe_empty_project(self) -> None:
        """Creates an empy project, and displays a warning if there's unsaved
        data."""

        self._create_empty_project()

    @_save_before_closing
    def _safe_load(self) -> None:
        """Loads an existing project, and displays a warning if there's unsaved
        data."""

        self._load_project()

    def _disable_buttons(self) -> None:
        """Disables most of the buttons and menu entries when computing."""

        self.log("Disabling the buttons")

        # Disabling the buttons
        self._load_button['state'] = "disabled"
        self._save_button['state'] = "disabled"
        self._select_all_button['state'] = 'disabled'
        self._delete_all_button['state'] = 'disabled'

        # Disabling the menu entries
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
                 self.settings.fiber_colour.get(),
                 self.settings.minimum_fiber_intensity.get(),
                 self.settings.maximum_fiber_intensity.get(),
                 self.settings.minimum_nucleus_intensity.get(),
                 self.settings.maximum_nucleus_intensity.get(),
                 self.settings.minimum_nuc_diameter.get(),
                 self.settings.minimum_nuclei_count.get()))

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
                    (path, nuclei_color, fiber_color, minimum_fiber_intensity,
                     maximum_fiber_intensity, minimum_nucleus_intensity,
                     maximum_nucleus_intensity, minimum_nucleus_diameter,
                     minimum_nuclei_count) = job
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
                    file, nuclei_out, nuclei_in, fiber_contours, area = \
                        self._segmentation(path,
                                           nuclei_color,
                                           fiber_color,
                                           minimum_fiber_intensity,
                                           maximum_fiber_intensity,
                                           minimum_nucleus_intensity,
                                           maximum_nucleus_intensity,
                                           minimum_nucleus_diameter,
                                           minimum_nuclei_count)
                    self.log(f"Segmentation returned file: {file}, "
                             f"nuclei out: {len(nuclei_out)}, "
                             f"nuclei in: {len(nuclei_in)}, "
                             f"fiber contours: {len(fiber_contours)}, "
                             f"area: {area}")

                    # Not updating if the user wants to stop the computation
                    if self._stop_event.is_set():
                        continue

                    # Updating the image data with the result of the processing
                    self.log("Passing precessed data to the files table")
                    self._files_table.input_processed_data(nuclei_out,
                                                           nuclei_in,
                                                           fiber_contours,
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
            parent=self, title='Please select the images to open')

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

    def _set_indicators(self) -> None:
        """Updates the display of fibers and nuclei according to the user
        selection."""
        
        # Updating the display
        self.log("Setting the image indicators to display")
        self._image_canvas.set_indicators()

    def _nuclei_colour_sel(self, _, __, ___) -> None:
        """Ensures there's no conflict in the chosen image channels for fibers
        and nuclei."""

        # Sets one of the channels back to its previous value in case of
        # conflict
        if self.settings.nuclei_colour.get() == \
                self.settings.fiber_colour.get():
            if self._previous_nuclei_colour.get() != \
                    self.settings.nuclei_colour.get():
                self.settings.fiber_colour.set(
                    self._previous_nuclei_colour.get())
            elif self._previous_fiber_colour.get() != \
                    self.settings.fiber_colour.get():
                self.settings.nuclei_colour.set(
                    self._previous_fiber_colour.get())

        # Sets the previous values variables
        self._previous_nuclei_colour.set(self.settings.nuclei_colour.get())
        self._previous_fiber_colour.set(self.settings.fiber_colour.get())

        # Finally, save and redraw the nuclei and fibers
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
        open_new("https://tissueengineeringlab.github.io/MyoFInDer/")
