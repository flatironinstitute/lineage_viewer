
"""
This script launches a lineage editor/viewer using data configured like 
awatters@rusty:/mnt/ceph/users/lbrown/MouseData/Maddy/220827_stack6

I launch this on rusty in an srun allocated core:

[awatters@rustyamd2 ~]$ srun -N1 --pty bash -i

srun: job 2024926 queued and waiting for resources
srun: job 2024926 has been allocated resources

(base) bash-4.4$ cd ~/repos/lineage_viewer/examples/
(base) bash-4.4$ python load_rusty_test_data.py 

...
Open gizmo using link (control-click / open link)

<a href="http://10.128.145.31:41145/gizmo/http/MGR_1669912036163_6/index.html" target="_blank">Click to open</a> <br> 
 GIZMO_LINK: http://10.128.145.31:41145/gizmo/http/MGR_1669912036163_6/index.html 

Then I open the link in a browser.
"""

from lineage_viewer import lineage_forest
from lineage_viewer import images_gizmos
from H5Gizmos import serve
import json
from mouse_embryo_labeller import tools
import os

# get the label assignment
"""
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
        assignment[identity] = label"""

#print(assignment)

prefix = "/mnt/ceph/users/lbrown/MouseData/Maddy/220827_stack6/"

fn = prefix + "LineageGraph.json"
json_ob = json.load(open(fn))
F = lineage_forest.make_forest_from_haydens_json_graph(json_ob)

trivialize = False

if trivialize:
    F.use_trivial_null_loaders()
else:
    #image_pattern = "klbOut_Cam_Long_%(ordinal)05d.crop.klb"
    image_pattern = prefix + "registered_images/nuclei_reg8_%(ordinal)d.tif"
    #label_pattern = "klbOut_Cam_Long_%(ordinal)05d.crop_cp_masks.klb"
    label_pattern = prefix + "registered_label_images/label_reg8_%(ordinal)d.tif"

    def img_loader(ordinal, pattern=image_pattern):
        #import pyklb
        #subs = {"ordinal": ordinal}
        subs = {"ordinal": ordinal}  # files are zero based?
        path = pattern % subs
        print("attempting to load path", repr(path))
        if os.path.exists(path):
            return  tools.load_tiff_array(path)
        else:
            return None  # no data for this timeslice.
    def label_loader(ordinal):
        return img_loader(ordinal, label_pattern)

    F.image_volume_loader = img_loader
    F.label_volume_loader = label_loader

    test_ordinal = 29
    img = F.load_image_for_timestamp(test_ordinal)
    assert img is not None, "Could not load image for: " + repr(test_ordinal)
    lab = F.load_labels_for_timestamp(test_ordinal)
    assert lab is not None, "Could not load image for: " + repr(test_ordinal)


viewer = images_gizmos.LineageViewer(F, 600, title="maddy data")

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
