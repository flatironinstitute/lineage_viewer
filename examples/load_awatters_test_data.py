
"""
This script launches a lineage editor/viewer using data configured like awatters's laptop.
"""

from lineage_viewer import lineage_forest
from lineage_viewer import images_gizmos
from H5Gizmos import serve
import json

# get the label assignment
ass_file = open("nuc_to_cells.csv")
assignment = {}
duplicate_check = {}
ignore_headers = ass_file.readline()
while 1:
    line = ass_file.readline()
    if not line:
        break
    [stack, identity, label_string] = line.strip().split(",")
    #print (repr(label_string))
    if label_string:
        [tsid, old_label] = identity.split("_")
        label = int(float(label_string))
        check_key = (tsid, label)
        check = duplicate_check.get(check_key)
        if check != line:
            assert check is None, "duplicate label: " + repr((check, line))
        duplicate_check[check_key] = line
        assignment[identity] = label

#print(assignment)

fn = "Combined.json"
json_ob = json.load(open(fn))
F = lineage_forest.make_forest_from_haydens_json_graph(json_ob, label_assignment=assignment)

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

viewer = images_gizmos.LineageViewer(F, 400, title="Images provided for timestamps 7 to 30")

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

serve(debug_task())
