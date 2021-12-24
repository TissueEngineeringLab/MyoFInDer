# coding: utf-8

from tkinter import ttk, filedialog, N, E, S, W, Canvas, Tk, IntVar, \
    Toplevel, Scale, HORIZONTAL, DISABLED, NORMAL, PhotoImage, Menu, \
    StringVar, BooleanVar
from PIL import ImageTk, Image
from numpy import asarray, save, load
from os import path, mkdir

from table import ImageCanvasSize, ImageCanvasStandardFactor, Table
from ctypes import pythonapi, py_object, windll
from platform import release
from imagewindow import table, Zoom_Advanced
from validateFileName import is_pathname_valid
from shutil import rmtree
from webbrowser import open_new

from nucleiFibreSegmentation import deepcell_functie, initialize_mesmer

from threading import get_ident, active_count, Thread
from time import time

# show splash screen
root = Tk()
root.overrideredirect(True)

# set the window
root.grab_set()
SPLASH_SIZE_FACTOR = 0.35
SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()
root.geometry('%dx%d+%d+%d' % (SCREEN_WIDTH * SPLASH_SIZE_FACTOR,
                               SCREEN_HEIGHT * SPLASH_SIZE_FACTOR,
                               SCREEN_WIDTH * (1 - SPLASH_SIZE_FACTOR) * 0.5,
                               SCREEN_HEIGHT * (1 - SPLASH_SIZE_FACTOR) * 0.5))

# set the image
image_file = "movedim.png"
splashImage = Image.open(image_file)
maxFactor = SCREEN_WIDTH*SPLASH_SIZE_FACTOR / 1936
if SCREEN_HEIGHT * SPLASH_SIZE_FACTOR / 1460 > maxFactor:
    maxFactor = SCREEN_HEIGHT * SPLASH_SIZE_FACTOR / 1460
splashImage = splashImage.resize((int(maxFactor * 1936),
                                  int(maxFactor * 1460)), Image.ANTIALIAS)
splashImage = splashImage.convert("RGBA")

# start the fade
fadeStart = 0.4
fadeEnd = 0.6
for y in range(int(splashImage.size[1] - splashImage.size[1]*(1 - fadeStart)),
               splashImage.size[1]):
    for x in range(splashImage.size[0]):

        alpha = (- y / (splashImage.size[1]*(fadeEnd - fadeStart)) +
                 fadeEnd / (fadeEnd - fadeStart))
        alpha = min(alpha, 1)
        alpha = max(alpha, 0)

        rgba = list(splashImage.getpixel((x, y)))
        rgba = [int(rgba[0] * alpha), int(rgba[1] * alpha),
                int(rgba[2] * alpha), 255]
        splashImage.putpixel((x, y), tuple(rgba))

# draw the image and credits on the screen
photoImg = ImageTk.PhotoImage(splashImage)
splashCanvas = Canvas(root, height=SCREEN_HEIGHT * SPLASH_SIZE_FACTOR,
                      width=SCREEN_WIDTH * SPLASH_SIZE_FACTOR, bg="brown")
splashCanvas.create_image(SCREEN_WIDTH * SPLASH_SIZE_FACTOR / 2,
                          SCREEN_HEIGHT * SPLASH_SIZE_FACTOR / 2,
                          image=photoImg)
splashCanvas.create_text(20, int((fadeEnd - 0.05) * splashImage.size[1]),
                         anchor=W,
                         text="Cellen Tellen - A P&O project by Quentin De "
                              "Rore, Ibrahim El Kaddouri, \nEmiel "
                              "Vanspranghels and Henri Vermeersch, assisted "
                              "by Desmond Kabus, \nRebecca Wüst and "
                              "Maria Olenic", fill="white",
                         font='Helvetica 7 bold')
splashLoadingLabel = splashCanvas.create_text(20, int((0.7 - 0.05) *
                                                      splashImage.size[1]),
                                              anchor=W,
                                              text='Importing dependencies...',
                                              fill="white",
                                              font='Helvetica 7 bold')
splashCanvas.pack()
root.update()

# update splash screen
splashCanvas.itemconfig(splashLoadingLabel, text="Importing DeepCell...")
root.update()

# update splash screen
splashCanvas.itemconfig(splashLoadingLabel, text="Initialising Mesmer...")
root.update()
initialize_mesmer()
# update splash screen
splashCanvas.itemconfig(splashLoadingLabel, text="Starting program...")
root.update()


# get the absolute path to the exe file
BASE_PATH = path.abspath('')  # [:-7]
BASE_PATH += "/"

# set default numbers
previousMousePosition = [-5, -5]
ImageZoomFactor = 1.0
ImagePannedPosition = [0, 0]

# threads
currentThreads = []
totalImagesProcessed = 0
threadSlider = None
nThreads = IntVar()
nThreads.set(3)
nThreadsRunning = 0

# small objects slider
SmallObjectsSlider = None
smallObjectsThreshold = IntVar()
smallObjectsThreshold.set(400)
setViewSizeWindow = None


# link to gitHub
def open_github():
    open_new("https://github.com/Quentinderore2/Cellen-Tellen")


# this function gets called when changing the nuclei or fibre channels
def nuclei_colour_sel(previous_nuclei_colour_var,
                      nuclei_colour_var,
                      previous_fibre_colour_var,
                      fibre_colour_var):

    # if the two are the same, reset one
    if nuclei_colour_var.get() == fibre_colour_var.get():
        if previous_nuclei_colour_var.get() != nuclei_colour_var.get():
            fibre_colour_var.set(previous_nuclei_colour_var.get())
        elif previous_fibre_colour_var.get() != fibre_colour_var.get():
            nuclei_colour_var.set(previous_fibre_colour_var.get())

    # set the previous ones to the current one
    previous_nuclei_colour_var.set(nuclei_colour_var.get())
    previous_fibre_colour_var.set(fibre_colour_var.get())

    # save
    settings_changed()


