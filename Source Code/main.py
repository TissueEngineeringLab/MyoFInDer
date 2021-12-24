
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image


# show splash screen
root = Tk()
root.overrideredirect(True)

# set the window
root.grab_set()
SPLASH_SIZE_FACTOR = 0.35
SCREEN_WIDTH = root.winfo_screenwidth()
SCREEN_HEIGHT = root.winfo_screenheight()
root.geometry('%dx%d+%d+%d' % (SCREEN_WIDTH*SPLASH_SIZE_FACTOR, SCREEN_HEIGHT*SPLASH_SIZE_FACTOR, SCREEN_WIDTH*(1-SPLASH_SIZE_FACTOR)*0.5, SCREEN_HEIGHT*(1-SPLASH_SIZE_FACTOR)*0.5))

# set the image
image_file = "movedim.png"
splashImage = Image.open(image_file)
maxFactor = SCREEN_WIDTH*SPLASH_SIZE_FACTOR / 1936
if SCREEN_HEIGHT * SPLASH_SIZE_FACTOR / 1460 > maxFactor :
    maxFactor = SCREEN_HEIGHT * SPLASH_SIZE_FACTOR / 1460
splashImage = splashImage.resize((int(maxFactor * 1936), int(maxFactor * 1460)), Image.ANTIALIAS)
splashImage = splashImage.convert("RGBA")

# start the fade
fadeStart = 0.4
fadeEnd = 0.6
for y in range(int(splashImage.size[1] - splashImage.size[1]*(1 - fadeStart)), splashImage.size[1]) :
    for x in range(splashImage.size[0]) :

        alpha = (- y / (splashImage.size[1]*(fadeEnd - fadeStart)) + fadeEnd / (fadeEnd - fadeStart))
        alpha = min(alpha, 1)
        alpha = max(alpha, 0)

        rgba = list(splashImage.getpixel((x, y)))
        rgba = [int(rgba[0] * alpha), int(rgba[1] * alpha),  int(rgba[2] * alpha), 255]
        splashImage.putpixel((x, y), tuple(rgba))

# draw the image and credits on the screen
photoImg =  ImageTk.PhotoImage(splashImage)
splashCanvas = Canvas(root, height=SCREEN_HEIGHT*SPLASH_SIZE_FACTOR, width=SCREEN_WIDTH*SPLASH_SIZE_FACTOR, bg="brown")
splashCanvas.create_image(SCREEN_WIDTH*SPLASH_SIZE_FACTOR/2, SCREEN_HEIGHT*SPLASH_SIZE_FACTOR/2, image=photoImg)
splashCanvas.create_text(20, int((fadeEnd - 0.05)*splashImage.size[1]), anchor=W, text="Cellen Tellen - A P&O project by Quentin De Rore, Ibrahim El Kaddouri, \nEmiel Vanspranghels and Henri Vermeersch, assisted by Desmond Kabus, \nRebecca Wüst and Maria Olenic", fill="white", font=('Helvetica 7 bold'))
splashLoadingLabel = splashCanvas.create_text(20, int((0.7 - 0.05)*splashImage.size[1]),anchor=W, text = 'Importing dependencies...', fill="white", font=('Helvetica 7 bold'))
splashCanvas.pack()
root.update()

# import the rest of the dependencies, update the splash screen
from tkinter import filedialog
from table import *
import ctypes
import platform
from imagewindow import *
import validateFileName
import shutil
import webbrowser
# update splash screen
splashCanvas.itemconfig(splashLoadingLabel, text = "Importing DeepCell...")
root.update()
from nucleiFibreSegmentation import deepcell_functie, initializeMesmer
# update splash screen
splashCanvas.itemconfig(splashLoadingLabel, text = "Initialising Mesmer...")
root.update()
initializeMesmer()
# update splash screen
splashCanvas.itemconfig(splashLoadingLabel, text = "Starting program...")
root.update()
import threading
import time



# get the absolute path to the exe file
BASE_PATH = os.path.abspath('')#[:-7]
BASE_PATH += "/"

# set default numbers
previousMousePosition = [-5,-5]
ImageZoomFactor = 1.0
ImagePannedPosition = [0,0]

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

# link to github
def openGithub():
    webbrowser.open_new("https://github.com/Quentinderore2/Cellen-Tellen")

# this function gets called when changing the nuclei or fibre channels
def NucleiColourSel(previousNucleiColourVar, nucleiColourVar, previousFibreColourVar, fibreColourVar, nucleiColourButtons, fibreColourButtons) :



    # if the two are the same, reset one
    if (nucleiColourVar.get() == fibreColourVar.get()) :
        if (previousNucleiColourVar.get() != nucleiColourVar.get()) :
            fibreColourVar.set(previousNucleiColourVar.get())
        elif (previousFibreColourVar.get() != fibreColourVar.get()) :
            nucleiColourVar.set(previousFibreColourVar.get())

    # set the previous ones to the current one
    previousNucleiColourVar.set(nucleiColourVar.get())
    previousFibreColourVar.set(fibreColourVar.get())

    # save
    settingsChanged()


