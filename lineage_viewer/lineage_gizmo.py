
from jp_doodle import gz_doodle
from H5Gizmos.python import gz_resources
from H5Gizmos import Html, do
import os

my_dir = os.path.dirname(__file__)
support_file_name = "lineage_doodle.js"
support_file_path = gz_resources.get_file_path(support_file_name, my_dir=my_dir)

def install_js_files(to_gizmo):
    gz_doodle.add_js_files(to_gizmo)
    to_gizmo.js_file(support_file_path)

class TimeSliceDetail:

    def __init__(self, height, width, colorize="tracks"):
        self.height = height
        self.width = width
        self.colorize = colorize
        self.gizmo = Html("<div>Gizmo placeholder.</div>")
        install_js_files(self.gizmo)

    def configure_canvas(self):
        # run after gizmo is displayed.
        gizmo = self.gizmo
        element = gizmo.element
        window = gizmo.window
        do(self.gizmo.element.empty())
        self.detail_link = gizmo.cache("tsdetail", gizmo.new(window.TimeSliceDetail, element, self.width, self.height))
        #do(init)

    def on_select_node(self, callback):
        do(self.detail_link.on_status_change(callback))

    def update_selections(self, child_id, parent_id):
        do(self.detail_link.update_selections(child_id, parent_id))

    def load_json(self, json_ob):
        do(self.detail_link.load_json(json_ob))

class LineageDisplay(TimeSliceDetail):

    def configure_canvas(self, select_ts_callback=None):
        # run after gizmo is displayed.
        gizmo = self.gizmo
        element = gizmo.element
        window = gizmo.window
        do(self.gizmo.element.empty())
        self.detail_link = gizmo.cache("tsdetail", gizmo.new(window.LineageDisplay, element, self.width, self.height))
        do(self.detail_link.on_select_ts(select_ts_callback));
        #do(init)

    def load_forest(self, forest):
        F = forest
        F.find_tracks_and_lineages()
        F.assign_offsets()
        if self.colorize == "tracks":
            F.assign_colors_to_tracks()
        else:
            F.assign_colors_to_lineages()
        fjson = F.json_ob()
        self.load_json(fjson)

async def test_task():
    from H5Gizmos import Html
    greeting = Html("<h1>Hello</h1>")
    install_js_files(greeting)
    await greeting.link()
    return greeting

if __name__ == "__main__":
    from H5Gizmos import serve
    serve(test_task())