def create_project_name_window(new_project=False):

    # windowsize
    projectname_window_size = [505, 200]

    # create the window
    projectname_window = Toplevel(root)
    projectname_window.grab_set()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    projectname_window.geometry(str(projectname_window_size[0]) + 'x' +
                                str(projectname_window_size[1]) + "+" +
                                str(int(screen_width / 2 -
                                        projectname_window_size[0] / 2)) + "+"
                                + str(int(screen_height / 4 -
                                          projectname_window_size[1] / 2)))
    if new_project:
        projectname_window.title("Creating a New Empty Project")
    else:
        projectname_window.title("Saving the Current Project")

    # set label
    if new_project:
        ask_label = ttk.Label(projectname_window,
                              text='Choose a name for your NEW EMPTY Project')
        ask_label.place(x=projectname_window_size[0] / 2,
                        y=30, anchor='center')
    else:
        ask_label = ttk.Label(projectname_window,
                              text='Choose a name for your CURRENT Project')
        ask_label.place(x=projectname_window_size[0] / 2,
                        y=30, anchor='center')

    # set the warninglabel (gives warnings when the name is bad)
    global warningVar
    warningVar.set('')
    warning_label = ttk.Label(projectname_window, textvariable=warningVar,
                              foreground='red')
    warning_label.place(x=projectname_window_size[0] / 2, y=75,
                        anchor='center')
    validate_command = warning_label.register(check_project_name_entry)

    # set the entry box to input the name
    global nameEntry
    nameEntry = ttk.Entry(projectname_window, validate='key', state='normal',
                          text='Choose a name for your project', width=30,
                          validatecommand=(validate_command, '%P'))
    nameEntry.place(x=projectname_window_size[0] / 2, y=110, anchor='center')
    nameEntry.focus()
    nameEntry.icursor(len(nameEntry.get()))

    # savebutton
    global foldernameWindowSaveButton
    foldernameWindowSaveButton = ttk.Button(projectname_window, text='Save',
                                            width=30,
                                            command=lambda: save_project(
                                              nameEntry.get(), True))
    foldernameWindowSaveButton.place(x=projectname_window_size[0] / 2,
                                     y=150, anchor='center')
    projectname_window.bind('<Return>', enter_pressed)
    check_project_name_entry(nameEntry.get())


# you can press enter to be doen inputting the name of the project
def enter_pressed(event):

    # if the window exists and the save button is enabled
    if foldernameWindowSaveButton['state'] == 'enabled':
      save_project(nameEntry.get(), True)


# this function checks if the given name is valid
def check_project_name_entry(new_entry):

    # check if it is a valid name
    global warningVar, foldernameWindowSaveButton
    if not is_pathname_valid(new_entry) or '/' in new_entry \
            or '.' in new_entry:
        foldernameWindowSaveButton['state'] = 'disabled'
        if len(new_entry) != 0:
            warningVar.set('This is not a valid projectname')
        return True

    # check if it already exists
    if path.isdir(BASE_PATH + 'Projects/' + new_entry):
        warningVar.set('This project already exists')
        foldernameWindowSaveButton['state'] = 'disabled'
        return True

    # no warnings
    warningVar.set('')
    foldernameWindowSaveButton['state'] = 'enabled'
    return True