def createProjectnameWindow(newProject=False) :

    # windowsize
    projectnameWindowSize = [505, 200]

    # create the window
    projectnameWindow = Toplevel(root)
    projectnameWindow.grab_set()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    projectnameWindow.geometry(str(projectnameWindowSize[0]) + 'x' + str(projectnameWindowSize[1]) + "+" + str(int(screen_width/2 - projectnameWindowSize[0]/2)) + "+" + str(int(screen_height/4 - projectnameWindowSize[1]/2)))
    if newProject :
        projectnameWindow.title("Creating a New Empty Project")
    else :
        projectnameWindow.title("Saving the Current Project")

    # set label
    askLabel = None
    highlightwordLabel = None
    if newProject :
        askLabel = ttk.Label(projectnameWindow, text='Choose a name for your NEW EMPTY Project')
        askLabel.place(x=projectnameWindowSize[0]/2, y=30, anchor='center')
    else :
        askLabel = ttk.Label(projectnameWindow, text='Choose a name for your CURRENT Project')
        askLabel.place(x=projectnameWindowSize[0]/2, y=30, anchor='center')


    # set the warninglabel (gives warnings when the name is bad)
    global warningVar
    warningVar.set('')
    warningLabel = ttk.Label(projectnameWindow, textvariable=warningVar, foreground='red')
    warningLabel.place(x=projectnameWindowSize[0]/2, y=75, anchor='center')
    validateCommand = warningLabel.register(checkProjectnameEntry)

    # set the entry box to input the name
    global nameEntry
    nameEntry = ttk.Entry(projectnameWindow, validate='key', state='normal', text='Choose a name for your project', width=30, validatecommand=(validateCommand, '%P'))
    nameEntry.place(x=projectnameWindowSize[0] / 2, y=110, anchor='center')
    nameEntry.focus()
    nameEntry.icursor(len(nameEntry.get()))

    # savebutton
    global foldernameWindowSaveButton
    foldernameWindowSaveButton = ttk.Button(projectnameWindow, text='Save', width=30, command = lambda:saveProject(nameEntry.get(), True))
    foldernameWindowSaveButton.place(x=projectnameWindowSize[0] / 2, y=150, anchor='center')
    projectnameWindow.bind('<Return>', enterPressed)
    checkProjectnameEntry(nameEntry.get())

# you can press enter to be doen inputting the name of the project
def enterPressed(event) :

    # if the window exists and the save button is enabled
    if foldernameWindowSaveButton['state'] == 'enabled' :
        saveProject(nameEntry.get(), True)

# this function checks if the given name is valid
def checkProjectnameEntry(newEntry) :

    # check if it is a valid name
    global warningVar, foldernameWindowSaveButton
    if (not validateFileName.is_pathname_valid(newEntry)) or '/' in newEntry or '.' in newEntry :
        foldernameWindowSaveButton['state'] = 'disabled'
        if len(newEntry) != 0 :
            warningVar.set('This is not a valid projectname')
        return True

    # check if it already exists
    if os.path.isdir(BASE_PATH + 'Projects/' + newEntry) :
        warningVar.set('This project already exists')
        foldernameWindowSaveButton['state'] = 'disabled'
        return True

    # no warnings
    warningVar.set('')
    foldernameWindowSaveButton['state'] = 'enabled'
    return True


