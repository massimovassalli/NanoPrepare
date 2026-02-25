# NanoPrepare 
Simple graphical user interface (GUI) to screen and pack nanoindentation curves for further analysis.

**Note: this is the new branch for version 1. If you are looking for the old NanoPrepare, either download one of the stored v0 releases or clone the branch v0!**

## Introduction 
This GUI  is designed to open nanoindentation data (force-displacement curves), screen them (eliminating bad curves) and packing them together in a bundle file to be used for further analysis. This packaged file can be opened and processed using the softmech project https://github.com/CellMechLab/softmech.

## Documentation 
A step-by-step guide and video tutorials on how to use the previous software version is avilable in our recent paper:

- Ciccone, G., Azevedo Gonzalez Oliva, M., Antonovaite, N., Lüchtefeld, I., Salmeron-Sanchez, M. and Vassalli, M., 2021. Experimental and data analysis workflow for soft matter nanoindentation. Journal of Visualized Experiments (10.3791/63401).

We are updating the documentation to match the new version.

## Supported file types 
Right now, the software opens Optics11 .txt files (both old and new versions are supported). We are working to add support for Nanosurf files.

## Installation 
No installer is currently provided. In order use the GUI, a Python 3 environment with the following packages is required: PyQt5, NumPy, SciPy, PyQtGraph, matplotlib.

## Output format
The current packing format is HDF5 (compatible with the softmech analysis pipeline). JSON export has been removed in this consolidation release.

## Running the GUI 
In order to access the GUI, run the prepare file from the command line:
```bash
python prepare.py 
```

## Citation 
If you use this software in your publication and research, please cite the following paper: 

- Ciccone, G., Azevedo Gonzalez Oliva, M., Antonovaite, N., Lüchtefeld, I., Salmeron-Sanchez, M. and Vassalli, M., 2021. Experimental and data analysis workflow for soft matter nanoindentation. Journal of Visualized Experiments (10.3791/63401
).
