# CellenTellen
> *"One nucleus, two nuclei, three nuclei, ... Ah-ah-ah!"*
>
> Count von Count, Sesame Street

Welcome to the GitHub repository of CellenTellen! This repo contains the source code of the program as well as all the necessary files for the installation of CellenTellen. CellenTellen is an open source platform for nuclei segmentation. It was developed by university students of KULeuven campus Kulak to aid the Tissue Engineering Lab at the Department of Development and Regeneration with their research. We hope this code could be of use to other people who are interested in segmenting cells. 

## Table of contents
* [General info](#general-info)
* [install](#How-to-install)
* [Use](#How-to-use)
* [GPU usage](#GPU-usage-with-NVIDIA-graphics-card)

## General info
This repo contains the source code of the program as well as all the necessary files for the installation of CellenTellen. The program is fully written in Python and uses Deepcell as the prediction model.
The program has been tested on `Windows 10` and `Windows 11` but is not supported for `Linux` or `macOS`. 

This application uses the library DeepCell (https://github.com/vanvalenlab/deepcell-tf) that is available under the Apache 2.0 license, which can be obtained from http://www.apache.org/licenses/LICENSE-2.0.

## How to install

There are two installations that need to be done, the first one is C++ buildtools from Microsoft Visual Studio which you can install by pressing <a href="https://visualstudio.microsoft.com/visual-cpp-build-tools/"> this link </a>. Once downloaded you'll need to restart your pc, this is needed for activating the buildtools. If you prefer you can read the rest of the download section and restart your pc at the end before executing the program.
You can install the main program by clicking <a href="https://gitlab.kuleuven.be/u0143112/graaftel/-/raw/master/Code/Graphical%20Interface/Cellen_Tellen.zip
"> this link </a>which should start downloading the zip file. Once downloaded, unpack the zip file and place the folder somewhere on your computer. 

There are two ways to start the program: you can type 'CellenTellen.exe' in your windows search bar or make a shortcut for the exe on your Desktop. After restarting your pc for activating the buildtools you can execute the program. It is possible that a firewall warning appears which you need to ignore by pressing `More information` and accepting the program. 



## How to use
### Nuclei and Fibre indication

The user can load (additional) images with the `Load Images` button. These images can be imported from anywhere on the computer. The names of the images will be shown in a table together with the number of indicated nuclei, the number of indicated tropomyosin positive nuclei, the fusion index and the number of indicated fibres. All these numbers will be set at zero after loading the images. The user can click on an entry of the table to display that image in the image window. Under the buttons at the top of the screen, it is possible to select which colour channels of the picture are displayed (`Channels`), as well as select whether the currently indicated nuclei or fibres will be shown (`Indicators`). If at least one image is loaded, the `Process Images` button will appear. This button runs the nuclei detection and, if desired, the fibre detection algorithm and starts overwriting all currently indicated nuclei (and fibres, if desired) of all the images in the table.

To interact with the displayed image, the user can use the mouse buttons or keyboard buttons. If the user wants to zoom in on the picture, they need to use the mouse wheel or the *+ and *- buttons. To move the image around, the user can hold down the middle mouse button or use the arrow keys on the keyboard. Indicating a new nucleus or fibre happens with the left mouse button. Left-clicking an existing nucleus will transfer it from a tropomyosin positive nucleus to a negative one or vice versa. Right-clicking an existing nucleus or fibre will remove it. While performing these actions, the variables in the table will change for that image. Switching between interacting with the nuclei or the fibres can be done with the third button at the top of the screen (`Manual : ...`).
It is only possible to select to interact with the nuclei if the indicated nuclei are also being shown, which can be selected below the buttons (at `Indicators`). Likewise, it is not possible to interact with the fibres if the indicated fibres are not being shown.

### Projects

The user can save working spaces in projects. Initially, after starting the program, a new empty and unsaved work space is created in which the user can start loading images. Creating a new project folder and saving the current space in that folder is done by choosing `Save Project As` in the File menu. After providing a name for the project, the current working space will be saved in that folder. 

Loading a project folder can be done directly from the `Recent Projects` option in the menu as well as from the `Load From Explorer` option in the menu. This option will guide the user to the folder where all the saved projects are located. Choosing one of the project folders will load that project. In the File menu, it is also possible to delete the current project or start a new empty project (make sure to save the current working space or project before doing this). Finally, the option `Load Automatic Save` in the File menu will load the latest automatic save.

After loading a project folder or saving the current working space to a project folder, the user will now be working inside that project. The name of the current project is contained in the title of the window. This title also indicates whether the current working space or project is unsaved. If the user is working inside a project, it is possible to save the current working space immediately to that project by clicking the `Save` button at the top right of the window. 

All projects are saved in one folder which is automatically created by the program, the user is expected to only alter these projects folders through the interface. When saving a project, an Excel sheet will also be created, which contains the relevant variables for each image like the total number of nuclei, the number of tropomyosin positive nuclei, the fusion index and the number of disconnected fibres. It is possible to also save altered images, these are the original images with the detected nuclei and fibres indicated. Both the Excel sheet and altered images can be found in the project's folder after saving the project.

### Settings

In the Settings menu, available in the menu bar, there are a number of options.
* It is possible to indicate which channels are occupied by the nuclei and the fibres. The automatic nuclei and fibre detection is based on these selections. * The user can indicate how long the autosave interval is, this is the interval between automatically saving the current project to the automatic save folder. 
* It is possible to enable saving altered images when saving projects. These altered images are the original images with the detected nuclei and fibres indicated on them.
* One of the performance boosting functions of the program is multithreading. The number of threads can be chosen from 5 to zero (zero means no multithreading, this will temporarily block the program when running the process). It is advised to set the number of threads to one when using GPU optimisation (see further).
* Since it is not always desired to count and indicate the fibres, this functionality can be switched off.
* If desired, the user can adjust the `Small objects threshold` which is used to remove dead cells by eliminating nuclei smaller than this threshold.


## GPU usage with NVIDIA graphics card
Our program supports NVIDIA GPU usage for speeding up the algorithms. In order to check if you have an NVIDIA graphics card, you can search for `Device manager` in the windows search bar. Thereafter, go to `Display adapters` and you'll find your processors. If your computer doesn't have an NVIDIA graphics card, you will not be able to make use of this feature.

Firstly, you need to install the right CUDA version. As we use `tensorflow version 2.5.1`, you'll need to install `CUDA version 11.2` which can be found at the official NVIDIA website. for `Windows 10` and `Windows 11`, you can click 
<a href="https://developer.download.nvidia.com/compute/cuda/11.2.2/local_installers/cuda_11.2.2_461.33_win10.exe">
this link
</a> to install directly.

After the (hopefully) successful installation of CUDA, we need to install cuDNN. 
Unfortunately, to install cudnn you do need to log into the 
<a href=https://developer.nvidia.com/compute/machine-learning/cudnn/secure/8.1.1.33/11.2_20210301/cudnn-11.2-windows-x64-v8.1.1.33.zip>
official website of NVIDIA </a>.
After logging in or registering, it should have automatically downloaded the zip-folder. If not, click 
<a href=https://developer.nvidia.com/compute/machine-learning/cudnn/secure/8.1.1.33/11.2_20210301/cudnn-11.2-windows-x64-v8.1.1.33.zip>
here
</a> again.
After downloading, follow the steps below.
<p align="left">
<img src="https://github.com/Quentinderore2/Cellen-Tellen/blob/main/Assets/image0.png" width="100">
Click on the downloaded cuda executable. 
</p>
Follow the installation instruction as seen in the images below. 

|                                                                                                     |                                                                                                     |                                                                                                     |
|:---------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------:|
| <img width="300" src="https://github.com/Quentinderore2/Cellen-Tellen/blob/main/Assets/image1.png"> | <img width="300" src="https://github.com/Quentinderore2/Cellen-Tellen/blob/main/Assets/image2.png"> | <img width="300" src="https://github.com/Quentinderore2/Cellen-Tellen/blob/main/Assets/image3.png"> |
| <img width="300" src="https://github.com/Quentinderore2/Cellen-Tellen/blob/main/Assets/image4.png"> | <img width="300" src="https://github.com/Quentinderore2/Cellen-Tellen/blob/main/Assets/image5.png"> | <img width="300" src="https://github.com/Quentinderore2/Cellen-Tellen/blob/main/Assets/image6.png"> |

When the installation is complete, you have to copy all the contents from the cudnn folder to the folder `C:\Program Files\NVIDIA GPU computing toolkit\CUDA\v11.2`. This is shown in the images below.

|                                                                                                     |                                                                                                     |     |
|:---------------------------------------------------------------------------------------------------:|:---------------------------------------------------------------------------------------------------:|:---:|
| <img width="300" src="https://github.com/Quentinderore2/Cellen-Tellen/blob/main/Assets/image7.png"> | <img width="300" src="https://github.com/Quentinderore2/Cellen-Tellen/blob/main/Assets/image8.png"> |     |