def createSettingsWindow(root) :

    # create the window
    newWindow = Toplevel(root)
    newWindow.grab_set()  # when you show the popup
    newWindow.geometry("500x700+100+100")
    newWindow.title("Settings")



    frm = ttk.Frame(newWindow, padding="10 10 150 150")
    frm.grid(column=0, row=0, sticky=(N, W, E, S))


    # nuclei colour
    nucleiColourButtons = []
    fibreColourButtons = []
    ttk.Label(frm, text="Nuclei Colour :    ").grid(column=0, row=0,  sticky=(N, E))
    nucleiColourR1 = ttk.Radiobutton(frm, text="Blue Channel", variable=nucleiColourVar, value="Blue", command = lambda : NucleiColourSel(previousNucleiColourVar, nucleiColourVar, previousFibreColourVar, fibreColourVar, nucleiColourButtons, fibreColourButtons))
    nucleiColourR1.grid(column=1, row=0, sticky=(N, W))
    nucleiColourR2 = ttk.Radiobutton(frm, text="Green Channel", variable=nucleiColourVar, value="Green",
                    command=lambda : NucleiColourSel(previousNucleiColourVar, nucleiColourVar, previousFibreColourVar, fibreColourVar, nucleiColourButtons, fibreColourButtons))
    nucleiColourR2.grid(column=1, row=1, sticky=(N, W))
    nucleiColourR3 = ttk.Radiobutton(frm, text="Red Channel", variable=nucleiColourVar, value="Red",
                    command=lambda : NucleiColourSel(previousNucleiColourVar, nucleiColourVar, previousFibreColourVar, fibreColourVar, nucleiColourButtons, fibreColourButtons))
    nucleiColourR3.grid(column=1, row=2, sticky=(N, W))

    # fibre colour
    ttk.Label(frm, text="Fibre Colour :    ").grid(column=0, row=5,  sticky=(N, E))
    fibreColourR1 = ttk.Radiobutton(frm, text="Blue Channel", variable=fibreColourVar, value="Blue", command = lambda : NucleiColourSel(previousNucleiColourVar, nucleiColourVar, previousFibreColourVar, fibreColourVar, nucleiColourButtons, fibreColourButtons))
    fibreColourR1.grid(column=1, row=5, sticky=(N, W))
    fibreColourR2 = ttk.Radiobutton(frm, text="Green Channel", variable=fibreColourVar, value="Green",
                    command=lambda : NucleiColourSel(previousNucleiColourVar, nucleiColourVar, previousFibreColourVar, fibreColourVar, nucleiColourButtons, fibreColourButtons))
    fibreColourR2.grid(column=1, row=6, sticky=(N, W))
    fibreColourR3 = ttk.Radiobutton(frm, text="Red Channel", variable=fibreColourVar, value="Red",
                    command=lambda : NucleiColourSel(previousNucleiColourVar, nucleiColourVar, previousFibreColourVar, fibreColourVar, nucleiColourButtons, fibreColourButtons))
    fibreColourR3.grid(column=1, row=7, sticky=(N, W))


    nucleiColourButtons = [nucleiColourR1, nucleiColourR2, nucleiColourR3]
    fibreColourButtons = [fibreColourR1, fibreColourR2, fibreColourR3]


    # autosave timer
    ttk.Label(frm, text='Autosave Interval :    ').grid(column=0, row=10,  sticky=(N, E))
    ttk.Radiobutton(frm, text="5 Minutes", variable=autoSaveTime, value=5*60, command=lambda:settingsChanged(2)).grid(column=1, row=10, sticky=(N, W))
    ttk.Radiobutton(frm, text="15 Minutes", variable=autoSaveTime, value=15*60, command=lambda:settingsChanged(2)).grid(column=1, row=11, sticky=(N, W))
    ttk.Radiobutton(frm, text="30 Minutes", variable=autoSaveTime, value=30*60, command=lambda:settingsChanged(2)).grid(column=1, row=12, sticky=(N, W))
    ttk.Radiobutton(frm, text="60 Minutes", variable=autoSaveTime, value=60*60, command=lambda:settingsChanged(2)).grid(column=1, row=13, sticky=(N, W))
    ttk.Radiobutton(frm, text="Never", variable=autoSaveTime, value=-1, command=lambda:settingsChanged(2)).grid(column=1, row=14, sticky=(N, W))

    # save altered images
    ttk.Label(frm, text='Save Altered Images :    ').grid(column=0, row=16,  sticky=(N, E))
    ttk.Radiobutton(frm, text="On", variable=saveAlteredImagesBoolean, value=1, command=lambda:settingsChanged(3)).grid(
        column=1, row=16, sticky=(N, W))
    ttk.Radiobutton(frm, text="Off", variable=saveAlteredImagesBoolean, value=0, command=lambda:settingsChanged(3)).grid(
        column=1, row=17, sticky=(N, W))


    # fibre counting
    ttk.Label(frm, text='Count Fibres :    ').grid(column=0, row=19,  sticky=(N, E))
    ttk.Radiobutton(frm, text="On", variable=doFibreCounting, value=1, command=lambda:settingsChanged(4)).grid(
        column=1, row=19, sticky=(N, W))
    ttk.Radiobutton(frm, text="Off", variable=doFibreCounting, value=0, command=lambda:settingsChanged(4)).grid(
        column=1, row=20, sticky=(N, W))


    # multithreading
    ttk.Label(frm, text='Number of Threads :    ').grid(column=0, row=22,  sticky=(N, E))
    global threadSlider
    threadSlider = Scale(frm, from_=0, to=5, orient=HORIZONTAL, label='Off', command=ThreadSlider, showvalue=0, length=150)
    threadSlider.set(int(nThreads.get()))
    threadSlider.grid(column=1, row=22, sticky=(N, W))


    # small objects threshold
    ttk.Label(frm, text='Dead cells size Threshold :    ').grid(column=0, row=23,  sticky=(N, E))
    global SmallObjectsSlider
    SmallObjectsSlider = Scale(frm, from_=10, to=1000, label=str(int(smallObjectsThreshold.get())), orient=HORIZONTAL, command=smallObjectsSlider, showvalue=0, length=150)
    SmallObjectsSlider.set(int(smallObjectsThreshold.get()))
    SmallObjectsSlider.grid(column=1, row=23, sticky=(N, W))

    # set row heights
    frm.grid_rowconfigure(4, minsize=20)
    frm.grid_rowconfigure(9, minsize=20)
    frm.grid_rowconfigure(15, minsize=20)
    frm.grid_rowconfigure(18, minsize=20)
    frm.grid_rowconfigure(23, minsize=20)
    frm.grid_rowconfigure(21, minsize=20)
    frm.grid_columnconfigure(0, minsize=250)

# set the number of threads and threadslider label when moving the slider
def ThreadSlider(n):
    global threadSlider
    if int(n) == 0 :
        threadSlider.configure(label='Off')
    else :
        threadSlider.configure(label=str(n))
    nThreads.set(int(n))
    settingsChanged()

# this function gets called when changing the small objects slider
def smallObjectsSlider(n) :
    global smallObjectsThreshold
    SmallObjectsSlider.configure(label=str(n))
    smallObjectsThreshold.set(n)
    settingsChanged()

