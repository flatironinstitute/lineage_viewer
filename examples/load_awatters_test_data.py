
"""
This script launches a lineage editor/viewer using data configured like awatters's laptop.
"""

from lineage_viewer import lineage_forest
from lineage_viewer import images_gizmos
from H5Gizmos import serve
import json

fn = "Combined.json"
json_ob = json.load(open(fn))
F = lineage_forest.make_forest_from_haydens_json_graph(json_ob)

trivialize = False

if trivialize:
    F.use_trivial_null_loaders()
else:
    img_folder = "/Users/awatters/test/mouse_embryo_images/"
    image_pattern = img_folder + "klbOut_Cam_Long_%(ordinal)05d.crop.klb"
    label_pattern = img_folder + "klbOut_Cam_Long_%(ordinal)05d.crop_cp_masks.klb"
    F.load_klb_using_file_patterns(
            image_pattern=image_pattern,
            label_pattern=label_pattern,
        )

viewer = images_gizmos.LineageViewer(F, 400)

async def task():
    print (__doc__)
    await viewer.gizmo.link()
    viewer.configure_gizmo()

serve(task())
