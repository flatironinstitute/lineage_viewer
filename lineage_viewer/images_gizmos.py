
"""
Displays for labels and images
"""

import numpy as np
from H5Gizmos import (
    Stack, Slider, Image, Shelf, Button, Text, Input, RangeSlider, do, ClickableText)
from H5Gizmos.python.file_selector import select_any_file
from array_gizmos import colorizers, operations3d
from scipy.ndimage import gaussian_filter
from . import lineage_gizmo
from . import lineage_forest
import json
import os

ENHANCE_CONTRAST = True
HACK_SHAPES = True
dummy_image = np.zeros((2,2), dtype=np.int)
YES_ENHANCED = "✓ enhanced"
NOT_ENHANCED = "✖ not enhanced"
YES_BLUR = "✓ blurred"
NO_BLUR = "✖ no blur"
YES_MASK = "✓ masked"
NO_MASK = "✖ no mask"
YES_SPECKLE = "✓ speckled"
NO_SPECKLE = "✖ unspeckled"
YES_RESTRICT = "✓ restricted"
NO_RESTRICT = "✖ unrestricted"

STD_SPECKLE_RATIO = 0.03

class LineageViewer:

    def __init__(self, forest, side, title="Lineage Viewer", colorize="tracks"):
        self.forest = forest
        self.side = side
        self.title = title
        self.compare = CompareTimeStamps(forest, side, title)
        self.lineage = lineage_gizmo.LineageDisplay(2.2 * side, side, colorize=colorize)
        self.detail = lineage_gizmo.TimeSliceDetail(height=side * 0.3, width=3.1*side)
        self.info_area = Text("No timestamp selected.")
        self.reparent_button = Button("reparent")
        self.disconnect_button = Button("disconnect")
        misc_controls = [self.reparent_button, self.disconnect_button]
        self.filename_input = Input("lineage.json", size=80)
        self.save_button = Button("Save", on_click=self.save_click)
        self.load_button = Button("Load", on_click=self.load_click)
        self.browse_button = Button("Browse", on_click=self.browse_click)
        #file_controls = [["File name:", self.filename_input], [self.load_button, self.save_button]]
        file_controls = [["File name:", self.filename_input], self.load_button, self.save_button, self.browse_button]
        misc_controls += file_controls
        self.gizmo = Stack([ 
            [self.compare.gizmo, self.lineage.gizmo],
            self.detail.gizmo,
            misc_controls,
            self.info_area,
        ])
        start = os.path.abspath(".")
        self.file_selector = select_any_file(on_select=self.select_file, root_folder="/", start_location=start, input_width=200)

    def info(self, text):
        self.info_area.text(text)

    def configure_gizmo(self):
        self.lineage.configure_canvas(self.ts_select_callback)
        self.lineage.load_forest(self.forest)
        self.detail.configure_canvas()
        self.compare.configure_gizmo()
        self.compare.on_label_select(self.update_label_selection)
        self.detail.on_select_node(self.update_selected_ids)
        self.reparent_button.set_on_click(self.reparent_click)
        self.disconnect_button.set_on_click(self.disconnect_click)
        self.reparent_button.set_enabled(False)
        self.disconnect_button.set_enabled(False)
        self.file_selector.add_as_dialog_to(self.gizmo)

    def browse_click(self, *ignored):
        self.file_selector.gizmo.open_dialog()

    def select_file(self, filename):
        self.filename_input.set_value(filename)
        self.file_selector.gizmo.close_dialog()
        self.info("Use buttons to load or save " + repr(filename))

    def load_click(self, *ignored):
        self.info("load clicked.")
        filename = self.filename_input.value
        try:
            infile = open(filename)
        except Exception as e:
            self.info("could not open %s: %s" % (repr(filename), e))
            raise
        else:
            json_ob = json.load(infile)
            infile.close()
            new_forest = lineage_forest.Forest()
            self.forest.use_same_loaders(new_forest)
            new_forest.load_json(json_ob)
            self.recalculate_forest(new_forest)
            self.info("lineage loaded from " + repr(filename))

    def save_click(self, *ignored):
        self.info("save clicked.")
        filename = self.filename_input.value
        try:
            outfile = open(filename, 'w')
        except Exception as e:
            self.info("could not open %s: %s" % (repr(filename), e))
            raise
        else:
            json_ob = self.forest.json_ob(exclude_isolated=False)
            json.dump(json_ob, outfile)
            outfile.close()
            self.info("lineage stored to " + repr(filename))

    def reparent_click(self, *ignored):
        self.info("reparent clicked.")
        compare = self.compare
        child_node = compare.child_display.focus_node()
        parent_node = compare.parent_display.focus_node()
        if child_node is None:
            self.info("cannot reparent: no child selected.")
        elif parent_node is None:
            self.info("cannot reparent: no parent selected.")
        else:
            child_node.parent = parent_node
            self.recalculate_forest()

    def disconnect_click(self, *ignored):
        self.info("disconnect clicked.")
        compare = self.compare
        child_node = compare.child_display.focus_node()
        current_parent = child_node.parent
        if current_parent is None:
            self.info("cannot disconnect -- node has no parent.")
        else:
            child_node.parent = None
            self.recalculate_forest()

    def recalculate_forest(self, new_forest=None):
        compare = self.compare
        child_display = compare.child_display
        parent_display = compare.parent_display
        child_ts = child_display.timestamp
        #parent_ts = parent_display.timestamp
        child_label = child_display.focus_label
        parent_label = parent_display.focus_label
        if new_forest is None:
            forest = self.forest.clean_clone()
        else:
            forest = new_forest
        #forest.reset()
        forest.find_tracks_and_lineages()
        forest.assign_offsets()
        self.forest = forest
        self.lineage.load_forest(forest)
        self.compare.forest = forest
        if child_ts is not None:
            self.ts_select_callback(child_ts.ordinal)
            self.lineage.focus_ts(child_ts.ordinal)
        child_display.focus_label = child_label
        parent_display.focus_label = parent_label
        child_display._focus_node = parent_display._focus_node = None
        self.update_label_selection()

    def ts_select_callback(self, ordinal):
        self.info("ts selected: " + repr(ordinal))
        try:
            tjson = self.forest.timestamp_region_json(ordinal)
        except Exception as e:
            self.info("for ts %s got %s" % (ordinal, e))
            raise
        else:
            self.detail.load_json(tjson)
            self.compare.clear_images()
            self.compare.set_child_timestamp(ordinal)
            if ordinal > 0:
                self.compare.set_parent_timestamp(ordinal - 1)
            self.compare.rotate_volumes()
            self.compare.display_images()

    def update_label_selection(self, *ignored):
        compare = self.compare
        self.update_selected_ids(
            compare.child_display.selected_ids(),
            compare.parent_display.selected_ids(),
            update_detail=True
        )
        #self.update_selected_nodes(compare.child_display.focus_node(), compare.parent_display.focus_node())
        #compare.display_images()

    def update_selected_ids(self, child_ids, parent_ids, update_detail=False):
        # temporary for debugging
        #print("update selected ids", child_ids, parent_ids)
        self.child_ids = child_ids
        self.parent_ids = parent_ids
        compare = self.compare
        compare.child_display.select_ids(child_ids)
        compare.parent_display.select_ids(parent_ids)
        compare.display_images()
        if update_detail:
            self.detail.update_selections(child_ids, parent_ids)

    def update_selected_ids0(self, child_id, parent_id):
        # temp to delete...
        id_to_node = self.forest.id_to_node
        child_node = id_to_node.get(child_id)
        parent_node = id_to_node.get(parent_id)
        self.update_selected_nodes(child_node, parent_node, update_detail=False)

    def update_selected_nodes(self, child_node, parent_node, update_detail=True):
        # temporary -- need to generalize for multiselect
        cid = pid = None
        cids = []
        pids = []
        if child_node is not None:
            cid = child_node.node_id
            cids = [cid]
        if parent_node is not None:
            pid = parent_node.node_id
            pids = [pid]
        compare = self.compare
        compare.child_display.focus_on_node(child_node)
        compare.parent_display.focus_on_node(parent_node)
        compare.display_images()
        #if cid is not None and pid is not None:
        #    self.detail.update_selections(cid, pid)
        if update_detail:
            self.detail.update_selections(cids, pids)
        # set buttons enabled or not
        child_current_parent_id = None
        if child_node is not None and child_node.parent is not None:
            child_current_parent_id = child_node.parent.node_id
        if parent_node is not None and parent_node.node_id != child_current_parent_id:
            self.reparent_button.set_enabled(True)
        else:
            self.reparent_button.set_enabled(False)
        self.disconnect_button.set_enabled(child_current_parent_id is not None)