# save the settings and update the autosave time
def settingsChanged(settingIndex=0) :

    # save the settings
    # create settings list
    settings = [fibreColourVar.get(), nucleiColourVar.get(), autoSaveTime.get(), saveAlteredImagesBoolean.get(), doFibreCounting.get(), nThreads.get(), smallObjectsThreshold.get(),recentProjects, blueChannelBool.get(), greenChannelBool.get(), redChannelBool.get(), showNucleiBool.get(), showFibresBool.get(), table.ImageCanvasSize[0], table.ImageCanvasSize[1]]

    # convert to numpy and save
    arr = np.asarray(settings)
    np.save(BASE_PATH + 'general', arr)

    # enable save button if needed
    if (settingIndex == 3) :
        saveButton['state'] = 'enabled'


    # set the autosave timer
    if (settingIndex == 2) :
        updateAutosaveTime()

# update the autosave time
def updateAutosaveTime() :

    # if a previous timer was set, cancel it
    global autoSaveJob
    if autoSaveJob is not None :
        root.after_cancel(autoSaveJob)
    autoSaveJob = None

    # set a new timer if needed
    if (autoSaveTime.get() > 0) :
        autoSaveJob = root.after(autoSaveTime.get() * 1000, lambda autoSaveName=autoSaveName: saveProject(autoSaveName))

# this window gets shown when attempting to close the program when the project is still unsaved
def createWarningWindow() :

    # if unsaved, show the window
    if saveButton['state'] == 'enabled' and not len(nucleiTable.getFileNames()) == 0:
        # create
        global warningwindow
        warningwindow = Toplevel(root)
        warningwindow.grab_set()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        warningwindow.geometry("500x200+" + str(int(screen_width/2 - 500/2)) + "+" + str(int(screen_height/4 - 200/2)))

        warningwindow.title("Hold on!")
        global close
        close = True

        # create the label
        ttk.Label(warningwindow, text="Are you sure about closing an unsaved project?").place(x=250, y=30, anchor='center')

        # create the buttons
        ttk.Button(warningwindow, text='Close Without Saving', command=root.destroy, width=40).place(x=250, y=115, anchor='center')
        ttk.Button(warningwindow, text='Save and Close', command=saveButtonPressed, width=40).place(x=250, y=75, anchor='center')
        ttk.Button(warningwindow, text='Cancel', command=quitWarningWindow, width=40).place(x=250, y=155, anchor='center')

    else :
        # if saved, destroy the window
        root.destroy()

def quitWarningWindow() :
    global close
    close = False
    warningwindow.destroy()

# this function is the process that gets called for every thread
def processThread(index, fileNames, isThread, smallObjectsThresh) :

        # add the thread
        if isThread :
            global currentThreads
            id = threading.get_ident()
            if id not in currentThreads :
                currentThreads.append(id)


        file = fileNames[index]

        start = time.time()

        # get result
        nuclei, nucleiInFibre, fibrePositions, imageWidth, imageHeight = deepcell_functie(file, nucleiColourVar.get(), fibreColourVar.get(), doFibreCounting.get(), smallObjectsThresh)

        end1 = time.time()

        # convert image coordinates to relative between 0 and 1
        for i in range(len(nuclei)):
            nuclei[i][0] = float(nuclei[i][0]) / float(imageWidth)
            nuclei[i][1] = float(nuclei[i][1]) / float(imageHeight)
        for i in range(len(nucleiInFibre)):
            nucleiInFibre[i][0] = float(nucleiInFibre[i][0]) / float(imageWidth)
            nucleiInFibre[i][1] = float(nucleiInFibre[i][1]) / float(imageHeight)
        for i in range(len(fibrePositions)):
            fibrePositions[i][0] = float(fibrePositions[i][0]) / float(imageWidth)
            fibrePositions[i][1] = float(fibrePositions[i][1]) / float(imageHeight)


        end2 = time.time()

        print("file : ", end1 - start)

        # send the output to the table
        nucleiTable.inputProcessedData(nuclei, nucleiInFibre, fibrePositions, index)

        # close if necessary
        updateProcessedImages(fileNames)
        setUnsavedStatus()

        if isThread :
            if index >= len(fileNames) - nThreadsRunning :
                # close the threshold
                threadExitted(threading.get_ident())
            else :
                # keep on processing more images
                processThread(index + nThreadsRunning, fileNames, True, smallObjectsThresh)
        else :
            if index + 1 < len(fileNames) :
                # keep on processing more images
                processThread(index + 1, fileNames, False, smallObjectsThresh)
            else :
                # all images are done
                stopProcessing()

def updateProcessedImages(fileNames) :

    # change the label
    global totalImagesProcessed
    totalImagesProcessed += 1
    processingLabel['text'] = str(totalImagesProcessed) + " of " + str(len(fileNames)) + " Images Processed"

# this function gets called if a thread gets exitted
def threadExitted(id) :
    global currentThreads, totalImagesProcessed
    currentThreads.remove(id)
    if len(currentThreads) == 0 :
        stopProcessing()


# force ending the threads
def stopProcessing() :

    # end the threads
    global currentThreads, totalImagesProcessed
    for id in currentThreads :
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(id, 0)
            print('Exception raise failure')

    print("Still running threads (should be 1) :", threading.active_count())


    # empty threads
    currentThreads = []
    totalImagesProcessed = 0
    processImagesbutton['text'] = "Process Images"
    processImagesbutton.configure(command = processImages)
    processingLabel['text'] = ""

