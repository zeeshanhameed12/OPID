import json
from graphviz import Digraph
import colorsys

# === Load JSON data ===
with open("opid_fi_v2.json", "r") as f:
    ocpn_data_list = json.load(f)

# Function to get consistent color mapping
def get_color_palette(object_types):
    palette = {}
    total = len(object_types)
    for idx, ot in enumerate(sorted(object_types)):
        hue = idx / total
        rgb = colorsys.hsv_to_rgb(hue, 0.6, 0.85)
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
        )
        palette[ot] = hex_color
    return palette

# Loop through each pair in the JSON data
for pair_data in ocpn_data_list:
    object_type_pair = pair_data["object_type_pair"]
    ocpn_json = pair_data["data"]

    # Extract all object types for color mapping
    object_types = set(p["objectType"] for p in ocpn_json["places"])
    color_map = get_color_palette(object_types)

    # Initialize Graphviz Digraph
    pair_label = f"{object_type_pair[0]}_{object_type_pair[1]}"
    dot = Digraph(f"OCPN_{pair_label}", format="png")
    dot.attr(rankdir="LR")

    # Draw Places
    for place in ocpn_json["places"]:
        place_name = place["name"]
        obj_type = place["objectType"]
        fillcolor = color_map.get(obj_type, "lightgray")

        dot.node(place_name,
                 label="",
                 shape="circle",
                 style="filled",
                 fillcolor=fillcolor)

    # Draw Transitions
    for transition in ocpn_json["transitions"]:
        label = transition["label"] if not transition["silent"] else "τ"
        style = "dashed" if transition["silent"] else "filled"
        dot.node(transition["name"],
                 label=label,
                 shape="box",
                 style=style)

    # Draw Arcs
    drawn_arcs = set()
    for arc in ocpn_json["arcs"]:
        key = (arc["source"], arc["target"])
        if key in drawn_arcs:
            continue

        source = arc["source"]
        target = arc["target"]
        label = arc.get("inscription", "")
        penwidth = "3" if arc["variable"] else "1"
        direction = "both" if arc.get("bidirectional", False) else "forward"

        # Determine arc color
        color = "black"
        for place in ocpn_json["places"]:
            if place["name"] in [source, target]:
                color = color_map.get(place["objectType"], "black")
                break

        dot.edge(source, target,
                 label=label,
                 color=color,
                 fontcolor=color,
                 penwidth=penwidth,
                 dir=direction)

        drawn_arcs.add(key)
        if direction == "both":
            drawn_arcs.add((target, source))

    # Render graph
    output_file = f"opid_view_{pair_label}"
    dot.render(output_file, view=True)




"""import json
from graphviz import Digraph
import colorsys

# === Load JSON data ===
with open("opid_view.json", "r") as f:
    ocpn_data_list = json.load(f)

# Function to get consistent color mapping
def get_color_palette(object_types):
    palette = {}
    total = len(object_types)
    for idx, ot in enumerate(sorted(object_types)):
        hue = idx / total
        rgb = colorsys.hsv_to_rgb(hue, 0.6, 0.85)
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
        )
        palette[ot] = hex_color
    return palette

# Initialize Graphviz Digraph for the entire OCPN
dot = Digraph("OCPN_All_Pairs", format="png")
dot.attr(rankdir="LR")  # Left to right layout to fit everything

# Loop through each pair in the JSON data and draw their components
drawn_arcs = set()
for pair_data in ocpn_data_list:
    object_type_pair = pair_data["object_type_pair"]
    ocpn_json = pair_data["data"]

    # Extract all object types for color mapping
    object_types = set(p["objectType"] for p in ocpn_json["places"])
    color_map = get_color_palette(object_types)

    # Draw Places
    for place in ocpn_json["places"]:
        place_name = place["name"]
        obj_type = place["objectType"]
        fillcolor = color_map.get(obj_type, "lightgray")

        dot.node(place_name,
                 label="",
                 shape="circle",
                 style="filled",
                 fillcolor=fillcolor)

    # Draw Transitions
    for transition in ocpn_json["transitions"]:
        label = transition["label"] if not transition["silent"] else "τ"
        style = "dashed" if transition["silent"] else "filled"
        dot.node(transition["name"],
                 label=label,
                 shape="box",
                 style=style)

    # Draw Arcs (detect bidirectional and avoid duplicates)
    for arc in ocpn_json["arcs"]:
        key = (arc["source"], arc["target"])
        if key in drawn_arcs:
            continue

        source = arc["source"]
        target = arc["target"]
        label = arc.get("inscription", "")
        penwidth = "3" if arc["variable"] else "1"
        direction = "both" if arc.get("bidirectional", False) else "forward"

        # Determine arc color
        color = "black"
        for place in ocpn_json["places"]:
            if place["name"] in [source, target]:
                color = color_map.get(place["objectType"], "black")
                break

        dot.edge(source, target,
                 label=label,
                 color=color,
                 fontcolor=color,
                 penwidth=penwidth,
                 dir=direction)

        drawn_arcs.add(key)
        if direction == "both":
            drawn_arcs.add((target, source))

# Render and view the entire OCPN visualization with all pairs in one graph
output_file = "opid_view_all_pairs"
dot.render(output_file, view=True)
"""
