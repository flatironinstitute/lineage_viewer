# lineage_viewer
Graphical interface for editing a lineage and viewing related microscopy images.

<img src="viewer.png"/>


# Installation

This package requires Python 3.7 or higher.  If you need to install an appropriate Python
I recommend using conda installed in single user mode (for easy maintenance) 
<a href="http://bit.ly/tryconda">http://bit.ly/tryconda</a>.

The package install procedure is not fully automated.

Please install the following dependencies manually in the following order.

```
 pip install git+https://github.com/AaronWatters/H5Gizmos
 pip install git+https://github.com/AaronWatters/jp_doodle
 pip install git+https://github.com/AaronWatters/array_gizmos
 pip install git+https://github.com/flatironinstitute/mouse_embryo_labeller
```

Then clone this repository and in the top level folder of the repository install the module in development mode as follows:

```bash
 git clone https://github.com/flatironinstitute/lineage_viewer.git
 cd lineage_viewer
 pip install -e .
```

# Starting the example lineage

The repository includes a script with some data for an example lineage
which should work "out of the box."  The sample includes a full
lineage tree description but only includes image data
for timestamps 1 and 2 of the tree.

To try the example lineage go to the `lineage_viewer/examples/lineage_sample`
directory and run the `load_sample_lineage.py` script.  

For example on my laptop:

```bash
(base) C02XD1KGJGH8:lineage_sample awatters$ cd ~/repos/lineage_viewer/
(base) C02XD1KGJGH8:lineage_viewer awatters$ cd examples/lineage_sample/
(base) C02XD1KGJGH8:lineage_sample awatters$ python load_sample_lineage.py 
Open gizmo using link (control-click / open link)

<a href="http://127.0.0.1:56998/gizmo/http/MGR_1671120997917_6/index.html" target="_blank">Click to open</a> <br> 
 GIZMO_LINK: http://127.0.0.1:56998/gizmo/http/MGR_1671120997917_6/index.html 

```
On my Mac laptop I have to confirm that Python can accept incoming connections in a pop up dialogue.

Then open the provided link URL in a browser to start the interface.
When the interface loads click on timestamp 2 near the top of the lineage tree
summary to load the images for timestamps 1 and 2 (as discussed in more detail below).


# The graphical interface

The graphical interface for the viewer displays in a web browser.
For flexibility the example scripts do not start the browser interface automatically
but instead provide a URL link so the user may choose what browser to use.  For example

```bash
(base) bash-4.4$ python load_rusty_test_data.py 
...
Open gizmo using link (control-click / open link)

<a href="http://10.128.146.57:59663/gizmo/http/MGR_1671116590930_6/index.html" target="_blank">Click to open</a> <br> 
 GIZMO_LINK: http://10.128.146.57:59663/gizmo/http/MGR_1671116590930_6/index.html 
```

The user may open the generated link `http://10.128.146.57:59663/gizmo/http/MGR_1671116590930_6/index.html`
by control-clicking the link (on a Mac OS for example).

The interface starts with no timestamp selected.  With no timestamp selected only the lineage tree summary
in the right panel displays.

Select a current time stamp by clicking on the lineage
tree summary on the right.  When a time stamp is selected the interface looks like the annotated
image below.

## Overview and motivation

## The Lineage tree summary

## The current and previous timestamp

## The lineage timestamp detail

## The microscopy volumes

## The image filter toggles

## The segmentation structure volumes

## The selected structures

## The selected strucure volume projections

## The rotation sliders

## The slicing sliders

## The edit controls

## The storage controls

<img src="annotated.png"/>