# process images button is presssed
def processImages() :

    # stop vorige threads
    stopProcessing()

    # get the fileNames
    fileNames = nucleiTable.getFileNames()
    setUnsavedStatus()

    # switch off process button
    global totalImagesProcessed
    totalImagesProcessed = 0
    processImagesbutton['text'] = 'Stop Processing'
    processImagesbutton.configure(command = stopProcessing)
    processingLabel['text'] = "0 of " + str(len(fileNames)) + " Images Processed"
    root.update()

    # start threading
    global nThreadsRunning, threadSlider
    nThreadsRunning = nThreads.get()
    if int(nThreads.get()) == 0 :
        processThread(0, fileNames, False, smallObjectsThreshold.get())
    else :
        # loop over the total number of threads and start the first n images
        for i in range(nThreadsRunning) :
            if i <= len(fileNames) - 1:
                t1 = threading.Thread(target=processThread, args=(i, fileNames, True, smallObjectsThreshold.get()), daemon=True)
                t1.start()
                print(t1)



def selectImages(root) :

    # get the filenames with a dialogbox
    fileNames = filedialog.askopenfilenames(filetypes=[('Image Files', ('.tif', '.png', '.jpg', '.jpeg', '.bmp', '.hdr'))], parent=root, initialdir="/", title='Please select a directory')

    if len(fileNames) != 0 :

        # stop processing
        stopProcessing()

        # enable the process image buttons
        processImagesbutton["state"] = 'enabled'

        # add them to the table
        global resaveImages
        resaveImages = True
        nucleiTable.addImages(fileNames)
        setUnsavedStatus()

# when leftclicking, the position of the cursor is sent to the table and imagecanvas
def leftClick(event) :
    nucleiTable.leftClick(root.winfo_pointerx(),root.winfo_pointery(), frm.winfo_rooty())
    if ImageCanvas.leftClick(root.winfo_pointerx(),root.winfo_pointery(), frm.winfo_rooty()) :
        setUnsavedStatus()

# when rightclicking, the position of the cursor is sent to the table and imagecanvas
def rightClick(event) :
    if ImageCanvas.rightClick(root.winfo_pointerx(),root.winfo_pointery(), frm.winfo_rooty()) :
        setUnsavedStatus()


def onwheel(event) :
    nucleiTable.onwheel(event.delta, root.winfo_pointerx(),root.winfo_pointery(), frm.winfo_rooty())

def motion(evet) :
    nucleiTable.motion(root.winfo_pointerx(),root.winfo_pointery(), frm.winfo_rooty())

# pass through the keypressing of the arrows to the imagecanvas to scroll around the imagecanvas
def onLeftPress(event):
    ImageCanvas.arrows(0)
def onUpPress(event):
    ImageCanvas.arrows(1)
def onRightPress(event):
    ImageCanvas.arrows(2)
def onDownPress(event):
    ImageCanvas.arrows(3)

def onZoomInPress(event) :
    ImageCanvas.zoom(ImageCanvasSize[0] / 2, ImageCanvasSize[1] / 2, 120)

def onZoomOutPress(event) :
    ImageCanvas.zoom(ImageCanvasSize[0] / 2, ImageCanvasSize[1] / 2, -120)

def deleteCurrentProject(root) :

    if currentProject != '' :
        # delete the project
        shutil.rmtree(BASE_PATH + 'Projects/' + currentProject)

        # remove the load button
        recentProjectsMenu.delete(recentProjectsMenu.index("Load '" + currentProject + "'"))
        global recentProjects
        recentProjects.remove(currentProject)
        if len(recentProjects) == 0 :
            fileMenu.entryconfig("Recent Projects", state='disabled')
        settingsChanged()

        # create empty project
        createEmptyProject()

        if currentProject == autoSaveName :
            fileMenu.entryconfig("Load Automatic Save", state='disabled')

def createEmptyProject() :

    # reset everything
    stopProcessing()
    nucleiTable.reset()
    ImageCanvas.reset()

    # set the save button
    saveButton['state'] = 'enabled'
    saveButton['text'] = 'Save As'
    processImagesbutton['state'] = 'disabled'
    fileMenu.entryconfig(fileMenu.index("Delete Current Project"), state=DISABLED)

    # set window title
    root.title("Cellen Tellen - New Project (Unsaved)")
    global currentProject
    currentProject = ''

    # call for project name
    createProjectnameWindow(True)

def loadProjectFromExplorer() :

    # ask a folder
    folder = filedialog.askdirectory(initialdir=os.path.normpath(BASE_PATH + "Projects"), title="Choose a Project Folder")

    # load this shit
    if (folder != '') and os.path.isdir(BASE_PATH + 'Projects/' + os.path.basename(folder)):
        loadProject(os.path.basename(folder))

