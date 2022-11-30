
var invisible = "rgba(0,0,0,0)";
var semi_transparent = "rgba(0,0,0,0.1)";
var up_arrow_key = 38;
var down_arrow_key = 40;

class LineageDisplay {
    // xxxx Should refactor/unify with TS detail belows
    constructor(element, width, height) {
        var that = this;
        this.element = element;
        this.width = width;
        this.height = height;
        var config = {
            width: width,
            height: height,
        };
        this.canvas_element = $("<div/>").appendTo(element);

        // stuff for arrow key handling...
        this.keypress_target = that.element.parent();
        this.keypress_target.keydown(function(event) { that.keypress_handler(event); });
        this.keypress_target.attr('tabindex', 0);
        this.keypress_target.focus();

        this.status_element = $("<div>Lineage canvas initialized</div>").appendTo(element);
        this.canvas_element.dual_canvas_helper(config);
        this.frame = null;
        this.hovered_ts = null;
        this.selected_ts = null;
        this.json_ob = null;
        this.selected_ts_callback = null;
    }
    on_select_ts(callback) {
        this.selected_ts_callback = callback;
    };
    update_status() {
        var h = this.hovered_ts;
        var s = this.selected_ts;
        var status = "Lineage time stamps: ";
        if (s !== null) {
            status += ` Selected ${s};`
        }
        if (h !== null) {
            status += ` Hover ${h};`
        }
        this.status_element.html(status)
    }
    load_json(json_ob) {
        var that = this;
        this.json_ob = json_ob;
        var element = this.canvas_element;
        element.reset_canvas();
        this.status_element.html("Drawing lineage.");
        // Y inverted!
        var f = element.frame_region(
            0, 0, this.width, this.height,
            -1, json_ob.height + 1, json_ob.width + 1, -1,
        );
        self.frame = f;
        var i2n = json_ob.id_to_node;
        for (var id in i2n) {
            var n = i2n[id];
            var x = n.offset;
            var y = n.timestamp_ordinal;
            var color = n.color || "#999";
            f.frame_rect({
                x: x,
                y: y,
                w: 0.8,
                h: 0.8,
                dx: 0.1,
                dy: 0.1,
                color: color,
            });
            var pid = n.parent_id;
            if (pid) {
                var p = i2n[pid];
                //console.log("parentage", id, n, pid, p);
                if (p) {
                    var x2 = p.offset;
                    var y2 = p.timestamp_ordinal;
                    f.line({
                        x1: x2 + 0.5,
                        y1: y2 + 0.8,
                        x2: x + 0.5,
                        y2: y + 0.2,
                    })
                }
            }
        }
        this.hover_rect = f.frame_rect({
            name: true,
            color: invisible,
            x: 0,
            y: 0,
            w: json_ob.width,
            h: 1,
        });
        this.select_rect = f.frame_rect({
            name: true,
            color: invisible,
            x: 0,
            y: 0,
            w: json_ob.width,
            h: 1,
            fill: false,
        });
        this.event_rect = f.frame_rect({
            name: true,
            color: invisible,
            x: 0,
            y: 0,
            w: json_ob.width,
            h: json_ob.height,
        });
        var event_hover = function(event) { that.update_hover(event); };
        this.event_rect.on("mousemove", event_hover);
        var event_out = function(event) { that.no_hover(event); };
        this.event_rect.on("mouseout", event_out);
        var event_click = function(event) { that.select_ts(event); };
        this.event_rect.on("click", event_click);
    };
    update_hover(event) {
        var loc = event.model_location;
        var nearest = this.nearest_ts(loc);
        this.hover_rect.change({
            y: nearest,
            color: semi_transparent,
        })
        this.hovered_ts = nearest;
        this.update_status();
        this.keypress_target.focus();
    };
    select_ts(event) {
        var loc = event.model_location;
        var nearest = this.nearest_ts(loc);
        this.focus_ts(nearest);
    };
    focus_ts(nearest) {
        this.select_rect.change({
            y: nearest,
            color: "black",
        })
        this.selected_ts = nearest;
        this.update_status();
        var cb = this.selected_ts_callback;
        if (cb) {
            cb(nearest);
        }
        this.keypress_target.focus();
    };
    keypress_handler(event) {
        var num = event.which;
        console.log("keypress num: ", num);
        var current_ts = this.selected_ts;
        var new_ts = null;
        if ((num == up_arrow_key) && (current_ts > 0)) {
            new_ts = current_ts - 1;
        }
        if ((num == down_arrow_key) && (current_ts < this.json_ob.height)) {
            new_ts = current_ts + 1;
        }
        if (new_ts !== null) {
            this.focus_ts(new_ts);
            event.preventDefault();  // don't propagate handled event
        }
    };
    no_hover(event) {
        this.hover_rect.change({
            color: invisible,
        })
        this.hovered_ts = null;
        this.update_status();
    };
    nearest_ts(loc) {
        var json_ob = this.json_ob;
        var ts = Math.floor(loc.y);
        if (ts < 0) {
            ts = 0;
        }
        if (ts > json_ob.height) {
            ts = json_ob.heignt;
        }
        return ts;
    };
}

