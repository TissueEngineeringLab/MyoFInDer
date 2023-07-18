The Myoblast Fusion Index Determination Software
================================================

The MyoFInDer Python package aims to provide an open-source graphical interface 
for automatic calculation of the fusion index in muscle cell cultures, based on 
fluorescence microscopy images.

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

To install and run MyoFInDer, you'll need Python 3 (3.7 to 3.10), approximately 
1GB of disk space, and preferably 8GB of memory or more. MyoFInDer runs on 
Windows, Linux, macOS, and potentially other OS able to run a compatible 
version of Python.

The dependencies of the module are :

- [Pillow](https://python-pillow.org/)
- [opencv-python](https://pypi.org/project/opencv-python/)
- [DeepCell](https://pypi.org/project/DeepCell/)
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

Documentation
-------------

The latest version of the documentation can be accessed on the 
[project's website](https://tissueengineeringlab.github.io/MyoFInDer/). It 
contains detailed information about the installation, usage, and 
troubleshooting. 