def create_settings_window(root):

    # create the window
    new_window = Toplevel(root)
    new_window.grab_set()  # when you show the popup
    new_window.geometry("500x700+100+100")
    new_window.title("Settings")

    frm = ttk.Frame(new_window, padding="10 10 150 150")
    frm.grid(column=0, row=0, sticky='NESW')

    # nuclei colour
    nuclei_colour_buttons = []
    fibre_colour_buttons = []
    ttk.Label(frm, text="Nuclei Colour :    ").grid(column=0, row=0,
                                                    sticky='NE')
    nuclei_colour_r1 = ttk.Radiobutton(frm, text="Blue Channel",
                                       variable=nucleiColourVar, value="Blue",
                                       command=lambda: nuclei_colour_sel(
                                         previousNucleiColourVar,
                                         nucleiColourVar,
                                         previousFibreColourVar,
                                         fibreColourVar))
    nuclei_colour_r1.grid(column=1, row=0, sticky='NW')
    nuclei_colour_r2 = ttk.Radiobutton(frm, text="Green Channel",
                                       variable=nucleiColourVar, value="Green",
                                       command=lambda: nuclei_colour_sel(
                                         previousNucleiColourVar,
                                         nucleiColourVar,
                                         previousFibreColourVar,
                                         fibreColourVar))
    nuclei_colour_r2.grid(column=1, row=1, sticky='NW')
    nuclei_colour_r3 = ttk.Radiobutton(frm, text="Red Channel",
                                       variable=nucleiColourVar, value="Red",
                                       command=lambda: nuclei_colour_sel(
                                         previousNucleiColourVar,
                                         nucleiColourVar,
                                         previousFibreColourVar,
                                         fibreColourVar))
    nuclei_colour_r3.grid(column=1, row=2, sticky='NW')

    # fibre colour
    ttk.Label(frm, text="Fibre Colour :    ").grid(column=0, row=5,
                                                   sticky='NE')
    fibre_colour_r1 = ttk.Radiobutton(frm, text="Blue Channel",
                                      variable=fibreColourVar, value="Blue",
                                      command=lambda: nuclei_colour_sel(
                                        previousNucleiColourVar,
                                        nucleiColourVar,
                                        previousFibreColourVar,
                                        fibreColourVar))
    fibre_colour_r1.grid(column=1, row=5, sticky='NW')
    fibre_colour_r2 = ttk.Radiobutton(frm, text="Green Channel",
                                      variable=fibreColourVar, value="Green",
                                      command=lambda: nuclei_colour_sel(
                                        previousNucleiColourVar,
                                        nucleiColourVar,
                                        previousFibreColourVar,
                                        fibreColourVar))
    fibre_colour_r2.grid(column=1, row=6, sticky='NW')
    fibre_colour_r3 = ttk.Radiobutton(frm, text="Red Channel",
                                      variable=fibreColourVar, value="Red",
                                      command=lambda: nuclei_colour_sel(
                                        previousNucleiColourVar,
                                        nucleiColourVar,
                                        previousFibreColourVar,
                                        fibreColourVar))
    fibre_colour_r3.grid(column=1, row=7, sticky='NW')

    nuclei_colour_buttons = [nuclei_colour_r1, nuclei_colour_r2,
                             nuclei_colour_r3]
    fibre_colour_buttons = [fibre_colour_r1, fibre_colour_r2, fibre_colour_r3]

    # autosave timer
    ttk.Label(frm, text='Autosave Interval :    ').grid(column=0, row=10,
                                                        sticky='NE')
    ttk.Radiobutton(frm, text="5 Minutes", variable=autoSaveTime, value=5*60,
                    command=lambda: settings_changed(2)).grid(column=1, row=10,
                                                              sticky='NW')
    ttk.Radiobutton(frm, text="15 Minutes", variable=autoSaveTime, value=15*60,
                    command=lambda: settings_changed(2)).grid(column=1, row=11,
                                                              sticky='NW')
    ttk.Radiobutton(frm, text="30 Minutes", variable=autoSaveTime, value=30*60,
                    command=lambda: settings_changed(2)).grid(column=1, row=12,
                                                              sticky='NW')
    ttk.Radiobutton(frm, text="60 Minutes", variable=autoSaveTime, value=60*60,
                    command=lambda: settings_changed(2)).grid(column=1, row=13,
                                                              sticky='NW')
    ttk.Radiobutton(frm, text="Never", variable=autoSaveTime, value=-1,
                    command=lambda: settings_changed(2)).grid(column=1, row=14,
                                                              sticky='NW')

    # save altered images
    ttk.Label(frm, text='Save Altered Images :    ').grid(column=0, row=16,
                                                          sticky='NE')
    ttk.Radiobutton(frm, text="On", variable=saveAlteredImagesBoolean, value=1,
                    command=lambda: settings_changed(3)).grid(column=1, row=16,
                                                              sticky='NW')
    ttk.Radiobutton(frm, text="Off", variable=saveAlteredImagesBoolean,
                    value=0,
                    command=lambda: settings_changed(3)).grid(column=1, row=17,
                                                              sticky='NW')

    # fibre counting
    ttk.Label(frm, text='Count Fibres :    ').grid(column=0, row=19,
                                                   sticky='NE')
    ttk.Radiobutton(frm, text="On", variable=doFibreCounting, value=1,
                    command=lambda: settings_changed(4)).grid(column=1, row=19,
                                                              sticky='NW')
    ttk.Radiobutton(frm, text="Off", variable=doFibreCounting, value=0,
                    command=lambda: settings_changed(4)).grid(column=1, row=20,
                                                              sticky='NW')

    # multithreading
    ttk.Label(frm, text='Number of Threads :    ').grid(column=0, row=22,
                                                        sticky='NE')
    global threadSlider
    threadSlider = Scale(frm, from_=0, to=5, orient=HORIZONTAL, label='Off',
                         command=thread_slider, showvalue=False, length=150)
    threadSlider.set(int(nThreads.get()))
    threadSlider.grid(column=1, row=22, sticky='NW')

    # small objects threshold
    ttk.Label(frm, text='Dead cells size Threshold :    ').grid(column=0,
                                                                row=23,
                                                                sticky='NE')
    global SmallObjectsSlider
    SmallObjectsSlider = Scale(frm, from_=10, to=1000,
                               label=str(int(smallObjectsThreshold.get())),
                               orient=HORIZONTAL, command=small_objects_slider,
                               showvalue=False, length=150)
    SmallObjectsSlider.set(int(smallObjectsThreshold.get()))
    SmallObjectsSlider.grid(column=1, row=23, sticky='NW')

    # set row heights
    frm.grid_rowconfigure(4, minsize=20)
    frm.grid_rowconfigure(9, minsize=20)
    frm.grid_rowconfigure(15, minsize=20)
    frm.grid_rowconfigure(18, minsize=20)
    frm.grid_rowconfigure(23, minsize=20)
    frm.grid_rowconfigure(21, minsize=20)
    frm.grid_columnconfigure(0, minsize=250)


# set the number of threads and threadslider label when moving the slider
def thread_slider(n):
    global threadSlider
    if int(n) == 0:
        threadSlider.configure(label='Off')
    else:
        threadSlider.configure(label=str(n))
    nThreads.set(int(n))
    settings_changed()


# this function gets called when changing the small objects slider
def small_objects_slider(n):
    global smallObjectsThreshold
    SmallObjectsSlider.configure(label=str(n))
    smallObjectsThreshold.set(n)
    settings_changed()


# save the settings and update the autosave time
def settings_changed(setting_index=0):

    # save the settings
    # create settings list
    settings = [fibreColourVar.get(), nucleiColourVar.get(),
                autoSaveTime.get(), saveAlteredImagesBoolean.get(),
                doFibreCounting.get(), nThreads.get(),
                smallObjectsThreshold.get(), recentProjects,
                blueChannelBool.get(), greenChannelBool.get(),
                redChannelBool.get(), showNucleiBool.get(),
                showFibresBool.get(), table.ImageCanvasSize[0],
                table.ImageCanvasSize[1]]

    # convert to numpy and save
    arr = asarray(settings)
    save(BASE_PATH + 'general', arr)

    # enable save button if needed
    if setting_index == 3:
        saveButton['state'] = 'enabled'

    # set the autosave timer
    if setting_index == 2:
      update_autosave_time()


