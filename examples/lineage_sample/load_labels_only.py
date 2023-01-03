
"""
This script creates a lineage forest with no parent relationships.
The label names are inferred from the label volume data
"""


from lineage_viewer import lineage_forest
from lineage_viewer import images_gizmos
from H5Gizmos import serve
from mouse_embryo_labeller import tools
import os

# Make an empty forest.
F = lineage_forest.Forest()

# Define the volume loader functions for the forest.
image_pattern = "nuclei_reg8_%(ordinal)d.tif"
label_pattern = "label_reg8_%(ordinal)d.tif"

def img_loader(ordinal, pattern=image_pattern):
    #import pyklb
    #subs = {"ordinal": ordinal}
    subs = {"ordinal": ordinal}  # files are zero based?
    path = pattern % subs
    if os.path.exists(path):
        return  tools.load_tiff_array(path)
    else:
        return None  # no data for this timeslice.
def label_loader(ordinal):
    return img_loader(ordinal, label_pattern)

F.image_volume_loader = img_loader
F.label_volume_loader = label_loader

# Create nodes inferred from label volumes for timestamps 1 and 2

for timestamp_ordinal in range(1, 3):
    F.create_nodes_for_labels_in_timestamp(timestamp_ordinal)

# Create a viewer for the forest
viewer = images_gizmos.LineageViewer(F, 400, title="sample nodes only -- only timestamps 1 and 2 have images")

# display the viewer
async def task():
    print (__doc__)
    await viewer.gizmo.link()
    viewer.configure_gizmo()

serve(task())