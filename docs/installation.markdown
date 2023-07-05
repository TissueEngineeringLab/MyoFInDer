---
layout: default
title: Installation
---

[Home page](index.markdown)

As a Python module, Cellen-Tellen can be installed on almost any computer able
to run a version of Python between 3.7 and 3.10. It is in particular fully 
supported on **Windows 8 and later**, and on **Ubuntu 18.04 and later**. 

Because the installation and use as a Python module might not be 
straightforward for every user, a very **basic Windows installer** is also 
provided for convenience.

Index of the Installation page :

1. [On Windows](#1-on-windows)
   1. [Install Python](#11-install-python)
   2. [Installation of Cellen-Tellen using the Windows installer](#12-installation-of-cellen-tellen-using-the-windows-installer)
   3. [Installation of Cellen-Tellen from console](#13-installation-of-cellen-tellen-from-console)
2. [On Linux and macOS](#2-on-linux-and-macos)
   1. [Check your Python version](#21-check-your-python-version)
   2. [[Optional] Deploy a virtual environment](#22-optional-deploy-a-virtual-environment)
   3. [Install Cellen-Tellen](#23-install-cellen-tellen)

# 1. On Windows

## 1.1 Install Python

On Windows, Python is not natively installed. You can **first check if it is 
already installed on your machine** by typing `python --version` in a terminal. 
In case of failure you get a message similar to :

```console
C:\Users\User>python --version
'python' is not recognized as an internal or external command,
operable program or batch file.
```

Otherwise, you get a message displaying the installed version of Python :
```console
C:\Users\User>python --version
Python 3.9.7
```

> To open a terminal on Windows, you can search for the program called Command 
> Prompt (sometimes abbreviated cmd) and execute it. This terminal is the one 
> used in the presented code snippets. Alternatively, a more advanced terminal 
> program called Windows PowerShell can also be used.

If Python is not installed, or if the installed version is not between 3.7 and 
3.10 **you need to install a Python version between 3.7 and 3.10**. To do so,
you have two possible options.

### 1.1.1 Install Python from the Microsoft Store

**All the maintained versions of Python are available for installation in the 
Microsoft Store** application. This is the easiest way to install Python on a 
Windows machine, provided that your administrator does not restrict the 
software catalogue of the Microsoft Store.

Simply search for the Microsoft Store application, start it, search for Python,
and install the desired version.

Once Python is installed, you can **double-check the installation** by running 
again `python --version`.

### 1.1.2 Install Python from an installer

**On Python's [website](https://www.python.org/downloads/windows/) you can find 
.exe Windows installers for a number of Python versions**. Select the one you 
want (preferably a stable release), download the installer, run it, and follow
the instructions of the installation wizard. Make sure to check the 
*Add python.exe to PATH* checkbox.

Once Python is installed, you can **double-check the installation** by running 
again `python --version`.

## 1.2 Installation of Cellen-Tellen using the Windows installer

For convenience, **a very basic installer is provided for Windows users**. It 
requires a compatible version of Python to be installed, as described in the
previous section.

This installer makes user's life easier by :

- Handling the installation of the Cellen-Tellen module
- Adding Desktop and Menu Bar shortcuts for starting Cellen-Tellen
- Enabling the Recent Projects feature in the application

Note that compared to the command-line installation, the installer just 
installs additional features for easily starting Cellen-Tellen. Both 
installation methods are strictly equivalent otherwise.

## 1.3 Installation of Cellen-Tellen from console

In case the provided installer does not work properly, or simply if you prefer
using Cellen-Tellen from the command-line, **it is also possible to install it
using `pip` like any other Python module**. 

### 1.3.1 \[Optional] Deploy a virtual environment

It is **recommended to install Cellen-Tellen in a
[virtual environment](https://docs.python.org/3/library/venv.html)** to avoid 
conflicts with other Python packages installed at the user level. This step is
however not mandatory and Cellen-Tellen can also be installed directly at the
user level.

To create a virtual environment called `venv`, simply run the following 
command at the location of your choice (here in the *Documents* folder) :

```console
C:\Users\User>cd Documents
C:\Users\User\Documents>python -m venv venv
```

> Use the *cd* command to navigate to the desired location for your virtual
> environment.

A new folder called `venv` is created, containing more or less the following 
elements (depending on your platform) :

```console
C:\Users\User\Documents>dir venv

06/23/2023 02:16 PM    <DIR>          .
06/23/2023 02:16 PM    <DIR>          ..
06/23/2023 02:16 PM    <DIR>          Include
06/23/2023 02:16 PM    <DIR>          Lib
06/23/2023 02:16 PM               116 pyvenv.cfg
06/23/2023 02:16 PM    <DIR>          Scripts
              1 File(s)            116 bytes
              5 Dir(s)  12,378,255,360 bytes free
```

Once the environment is set, it needs to **be activated** before proceeding to 
the next step :

```console
C:\Users\User\Documents>venv\Scripts\activate.bat
(venv) C:\Users\User\Documents>
```

Note that if you run the console from another location, you have to adjust the 
path to your virtual environment accordingly :

```console
C:\Users\User><Path to your venv>\Scripts\activate.bat
(venv) C:\Users\User>
```

Where *\<Path to your venv\>* is the path to the created virtual environment.

### 1.3.2 Install Cellen-Tellen

Once the correct version of Python is installed, Cellen-Tellen can be 
installed using the `pip` module :

```console
C:\Users\User>python -m pip install Cellen-Tellen
```

Or if installing in a virtual environment :

```console
(venv) C:\Users\User>python -m pip install Cellen-Tellen
```

The console should display lines similar to :

```console
Collecting numpy
  Downloading numpy-1.25.0-cp39-cp39-win_amd64.whl (15.1 MB)
     ---------------------------------------- 15.1/15.1 MB 4.3 MB/s eta 0:00:00
Installing collected packages: numpy
Successfully installed numpy-1.25.0
```

You can then **check if Cellen-Tellen is correctly installed** by running :

```console
C:\Users\User>python -c "import CellenTellen; print(CellenTellen.__version__)"
1.0.0
```

Or if installed in a virtual environment :

```console
(venv) C:\Users\User>python -c "import CellenTellen; print(CellenTellen.__version__)"
1.0.0
```

# 2. On Linux and macOS

## 2.1 Check your Python version

On both Linux and macOS, **Python is natively installed**. In a terminal, you 
can check the current version of Python as follows :

```console
user@machine:~$ python --version
Python 3.10.6
```

Or, in cases where both Python 2 and 3 are installed :

```console
user@machine:~$ python3 --version
Python 3.10.6
```

> To open a terminal in Linux and mcOS you can simply search for the Terminal 
> application in the application menu. On Linux, you can also type CTRL+ALT+T.

If the current version of Python is not between 3.7 and 3.10, you will need to
**install another version matching the specification**. This can be done using
[pyenv](https://github.com/pyenv/pyenv) on macOS, or 
[other workarounds](https://hackersandslackers.com/multiple-
python-versions-ubuntu-20-04/) in Ubuntu.

## 2.2 \[Optional] Deploy a virtual environment

*In this section, replace* `python` *with* `python3` *or* `python3.x` 
*(7<=x<=10) if necessary.*

It is **recommended to install Cellen-Tellen in a
[virtual environment](https://docs.python.org/3/library/venv.html)** to avoid 
conflicts with other Python packages installed at the user level. This step is
however not mandatory and Cellen-Tellen can also be installed directly at the
user level.

To create a virtual environment called `venv`, simply run the following 
command at the location of your choice (here in the *Documents* folder) :

```console
user@machine:~$ cd Documents
user@machine:~/Documents$ python -m venv venv
```

> Use the *cd* command to navigate to the desired location for your virtual
> environment.

A new folder called `venv` is created, containing more or less the following 
elements (depending on your platform) :

```console
user@machine:~/Documents$ ls venv
bin  include  lib  lib64  pyvenv.cfg
```

Once the environment is set, it needs to **be activated** before proceeding to 
the next step :

```console
user@machine:~/Documents$ source venv/bin/activate
(venv) user@machine:~/Documents$ █
```

Note that if you run the console from another location, you have to adjust the 
path to your virtual environment accordingly :

```console
user@machine:~$ source <Path to your venv>/bin/activate
(venv) user@machine:~$ █
```

Where *\<Path to your venv\>* is the path to the created virtual environment.

## 2.3 Install Cellen-Tellen

*In this section, replace* `python` *with* `python3` *or* `python3.x` 
*(7<=x<=10) if necessary.*

Once the correct version of Python is installed, **Cellen-Tellen can be 
installed like any other package using the `pip` module** :

```console
user@machine:~$ python -m pip install Cellen-Tellen
```

Or if installing in a virtual environment :

```console
(venv) user@machine:~$ python -m pip install Cellen-Tellen
```

The console should display lines similar to :

```console
Collecting numpy
  Downloading numpy-1.25.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (17.6 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.6/17.6 MB 4.6 MB/s eta 0:00:00
Installing collected packages: numpy
Successfully installed numpy-1.25.0
```

You can then **check if Cellen-Tellen is correctly installed** by running :

```console
user@machine:~$ python -c "import CellenTellen; print(CellenTellen.__version__)"
1.0.0
```

Or if installed in a virtual environment :

```console
(venv) user@machine:~$ python -c "import CellenTellen; print(CellenTellen.__version__)"
1.0.0
```

[Home page](index.markdown)
