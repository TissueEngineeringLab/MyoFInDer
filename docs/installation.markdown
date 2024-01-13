---
layout: default
title: Installation
---

[Home page](index.markdown)

As a Python module, MyoFInDer can be installed on almost any computer able to 
run a version of Python between 3.7 and 3.10. It is in particular fully 
supported on **Windows 8 and later**, and on **Ubuntu 18.04 and later**. 

Because the installation and use as a Python module might not be 
straightforward for every user, a very **basic Windows installer** is also 
provided for convenience.

MyoFInDer's installation takes around 2GB of disk memory on Linux and macOS, 
and 5GB on Windows. It uses around 1GB of RAM when running, and might use up to 
100% of the CPU. For a good performance, it is advised to have at least 8GB of 
RAM on your computer, and 4 CPU cores or more. It is also recommended not to 
run MyoFInDer along with other CPU-intensive applications, like 
image-processing software.

Index of the Installation page :

1. [On Windows](#1-on-windows)
   1. [Install Python](#11-install-python)
   2. [Install the C++ build tools](#12-install-the-c-build-tools)
   3. [Installation of MyoFInDer using the Windows installer](#13-installation-of-myofinder-using-the-windows-installer)
   4. [Installation of MyoFInDer from console](#14-installation-of-myofinder-from-console)
2. [On Linux and macOS](#2-on-linux-and-macos)
   1. [Check your Python version](#21-check-your-python-version)
   2. [[Optional] Deploy a virtual environment](#22-optional-deploy-a-virtual-environment)
   3. [Install MyoFInDer](#23-install-myofinder)
3. [GPU acceleration](#3-gpu-acceleration)

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

## 1.2 Install the C++ Build tools

On Windows only, **some extra tools need to be installed before installing
MyoFInDer**. These extra tools are necessary for successfully installing one of
the dependencies, and are not optional.

First, go to the [Microsoft C++ Build Tools website](https://visualstudio.
microsoft.com/visual-cpp-build-tools/) and download the Build Tools. When 
starting the downloaded program, you will be asked to choose features to 
install from a list of possible options. In the *Individual Components* tab,
select the necessary features as shown on the picture below. Select a correct
SDK (Windows **10** or Windows **11**) depending on your OS version ! Also, for 
the MSCV, select the one ending with *x64/x86 build tools (Latest)*, it won't 
necessarily be the *v143* one as shown on the picture. Then, click on Install 
and wait for the installation to complete. This step requires about 3GB of 
available disk space.

<img src="./cpp_build_tools.png" title="Components to select for build tools">

## 1.3 Installation of MyoFInDer using the Windows installer

For convenience, **a very basic installer is provided for Windows users**. It 
requires a compatible version of Python to be installed, as described in the
previous section.

This installer makes user's life easier by :

- Handling the installation of the MyoFInDer module
- Adding Desktop and Menu Bar shortcuts for starting MyoFInDer

Note that compared to the command-line installation, the installer just 
installs additional features for easily starting MyoFInDer. Both installation 
methods are strictly equivalent otherwise.

To run the installer, just double-click on the `myofinder.msi` file and follow 
the displayed instructions. You might have to enter an administrator password 
at some point. Then, when opening the application for the first time, the 
required Python modules and MyoFInDer will be installed automatically. Note 
that a working internet connection is required for this step, and that it might 
take up a few minutes for this step to complete. A number of messages will be 
displayed in the console, which is totally normal. The console should look 
similar to:

<img src="./pip_install.png" width="1000" title="Installation in console">

**The Windows installer can be downloaded 
[here](https://github.com/TissueEngineeringLab/MyoFInDer/blob/main/bin/myofinder.msi).
The installer is called `myofinder.msi`, do not mistake it for 
`myofinder.exe`!**

## 1.4 Installation of MyoFInDer from console

In case the provided installer does not work properly, or simply if you prefer
using MyoFInDer from the command-line, **it is also possible to install it
using `pip` like any other Python module**. 

### 1.4.1 \[Optional] Deploy a virtual environment

> The commands below are intended for experimented users who know what they're
> doing ! Do not try to run them unless you understand what they do ! For 
> Windows users, the [installation using the Windows installer](#13-installation-of-myofinder-using-the-windows-installer) 
> is recommended. If you face any problem with the installation and don't know 
> what to do, please refer to the [Troubleshooting page](troubleshooting.markdown) 
> or get in touch with the maintainer.

It is **recommended to install MyoFInDer in a
[virtual environment](https://docs.python.org/3/library/venv.html)** to avoid 
conflicts with other Python packages installed at the user level. This step is
however not mandatory and MyoFInDer can also be installed directly at the user 
level.

To create a virtual environment called `venv`, simply run the following 
command at the location of your choice (here in the `Documents` folder) :

```console
C:\Users\User>cd Documents
C:\Users\User\Documents>python -m venv venv
```

> Use the `cd` command to navigate to the desired location for your virtual
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

Where `<Path to your venv>` is the path to the created virtual environment.

### 1.4.2 Install MyoFInDer

> The commands below are intended for experimented users who know what they're
> doing ! Do not try to run them unless you understand what they do ! For 
> Windows users, the [installation using the Windows installer](#13-installation-of-myofinder-using-the-windows-installer) 
> is recommended. If you face any problem with the installation and don't know 
> what to do, please refer to the [Troubleshooting page](troubleshooting.markdown) 
> or get in touch with the maintainer.

Once the correct version of Python is installed, MyoFInDer can be installed 
using the `pip` module :

```console
C:\Users\User>python -m pip install myofinder
```

Or if installing in a virtual environment :

```console
(venv) C:\Users\User>python -m pip install myofinder
```

The console should display progress bars corresponding to the installation of
various Python modules. You can then **check if MyoFInDer is correctly 
installed** by running :

```console
C:\Users\User>python -c "import myofinder; print(myofinder.__version__)"
1.0.0
```

Or if installed in a virtual environment :

```console
(venv) C:\Users\User>python -c "import myofinder; print(myofinder.__version__)"
1.0.0
```

# 2. On Linux and macOS

On Linux and macOS, **MyoFInDer can only be installed as a Python module using 
`pip`**. Therefore, a very basic knowledge of Python and command-line terminals 
is  required, as this page is not meant to be a Python tutorial. In particular, 
users are expected to know how to open a terminal in their OS, how to navigate
through the folders in the terminal, and how to execute a command in the 
terminal. Note that in all the command-line snippets given below, the entire
console is displayed as it would appear in the default terminal of Ubuntu 22.04
with an XFCE desktop environment. The actual command to type in your terminal
is the part of the line located after the `$` symbol. The lines that do not
contain a `user@machine:~$` header represent the output of the commands, and 
you should therefore not try to type and execute them !

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

It is **recommended to install MyoFInDer in a
[virtual environment](https://docs.python.org/3/library/venv.html)** to avoid 
conflicts with other Python packages installed at the user level. This step is
however not mandatory and MyoFInDer can also be installed directly at the user 
level.

To create a virtual environment called `venv`, simply run the following 
command at the location of your choice (here in the `Documents` folder) :

```console
user@machine:~$ cd Documents
user@machine:~/Documents$ python -m venv venv
```

> Use the `cd` command to navigate to the desired location for your virtual
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

Where `<Path to your venv>` is the path to the created virtual environment.

## 2.3 Install MyoFInDer

*In this section, replace* `python` *with* `python3` *or* `python3.x` 
*(7<=x<=10) if necessary.*

Once the correct version of Python is installed, **MyoFInDer can be installed 
like any other package using the `pip` module** :

```console
user@machine:~$ python -m pip install myofinder
```

Note that a working internet connection is required for this step, and that it 
might take up a few minutes for this step to complete.

Or if installing in a virtual environment :

```console
(venv) user@machine:~$ python -m pip install myofinder
```

The console should display progress bars corresponding to the installation of
various Python modules. You can then **check if MyoFInDer is correctly 
installed** by running :

```console
user@machine:~$ python -c "import myofinder; print(myofinder.__version__)"
1.0.0
```

Or if installed in a virtual environment :

```console
(venv) user@machine:~$ python -c "import myofinder; print(myofinder.__version__)"
1.0.0
```

> Note that tkinter might not be distributed by default with Python, you might
> have to install it manually. On Ubuntu, that can be done by calling
> `sudo apt install python3-tk`.

# 3. GPU-acceleration

The [TensorFlow](https://www.tensorflow.org/) library that runs the AI model 
used by MyoFInDern supports GPU acceleration. When it is enabled, it can 
drastically improve the computation speed of the module by performing the
calculations on the GPU rather than on the CPU. Depending on your machine, you 
might however not be able to enable GPU acceleration.

The first requirement is to have a machine equipped with an Nvidia graphic 
card. If that's the case, you then need to install the right CUDA drivers for
your OS and GPU model. The available drivers can be downloaded 
[here](https://developer.nvidia.com/cuda-downloads). Finally, you need to 
install the cuDNN library, again with the correct version for your OS and 
platform. An installation guide for cuDNN can be found 
[here](https://docs.nvidia.com/deeplearning/cudnn/install-guide/). Once this is 
done, GPU acceleration should be automatically enabled when processing images
with MyoFInDer.

[Home page](index.markdown)
