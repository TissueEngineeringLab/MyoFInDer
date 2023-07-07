---
layout: default
title: Usage
---

[Home page](index.markdown)

This page describes the **procedures for using Cellen-Tellen** and its 
different features. Everything you have to know about the module is explained 
here, please report it if you consider that this section is incomplete.

Index of the Usage page :

1. [Starting Cellen-Tellen](#1-starting-cellen-tellen)
   1. [Using the shortcuts (Windows installer only)](#11-using-the-shortcuts-windows-installer-only)
   2. [From the command line](#12-from-the-command-line)
   3. [Startup window](#13-startup-window)
2. [Basic usage](#2-basic-usage)
   1. [Loading images](#21-loading-images)
   2. [Tuning the settings](#22-tuning-the-settings)
   3. [Starting a computation](#23-starting-a-computation)
   4. [Adjusting the display](#24-adjusting-the-display)
   5. [Manually correcting the output](#25-manually-correcting-the-output)
3. [Managing your projects](#3-managing-your-projects)
   1. [Saving your data into a project](#31-saving-your-data-into-a-project)
   2. [Loading data from an existing project](#32-loading-data-from-an-existing-project)
   3. [Operations on saved projects](#33-operations-on-saved-projects)
4. [Advanced usage](#4-advanced-usage)
   1. [Command-line option](#41-command-line-option)
   2. [Retrieving the log messages](#42-retrieving-the-log-messages)

# 1. Starting Cellen-Tellen

There are **two possible ways to start Cellen-Tellen**, depending if the 
application was installed using the Windows installer or not. This section
re-uses names introduced on the [Installation page](installation.markdown), so 
it is advised to first read the Installation page before this one.

## 1.1 Using the shortcuts (Windows installer only)

The first and most straightforward way to start Cellen-Tellen is to **click on
the Menu-bar or Desktop shortcuts** that were created when running the Windows 
installer. It can also be started by searching for "Cellen-Tellen" in the 
Menu-bar, or by any other standard way offered by Windows for opening 
applications.

## 1.2 From the command line

*In this section, replace* `python` *with* `python3` *or* `python3.x` 
*(7<=x<=10) if necessary.*

### 1.2.1 After manual installation

No matter which installation method you chose, **it is always possible to start
Cellen-Tellen from the command-line**. This operation is however a bit more 
complex if you used the Windows installer, so this specific case is covered 
separately in the 
[next subsection](#122-after-installation-using-the-windows-installer).

If you installed Cellen-Tellen in a virtual environment, you should first 
**activate it** :

```console
C:\Users\User><Path to your venv>\Scripts\activate.bat
(venv) C:\Users\User>
```

With `<Path to your venv>` the path to the virtual environment you created. 
Or in Linux :

```console
user@machine:~$ source <Path to your venv>/bin/activate
(venv) user@machine:~$ █
```

Then, you can simply **start Cellen-Tellen** by running the following line 
(ignore the `venv` part if not running in a virtual environment) :

```console
(venv) C:\Users\User>python -m CellenTellen
```

Or in Linux :

```console
(venv) user@machine:~$ python -m CellenTellen
```

### 1.2.2 After installation using the Windows installer

Starting Cellen-Tellen from the command-line might be your only option if for 
some reason **you cannot start it using the shortcuts** created by the 
installer (in which case you should report that as a bug). When run, the 
installer deploys a virtual environment at 
`C:\Users\<User>\AppData\Local\CellenTellen\venv`, where `<User>` is your 
username on the computer. First, **activate this virtual environment** by 
running :

```console
C:\Users\User>C:\Users\User\AppData\Local\CellenTellen\venv\Scripts\activate.bat
(venv) C:\Users\User>
```

Then, you can **start Cellen-Tellen** the same way as described in the previous 
subsection :

```console
(venv) C:\Users\User>python -m CellenTellen
```

Or in Linux :

```console
(venv) user@machine:~$ python -m CellenTellen
```

## 1.3 Startup window

Once Cellen-Tellen is running, **a console should first appear** with log 
messages displaying in it. If started from the command-line, this console is 
already open and is the one you typed your commands in. This console simply 
displays the log messages, which may be useful for tracking errors.

Shortly after the console, **a Splash window should also appear** while the 
module is loading. It can take up to 30s for the application to open, and even 
more on the first run as it has to download some data. The Splash window should 
look as such :

<img src="./usage_images/splash.png" width="300">

# 2. Basic usage

## 2.1 Loading images

The first step for processing images is to **load them in the interface**. To 
do so, click on the *Load Images* button located at the top-right of the 
interface.

**A file explorer then appears**, in which you can browse the files in your 
computer and in the network drives. In this explorer, select one or several 
images to import and click on *Open*.

Information on the imported images is then displayed in **the information 
frame** on the right of the interface. 

In the main frame, **the currently selected image is displayed**. You can 
select another image by left-clicking on it in the information frame. 

It is also possible to **delete a loaded image** by clicking on the *X* Delete 
button at the top-right of its information display. You will be asked to 
confirm your choice in a popup window.

**The checkboxes of the images** allow to apply the Delete and Process 
operations to only part of the loaded images. The deletion of all the checked 
images is achieved by using the master Delete button. The master checkbox 
allows to (un)select all the images at once.

## 2.2 Tuning the settings

Before processing the loaded images, you might want to **adjust the processing
parameters**. That can be done by clicking on the Settings button, that opens a
new window containing the Settings menu.

In this menu, you can adjust various parameters like the channels to use for
the fibers and nuclei or thresholds to use when processing images. **The 
settings are applied as soon as you modify them**, there is no need to validate 
your choice. Just close this window when you're done.

## 2.3 Starting a computation

Once you have adjusted the computation parameters, it is time to **start 
processing images**. To do so, simply click on the *Process Images* button.

> If you use images from a network drive, is advised to first save the project
> before processing them. This way, the images will first be copied locally and
> Cellen-Tellen won't be affected by network issues.

All the checked images then start being processed, and a message displays the
progress status. The images are processed one by one, in the same order as they
appear in the information frame.

On each processed image **the nuclei and fibers are detected**, and the 
information on the right frame is updated accordingly. 

The display for the selected image in the main frame might also be updated, 
depending on the selected display options. **The positive and negative nuclei 
are displayed** in different colors, and these color vary depending on the 
channels carrying the nuclei and fiber information.

It is possible to **stop the computation** while it is running by clicking on 
the *Stop Processing* button. It might take a few seconds for the computation 
to effectively stop.

## 2.4 Adjusting the display

At the top-right of the interface, several checkboxes allow to **tune the 
display of the currently selected image** in the main frame. It is possible to 
choose which channels are displayed, and if the nuclei and fibers overlay are 
added.

Using the mouse scroll wheel, **you can zoom in and out** on the displayed 
image. The *-*, *_*, *+* and *=* keys also allow zooming in and out. Click on 
the mouse wheel and drag to **move the view** on a zoomed image.

## 2.5 Manually correcting the output

Once the images have been processed, you can **manually correct the detected
nuclei** by adding, inverting or deleting ones. To do so, the nuclei overlay 
must be enabled. To add a nucleus, left-click on an area where no nucleus is 
present. To invert a nucleus, i.e. switch it from positive to negative or 
vice-versa, left-click on an already existing one. And to delete a nucleus, 
right-click on an already existing one.

It is also possible to **invert or delete multiple nuclei at once**. To do so,
left- or right-click and drag to form a selection box. All the nuclei inside
the selection box are inverted or deleted, depending on the side of the click.

# 3. Managing your projects

## 3.1 Saving your data into a project

In Cellen-Tellen the **data is saved as a project**, which means that the data 
for all the loaded images is saved at once. To save a project, simply click on 
the *Save As* button at the top-right of the interface. Alternatively, you can 
also click on the *Save Project As* button in the *File* menu.

A file explorer then appears, in which you have to **select the folder in which 
to save the project**. This folder has to be a newly created one. To save in a 
new folder, place the file explorer in the parent folder that will contain your 
new folder, enter the name of the new folder in the *File name* field of the 
explorer, and validate using the *Save* button.

If you look inside a saved project folder, you will find first an Excel file
containing a **summary of the detected nuclei and fibers** for each image in 
the project. Then, a `settings.pickle` file containing the setting values at 
the moment when the project was saved. The `data.pickle` files contains the 
location and nature of all the detected nuclei and fibers. The original images
are copied and saved to the `Original Images` folder, so the project folder 
contains all the information needed for reloading the project. Optionally, if 
the *Save Images with Overlay* setting is enabled, an `Overlay Images` folder
contains the images with an overlay showing the detected fibers and nuclei.

## 3.2 Loading data from an existing project

To **load data from an existing project**, first click on the *Load From 
Explorer* button in the *File* menu.

A file explorer then appears, in which you have to **select the project folder 
to load**. It is not sufficient to simply have the name of the folder 
highlighted, you need to double-click on it to place the explorer inside the 
folder to open. Once you are inside the project to open, validate your choice 
using the *Ok* button.

After loading the project, all the images it contains should be listed in the
information frame and the detected nuclei and fibers should also appear in the
nuclei and fiber overlays. 

## 3.3 Operations on saved projects

The saved projects can be located anywhere on the computer, preferably in 
folders where Cellen-Tellen has read and write access. Because they contain all
the information needed to reconstruct a project, **the project folders can be
renamed or moved**, including to a different computer. They can also be 
compressed for sharing. **The project folders can be safely deleted**, with no
impact on the behavior of Cellen-Tellen.

# 4. Advanced usage

## 4.1 Command-line option

A single command-line option is available when starting Cellen-Tellen from the
console. It allows to **disable logging**, by adding the `-n` or `--nolog` 
option. It disables both the display of log messages in the console, and 
recording of the log messages to the log file.

## 4.2 Retrieving the log messages

The log messages are, if possible, recorded to an application folder whose 
location depends on the OS. On Linux and macOS, the application folder is 
located in `/home/<user>/.Cellen-Tellen`. On Windows, the application folder
is located in `C:\Users\<user>\AppData\Local\Cellen-Tellen`. This application 
folder normally contains only the log messages for the last run of the 
application, as well as a `settings.pickle` file containing the last used 
settings.

[Home page](index.markdown)