class CompareTimeStamps:
    """
    Show image and labels for 2 time stamps.
    """

    def __init__(self, forest, side, title="Timeslices"):
        self.forest = forest
        self.side = side
        self.title = title
        # gizmo scaffolding
        self.title_area = Text(self.title)
        self.title_area.resize(width=side * 2)
        self.info_area = Text("Building scaffolding.")
        #self.info_area.resize(width=side * 2)
        self.parent_display = ImageAndLabels2d(side, None, title="Parent images")
        self.child_display = ImageAndLabels2d(side, None, title="Child images")
        self.enhanced_link = ClickableText(NOT_ENHANCED, on_click=self.toggle_enhanced)
        self.blur_link = ClickableText(NO_BLUR, on_click=self.toggle_blur)
        self.mask_link = ClickableText(NO_MASK, on_click=self.toggle_mask)
        self.speckle_link = ClickableText(NO_SPECKLE, on_click=self.toggle_speckle)
        self.restrict_link = ClickableText(NO_RESTRICT, on_click=self.toggle_restrict)
        self.enhanced_images = False
        self.blur_images = False
        self.mask_images = False
        self.speckle_images = False
        self.restrict_images = False
        info_bar = [
            self.enhanced_link, 
            self.blur_link, 
            self.mask_link, 
            self.speckle_link,
            self.restrict_link,
            self.info_area,
        ]
        self.displays = Stack([ 
            self.title_area,
            self.parent_display.gizmo,
            self.child_display.gizmo,
            info_bar,
        ])
        sliders = self.get_sliders(side)
        self.gizmo = Shelf([ 
            self.displays,
            sliders,
        ])
        # array shape (maxima)
        self.slicing = None
        self.theta = 0
        self.phi = 0
        self.gamma = 0
        self.theta2 = 0
        self.phi2 = 0
        self.gamma2 = 0
        self.label_select_callback = None

    def get_sliders(self, side):
        limit = np.pi
        self.theta_slider = Slider(
            title="theta", 
            orientation="vertical",
            value=0, 
            minimum=-limit, 
            maximum=+limit, 
            step=0.02, 
            on_change=self.project_and_display)
        self.theta_slider.resize(height=side/2)
        self.phi_slider = Slider(
            title="theta", 
            orientation="vertical",
            value=0, 
            minimum=-limit, 
            maximum=+limit, 
            step=0.02, 
            on_change=self.project_and_display)
        self.phi_slider.resize(height=side/2)
        self.gamma_slider = Slider(
            title="gamma", 
            orientation="vertical",
            value=0, 
            minimum=-limit, 
            maximum=+limit, 
            step=0.02, 
            on_change=self.project_and_display)
        self.gamma_slider.resize(height=side/2)
        self.theta2_slider = Slider(
            title="theta2", 
            orientation="vertical",
            value=0, 
            minimum=-limit, 
            maximum=+limit, 
            step=0.02, 
            on_change=self.project_and_display)
        self.theta2_slider.resize(height=side/2)
        self.phi2_slider = Slider(
            title="phi2", 
            orientation="vertical",
            value=0, 
            minimum=-limit, 
            maximum=+limit, 
            step=0.02, 
            on_change=self.project_and_display)
        self.phi2_slider.resize(height=side/2)
        self.gamma2_slider = Slider(
            title="gamma2", 
            orientation="vertical",
            value=0, 
            minimum=-limit, 
            maximum=+limit, 
            step=0.02, 
            on_change=self.project_and_display)
        self.gamma2_slider.resize(height=side/2)
        # dummy values for now
        I = 100
        self.I_slider = RangeSlider(
            orientation="vertical",
            minimum=0,
            maximum=I,
            low_value=0,
            high_value=I,
            step=1,
            title="I slider",
            on_change=self.project_and_display,
        )
        self.I_slider.resize(height=side)
        self.J_slider = RangeSlider(
            orientation="vertical",
            minimum=0,
            maximum=I,
            low_value=0,
            high_value=I,
            step=1,
            title="K slider",
            on_change=self.project_and_display,
        )
        self.J_slider.resize(height=side)
        self.K_slider = RangeSlider(
            orientation="vertical",
            minimum=0,
            maximum=I,
            low_value=0,
            high_value=I,
            step=1,
            title="K slider",
            on_change=self.project_and_display,
        )
        self.K_slider.resize(height=side)
        return [
            [
                ["ϕ", self.phi_slider],
                ["θ", self.theta_slider],
                ["γ", self.gamma_slider],
            ],
            [
                ["ϕ'", self.phi2_slider],
                ["θ'", self.theta2_slider],
                ["γ'", self.gamma2_slider],
            ],
            [ 
                ["I", self.I_slider],
                ["J", self.J_slider],
                ["K", self.K_slider],
            ]
        ]

    def on_label_select(self, callback):
        self.on_label_select_callback = callback
        self.child_display.on_label_select(callback)
        self.parent_display.on_label_select(callback)

    def toggle_enhanced(self, *ignored):
        e = self.enhanced_images = not self.enhanced_images
        self.child_display.enhance = e
        self.parent_display.enhance = e
        if e:
            self.enhanced_link.text(YES_ENHANCED)
        else:
            self.enhanced_link.text(NOT_ENHANCED)
        self.reload_volumes_and_images()

    def toggle_blur(self, *ignored):
        e = self.blur_images = not self.blur_images
        self.child_display.blur = e
        self.parent_display.blur = e
        if e:
            self.blur_link.text(YES_BLUR)
        else:
            self.blur_link.text(NO_BLUR)
        self.reload_volumes_and_images()

    def toggle_mask(self, *ignored):
        e = self.mask_images = not self.mask_images
        self.child_display.mask = e
        self.parent_display.mask = e
        if e:
            self.mask_link.text(YES_MASK)
        else:
            self.mask_link.text(NO_MASK)
        self.reload_volumes_and_images()

    def toggle_speckle(self, *ignored):
        e = self.speckle_images = not self.speckle_images
        self.child_display.speckle = e
        self.parent_display.speckle = e
        if e:
            self.speckle_link.text(YES_SPECKLE)
        else:
            self.speckle_link.text(NO_SPECKLE)
        self.reload_volumes_and_images()

    def toggle_restrict(self, *ignored):
        e = self.restrict_images = not self.restrict_images
        self.child_display.restrict = e
        self.parent_display.restrict = e
        if e:
            self.restrict_link.text(YES_RESTRICT)
        else:
            self.restrict_link.text(NO_RESTRICT)
        self.reload_volumes_and_images()

    def reload_volumes_and_images(self):
        self.child_display.reload_cached_volumes()
        self.parent_display.reload_cached_volumes()
        self.rotate_volumes()
        self.display_images()

    def reset_slider_maxes(self):
        Mc = self.child_display.shape()
        Mp = self.parent_display.shape()
        M = Mc
        if Mp is not None:
            if M is None:
                M = Mp
            else:
                M = np.maximum(M, Mp)
        if M is not None:
            for (slider, maximum) in zip([self.I_slider, self.J_slider, self.K_slider], M):
                do(slider.element.slider({"maximum": maximum, }))
                # https://stackoverflow.com/questions/6333152/how-to-refresh-a-jquery-ui-slider-after-setting-min-or-max-values
                # This should be wrapped in gz_jQuery?
                do(slider.element.slider("option", "max", maximum))
                do(slider.element.slider("option", "values", [0, maximum]))
            self.info_area.text("Maxima: " + repr(list(M)))

    def configure_gizmo(self):
        self.parent_display.configure_gizmo()
        self.child_display.configure_gizmo()
        self.gizmo.css({"background-color": "#ddd"})

    def set_parent_timestamp(self, ordinal):
        ts = self.forest.ordinal_to_timestamp.get(ordinal)
        if ts is None:
            self.info_area.text("No such parent timestamp ordinal: " + repr(ordinal))
        self.parent_display.reset(ts, self.forest, self)
        self.reset_slider_maxes()
        return ts

    def set_child_timestamp(self, ordinal):
        ts = self.forest.ordinal_to_timestamp.get(ordinal)
        if ts is None:
            self.info_area.text("No such child timestamp ordinal: " + repr(ordinal))
        self.child_display.reset(ts, self.forest, self)
        self.reset_slider_maxes()
        return ts

    def project_and_display(self, *ignored):
        self.theta = self.theta_slider.value
        self.phi = self.phi_slider.value
        self.gamma = self.gamma_slider.value
        self.theta2 = self.theta2_slider.value
        self.phi2 = self.phi2_slider.value
        self.gamma2 = self.gamma2_slider.value
        s = [
            self.I_slider.values,
            self.J_slider.values,
            self.K_slider.values,
        ]
        self.slicing = np.array(s, dtype=np.int)
        self.rotate_volumes()
        self.display_images()

    def rotate_volumes(self):
        self.parent_display.rotate_volumes(self, parent=True)
        self.child_display.rotate_volumes(self, parent=False)

    def display_images(self):
        self.parent_display.create_mask()
        self.child_display.create_mask()
        self.parent_display.load_mask(self.child_display)
        self.child_display.load_mask(self.parent_display)
        self.parent_display.display_images()
        self.child_display.display_images()

    def clear_images(self):
        self.parent_display.clear_images()
        self.child_display.clear_images()
        self.parent_display.reset()
        self.child_display.reset()

    def rotate_image(self, img, parent=False):
        sl = self.slicing
        simg = img
        if sl is not None:
            simg = operations3d.slice3(img, sl)
        buffer = operations3d.rotation_buffer(simg)
        def adjust_range(theta):
            if theta > np.pi:
                return theta - 2 * np.pi
            elif theta < -np.pi:
                return theta + 2 * np.pi
            else:
                return theta
        if parent:
            theta = adjust_range(self.theta)
            phi = adjust_range(self.phi)
            gamma = adjust_range(self.gamma)
        else:
            theta = adjust_range(self.theta + self.theta2)
            phi = adjust_range(self.phi + self.phi2)
            gamma = adjust_range(self.gamma + self.gamma2)
        rbuffer = operations3d.rotate3d(buffer, theta, phi, gamma)
        return rbuffer