class TimeSliceDetail {
    constructor(element, width, height) {
        this.element = element;
        this.width = width;
        this.height = height;
        var config = {
            width: width,
            height: height,
        };
        this.canvas_element = $("<div/>").appendTo(element);
        this.status_element = $("<div>timeslice detail canvas initialized</div>").appendTo(element);
        this.canvas_element.dual_canvas_helper(config);
        this.frame = null;
        this.status_change_callback = null;
        /*
        element.circle({x:0, y:0, r:100, color:"#e99"})
        element.text({x:0, y:0, text:"Hello World", degrees:45,
        font: "40pt Arial", color:"#ee3", background:"#9e9", align:"center", valign:"center"})
        element.fit()
        */
    };
    load_json(json_ob) {
        var that = this;
        this.json_ob = json_ob;
        this.hovering_node = null;
        this.selected_child = null;
        this.selected_ancestor = null;
        this.status_element.html("Drawing timeslice.");
        var element = this.canvas_element;
        element.reset_canvas();
        var f = element.frame_region(
            0, 0, this.width, this.height,
            -1, -1, json_ob.width + 1, json_ob.height + 1,
        );
        self.frame = f;
        var i2n = json_ob.id_to_node;
        for (var id in i2n) {
            var n = i2n[id];
            var x = n.x;
            var y = n.y;
            var color = n.color || "#999";
            f.frame_rect({
                x: x,
                y: y,
                w: 0.6,
                h: 0.6,
                dx: 0.2,
                dy: 0.2,
                color: color,
            });
        }
        
        for (var id in i2n) {
            var n = i2n[id];
            var pid = n.parent_id;
            if (pid) {
                var p = i2n[pid];
                //console.log("parentage", id, n, pid, p);
                if (p) {
                    var x1 = n.x;
                    var y1 = n.y;
                    var x2 = p.x;
                    var y2 = p.y;
                    f.line({
                        x1: x1 + 0.5,
                        y1: y1 + 0.8,
                        x2: x2 + 0.5,
                        y2: y2 + 0.2,
                    })
                }
            }
        } 
        this.child_rect = f.frame_rect({
            name: true,
            color: invisible,
            x: 0,
            y: 0,
            w: 0.8,
            h: 0.8,
            dx: 0.1,
            dy: 0.1,
            fill: false,
            lineWidth: 3,
        });
        this.ancestor_rect = f.frame_rect({
            name: true,
            color: invisible,
            x: 0,
            y: 0,
            w: 0.8,
            h: 0.8,
            dx: 0.1,
            dy: 0.1,
            fill: false,
            lineWidth: 3,
        });
        this.hover_rect = f.frame_rect({
            name: true,
            color: invisible,
            x: 0,
            y: 0,
            w: 1,
            h: 1,
        });
        this.event_rect = f.frame_rect({
            name: true,
            color: invisible,
            x: 0,
            y: 0,
            w: json_ob.width,
            h: json_ob.height,
        });
        var event_hover = function(event) { that.update_hover(event); };
        this.event_rect.on("mousemove", event_hover);
        var event_out = function(event) { that.no_hover(event); };
        this.event_rect.on("mouseout", event_out);
        var event_click = function(event) { that.select_node(event); };
        this.event_rect.on("click", event_click);
    };
    on_status_change(callback) {
        this.status_change_callback = callback;
    };
    update_status() {
        var h = this.hovering_node;
        var c = this.selected_child;
        var a = this.selected_ancestor;
        var status = "";
        if (c) {
            var cp = "(no parent)";
            if (c.parent_id) {
                cp = `[${c.parent_id}]`;
            }
            status += `Child ${c.identity} ${cp}; `;
        }
        if (a) {
            status += `Ancestor ${a.identity}; `;
        }
        if (h) {
            status += `Hover ${h.identity}; `;
        }
        this.status_element.html(status);
    }
    select_node(event) {
        var loc = event.model_location;
        var nearest = this.nearest_node(loc);
        if (nearest.is_child) {
            //console.log("selected child", nearest);
            this.child_rect.change({
                x: nearest.x,
                y: nearest.y,
                color: "black",
            });
            this.selected_child = nearest;
        } else {
            //console.log("selected ancestor", nearest);
            this.ancestor_rect.change({
                x: nearest.x,
                y: nearest.y,
                color: "silver",
            });
            this.selected_ancestor = nearest;
        }
        this.update_status();
        var callback = this.status_change_callback;
        if (callback) {
            var cid = null
            var pid = null
            if (this.selected_child) {
                cid = this.selected_child.identity
            }
            if (this.selected_ancestor) {
                pid = this.selected_ancestor.identity;
            }
            callback(cid, pid)
        }
    }
    update_selections(child_identity, ancestor_identity) {
        //console.log("update selection", child_identity, ancestor_identity)
        var i2n = this.json_ob.id_to_node;
        this.selected_ancestor = i2n[ancestor_identity];
        this.selected_child = i2n[child_identity];
        this.update_rectangles()
    };
    update_rectangles() {
        this.update_rectangle(this.child_rect, this.selected_child, "black");
        this.update_rectangle(this.ancestor_rect, this.selected_ancestor, "silver");
    }
    update_rectangle(rectangle, node, color) {
        if (node) {
            rectangle.change({
                x: node.x,
                y: node.y,
                color: color,
            });
        } else {
            rectangle.change({
                x: -1,
                y: -1,
                color: invisible,
            });
        }
    }
    no_hover() {
        this.hovering_node = null;
        this.hover_rect.change({
            color: invisible,
        });
        this.update_status();
    }
    update_hover(event) {
        //console.log("update hover", event);
        var loc = event.model_location;
        var nearest = this.nearest_node(loc);
        this.hover_rect.change({
            x: nearest.x,
            y: nearest.y,
            color: semi_transparent,
        });
        this.hovering_node = nearest;
        this.update_status();
    };
    nearest_node(loc) {
        var nearest = null;
        var min_distance = null;
        var i2n = this.json_ob.id_to_node;
        for (var id in i2n) {
            var n = i2n[id];
            var distance = (loc.x - 0.5 - n.x) ** 2 + (loc.y - 0.5 - n.y) ** 2;
            if (!nearest) {
                nearest = n;
                min_distance = distance;
            } else {
                if (min_distance > distance) {
                    nearest = n;
                    min_distance = distance;
                }
            }
        }
        return nearest;
    }
};

window.TimeSliceDetail = TimeSliceDetail

window.LineageDisplay = LineageDisplay;

console.log("lineage_doodle.js loaded.")
