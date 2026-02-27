---
layout: default
title: Troubleshooting
---

[Home page](index.markdown)

MyoFInDer is a free and open-source software developed as a side-project. As 
such, **it comes "as is" with no warranty of any kind**. That being said, its 
developer will gladly do its best to maintain it and fix any bug brought to his 
attention, within reasonable limits.

When encountering a problem with MyoFInDer, please **first thoroughly read the 
[Installation](installation.markdown) and [Usage](usage.markdown) sections**. 
If you cannot find information about your problem there, check if it isn't 
listed in **the [Common problems at runtime](#common-problems-at-runtime) or 
[Installation problems](#installation-problems) sections below**. If you 
still cannot find anything, you can also check **the 
[Issues](https://github.com/TissueEngineeringLab/MyoFInDer/issues) and 
[Discussions](https://github.com/TissueEngineeringLab/MyoFInDer/discussions) 
pages** of the GitHub repository.

If your problem has never been reported before, **the best way to report it is
to [open a new issue](https://github.com/TissueEngineeringLab/MyoFInDer/issues/new) 
on GitHub**. Issues are not only intended for bugs, they can also be opened for
requesting help or suggesting improvements. Alternatively, you can also 
**[start a new discussion](https://github.com/TissueEngineeringLab/MyoFInDer/discussions/new/choose)
on GitHub** for chatting with the maintainer in a more informal way. Both of 
these solutions require you to 
[create a GitHub account](https://github.com/join). If for some reason you 
would absolutely refuse to create a GitHub account, you can also 
<a href="mailto:antoine.weisrock@gmail.com">email the maintainer</a>, although
I would prefer you not to contact me this way.

# Bug report guidelines

In case you encounter a bug and cannot solve it using the documentation 
presented here, please report it to the maintainer. When doing so, make sure to
include the following information:
- Describe the exact steps you took (type of installer you use, buttons on 
  which you click, etc.).
- Describe what the expected behavior was versus what happened instead.
- Describe the system on which you're running MyoFInDer (OS type
  (Windows/linux/macOS) and version, Python version and provenance 
  (*python.org*, Microsoft Store, for example), if you're admin on this 
  system).
- If relevant, any material that can allow to reproduce the issue (likely 
  images).
- If the bug prevents MyoFInDer's installation with the installer, please 
  attach the installation logs which you'll find in `%TEMP%\MyoFInDer\` 
  (copy-paste as-is in the file explorer's address bar).
- If the bug prevents MyoFInDer's installation in the terminal, please attach 
  the `pip install` logs as displayed in the terminal.
- If the bug occurs at runtime, please attach the log file that can be found 
  following the instructions in section 
  [Retrieving the log messages](usage.markdown/#42-retrieving-the-log-messages).

# Installation problems

- **I do not have the permissions to install Python, or to run the Windows 
  installer**
  
  Depending on your computer configuration, you might need specific permissions 
  to install Python and/or to run the Windows installer of MyoFInDer. If
  that's the case, you will probably be asked to enter an administrator 
  password during the installation procedure. If you don't have the necessary 
  privileges, your only option is then to contact your local administrator.

- **The installer says Python is missing or no compatible version is found**

  MyoFInDer requires Python 3.9, 3.10, 3.11, 2.12 or 3.13 to be installed. In
  addition, installing the version provided on the official *python.org* 
  website is strongly recommended, instead for example of Python versions
  distributed in the Microsoft Store.

# Common problems at runtime

- **I cannot load a project into MyoFInDer**

  When you want to load a MyoFInDer project from the explorer, make sure 
  that the file explorer path corresponds to that of folder containing the 
  project files. For example if you want to load the 
  *C:\Users\User\Desktop\Proj* project, the "Selection" section of the file
  explorer should display exactly this path. In practice, it means you have to 
  double-click on the folder containing your project files before clicking on 
  Ok.
  
  If you're getting an error when trying to open a project, it might be that 
  this project was generated in a different version of MyoFInDer, which isn't 
  compatible with your version. We try to maintain maximum forward- and 
  backward-compatibility between the versions, but some major changes require 
  breaking compatibility. If truly necessary, a converter script can be 
  provided by the maintainer to upgrade the format of your project's data.

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
