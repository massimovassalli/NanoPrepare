# NanoPrepare 
A Python-based graphical interface for processing nanoindentation and atomic force microscopy (AFM) data.

**Note: this is the new branch for version 1. If you are looking for the old NanoPrepare, either download one of the stored v0 releases or clone the branch v0!**

## What is NanoPrepare?

NanoPrepare is designed to streamline the workflow of nanoindentation and AFM data analysis. It helps researchers:
- **Import** force-displacement curves from various instrument manufacturers
- **Screen** datasets to remove poor quality or invalid measurements through both manual inspection and automated filtering rules
- **Export** validated data in universal formats (JSON and HDF5) for downstream analysis

This tool is particularly useful for soft materials research (gels, cells, tissues) but supports analysis of harder materials and coatings as well. The modular plugin architecture allows easy extension for custom screening protocols and new file formats.

## Workflow Integration

NanoPrepare is part of a broader data analysis pipeline. After screening and packaging your data with NanoPrepare, you can use the [softmech project](https://github.com/CellMechLab/softmech) for advanced mechanical property analysis and interpretation of your nanoindentation measurements.

## Documentation 
A step-by-step guide and video tutorials for the previous software version are available in our recent paper:

- Ciccone, G., Azevedo Gonzalez Oliva, M., Antonovaite, N., Lüchtefeld, I., Salmeron-Sanchez, M. and Vassalli, M., 2021. Experimental and data analysis workflow for soft matter nanoindentation. Journal of Visualized Experiments (10.3791/63401).

Documentation for version 1 is currently being prepared.

## Supported File Formats

**Input formats:**
- **Optics11 (.txt)** - Full support for both old and new file variants
- **Nanosurf (.nhf)** - Supported
- **AFM formats** - Experimental support (optional dependency, install separately if needed)

**Output formats:**
- **HDF5** - Recommended for integration with the softmech analysis pipeline
- **JSON** - Alternative export format (more formats coming soon)

## Data Screening

NanoPrepare provides flexible screening tools to ensure data quality before analysis:

- **Manual screening** - Interactive visual inspection and rejection of individual curves
- **Automated filtering** - Plugin-based filtering rules (e.g., reject curves where maximum force falls below a threshold, indicating failed contact)
- **Extensible architecture** - Custom screening protocols can be easily added as plugins for your specific research needs

## Installation 
No installer is currently provided. In order use the GUI, a Python 3 environment is required with the dependencies specified in `requirements.txt`.

To install the required packages, run:
```bash
pip install -r requirements.txt
```

Note: `afmformats` is optional and only needed if you want to open AFM-formatted files. It can be installed separately with `pip install afmformats` if needed.

## Running the GUI 
In order to access the GUI, run the prepare file from the command line:
```bash
python prepare.py 
```

## Citation 
If you use this software in your publication and research, please cite the following paper: 

- Ciccone, G., Azevedo Gonzalez Oliva, M., Antonovaite, N., Lüchtefeld, I., Salmeron-Sanchez, M. and Vassalli, M., 2021. Experimental and data analysis workflow for soft matter nanoindentation. Journal of Visualized Experiments (10.3791/63401
).
