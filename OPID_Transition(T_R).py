import pm4py
import json
import uuid
from pm4py.algo.discovery.ocel.ocpn.variants import classic as ocpn_discovery
from pm4py.objects.petri_net.obj import PetriNet

class Place:
    def __init__(self, name, objectType, initial=False, final=False):
        self.name = name
        self.objectType = objectType
        self.initial = initial
        self.final = final

class Transition:
    def __init__(self, name, label, silent=True, properties=None):
        self.name = name
        self.label = label
        self.silent = silent
        self.properties = properties or {}

class Arc:
    def __init__(self, source, target, weight="1.0", variable=False, inscription="", properties=None):
        self.source = source
        self.target = target
        self.weight = weight
        self.variable = variable
        self.inscription = inscription
        self.properties = properties or {}

class OPID:
    def __init__(self, name):
        self.name = name
        self.places = []
        self.transitions = []
        self.arcs = []
        self.place_name_map = {}
        self.transition_name_set = set()
        self.silent_map = {}
        self.unique_place_id = 0

    def add_place(self, place):
        self.places.append(place)

    def add_transition(self, transition):
        self.transitions.append(transition)
        self.transition_name_set.add(transition.name)

    def add_arc(self, arc):
        self.arcs.append(arc)

    def get_transition_name(self, transition):
        if transition.label:
            return transition.label
        else:
            if transition in self.silent_map:
                return self.silent_map[transition]
            base_name = transition.name if transition.name else "tau"
            silent_name = base_name
            counter = 0
            while silent_name in self.transition_name_set:
                counter += 1
                silent_name = f"{base_name}_{counter}"
            self.silent_map[transition] = silent_name
            self.transition_name_set.add(silent_name)
            self.add_transition(Transition(silent_name, silent_name, silent=True))
            return silent_name

    def to_json(self):
        return {
            "name": self.name,
            "places": [vars(p) for p in self.places],
            "transitions": [vars(t) for t in self.transitions],
            "arcs": [vars(a) for a in self.arcs],
            "properties": {
                "creator": "PM4Py",
                "source": "OCPN Export",
                "version": "1.0"
            }
        }

# Load OCEL log
filename = "selfocel.xml"
ocel = pm4py.read_ocel2_xml(filename)
customized_View = input("please enter the pair of object types (R) you want to visualize in the OPID view (e.g., 'frame,handle'): ")
# Split the input by comma and strip whitespace and store in a list
object_types = customized_View.split(',')

# Filter OCEL by object types
filtered_ocel = pm4py.filtering.filter_ocel_object_types(ocel, object_types)
ocpn = ocpn_discovery.apply(filtered_ocel)

opid = OPID("Self OCPN Export")
# Add transitions
for act in ocpn["activities"]:
    opid.add_transition(Transition(name=act, label=act, silent=False))
#print("items", ocpn["petri_nets"].items())
# Places and Arcs
for ot, (net, initial_marking, final_marking) in ocpn["petri_nets"].items():
    for place in net.places:
        place_name = f"place_{opid.unique_place_id}"
        opid.place_name_map[place] = place_name
        opid.unique_place_id += 1

        opid.add_place(Place(
            name=opid.place_name_map[place],
            objectType=ot,
            initial=place in initial_marking,
            final=place in final_marking
        ))

    for arc in net.arcs:
        if arc.source in opid.place_name_map:
                source_name = opid.place_name_map[arc.source]
                target_name = opid.get_transition_name(arc.target) 
        else:
                source_name = opid.get_transition_name(arc.source)
                target_name = opid.place_name_map[arc.target]

        if type(arc.source) is PetriNet.Place:
                is_double = (
                    arc.target.label in ocpn["double_arcs_on_activity"][ot]
                    and ocpn["double_arcs_on_activity"][ot][arc.target.label]
                )
                penwidth = "4.0" if is_double else "1.0"
        elif type(arc.source) is PetriNet.Transition:
                is_double = (
                    arc.source.label in ocpn["double_arcs_on_activity"][ot]
                    and ocpn["double_arcs_on_activity"][ot][arc.source.label]
                )
                penwidth = "4.0" if is_double else "1.0"

        opid.add_arc(Arc(
            source=source_name,
            target=target_name,
            weight=penwidth,
            variable=is_double,
            inscription=ot[0].capitalize() if is_double else ot[0],
        ))

    for place in initial_marking:
        silent_name = f"tau_start_{ot}_{uuid.uuid4()}"
        opid.add_transition(Transition(name=silent_name, label="", silent=True))
        opid.add_arc(Arc(
            source=silent_name,
            target=opid.place_name_map[place],
            inscription=f"v_{ot[0]}"
        ))

    for place in final_marking:
        silent_name = f"tau_end_{ot}_{uuid.uuid4()}"
        opid.add_transition(Transition(name=silent_name, label="", silent=True))
        opid.add_arc(Arc(
            source=opid.place_name_map[place],
            target=silent_name,
            inscription=ot[0]
        ))

# adding places arcs and transition in a dictionary
opid_dic = {
    "places": [vars(place) for place in opid.places],
    "transitions": [vars(transition) for transition in opid.transitions],
    "arcs": [vars(arc) for arc in opid.arcs],
    "properties": {"First transition (R1)"}
}
#print("opid_dic:", opid_dic)


output_path = "opid_view.json"
with open(output_path, 'w') as json_file:
    json.dump(opid.to_json(), json_file, indent=4)

"""# view the opid_view using graphviz and save it as PNG
from graphviz import Digraph
def visualize_opid(opid_view):
    dot = Digraph("OCPN_Visualization", format="png")
    dot.attr(rankdir="LR")  # Left to right layout

    # Draw Places
    for place in opid_view["places"]:
        fillcolor = "lightgray"  # Default color
        if place["initial"]:
            fillcolor = "green"
        elif place["final"]:
            fillcolor = "red"

        dot.node(place["name"],
                 label=place["name"],
                 shape="circle",
                 style="filled",
                 fillcolor=fillcolor)

    # Draw Transitions
    for transition in opid_view["transitions"]:
        label = transition["label"] if transition["label"] else "τ"
        style = "dashed" if transition["silent"] else "filled"
        dot.node(transition["name"],
                 label=label,
                 shape="box",
                 style=style)

    # Draw Arcs
    for arc in opid_view["arcs"]:
        source = arc["source"]
        target = arc["target"]
        label = arc.get("inscription", "")
        penwidth = "3" if arc["variable"] else "1"
        dot.edge(source, target, label=label, penwidth=penwidth)

    return dot
# Render and view the graph
opid_graph = visualize_opid(opid_dic)
output_graph_path = "opid_view"
opid_graph.render(output_graph_path, view=True)
# The code above creates an OPID (Object-centric Petri net) from an OCEL (Object-centric Event Log) and visualizes it using Graphviz."""