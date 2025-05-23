The Myoblast Fusion Index Determination Software
================================================

The MyoFInDer Python package aims to provide an open-source graphical interface 
for automatic calculation of the fusion index in muscle cell cultures, based on 
fluorescence microscopy images.

> [!IMPORTANT]
> MyoFInDer is currently in maintenance-only development phase. This means that
> reported bugs will be fixed, minor changes will be brought to support new
> Python versions if possible, but no major improvements or updates should be 
> expected. User requests for new features could still be addressed, depending
> on how large they are.

> [!WARNING]
> MyoFInDer version 1.1.0 now uses [CellPose](https://www.cellpose.org/) for 
> nuclei segmentation instead of [DeepCell](https://www.deepcell.org/). This is
> a major breaking change. Differences are to be expected in the results 
> obtained with version 1.1.0 and earlier ones, even with similar processing
> parameters.

Presentation
------------

MyoFInDer is based on an Artificial Intelligence library for cell segmentation, 
that it makes easily accessible to researchers with limited computer skills. In 
the interface, users can manage multiple images at once, adjust processing 
parameters, and manually correct the output of the computation. It is also 
possible to save the result of the processing as a project, that can be shared 
and re-opened later.

A more detailed description of the features and usage of MyoFInDer can be found 
in the 
[usage section](https://tissueengineeringlab.github.io/MyoFInDer/usage.html)
of the documentation.

MyoFInDer was developed at the 
[Tissue Engineering Lab](https://tissueengineering.kuleuven-kulak.be/) in 
Kortrijk, Belgium, which is part of the 
[KU Leuven](https://www.kuleuven.be/kuleuven/) university. It is today the
preferred solution in our laboratory for assessing the fusion index of a cell 
population.

Requirements
------------

To install and run MyoFInDer, you'll need Python 3 (3.9 to 3.13), approximately 
6GB of disk space, and preferably 8GB of memory or more. MyoFInDer runs on 
Windows, Linux, macOS, and potentially other OS able to run a compatible 
version of Python.

The dependencies of the module are :

- [Pillow](https://python-pillow.org/)
- [opencv-python](https://pypi.org/project/opencv-python/)
- [CellPose](https://pypi.org/project/cellpose/)
- [XlsxWriter](https://pypi.org/project/XlsxWriter/)
- [screeninfo](https://pypi.org/project/screeninfo/)
- [numpy](https://numpy.org/)

Installation
------------

MyoFInDer is distributed on PyPI, and can thus be installed using the `pip` 
module of Python :

```console
python -m pip install myofinder
```

Note that in the `bin` folder of this repository, a very basic `.msi` Windows
installer allows automatically installing the module and its dependencies for
Windows users who don't feel comfortable with command-line operations.

A more detailed description of the installation procedure can be found in the 
[installation section](https://tissueengineeringlab.github.io/MyoFInDer/installation.html)
of the documentation.

Citing MyoFInDer
----------------

If MyoFInDer has been of help in your research, please reference it in your 
academic publications by citing the following article:

- Weisrock A., Wüst R., Olenic M. et al., *MyoFInDer: An AI-Based Tool for 
Myotube Fusion Index Determination*, Tissue Eng. Part A (30), 19-20, 2024, 
DOI: 10.1089/ten.TEA.2024.0049. 
([link to Weisrock et al.](https://www.liebertpub.com/doi/10.1089/ten.tea.2024.0049))

Documentation
-------------

The latest version of the documentation can be accessed on the 
[project's website](https://tissueengineeringlab.github.io/MyoFInDer/). It 
contains detailed information about the installation, usage, and 
troubleshooting. 