# update the autosave time
def update_autosave_time():

    # if a previous timer was set, cancel it
    global autoSaveJob
    if autoSaveJob is not None:
        root.after_cancel(autoSaveJob)
    autoSaveJob = None

    # set a new timer if needed
    if autoSaveTime.get() > 0:
        autoSaveJob = root.after(autoSaveTime.get() * 1000,
                                 lambda auto_save_name=autoSaveName:
                                 save_project(auto_save_name))


# this window gets shown when attempting to close the program when the project
# is still unsaved
def create_warning_window():

    # if unsaved, show the window
    if saveButton['state'] == 'enabled' and \
            not len(nucleiTable.get_file_names()) == 0:
        # create
        global warningwindow
        warningwindow = Toplevel(root)
        warningwindow.grab_set()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        warningwindow.geometry("500x200+" + str(int(screen_width/2 - 500/2))
                               + "+" + str(int(screen_height/4 - 200/2)))

        warningwindow.title("Hold on!")
        global close
        close = True

        # create the label
        ttk.Label(warningwindow,
                  text="Are you sure about closing an unsaved project?").\
            place(x=250, y=30, anchor='center')

        # create the buttons
        ttk.Button(warningwindow, text='Close Without Saving',
                   command=root.destroy, width=40).place(x=250, y=115,
                                                         anchor='center')
        ttk.Button(warningwindow, text='Save and Close',
                   command=save_button_pressed, width=40).\
            place(x=250, y=75, anchor='center')
        ttk.Button(warningwindow, text='Cancel', command=quit_warning_window,
                   width=40).place(x=250, y=155, anchor='center')

    else:
        # if saved, destroy the window
        root.destroy()


def quit_warning_window():
    global close
    close = False
    warningwindow.destroy()


# this function is the process that gets called for every thread
def process_thread(index, file_names, is_thread, small_objects_thresh):

    # add the thread
    if is_thread:
        global currentThreads
        id_ = get_ident()
        if id_ not in currentThreads:
            currentThreads.append(id_)

    file = file_names[index]

    start = time()

    # get result
    nuclei, nuclei_in_fibre, fibre_positions, image_width, image_height = \
        deepcell_functie(file, nucleiColourVar.get(), fibreColourVar.get(),
                         doFibreCounting.get(), small_objects_thresh)

    end1 = time()

    # convert image coordinates to relative between 0 and 1
    for i in range(len(nuclei)):
        nuclei[i][0] = float(nuclei[i][0]) / float(image_width)
        nuclei[i][1] = float(nuclei[i][1]) / float(image_height)
    for i in range(len(nuclei_in_fibre)):
        nuclei_in_fibre[i][0] = float(nuclei_in_fibre[i][0]) / \
            float(image_width)
        nuclei_in_fibre[i][1] = float(nuclei_in_fibre[i][1]) / \
            float(image_height)
    for i in range(len(fibre_positions)):
        fibre_positions[i][0] = float(fibre_positions[i][0]) / \
            float(image_width)
        fibre_positions[i][1] = float(fibre_positions[i][1]) / \
            float(image_height)

    print("file : ", end1 - start)

    # send the output to the table
    nucleiTable.input_processed_data(nuclei, nuclei_in_fibre, fibre_positions,
                                     index)

    # close if necessary
    update_processed_images(file_names)
    set_unsaved_status()

    if is_thread:
        if index >= len(file_names) - nThreadsRunning:
            # close the threshold
            thread_exitted(get_ident())
        else:
            # keep on processing more images
            process_thread(index + nThreadsRunning, file_names, True,
                           small_objects_thresh)
    else:
        if index + 1 < len(file_names):
            # keep on processing more images
            process_thread(index + 1, file_names, False, small_objects_thresh)
        else:
            # all images are done
            stop_processing()


def update_processed_images(file_names):

    # change the label
    global totalImagesProcessed
    totalImagesProcessed += 1
    processingLabel['text'] = str(totalImagesProcessed) + " of " + \
        str(len(file_names)) + " Images Processed"


# this function gets called if a thread gets excited
def thread_exitted(id_):
    global currentThreads, totalImagesProcessed
    currentThreads.remove(id_)
    if len(currentThreads) == 0:
      stop_processing()


# force ending the threads
def stop_processing():

    # end the threads
    global currentThreads, totalImagesProcessed
    for it in currentThreads:
        res = pythonapi.PyThreadState_SetAsyncExc(it, py_object(SystemExit))
        if res > 1:
            pythonapi.PyThreadState_SetAsyncExc(it, 0)
            print('Exception raise failure')

    print("Still running threads (should be 1) :", active_count())

    # empty threads
    currentThreads = []
    totalImagesProcessed = 0
    processImagesbutton['text'] = "Process Images"
    processImagesbutton.configure(command=process_images)
    processingLabel['text'] = ""


# process images button is pressed
def process_images():

    # stop vorige threads
    stop_processing()

    # get the file_names
    file_names = nucleiTable.get_file_names()
    set_unsaved_status()

    # switch off process button
    global totalImagesProcessed
    totalImagesProcessed = 0
    processImagesbutton['text'] = 'Stop Processing'
    processImagesbutton.configure(command=stop_processing)
    processingLabel['text'] = "0 of " + str(len(file_names)) + \
        " Images Processed"
    root.update()

    # start threading
    global nThreadsRunning, threadSlider
    nThreadsRunning = nThreads.get()
    if int(nThreads.get()) == 0:
      process_thread(0, file_names, False, smallObjectsThreshold.get())
    else:
        # loop over the total number of threads and start the first n images
        for i in range(nThreadsRunning):
            if i <= len(file_names) - 1:
                t1 = Thread(target=process_thread,
                            args=(i, file_names,
                                  True, smallObjectsThreshold.get()),
                            daemon=True)
                t1.start()
                print(t1)


