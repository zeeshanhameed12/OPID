import pm4py
import pandas as pd
from typing import Optional, Dict, Any
from copy import copy

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

