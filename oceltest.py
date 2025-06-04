import pm4py
import pandas as pd
from typing import Optional, Dict, Any
from copy import copy
import json
from pm4py.ocel import ocel_get_object_types, ocel_object_type_activities, ocel_get_attribute_names
from pm4py import ocel_objects_interactions_summary, ocel_objects_summary
from pm4py.visualization.ocel.ocpn import visualizer as ocpn_visualizer
from pm4py.algo.discovery.ocel.ocdfg import algorithm as ocdfg_discovery
from pm4py.visualization.ocel.ocdfg import visualizer as ocdfg_visualizer
from pm4py.util import exec_utils

filename = "selfocel.xml"
ocel = pm4py.read_ocel2_xml(filename)
#print(ocel)

objects = ocel.objects # get all the objects in the OCEL
print("the objects in the OCEL are:")
print(objects)
print("--------------------------------")
object_types = pm4py.ocel.ocel_get_object_types(ocel)
print("the object types in the OCEL are:")
print(object_types)
print("--------------------------------")
obtypes_activities = pm4py.ocel_object_type_activities(ocel) # get the activities of each object type
print("the activities of each object type in the OCEL are:")
print(obtypes_activities)
print("--------------------------------")
# get the object-object relations
object_object_relations = ocel_objects_interactions_summary(ocel)
print("the relationship between the objects in the OCEL are:")
print(object_object_relations)
print("--------------------------------")
obj_activ_relations = ocel.relations # get all the relations in the OCEL
print(" the relationship between the objects and events in the OCEL are:")
print(obj_activ_relations)
print("--------------------------------")
sumary = pm4py.ocel_objects_summary(ocel) # get the summary of the objects
print("The objects summary provides a table that reports each object along with the list of related activities, the start/end timestamps of the object's lifecycle, the lifecycle's duration, and related objects in the interaction graph")
print((sumary))
print("--------------------------------")



# basic to advanced statistics on the OCEL


events = ocel.events # get all the events in the OCEL
print("the events in the OCEL are:")
print(events)
print("--------------------------------")




# get the attributes of the OCEL
"""
# we can inspect the OCEL
object_types = ocel_get_object_types(ocel)
print("the object types in the OCEL are:")
print(object_types)
print("--------------------------------")

events = (ocel.events)
print("the events in the OCEL are:")
print(events)
print("--------------------------------")

objects = (ocel.objects)
print("the objects in the OCEL are:")
print(objects)
print("--------------------------------")
relation = (ocel.relations)
print("the relations in the OCEL are:")
print(relation)
print("--------------------------------")

parameters = {}
parameters["double_arc_threshold"] = 0.8
parameters["inductive_miner_variant"] = "im"
parameters["diagnostics_with_tbr"] = False

ocdfg_parameters = copy(parameters)
ocdfg_parameters["compute_edges_performance"] = False
ocdfg = ocdfg_discovery.apply(ocel, parameters=ocdfg_parameters)
gviz = ocdfg_visualizer.apply(ocdfg)
ocdfg_visualizer.save(gviz, "ocdfg_graph.png")
print("Graph saved as 'ocdfg_graph.png'")
#ocpn = pm4py.discover_oc_petri_net(ocel)


ocdfg = ocdfg_discovery.apply(ocel)
gviz = ocdfg_visualizer.apply(ocdfg)
ocdfg_visualizer.view(gviz)
object_summary = ocel_objects_summary(ocel)
print("here is a part of the object summary:")
print(object_summary.head(10))
"""
print("now we discover an OCPN from the OCEL ...")
ocpn = pm4py.discover_oc_petri_net(ocel)
print("activities in the OCPN:")
print(ocpn["activities"])
print("------------------")
print("OCPN object types:")
print(ocpn["object_types"])
print("------------------")
print("OCPN edges:")
print(ocpn["edges"])  
print("------------------")
print("event couples in edges:")
print(ocpn["edges"]["event_couples"])
print("------------------")
print("unique objects in edges:")
print(ocpn["edges"]["unique_objects"])
print("------------------")
print("total objects in edges:")
print(ocpn["edges"]["total_objects"])
print("------------------") 
#ocpn_visualizer.view(ocpn)
gviz = ocpn_visualizer.apply(ocpn)
ocpn_visualizer.save(gviz, "ocpnself.png")
print("Graph saved as 'ocpn_graph.png'")
#ocpn_visualizer.view(gviz)
#ocpn_visualizer.view(gviz)
#pm4py.view_ocpn(ocpn)