def select_images(root):

    # get the filenames with a dialogbox
    file_names = filedialog.askopenfilenames(filetypes=[('Image Files',
                                                         ('.tif', '.png',
                                                          '.jpg', '.jpeg',
                                                          '.bmp', '.hdr'))],
                                             parent=root, initialdir="/",
                                             title='Please select a directory')

    if len(file_names) != 0:

        # stop processing
        stop_processing()

        # enable the process image buttons
        processImagesbutton["state"] = 'enabled'

        # add them to the table
        global resaveImages
        resaveImages = True
        nucleiTable.add_images(file_names)
        set_unsaved_status()


# when leftclicking, the position of the cursor is sent to the table and
# imagecanvas
def left_click(event):
    nucleiTable.left_click(root.winfo_pointerx(), root.winfo_pointery(),
                           frm.winfo_rooty())
    if ImageCanvas.left_click(root.winfo_pointerx(), root.winfo_pointery(),
                              frm.winfo_rooty()):
      set_unsaved_status()


# when rightclicking, the position of the cursor is sent to the table and
# imagecanvas
def right_click(event):
    if ImageCanvas.right_click(root.winfo_pointerx(), root.winfo_pointery(),
                               frm.winfo_rooty()):
      set_unsaved_status()


def onwheel(event):
    nucleiTable.onwheel(event.delta, root.winfo_pointerx(),
                        root.winfo_pointery(), frm.winfo_rooty())


def motion(evet):
    nucleiTable.motion(root.winfo_pointerx(), root.winfo_pointery(),
                       frm.winfo_rooty())


# pass through the keypressing of the arrows to the imagecanvas to scroll
# around the imagecanvas
def on_left_press(event):
  ImageCanvas.arrows(0)


def on_up_press(event):
  ImageCanvas.arrows(1)


def on_right_press(event):
  ImageCanvas.arrows(2)


def on_down_press(event):
  ImageCanvas.arrows(3)


def on_zoom_in_press(event):
    ImageCanvas.zoom(ImageCanvasSize[0] / 2, ImageCanvasSize[1] / 2, 120)


def on_zoom_out_press(event):
    ImageCanvas.zoom(ImageCanvasSize[0] / 2, ImageCanvasSize[1] / 2, -120)


def delete_current_project(root):

    if currentProject != '':
        # delete the project
        rmtree(BASE_PATH + 'Projects/' + currentProject)

        # remove the load button
        recentProjectsMenu.delete(
            recentProjectsMenu.index("Load '" + currentProject + "'"))
        global recentProjects
        recentProjects.remove(currentProject)
        if len(recentProjects) == 0:
            fileMenu.entryconfig("Recent Projects", state='disabled')
        settings_changed()

        # create empty project
        create_empty_project()

        if currentProject == autoSaveName:
            fileMenu.entryconfig("Load Automatic Save", state='disabled')


def create_empty_project():

    # reset everything
    stop_processing()
    nucleiTable.reset()
    ImageCanvas.reset()

    # set the save button
    saveButton['state'] = 'enabled'
    saveButton['text'] = 'Save As'
    processImagesbutton['state'] = 'disabled'
    fileMenu.entryconfig(fileMenu.index("Delete Current Project"),
                         state=DISABLED)

    # set window title
    root.title("Cellen Tellen - New Project (Unsaved)")
    global currentProject
    currentProject = ''

    # call for project name
    create_project_name_window(True)


def load_project_from_explorer():

    # ask a folder
    folder = filedialog.askdirectory(initialdir=path.normpath(BASE_PATH +
                                                              "Projects"),
                                     title="Choose a Project Folder")

    # load this shit
    if (folder != '') and path.isdir(BASE_PATH + 'Projects/' +
                                     path.basename(folder)):
      load_project(path.basename(folder))


# this function loads a project, given a directory
def load_project(directory):

    # stop processing
    stop_processing()

    # set the window title
    root.title("Cellen Tellen - Project '" + directory + "'")
    global currentProject
    currentProject = directory

    # set the save button
    saveButton['state'] = 'disabled'
    saveButton['text'] = 'Save'
    fileMenu.entryconfig(fileMenu.index("Delete Current Project"),
                         state=NORMAL)

    # do the recent projects shit
    if path.isdir(BASE_PATH + 'Projects/' + directory) \
            and not directory == autoSaveName:
        # remove it first
        if directory in recentProjects:
            recentProjectsMenu.delete("Load '" + directory + "'")
            recentProjects.remove(directory)

        recentProjectsMenu.insert_command(index=0, label="Load '" +
                                                         directory + "'",
                                          command=lambda direct=directory:
                                          load_project(direct))
        recentProjects.insert(0, directory)
        fileMenu.entryconfig("Recent Projects", state='normal')
        if len(recentProjects) > MAX_RECENT_PROJECTS:
            # remove the last
            recentProjectsMenu.delete("Load '" + recentProjects[-1] + "'")
            recentProjects.pop(len(recentProjects) - 1)

        settings_changed()

    # load the project
    nucleiTable.load_project(BASE_PATH + 'Projects/' + directory)
    global resaveImages
    resaveImages = False

    # if there are images loaded
    if nucleiTable.images_available():
        processImagesbutton['state'] = 'enabled'
    else:
        processImagesbutton['state'] = 'disabled'


def save_button_pressed():

    # save as if necessary
    if currentProject == '':
      create_project_name_window()
    else:
        # perform normal save
        save_project(currentProject)