# this function loads a project, given a directory
def loadProject(directory) :

    # stop processing
    stopProcessing()

    # set the window title
    root.title("Cellen Tellen - Project '" + directory + "'")
    global currentProject
    currentProject = directory

    # set the save button
    saveButton['state'] = 'disabled'
    saveButton['text'] = 'Save'
    fileMenu.entryconfig(fileMenu.index("Delete Current Project"), state=NORMAL)

    # do the recent projects shit
    if os.path.isdir(BASE_PATH + 'Projects/' + directory) and not directory == autoSaveName:
        # remove it first
        if directory in recentProjects :
            recentProjectsMenu.delete("Load '" + directory + "'")
            recentProjects.remove(directory)

        recentProjectsMenu.insert_command(index=0, label="Load '" + directory + "'",
                                          command=lambda directory=directory: loadProject(directory))
        recentProjects.insert(0, directory)
        fileMenu.entryconfig("Recent Projects", state='normal')
        if (len(recentProjects) > MAX_RECENT_PROJECTS):
            # remove the last
            recentProjectsMenu.delete("Load '" + recentProjects[-1] + "'")
            recentProjects.pop(len(recentProjects) - 1)

        settingsChanged()

    # load the project
    nucleiTable.loadProject(BASE_PATH + 'Projects/' + directory)
    global resaveImages
    resaveImages = False

    # if there are images loaded
    if nucleiTable.imagesAvailable() :
        processImagesbutton['state'] = 'enabled'
    else :
        processImagesbutton['state'] = 'disabled'

def saveButtonPressed() :

    # save as if necessary
    if currentProject == '' :
        createProjectnameWindow()
    else :
        # perform normal save
        saveProject(currentProject)


def saveProject(directory, saveas=False) :

    # do we want to save the images
    global resaveImages
    if (saveas) :
        resaveImages = True

    # don't autosave if not needed
    if not (autoSaveTime.get() < 0 and directory == autoSaveName) :
        if (directory != autoSaveName) :
            # destroy the save as window if it exists
            if not foldernameWindowSaveButton is None :
                foldernameWindowSaveButton.master.destroy()

            # set the save button
            saveButton['state'] = 'disabled'
            saveButton['text'] = 'Save'
            fileMenu.entryconfig(fileMenu.index("Delete Current Project"), state=NORMAL)

            # change the current project name
            global currentProject
            currentProject = directory
            root.title("Cellen Tellen - Project '" + currentProject + "'")

            # do the recent projects shit
            if not os.path.isdir(BASE_PATH + 'Projects/' + directory):
                recentProjectsMenu.insert_command(index=0, label="Load '" + directory + "'",
                                               command=lambda directory=directory: loadProject(directory))
                recentProjects.insert(0, directory)
                fileMenu.entryconfig("Recent Projects", state='normal')
                if (len(recentProjects) > MAX_RECENT_PROJECTS) :
                    # remove the last
                    recentProjectsMenu.delete("Load '" + recentProjects[-1] + "'")
                    recentProjects.pop(len(recentProjects)-1)

                settingsChanged()


        else :
            # set the automatic save entry
            fileMenu.entryconfig("Load Automatic Save", state='normal')
            if (autoSaveTime.get() > 0 ) : # recall the autosave
                updateAutosaveTime()

        # create the folder
        if not os.path.isdir(BASE_PATH + 'Projects/' + directory):
            os.mkdir(BASE_PATH + 'Projects/' + directory)

        # create saving popup
        savingPopup = Toplevel(root)
        savingPopup.grab_set()
        savingPopup.title("Saving....")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        savingPopup.geometry("400x200+" + str(int(screen_width/2 - 400/2)) + "+" + str(int(screen_height/2 - 200/2)))
        ttk.Label(savingPopup, text="Saving to '" + directory + "' ...").place(x=200, y=75, anchor='center')
        savingPopup.update()
        root.update()
        savingPopup.update()
        savingPopup.protocol("WM_DELETE_WINDOW", dontdoshit())

        # save the table
        nucleiTable.saveTable(directory)

        # save the originals
        if (resaveImages or directory == autoSaveName) :
            nucleiTable.saveOriginals(directory)
        resaveImages = False

        # save the altered images
        if (saveAlteredImagesBoolean.get() == 1 or directory == autoSaveName) :
            nucleiTable.saveAlteredImages(directory)

        # save the data
        nucleiTable.saveData(directory)

        # destroy the popup
        savingPopup.destroy()

        # als het nodig is, close
        if (close) :
            root.destroy()

def dontdoshit() :
    pass

def setUnsavedStatus() :

    # set the unsaved status
    if (currentProject != '') :
        root.title("Cellen Tellen - Project '" + currentProject + "' (Unsaved)")
        saveButton['state'] = 'enabled'
        saveButton['text'] = 'Save'

# change the displayed image channels
def setImageChannels() :
    ImageCanvas.setChannels(blueChannelBool.get(), greenChannelBool.get(), redChannelBool.get())
    settingsChanged(True)

# change the third button
def setIndicators() :
    # set the indicators
    ImageCanvas.setIndicators(showNucleiBool.get(), showFibresBool.get())
    settingsChanged(True)

    # set which indication
    global indicatingNuclei
    if showFibresBool.get() and not showNucleiBool.get() :
        indicatingNuclei = False
        whichIndicatorButton['text'] = 'Manual : Fibres'
        whichIndicatorButton['state'] = 'disabled'

    if (showFibresBool.get() and showNucleiBool.get()) :
        whichIndicatorButton['state'] = 'enabled'

    if not showFibresBool.get() and showNucleiBool.get() :
        indicatingNuclei = True
        whichIndicatorButton['text'] = 'Manual : Nuclei'
        whichIndicatorButton['state'] = 'disabled'

    # pass through the indications to the imagecanvas
    ImageCanvas.setWhichIndcation(indicatingNuclei)