class CachedVolumeData:

    def __init__(self, ordinal, label_volume, image_volume):
        self.ordinal = ordinal
        self.label_volume = label_volume
        self.image_volume = image_volume

class MaskImaging:

    def __init__(self, label_array, selected_labels, label_to_color):
        self.rotated_labels = None
        self.label_array = np.array(label_array, dtype=np.int32)
        self.selected_labels = selected_labels
        self.shape = self.label_array.shape
        self.label_to_color = label_to_color
        self.maxlabel = self.label_array.max()
        if label_to_color:
            self.maxlabel = max(self.maxlabel, max(label_to_color.keys()))
        #self.maxlabel = max(self.label_array.max(), max(label_to_color.keys()))
        self.label_mapper = np.zeros((self.maxlabel + 1,), dtype=np.int32)
        for label in selected_labels:
            self.label_mapper[label] = label
        self.restricted_label_array = self.label_mapper[self.label_array]
        self.selected_label_mask = (self.restricted_label_array > 0).astype(np.uint8)
        self.color_mapper = np.zeros((self.maxlabel + 1, 3), dtype=np.int32)
        for label in label_to_color.keys():
            self.color_mapper[label] = label_to_color[label]
        self.selected_color_mapper = np.zeros(self.color_mapper.shape, dtype=np.int32)
        for label in selected_labels:
            self.selected_color_mapper[label] = self.color_mapper[label]
        #self.extruded_labels = operations3d.extrude0(self.restricted_label_array)
        #REC = self.restricted_extruded_colors = self.color_mapper[self.extruded_labels]
        boundaries = None
        if selected_labels:
            for label in selected_labels:
                target = (label_array == label).astype(np.ubyte)
                projected = operations3d.extrude0(target)
                mask = colorizers.boundary_image(projected, 1)
                if boundaries is None:
                    boundaries = mask * label
                else:
                    boundaries = np.choose(mask, [boundaries, label])
        self.boundaries = boundaries
        self.colored_boundaries = self.color_mapper[boundaries]

    def max_value_projection(self, r_image, mask=False, restricted=False):
        if self.nontrivial() and restricted:
            r_image = np.where(self.restricted_label_array > 0, r_image, 0)
        elif mask or restricted:
            test_array = self.label_array
            if restricted and self.nontrivial():
                test_array = self.restricted_label_array
            r_image = np.where(test_array > 0, r_image, 0)
        return r_image.max(axis=0)

    def nontrivial(self):
        return (len(self.selected_labels) > 0)

    def extrusion(self, speckle_ratio=None, restricted=False):
        label_array = self.label_array
        if restricted and self.nontrivial():
            label_array = self.restricted_label_array
        if speckle_ratio is not None:
            assert speckle_ratio > 0 and speckle_ratio < 1, "bad speckle ratio: " + repr(speckle_ratio)
            r = np.random.random(label_array.shape)
            filter = (r < speckle_ratio)
            label_array = np.where(filter, label_array, 0)
        return operations3d.extrude0(label_array)

    def colored_extrusion(self, speckle_ratio=None):
        extrusion = self.extrusion(speckle_ratio=speckle_ratio)
        return self.color_mapper[extrusion]

    def overlay_boundaries(self, on_image, color=None):
        if self.boundaries is None:
            return on_image
        if color is None:
            color = self.colored_boundaries
        mask = (self.boundaries > 0)
        return colorizers.overlay_color(on_image, mask, color, center=True)

