
"""
This script launches a lineage editor/viewer using data configured like awatters's laptop.
"""

from lineage_viewer import lineage_forest
from lineage_viewer import images_gizmos
from H5Gizmos import serve
import json
from mouse_embryo_labeller import tools
import os

fn = "LineageGraph.json"
json_ob = json.load(open(fn))
F = lineage_forest.make_forest_from_haydens_json_graph(json_ob)

trivialize = False

if trivialize:
    F.use_trivial_null_loaders()
else:
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

viewer = images_gizmos.LineageViewer(F, 400, title="sample lineage -- only timestamps 1 and 2 have images")

async def task():
    print (__doc__)
    await viewer.gizmo.link()
    viewer.configure_gizmo()

async def debug_task():
    print (__doc__)
    from H5Gizmos.python.examine import explorer
    from H5Gizmos import Stack
    ex = explorer(viewer).gizmo()
    st = Stack([viewer.gizmo, ex])
    await st.link()
    viewer.configure_gizmo()

serve(task())