def export_ocpn_to_json(ocpn, file_path, name="Object-Centric Petri Net"):
    """
    Exports an object-centric Petri net (OCPN) from PM4Py into a JSON structure and file.
    
    Parameters:
        ocpn (dict): The object-centric Petri net structure from PM4Py (expects ocpn["petri_nets"]).
        file_path (str): File path to save the resulting JSON.
        name (str): Name for the Petri net (will appear in the JSON "name" field).
    
    Returns:
        dict: The JSON-serializable dictionary representing the OCPN.
    """
    # Initialize the JSON structure components
    places_json = []       # list of place dictionaries
    transitions_json = []  # list of transition dictionaries
    arcs_json = []         # list of arc dictionaries
    
    # Keep track of used transition names (to ensure uniqueness) and a map for silent transitions
    used_transition_names = set()    # collects all transition 'name' values added (both labeled and silent)
    silent_map = {}                 # maps Transition objects (silent) to their assigned unique name
    
    # 1. Collect all non-silent transition labels (activities) to define transitions.
    # If the ocpn dict provides an 'activities' list, use that; otherwise, gather from the Petri nets.
    activities = ocpn.get("activities")
    if activities is None:
        # Gather unique labels from transitions in all nets
        activities = set()
        for ot, (net, _, _) in ocpn["petri_nets"].items():
            for trans in net.transitions:
                if trans.label is not None:
                    activities.add(str(trans.label))
        activities = sorted(activities)  # optional: sort the activities list (for consistency)
    else:
        # If activities is provided (likely as a list), ensure unique and preserve order
        activities = list(dict.fromkeys(activities))  # remove any duplicates while preserving order
    
    # Add each activity as a transition in the JSON (non-silent transitions)
    for act in activities:
        transitions_json.append({
            "name": str(act),    # use the activity label as the transition's unique name
            "label": str(act),   # display label (same as name for non-silent transitions)
            "silent": False,
            "properties": {}       # default empty properties
        })
        used_transition_names.add(str(act))
    
    # 2. Assign unique names to all places across object types and record their attributes.
    place_name_map = {}  # map from Place object to unique place name
    unique_place_id = 0
    for ot, (net, initial_marking, final_marking) in ocpn["petri_nets"].items():
        for place in net.places:
            # Generate a unique place name (e.g., append an incrementing index)
            base_name = place.name if place.name is not None else "place"
            unique_name = f"{base_name}_{unique_place_id}"
            unique_place_id += 1
            # Determine if this place is initial or final by checking the markings
            is_initial = False
            is_final = False
            if initial_marking is not None and place in initial_marking:
                # initial_marking[place] gives the number of tokens in the place at start
                is_initial = initial_marking[place] > 0
            if final_marking is not None and place in final_marking:
                # final_marking[place] gives number of tokens in place at end
                is_final = final_marking[place] > 0
            # Append the place to the JSON list
            places_json.append({
                "name": unique_name,
                "objectType": str(ot),
                "initial": is_initial,
                "final": is_final
            })
            # Store mapping from the place object to its new unique name
            place_name_map[place] = unique_name
    
    # 3. Helper function to get transition name (and handle silent transitions)
    def get_transition_name(trans_obj):
        """
        Return the unique transition name for a Transition object, adding to transitions_json if needed.
        For silent transitions (trans_obj.label is None), assign a unique name and mark as silent.
        """
        if trans_obj.label is not None:
            # Labeled transition: use the label as the name (already added in transitions_json)
            return str(trans_obj.label)
        else:
            # Silent transition: assign or retrieve a unique name
            if trans_obj in silent_map:
                return silent_map[trans_obj]
            # If not seen before, create a new entry for this silent transition
            base_name = trans_obj.name if trans_obj.name is not None else "tau"  # base identifier
            silent_name = base_name
            # Ensure the chosen name is unique among all transition names used so far
            counter = 0
            while silent_name in used_transition_names:
                counter += 1
                silent_name = f"{base_name}_{counter}"
            # Mark this transition as used and add to transitions list
            silent_map[trans_obj] = silent_name
            used_transition_names.add(silent_name)
            transitions_json.append({
                "name": silent_name,
                "label": silent_name,  # for silent transitions, we use the name as the label placeholder
                "silent": True,
                "properties": {}
            })
            return silent_name
    
    # Traverse each net's arcs and build the arcs list in the JSON structure
    for ot, (net, _, _) in ocpn["petri_nets"].items():
        for arc in net.arcs:
            # Determine if arc is place-to-transition or transition-to-place by source/target type
            if arc.source in place_name_map:
                # Source is a Place, target must be a Transition
                source_name = place_name_map[arc.source]
                target_name = get_transition_name(arc.target)
            else:
                # Source is a Transition, target is a Place
                source_name = get_transition_name(arc.source)
                target_name = place_name_map[arc.target]
            # Append arc information to arcs list
            arcs_json.append({
                "source": source_name,
                "target": target_name,
                "weight": 1,
                "variable": False,
                "properties": {}
            })
    
    # 4. Compile the final JSON structure
    ocpn_json = {
        "name": name,
        "places": places_json,
        "transitions": transitions_json,
        "arcs": arcs_json,
        "properties": {
            "creator": "PM4Py",
            "source": "OCPN Export",
            "version": "1.0"
        }
    }
    
    # Save the JSON dictionary to the specified file path
    with open(file_path, "w") as f:
        json.dump(ocpn_json, f, indent=4)
    
    return ocpn_json

export_ocpn_to_json(ocpn, "ocpn_exported.json", name="Self OCPN Export")