def save_project(directory, saveas=False):

    # do we want to save the images
    global resaveImages
    if saveas:
        resaveImages = True

    # don't autosave if not needed
    if not (autoSaveTime.get() < 0 and directory == autoSaveName):
        if directory != autoSaveName:
            # destroy the save as window if it exists
            if foldernameWindowSaveButton is not None:
                foldernameWindowSaveButton.master.destroy()

            # set the save button
            saveButton['state'] = 'disabled'
            saveButton['text'] = 'Save'
            fileMenu.entryconfig(fileMenu.index("Delete Current Project"),
                                 state=NORMAL)

            # change the current project name
            global currentProject
            currentProject = directory
            root.title("Cellen Tellen - Project '" + currentProject + "'")

            # do the recent projects shit
            if not path.isdir(BASE_PATH + 'Projects/' + directory):
                recentProjectsMenu.insert_command(
                    index=0, label="Load '" + directory + "'",
                    command=lambda direct=directory: load_project(direct))
                recentProjects.insert(0, directory)
                fileMenu.entryconfig("Recent Projects", state='normal')
                if len(recentProjects) > MAX_RECENT_PROJECTS:
                    # remove the last
                    recentProjectsMenu.delete("Load '" + recentProjects[-1] +
                                              "'")
                    recentProjects.pop(len(recentProjects)-1)

                settings_changed()

        else:
            # set the automatic save entry
            fileMenu.entryconfig("Load Automatic Save", state='normal')
            if autoSaveTime.get() > 0:  # recall the autosave
              update_autosave_time()

        # create the folder
        if not path.isdir(BASE_PATH + 'Projects/' + directory):
            mkdir(BASE_PATH + 'Projects/' + directory)

        # create saving popup
        saving_popup = Toplevel(root)
        saving_popup.grab_set()
        saving_popup.title("Saving....")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        saving_popup.geometry("400x200+" + str(int(screen_width / 2 -
                                                   400 / 2)) +
                              "+" + str(int(screen_height/2 - 200/2)))
        ttk.Label(saving_popup, text="Saving to '" + directory + "' ...").\
            place(x=200, y=75, anchor='center')
        saving_popup.update()
        root.update()
        saving_popup.update()
        saving_popup.protocol("WM_DELETE_WINDOW", dontdoshit())

        # save the table
        nucleiTable.save_table(directory)

        # save the originals
        if resaveImages or directory == autoSaveName:
            nucleiTable.save_originals(directory)
        resaveImages = False

        # save the altered images
        if saveAlteredImagesBoolean.get() == 1 or directory == autoSaveName:
            nucleiTable.save_altered_images(directory)

        # save the data
        nucleiTable.save_data(directory)

        # destroy the popup
        saving_popup.destroy()

        # als het nodig is, close
        if close:
            root.destroy()


def dontdoshit():
    pass


def set_unsaved_status():

    # set the unsaved status
    if currentProject != '':
        root.title("Cellen Tellen - Project '" + currentProject +
                   "' (Unsaved)")
        saveButton['state'] = 'enabled'
        saveButton['text'] = 'Save'


# change the displayed image channels
def set_image_channels():
    ImageCanvas.set_channels(blueChannelBool.get(), greenChannelBool.get(),
                             redChannelBool.get())
    settings_changed(True)


# change the third button
def set_indicators():
    # set the indicators
    ImageCanvas.set_indicators(showNucleiBool.get(), showFibresBool.get())
    settings_changed(True)

    # set which indication
    global indicatingNuclei
    if showFibresBool.get() and not showNucleiBool.get():
        indicatingNuclei = False
        whichIndicatorButton['text'] = 'Manual : Fibres'
        whichIndicatorButton['state'] = 'disabled'

    if showFibresBool.get() and showNucleiBool.get():
        whichIndicatorButton['state'] = 'enabled'

    if not showFibresBool.get() and showNucleiBool.get():
        indicatingNuclei = True
        whichIndicatorButton['text'] = 'Manual : Nuclei'
        whichIndicatorButton['state'] = 'disabled'

    # pass through the indications to the imagecanvas
    ImageCanvas.set_which_indcation(indicatingNuclei)


# change the indications
def change_indications():
    global indicatingNuclei
    if indicatingNuclei:
        indicatingNuclei = False
        whichIndicatorButton['text'] = 'Manual : Fibres'
    else:
        indicatingNuclei = True
        whichIndicatorButton['text'] = 'Manual : Nuclei'
    ImageCanvas.set_which_indcation(indicatingNuclei)


# this function is used while opening the program the first time, to adjust
# the window size
def change_window_size(event):
    factor = 100
    if event.char == 'a':  # make smaller (but same ratio)
        table.ImageCanvasSize = (int(table.ImageCanvasSize[0] -
                                     table.ImageCanvasSize[0]/factor),
                                 int((table.ImageCanvasSize[0] -
                                      table.ImageCanvasSize[0]/factor) *
                                     ImageCanvasStandardFactor))
    elif event.char == 'z':  # make bigger (but same ratio)
        table.ImageCanvasSize = (int(table.ImageCanvasSize[0] +
                                     table.ImageCanvasSize[0]/factor),
                                 int((table.ImageCanvasSize[0] +
                                      table.ImageCanvasSize[0]/factor) *
                                     ImageCanvasStandardFactor))

    # update button gridpositions
    frm.grid_columnconfigure(0, minsize=table.ImageCanvasSize[0] + 4)

    # update canvas
    ImageCanvas.update_size(table.ImageCanvasSize)


