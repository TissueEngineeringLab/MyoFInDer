---
layout: default
title: Troubleshooting
---

[Home page](index.markdown)

Cellen-Tellen is a free and open-source software developed as a side-project.
As such, **it comes "as is" with no warranty of any kind**. That being said, 
its developer will gladly do their best to maintain it and fix any bug brought 
to his attention, within reasonable limits.

When encountering a problem with Cellen-Tellen, please **first thoroughly read 
the [Installation](installation.markdown) and [Usage](usage.markdown) 
sections**. If you cannot find information about your problem there, check if 
it isn't listed in **the [Common problems](#common-problems) section below**. 
If you still cannot find anything, you can also check **the 
[Issues](https://github.com/WeisLeDocto/Cellen-Tellen/issues) and 
[Discussions](https://github.com/WeisLeDocto/Cellen-Tellen/discussions) pages**
of the GitHub repository.

If your problem has never been reported before, **the best way to report it is
to [open a new issue](https://github.com/WeisLeDocto/Cellen-Tellen/issues/new) 
on GitHub**. Issues are not only intended for bugs, they can also be opened for
requesting help or suggesting improvements. Alternatively, you can also 
**[start a new discussion](https://github.com/WeisLeDocto/Cellen-Tellen/discussions/new/choose)
on GitHub** for chatting with the maintainer in a more informal way. Both of 
these solutions require you to 
[create a GitHub account](https://github.com/join). If for some reason you 
would absolutely refuse to create a GitHub account, you can also 
<a href="mailto:antoine.weisrock@gmail.com">email the maintainer</a>, although
I would prefer you not to contact me this way.

# Common problems

- **I do not have the permissions to install Python, or to run the Windows 
  installer**
  
  Depending on your computer configuration, you might need specific permissions 
  to install Python and/or to run the Windows installer of Cellen-Tellen. If
  that's the case, you will probably be asked to enter an administrator 
  password during the installation procedure. If you don't have the necessary 
  privileges, your only option is then to contact your local administrator.

- **Nuclei and/or fibers from a previous image are persisting on the screen**

  It may happen that detected nuclei and fibers from a previous image keep
  displaying on the screen even after switching to another image. These "ghost"
  nuclei will persist no matter what you try to do. This is a known bug, that
  fortunately only affect the display and not the data. To reset the display, 
  save your project, close Cellen-Tellen, re-open it, and load your project. 
  Please send feedback to the developer if you would encounter this bug, it 
  will help him troubleshoot it.

- **I cannot load my project from the file explorer**

  When you want to load a Cellen-Tellen project from the explorer, make sure 
  that the file explorer path corresponds to that of folder containing the 
  project files. For example if you want to load the 
  *C:\Users\User\Desktop\Proj* project, the "Selection" section of the file
  explorer should display exactly this path. In practice, it means you have to 
  double-click on the folder containing your project files before clicking on 
  Ok. If despite loading your project from the right path you're still not 
  able to open it, please report it as a bug to the developer.

- **Not a single nucleus is detected when running a computation**

  First, double-check that the number of detected nuclei is indeed 0 in the 
  information frame on the right of the application. If it is not, it is likely
  that the checkbox enabling the display of the detected nuclei is unchecked. 
  Otherwise, this is a graphical bug that should be reported. If 0 nuclei were
  detected, try to re-run computations with different sets of parameters. Some
  parameters have a strong influence on the detection, and a bit of fine-tuning 
  might be required. Also make sure that the right channel is selected for
  nuclei detection in the Settings menu. If the problem persists, you can
  request support on the GitHub page.

- **No fiber is detected when running a computation**

  First, double-check that the detected fiber area is indeed 0 in the 
  information frame on the right of the application. If it is not, it is likely
  that the checkbox enabling the display of the detected fibers is unchecked. 
  Otherwise, this is a graphical bug that should be reported. If no fiber was
  detected, try to re-run computations with different sets of parameters. Some
  parameters have a strong influence on the detection, and a bit of fine-tuning 
  might be required. Also make sure that the right channel is selected for
  fiber detection in the Settings menu. If the problem persists, you can
  request support on the GitHub page.

[Home page](index.markdown)