# change the indications
def changeIndications() :
    global indicatingNuclei
    if indicatingNuclei :
        indicatingNuclei = False
        whichIndicatorButton['text'] = 'Manual : Fibres'
    else :
        indicatingNuclei = True
        whichIndicatorButton['text'] = 'Manual : Nuclei'
    ImageCanvas.setWhichIndcation(indicatingNuclei)

# this function is used while opening the program the first time, to adjust the window size
def changeWindowSize(event) :
    factor = 100
    if event.char == 'a' : # make smaller (but same ratio)
        table.ImageCanvasSize = (int(table.ImageCanvasSize[0] - table.ImageCanvasSize[0]/factor), int((table.ImageCanvasSize[0] - table.ImageCanvasSize[0]/factor) * ImageCanvasStandardFactor))
    elif event.char == 'z' : # make bigger (but same ratio)
        table.ImageCanvasSize = (int(table.ImageCanvasSize[0] + table.ImageCanvasSize[0]/factor), int((table.ImageCanvasSize[0] + table.ImageCanvasSize[0]/factor) * ImageCanvasStandardFactor))

    # update button gridpositions
    frm.grid_columnconfigure(0, minsize=table.ImageCanvasSize[0]+4)

    # update canvas
    ImageCanvas.updateSize(table.ImageCanvasSize)

# initialised the ajdustment of the window size, the first time you boot up the program (if there is not general.npy)
def startWindowView() :
    global setViewSizeWindow

    # initialize window, size and position
    setWindowViewWindowSize = (500, 130)
    setViewSizeWindow = Toplevel(root)
    setViewSizeWindow.grab_set()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    setViewSizeWindow.geometry(str(setWindowViewWindowSize[0]) + 'x' + str(setWindowViewWindowSize[1]) + "+" + str(int(screen_width/2 - setWindowViewWindowSize[0]/2)) + "+" + str(int(screen_height/2 - setWindowViewWindowSize[1]/2)))
    setViewSizeWindow.title("Set Window Size")
    setViewSizeWindow.focus_force()

    # set key strokes bindings, link to changeWindowSize
    setViewSizeWindow.bind('a', changeWindowSize)
    setViewSizeWindow.bind('z', changeWindowSize)
    setViewSizeWindow.protocol("WM_DELETE_WINDOW", endWindowView)

    # create 'done' button, link to endWindowView
    setViewSizeFrame = ttk.Frame(setViewSizeWindow, padding="10 10 120 120")
    setViewSizeFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    ttk.Label(setViewSizeFrame, text="Use 'a' and 'z' keys to adjust the window view.").grid(column=0, row=0, pady=5)
    ttk.Button(setViewSizeFrame, text="Done", command= endWindowView, width=14).grid(column=0, row=1, pady= 15)
    setViewSizeFrame.grid_columnconfigure(0, minsize = setWindowViewWindowSize[0])


def endWindowView() :

    # destroy the viewsizewindow
    if setViewSizeWindow != None :
        setViewSizeWindow.destroy()

    # create the table
    global nucleiTable
    nucleiTable = Table(root)
    nucleiTable.setImageCanvas(ImageCanvas)
    ImageCanvas.setTable(nucleiTable)

    # save default settings
    settingsChanged(2)




# set better resolution
if int(platform.release()) >= 8:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)

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
photo = PhotoImage(file = BASE_PATH + "icon.png")
root.iconphoto(False, photo)



frm = ttk.Frame(root, padding="10 10 120 120")
frm.grid(column=0, row=0, sticky=(N, W, E, S))





# configure the menu
menubar = Menu(root)
root.config(menu=menubar)

menubar.config(font=("TKDefaultFont", 20))
fileMenu = Menu(menubar, tearoff=0)
fileMenu.add_command(label="New Empty Project", command=createEmptyProject)
fileMenu.add_command(label="Save Project As", command=createProjectnameWindow)
delButton = fileMenu.add_command(label="Delete Current Project", command=lambda: deleteCurrentProject(root))
fileMenu.entryconfig(fileMenu.index("Delete Current Project"), state=DISABLED)
fileMenu.add_command(label="Load From Explorer", command=loadProjectFromExplorer)
fileMenu.add_separator()

# automatic save
resaveImages = False
autoSaveJob = None
autoSaveName = 'AUTOSAVE'
autoSaveTime = IntVar()
autoSaveTime.set(-1) # in seconds
saveAlteredImagesBoolean = IntVar()
saveAlteredImagesBoolean.set(0)
doFibreCounting = IntVar()
doFibreCounting.set(0)

# add the automatic save command
fileMenu.add_command(label='Load Automatic Save', state='disabled', command = lambda autoSaveName=autoSaveName: loadProject(autoSaveName))
# if the automatic save already exists, link to it via the command
if os.path.isdir(BASE_PATH + 'Projects/' + autoSaveName) :
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
settingsMenu.add_command(label="Settings", command=lambda: createSettingsWindow(root))
menubar.add_cascade(label="Settings", menu=settingsMenu)