# initialised the ajdustment of the window size, the first time you boot up
# the program (if there is not general.npy)
def start_window_view():
    global setViewSizeWindow

    # initialize window, size and position
    set_window_view_window_size = (500, 130)
    setViewSizeWindow = Toplevel(root)
    setViewSizeWindow.grab_set()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    setViewSizeWindow.geometry(str(set_window_view_window_size[0]) + 'x' +
                               str(set_window_view_window_size[1]) + "+" +
                               str(int(screen_width / 2 -
                                       set_window_view_window_size[0] / 2))
                               + "+" +
                               str(int(screen_height / 2 -
                                       set_window_view_window_size[1] / 2)))
    setViewSizeWindow.title("Set Window Size")
    setViewSizeWindow.focus_force()

    # set key strokes bindings, link to changeWindowSize
    setViewSizeWindow.bind('a', change_window_size)
    setViewSizeWindow.bind('z', change_window_size)
    setViewSizeWindow.protocol("WM_DELETE_WINDOW", end_window_view)

    # create 'done' button, link to endWindowView
    set_view_size_frame = ttk.Frame(setViewSizeWindow, padding="10 10 120 120")
    set_view_size_frame.grid(column=0, row=0, sticky='NESW')
    ttk.Label(set_view_size_frame,
              text="Use 'a' and 'z' keys to adjust the window view.").\
        grid(column=0, row=0, pady=5)
    ttk.Button(set_view_size_frame,
               text="Done", command=end_window_view, width=14).\
        grid(column=0, row=1, pady=15)
    set_view_size_frame.grid_columnconfigure(
        0, minsize=set_window_view_window_size[0])


def end_window_view():

    # destroy the viewsizewindow
    if setViewSizeWindow is not None:
        setViewSizeWindow.destroy()

    # create the table
    global nucleiTable
    nucleiTable = Table(root)
    nucleiTable.set_image_canvas(ImageCanvas)
    ImageCanvas.set_table(nucleiTable)

    # save default settings
    settings_changed(2)


# set better resolution
if int(release()) >= 8:
    windll.shcore.SetProcessDpiAwareness(True)

# set default values
imagesChanged = False
warningwindow = None
close = False

# initialise the root
root.destroy()
root = Tk()
root.title("Cellen Tellen - New Project (Unsaved)")
root.state('zoomed')

# set icon
photo = PhotoImage(file=BASE_PATH + "icon.png")
root.iconphoto(False, photo)


frm = ttk.Frame(root, padding="10 10 120 120")
frm.grid(column=0, row=0, sticky='NESW')


# configure the menu
menubar = Menu(root)
root.config(menu=menubar)

menubar.config(font=("TKDefaultFont", 20))
fileMenu = Menu(menubar, tearoff=0)
fileMenu.add_command(label="New Empty Project", command=create_empty_project)
fileMenu.add_command(label="Save Project As",
                     command=create_project_name_window)
fileMenu.add_command(label="Delete Current Project",
                     command=lambda: delete_current_project(root))
fileMenu.entryconfig(fileMenu.index("Delete Current Project"), state=DISABLED)
fileMenu.add_command(label="Load From Explorer",
                     command=load_project_from_explorer)
fileMenu.add_separator()

# automatic save
resaveImages = False
autoSaveJob = None
autoSaveName = 'AUTOSAVE'
autoSaveTime = IntVar()
autoSaveTime.set(-1)  # in seconds
saveAlteredImagesBoolean = IntVar()
saveAlteredImagesBoolean.set(0)
doFibreCounting = IntVar()
doFibreCounting.set(0)

# add the automatic save command
fileMenu.add_command(label='Load Automatic Save', state='disabled',
                     command=lambda name=autoSaveName:
                     load_project(name))
# if the automatic save already exists, link to it via the command
if path.isdir(BASE_PATH + 'Projects/' + autoSaveName):
    fileMenu.entryconfig("Load Automatic Save", state='normal')
fileMenu.add_separator()

# directly loadable projects (previous projects)
recentProjectsMenu = Menu(fileMenu, tearoff=0)
fileMenu.add_cascade(label="Recent Projects", menu=recentProjectsMenu)
MAX_RECENT_PROJECTS = 20
recentProjects = []

menubar.add_cascade(label="File", menu=fileMenu)


# set the warning var for foldername input
warningVar = StringVar()
warningVar.set('')
nameEntry = None
foldernameWindowSaveButton = None
currentProject = ''

# settings menu
settingsMenu = Menu(menubar, tearoff=0)
settingsMenu.add_command(label="Settings",
                         command=lambda: create_settings_window(root))
menubar.add_cascade(label="Settings", menu=settingsMenu)

# help menu
helpMenu = Menu(menubar, tearoff=0)
helpMenu.add_command(label="Help", command=open_github)
menubar.add_cascade(label="Help", menu=helpMenu)

# Quit menu
quitMenu = Menu(menubar, tearoff=0)
quitMenu.add_command(label="Quit", command=root.destroy)
menubar.add_cascade(label="Quit", menu=quitMenu)


# get screen sizes
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
print("screensize : ", screen_width, screen_height)
print("vroot : ", root.winfo_vrootwidth(), root.winfo_vrootheight())
ButtonRowWidth = 150


# initialised table, the object itself is not yet created until we have
# set the window view
nucleiTable = None

# key bindings, zooming, clicking with mouse, as well as moving and zoom in
# the image with the keyboard
root.bind('<ButtonPress-1>', left_click)
root.bind('<ButtonPress-3>', right_click)
root.bind('<MouseWheel>', onwheel)
root.bind('<Motion>', motion)
root.bind('<Left>', on_left_press)
root.bind('<Right>', on_right_press)
root.bind('<Up>', on_up_press)
root.bind('<Down>', on_down_press)
root.bind('=', on_zoom_in_press)
root.bind('+', on_zoom_in_press)
root.bind('-', on_zoom_out_press)
root.bind('_', on_zoom_out_press)


