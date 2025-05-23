---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
title: Documentation of the MyoFInDer project
---

# Introduction

**The MyoFInDer Software** (The Myoblast Fusion Index Determination Software) 
is a [Python](https://www.python.org/) module for the **automatic calculation 
of the fusion index** on fluorescence-stained microscopy images of muscle cell 
cultures. It provides a **simple and user-friendly interface** for managing 
multiple images as a project. In the interface, users can open and save 
projects, tune settings, start computations, and manually correct the output. 

On this documentation website, you can find information about the :

- [Installation](installation.markdown)
- [Usage](usage.markdown)
- [Troubleshooting](troubleshooting.markdown)

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

# About

This module is **free and open-source**, hosted and distributed on 
[GitHub](https://github.com/TissueEngineeringLab/MyoFInDer) under the GNU 
GPL-3.0 license. It was developed at the
[Tissue Engineering Lab](https://tissueengineering.kuleuven-kulak.be/), part of
the [KU Leuven KULAK](https://kulak.kuleuven.be/) university. **Contributions,
bug reports or simple questions** are welcome in the dedicated sections of the
GitHub page.