class ImageAndLabels2d:

    """
    Fixed rotation view of image and labels for a timestamp.
    """

    def __init__(self, side, timestamp=None, title="Image and Labels"):
        self.side = side
        self.rotated_labels = self.rotated_image = None
        #self.timestamp = timestamp
        self.image_display = Image(height=side, width=side)
        self.labels_display = Image(height=side, width=side)
        self.focus_label = None
        self._focus_node = None
        displays = Shelf([
            self.image_display,
            self.labels_display,
        ])
        self.info_area = Text(title)
        self.info_area.resize(width=side * 2)
        self.gizmo = Stack([
            self.info_area,
            displays,
        ])
        self.img_volume = None
        self.label_volume = None
        self.on_label_select_callback = None
        self.cached_volume_data = None
        self.blur = False
        self.enhance = False
        self.mask = False
        self.speckle = False
        self.restrict = False
        self.reset(timestamp)

    def on_label_select(self, callback):
        self.on_label_select_callback = callback

    def reset(self, timestamp=None, forest=None, comparison=None):
        self.timestamp = timestamp
        self.forest = forest
        #self.color_mapping_array = timestamp.color_mapping_array()
        self.img = None  # 2d image before annotation
        self.labels = None  # 2d labels before annotation
        self.labels_imaging = None  # labels imaging encapsulation
        self.label_to_nodes = {}  # currently selected nodes indexed by label
        self.compare_labels_imaging = None  # comparison labels imaging encapsulation
        #self.focus_mask = None # labels mask for outlines
        #self.focus_color = None
        #self.focus_label = None
        #self._focus_node = None
        #self.compare_mask = None
        #self.compare_color = None
        self.volume_shape = None
        self.label_volume = None
        self.image_volume = None
        # flag set when the projection is derived from real data
        self.valid_projection = False
        if comparison is not None:
            assert type(comparison) is CompareTimeStamps
        self.comparison = comparison
        if forest is not None and timestamp is not None:
            ordinal = timestamp.ordinal
            cached = self.cached_volume_data
            if cached and cached.ordinal == ordinal:
                #print ("using cached volumes for", ordinal)
                self.load_volumes(cached.label_volume, cached.image_volume)
            else:
                label_volume = forest.load_labels_for_timestamp(ordinal)
                if label_volume is None:
                    msg = "Timestamp %s has no label data" % ordinal
                    #print(msg)
                    self.info(msg)
                else:
                    image_volume = forest.load_image_for_timestamp(ordinal)
                    if image_volume is None:
                        msg = "Timestamp %s has no image data" % ordinal
                        print(msg)
                        self.info(msg)
                    else:
                        self.info("Loaded timestamp " + repr(ordinal))
                        self.load_volumes(label_volume, image_volume)

    def reload_cached_volumes(self):
        cached = self.cached_volume_data
        if cached:
            self.load_volumes(cached.label_volume, cached.image_volume)

    def get_focus_node_delete(self):
        if self._focus_node is not None:
            return self._focus_node
        timestamp = self.timestamp
        focus_label = self.focus_label
        if timestamp is not None and focus_label is not None:
            return timestamp.label_to_node.get(focus_label)
        else:
            return None

    def shape(self):
        a = self.label_volume
        if a is None:
            a = self.image_volume
        if a is None:
            return None
        return a.shape

    def load_volumes(self, label_volume, image_volume):
        l_s = label_volume.shape
        i_s = image_volume.shape
        if not HACK_SHAPES:
            assert l_s == i_s, "volume shapes don't match: " + repr([l_s, i_s])
        else:
            if l_s != i_s:
                min_s = tuple(np.minimum(l_s, i_s))
                print ("hacking image and label shapes: ", l_s, i_s, min_s)
                (I, J, K) = min_s
                label_volume = label_volume[:I, :J, :K]
                image_volume = image_volume[:I, :J, :K]
        # need to fix this so slicing is unified across timestamps! xxxxx
        slicing = operations3d.positive_slicing(label_volume)
        self.label_volume = operations3d.slice3(label_volume, slicing)
        self.image_volume = operations3d.slice3(image_volume, slicing)
        self.cached_volume_data = CachedVolumeData(self.timestamp.ordinal, label_volume, image_volume)
        # masking NOT HERE
        #if self.mask:
        #    self.image_volume = np.where((self.label_volume != 0), self.image_volume, 0)
        # image enhancement
        if self.blur:
            im = self.unenhanced_image_volume = self.image_volume
            im = im.astype(np.float)
            im = gaussian_filter(im, sigma=1)
            im = colorizers.scaleN(im, to_max=10000)
            #im = colorizers.enhance_contrast(im,cutoff=0.01)
            self.image_volume = im
        self.volume_shape = self.label_volume.shape

    def rotate_volumes(self, comparison, parent=False):
        self.valid_projection = False # default
        #image2d = labels2d = None
        if self.label_volume is not None:
            rlabels = comparison.rotate_image(self.label_volume, parent=parent)
            self.rotated_labels = rlabels
            #labels2d = operations3d.extrude0(rlabels)
        if self.image_volume is not None:
            rimage = comparison.rotate_image(self.image_volume, parent=parent)
            self.rotated_image = rimage
            #image2d = rimage.max(axis=0)  # maximum value projection.
            #if self.enhance:
            #    image2d = colorizers.enhance_contrast(image2d, cutoff=0.05)
            #self.valid_projection = True
        #self.load_images(image2d, labels2d)

    def info(self, text):
        self.info_area.text(text)

    def configure_gizmo(self):
        self.labels_display.on_pixel(self.pixel_callback)

    def selected_ids(self):
        return [node.node_id for node in self.label_to_nodes.values()]

    def select_ids(self, ids):
        self.label_to_nodes = {}
        for identity in ids:
            node = self.forest.id_to_node.get(identity)
            if node is not None:
                label = node.label
                if label is not None:
                    self.label_to_nodes[label] = node

    def pixel_callback(self, event):
        row = event["pixel_row"]
        column = event["pixel_column"]
        labels = self.labels
        if labels is None:
            self.info("No labels to select")
            return 
        label = labels[row, column]
        node = self.timestamp.label_to_node.get(label)
        if node is not None:
            if label in self.label_to_nodes:
                self.info("Unselecting " + repr(node))
                del self.label_to_nodes[label]
            else:
                self.info("Selecting " + repr(node))
                self.label_to_nodes[label] = node
            callback = self.on_label_select_callback
            if callback:
                callback()
        else:
            self.info("No node for label: " + repr(label))

    def pixel_callback_delete(self, event):
        row = event["pixel_row"]
        column = event["pixel_column"]
        labels = self.labels
        if labels is None:
            self.info("No labels to select")
            return 
        label = labels[row, column]
        node = None
        self.focus_label = None
        self._focus_node = None
        white = [233,213,255]
        self.focus_color = white
        self.info("clicked label: %s for node %s" % (label, node))
        if label:
            node = self.timestamp.label_to_node.get(label)
            self.info("clicked label: %s for node %s" % (label, node))
            self.focus_label = label
        if node:
            self.focus_color = node.color_array
        # comparison display is triggerred by callback below.
        #if self.comparison is not None:
        #    self.comparison.display_images()
        callback = self.on_label_select_callback
        if callback:
            callback(self.focus_label)
        # reset the focus if needed
        redisplay = False
        if label and self.focus_label is None:
            self.focus_label = label
            redisplay = True
        if self.focus_color is None:
            self.focus_color = white
            redisplay = True
        if redisplay:
            #self.create_mask()
            self.display_images()

    def focus_on_node(self, node):
        self._focus_node = None
        self.focus_label = None
        self.focus_color = None
        if node is not None:
            self._focus_node = node
            self.focus_label = node.label
            self.focus_color = node.color_array

    def create_mask(self):
        self.labels_imaging = None
        rotated_labels = self.rotated_labels
        if rotated_labels is None:
            self.info("Can't create mask -- no rotated labels.")
            return
        #nodes = list(self.label_to_nodes.values())
        labels = list(self.label_to_nodes.keys())
        all_nodes = self.timestamp.label_to_node.values()
        label_to_color = {}
        for node in all_nodes:
            color = node.color_array
            label = node.label
            if color is not None and label is not None:
                label_to_color[label] = color
        self.labels_imaging = MaskImaging(rotated_labels, labels, label_to_color)

    def create_mask_delete(self):
        "create the focus mask"
        label = self.focus_label
        labels = self.labels
        if label is None or labels is None:
            self.focus_mask = None
            return
        node = self.timestamp.label_to_node.get(label)
        if node is not None:
            assert node.color_array is not None, "color not assigned to node: " + repr(node)
            self.focus_color = node.color_array
        rlabels = self.rotated_labels
        target = (rlabels == label).astype(np.ubyte)
        projected = operations3d.extrude0(target)
        self.focus_mask = colorizers.boundary_image(projected, 1)

    def clear_images(self):
        #self.load_images(None, None)
        #self.display_images()
        self.image_display.change_array(dummy_image)
        self.labels_display.change_array(dummy_image)

    def load_images_delete(self, img, labels):
        "load images *before* added annotations (like outlines)."
        if img is None:
            self.img = dummy_image
            self.valid_projection = False
        else:
            img = colorizers.scale256(img)  # ???? xxxx
            if (labels is not None) and self.mask:
                img = np.where((labels != 0), img, 0)
            img = colorizers.to_rgb(img, scaled=False)
            self.img = img
            self.valid_projection = True
        if labels is None:
            self.labels = dummy_image
        else:
            self.labels = labels

    def load_mask(self, other):
        #self.compare_mask = other.focus_mask
        #self.compare_color = other.focus_color
        self.compare_labels_imaging = other.labels_imaging

    def display_images(self):
        imaging = self.labels_imaging
        if imaging is None:
            self.clear_images()
            self.info("No imaging to display for " + repr(self.timestamp))
            return
        c_imaging = self.compare_labels_imaging
        rimage = self.rotated_image
        #if imaging.nontrivial() and self.mask:
        #    rimage = np.where(imaging.selected_label_mask, rimage, 0)
        #image2d = rimage.max(axis=0)  # maximum value projection.
        image2d = imaging.max_value_projection(rimage, mask=self.mask, restricted=self.restrict)
        if self.enhance:
            image2d = colorizers.enhance_contrast(image2d, cutoff=0.05)
        img = colorizers.scale256(image2d)  # ???? xxxx
        # add color boundaries to img
        img = imaging.overlay_boundaries(img)
        if c_imaging is not None:
            img = c_imaging.overlay_boundaries(img)
        # get labels with white outlines
        speckle_ratio = None
        restricted = self.restrict
        if self.speckle:
            speckle_ratio = STD_SPECKLE_RATIO
        labels = imaging.extrusion(speckle_ratio=speckle_ratio, restricted=restricted)
        self.labels = labels
        if self.speckle:
            # unspeckled array for mouse clicks
            self.labels = imaging.extrusion(speckle_ratio=None, restricted=restricted)
        colored_labels = imaging.color_mapper[labels]
        white = [255,255,255]
        colored_labels = imaging.overlay_boundaries(colored_labels, white)
        self.image_display.change_array(img)
        self.labels_display.change_array(colored_labels)

    def display_images_delete(self):
        #label = self.focus_label
        labels = self.labels
        if labels is None:
            self.info("No volume labels to display")
            return
        maxlabel = labels.max()
        color_mapping_array = None
        if self.timestamp is not None:
            color_mapping_array = self.timestamp.color_mapping_array(maxlabel)
        self.color_mapping_array = color_mapping_array # for debug
        labels = colorizers.colorize_array(labels, color_mapping_array)
        img = self.img
        fmask = self.focus_mask
        #cmask = self.compare_mask
        if self.valid_projection:
            if fmask is not None:
                white = [255,255,255]
                labels = colorizers.overlay_color(labels, fmask, white)
            for (mask, color) in [
                (self.focus_mask, self.focus_color),
                (self.compare_mask, self.compare_color)]:
                if mask is not None:
                    assert color is not None, "no color for mask?"
                    #assert img.shape == mask.shape, "shapes don't match: " + repr([img.shape, mask.shape])
                    img = colorizers.overlay_color(img, mask, color, center=True)
        img = self.pad_image(img)
        labels = self.pad_image(labels)
        self.image_display.change_array(img)
        self.labels_display.change_array(labels)

    def pad_image(self, img):
        "Pad image to square shape."
        shape = img.shape
        (w, h) = img.shape[:2]
        if w == h:
            return img
        if w < h:
            padding = int((h - w) / 2)
            new_shape = list(shape)
            new_shape[:2] = [h, h]
            imgp = np.zeros(new_shape, dtype=img.dtype)
            imgp[padding: w+padding] = img
            return imgp
        else:
            assert w > h
            padding = int((w - h) / 2)
            new_shape = list(shape)
            new_shape[:2] = [w, w]
            imgp = np.zeros(new_shape, dtype=img.dtype)
            imgp[:, padding: h+padding] = img
            return imgp