# load the settings
nucleiColourVar = StringVar()
nucleiColourVar.set("Blue")
previousNucleiColourVar = StringVar()
previousNucleiColourVar.set("Blue")
fibreColourVar = StringVar()
fibreColourVar.set("Green")
previousFibreColourVar = StringVar()
previousFibreColourVar.set("Green")
showNucleiBool = BooleanVar()
showFibresBool = BooleanVar()
showNucleiBool.set(True)
blueChannelBool = BooleanVar()
greenChannelBool = BooleanVar()
redChannelBool = BooleanVar()
blueChannelBool.set(True)
greenChannelBool.set(True)


# general buttons
ttk.Button(frm, text="Load Images", command=lambda: select_images(root),
           width=14).grid(column=1, row=0)
processImagesbutton = ttk.Button(frm, text="Process Images",
                                 command=process_images, width=14,
                                 state='disabled')
processImagesbutton.grid(column=2, row=0)

# image channel selection (which colour channels are displayed)
ttk.Label(frm, text="  Channels :   ").grid(column=1, row=2, sticky='w')
blueChannelCheckButton = ttk.Checkbutton(frm, text="Blue Channel",
                                         onvalue=True, offvalue=False,
                                         variable=blueChannelBool,
                                         command=set_image_channels)
blueChannelCheckButton.grid(column=2, row=2, sticky='w')
greenChannelCheckButton = ttk.Checkbutton(frm, text="Green Channel",
                                          onvalue=True, offvalue=False,
                                          variable=greenChannelBool,
                                          command=set_image_channels)
greenChannelCheckButton.grid(column=3, row=2, sticky='w')
redChannelCheckButton = ttk.Checkbutton(frm, text="Red Channel", onvalue=True,
                                        offvalue=False,
                                        variable=redChannelBool,
                                        command=set_image_channels)
redChannelCheckButton.grid(column=4, row=2, sticky='w')

# indicator selections (which indicators are shown)
ttk.Label(frm, text="  Indicators : ").grid(column=1, row=4, sticky='w')
showNucleiCheckButton = ttk.Checkbutton(frm, text="Nuclei", onvalue=True,
                                        offvalue=False,
                                        variable=showNucleiBool,
                                        command=set_indicators)
showNucleiCheckButton.grid(column=2, row=4, sticky='w')
showFibresCheckButton = ttk.Checkbutton(frm, text="Fibres", onvalue=True,
                                        offvalue=False,
                                        variable=showFibresBool,
                                        command=set_indicators)
showFibresCheckButton.grid(column=3, row=4, sticky='w')


processingLabel = ttk.Label(frm, text="")
processingLabel.grid(column=1, row=5, columnspan=4)


# save altered images and table
saveButton = ttk.Button(frm, text='Save As', width=14,
                        command=save_button_pressed, state='enabled')
saveButton.grid(column=4, row=0)

# set indicators
whichIndicatorButton = ttk.Button(frm, width=14, text='Manual : Nuclei',
                                  command=change_indications, state='enabled')
whichIndicatorButton.grid(column=3, row=0)

# load the general save (save settings, window view, etc)
if path.isfile(BASE_PATH + 'general.npy'):
    # get the list
    settingsarr = load(BASE_PATH + 'general.npy',
                       allow_pickle=True).tolist()

    # set the variables
    fibreColourVar.set(settingsarr[0])
    previousFibreColourVar.set(settingsarr[0])
    nucleiColourVar.set(settingsarr[1])
    previousNucleiColourVar.set(settingsarr[1])
    autoSaveTime.set(settingsarr[2])
    update_autosave_time()
    saveAlteredImagesBoolean.set(settingsarr[3])
    doFibreCounting.set(settingsarr[4])
    nThreads.set(settingsarr[5])
    smallObjectsThreshold.set(settingsarr[6])
    recentProjects = settingsarr[7]
    blueChannelBool.set(settingsarr[8])
    greenChannelBool.set(settingsarr[9])
    redChannelBool.set(settingsarr[10])
    showNucleiBool.set(settingsarr[11])
    showFibresBool.set(settingsarr[12])
    table.ImageCanvasSize = (settingsarr[13], settingsarr[14])

    # set the table and canvas
    ImageCanvas = Zoom_Advanced(root, nucleiTable)
    end_window_view()

else:
    # start windowsize selection
    ImageCanvas = Zoom_Advanced(root, nucleiTable)
    start_window_view()


# load the list of recent projects if these projects exist
if path.isdir(BASE_PATH + 'Projects'):
    temp = list(recentProjects)
    for foldername in temp:
        if path.isdir(BASE_PATH + 'Projects/' + foldername) \
                and foldername != '':
            recentProjectsMenu.add_command(
                label="Load '" + foldername + "'",
                command=lambda folder=foldername: load_project(folder))
        else:
            recentProjects.remove(foldername)
else:
    mkdir(BASE_PATH + 'Projects')

if len(recentProjects) == 0:
    fileMenu.entryconfig("Recent Projects", state='disabled')


# set the channels and indicators for the imagecanvas
indicatingNuclei = True
set_image_channels()
set_indicators()


# set grid sizes
frm.grid_columnconfigure(0, minsize=table.ImageCanvasSize[0]+4)
frm.grid_columnconfigure(1, minsize=ButtonRowWidth)
frm.grid_columnconfigure(2, minsize=ButtonRowWidth)
frm.grid_columnconfigure(3, minsize=ButtonRowWidth)
frm.grid_columnconfigure(4, minsize=ButtonRowWidth)
frm.grid_rowconfigure(1, minsize=10)
frm.grid_rowconfigure(3, minsize=1)


root.update()

# this protocol calls the createwarningwindow if we close the program
# (instead of directly exiting)
root.protocol("WM_DELETE_WINDOW", create_warning_window)
root.mainloop()  # tkinter main loop