# help menu
helpMenu = Menu(menubar, tearoff=0)
helpMenu.add_command(label="Help", command=openGithub)
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



# initialised table, the object itself is not yet created until we have set the window view
nucleiTable = None

# key bindings, zooming, clikcing with mouse, aswell as moving and zoom in the image with the keyboard
root.bind('<ButtonPress-1>', leftClick)
root.bind('<ButtonPress-3>', rightClick)
root.bind('<MouseWheel>', onwheel)
root.bind('<Motion>', motion)
root.bind('<Left>', onLeftPress)
root.bind('<Right>', onRightPress)
root.bind('<Up>', onUpPress)
root.bind('<Down>', onDownPress)
root.bind('=', onZoomInPress)
root.bind('+', onZoomInPress)
root.bind('-', onZoomOutPress)
root.bind('_', onZoomOutPress)





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
ttk.Button(frm, text="Load Images", command= lambda: selectImages(root), width=14).grid(column=1, row=0)
processImagesbutton = ttk.Button(frm, text="Process Images", command=processImages, width=14, state='disabled')
processImagesbutton.grid(column=2, row=0)

# image channel selection (which colour channels are displayed)
ttk.Label(frm, text="  Channels :   ").grid(column=1, row=2, sticky='w')
blueChannelCheckButton = ttk.Checkbutton(frm, text="Blue Channel", onvalue=True, offvalue=False, variable=blueChannelBool, command=setImageChannels)
blueChannelCheckButton.grid(column=2, row=2, sticky='w')
greenChannelCheckButton = ttk.Checkbutton(frm, text="Green Channel", onvalue=True, offvalue=False, variable=greenChannelBool, command=setImageChannels)
greenChannelCheckButton.grid(column=3, row=2, sticky='w')
redChannelCheckButton = ttk.Checkbutton(frm, text="Red Channel", onvalue=True, offvalue=False, variable=redChannelBool, command=setImageChannels)
redChannelCheckButton.grid(column=4, row=2, sticky='w')

# indicator selections (which indicators are shown)
ttk.Label(frm, text="  Indicators : ").grid(column=1, row=4, sticky='w')
showNucleiCheckButton = ttk.Checkbutton(frm, text="Nuclei", onvalue=True, offvalue=False, variable=showNucleiBool, command=setIndicators)
showNucleiCheckButton.grid(column=2, row=4, sticky='w')
showFibresCheckButton = ttk.Checkbutton(frm, text="Fibres", onvalue=True, offvalue=False, variable=showFibresBool, command=setIndicators)
showFibresCheckButton.grid(column=3, row=4, sticky='w')


processingLabel = ttk.Label(frm, text="")
processingLabel.grid(column=1, row=5, columnspan=4)


# save altered images and table
saveButton = ttk.Button(frm, text='Save As', width=14, command=saveButtonPressed, state='enabled')
saveButton.grid(column=4, row=0)

# set indicators
whichIndicatorButton = ttk.Button(frm, width=14, text='Manual : Nuclei', command=changeIndications, state='enabled')
whichIndicatorButton.grid(column=3, row=0)

# load the general save (save settings, window view, etc)
if os.path.isfile(BASE_PATH + 'general.npy'):
    # get the list
    settingsarr = np.load(BASE_PATH + 'general.npy', allow_pickle=True).tolist()

    # set the variables
    fibreColourVar.set(settingsarr[0])
    previousFibreColourVar.set(settingsarr[0])
    nucleiColourVar.set(settingsarr[1])
    previousNucleiColourVar.set(settingsarr[1])
    autoSaveTime.set(settingsarr[2])
    updateAutosaveTime()
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
    endWindowView()

else :
    # start windowsize selection
    ImageCanvas = Zoom_Advanced(root, nucleiTable)
    startWindowView()


# load the list of recent projects if these projects exist
if os.path.isdir(BASE_PATH + 'Projects') :
    temp = list(recentProjects)
    for foldername in temp:
        if os.path.isdir(BASE_PATH + 'Projects/' + foldername) and foldername != '' :
            recentProjectsMenu.add_command(label="Load '" + foldername + "'", command=lambda foldername=foldername: loadProject(foldername))
        else :
            recentProjects.remove(foldername)
else :
    os.mkdir(BASE_PATH + 'Projects')

if (len(recentProjects) == 0) :
    fileMenu.entryconfig("Recent Projects", state='disabled')


# set the channels and indicators for the imagecanvas
indicatingNuclei = True
setImageChannels()
setIndicators()


# set grid sizes
frm.grid_columnconfigure(0, minsize=table.ImageCanvasSize[0]+4)
frm.grid_columnconfigure(1, minsize=ButtonRowWidth)
frm.grid_columnconfigure(2, minsize=ButtonRowWidth)
frm.grid_columnconfigure(3, minsize=ButtonRowWidth)
frm.grid_columnconfigure(4, minsize=ButtonRowWidth)
frm.grid_rowconfigure(1, minsize=10)
frm.grid_rowconfigure(3, minsize=1)


root.update()

# this protocol calls the createwarningwindow if we close the program (instead of direclty exiting)
root.protocol("WM_DELETE_WINDOW", createWarningWindow)
root.mainloop() # tkinter main loop
