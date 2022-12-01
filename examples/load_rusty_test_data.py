
"""
This script launches a lineage editor/viewer using data configured like awatters@rusty:/220827_stack1/ 

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

fn = "Combined.json"
json_ob = json.load(open(fn))
F = lineage_forest.make_forest_from_haydens_json_graph(json_ob, label_assignment=assignment)

trivialize = False

if trivialize:
    F.use_trivial_null_loaders()
else:
    #assert trivialize, "non-trivial implementation is not finished."
    #img_folder = "/Users/awatters/test/mouse_embryo_images/"
    #image_pattern = img_folder + "klbOut_Cam_Long_%(ordinal)05d.crop.klb"
    #label_pattern = img_folder + "klbOut_Cam_Long_%(ordinal)05d.crop_cp_masks.klb"
    label_pattern = "/mnt/home/awatters/ceph/220827_stack1/Segmentation/stack_1_channel_0_obj_left/cropped/klbOut_Cam_Long_%(ordinal)05d.crop_cp_masks.klb"
    image_pattern = "/mnt/home/awatters/ceph/220827_stack1/Segmentation/stack_1_channel_0_obj_left/membrane/cropped/klbOut_Cam_Long_%(ordinal)05d.crop.klb"
    label_pattern = "labels/klbOut_Cam_Long_%(ordinal)05d.crop_cp_masks.klb"
    image_pattern = "images/klbOut_Cam_Long_%(ordinal)05d.crop.klb"
    F.load_klb_using_file_patterns(
            image_pattern=image_pattern,
            label_pattern=label_pattern,
        )
    test_ordinal = 29
    img = F.load_image_for_timestamp(test_ordinal)
    assert img is not None, "Could not load image for: " + repr(test_ordinal)
    lab = F.load_labels_for_timestamp(test_ordinal)
    assert lab is not None, "Could not load image for: " + repr(test_ordinal)

viewer = images_gizmos.LineageViewer(F, 350, "220827_stack1")

async def task():
    print (__doc__)
    await viewer.gizmo.link()
    viewer.configure_gizmo()

serve(task())
