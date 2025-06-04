import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
import xml.dom.minidom

def list_str(ls):
  s = ""
  for l in ls:
    s += l + ","
  return s[:-1]

class Place:
  def __init__(self, id, name, color, init=False, fin=False):
    self._id = id
    self._name = name
    self._color = color
    self._is_final = init
    self._is_initial = fin

  def to_pnml(self, doc):
    xp = doc.createElement("place")
    xp.setAttribute("id", str(self._id))
    xp.setAttribute("color", list_str(self._color))
    xname = doc.createElement("name")
    xpname = doc.createTextNode(self._name)
    xname.appendChild(xpname)
    xp.appendChild(xname)
    # FIXME also finalMarking tag?
    return xp


class Transition:
  def __init__(self, id, label, silent):
    self._id = id
    self._label = label
    self._is_silent = silent

  def to_pnml(self, doc):
    xt = doc.createElement("transition")
    xt.setAttribute("id", str(self._id))
    if self._is_silent:
      xt.setAttribute("invisible","true")
    xname = doc.createElement("name")
    xtname = doc.createTextNode(self._label)
    xname.appendChild(xtname)
    xt.appendChild(xname)
    return xt


class Inscription:
  def __init__(self):
    pass

  def mk_label(self,s):
    return s[0:1]

  def mk_labels(self,ls):
    return [ self.mk_label(l) for l in ls ]

  @staticmethod 
  def singleton(otype, is_variable):
    insc = Inscription()
    insc._is_variable = is_variable
    insc._is_nu = False
    insc._object_types = [otype]
    lab = otype.upper() if is_variable else otype.lower()
    insc._labels = [insc.mk_label(lab)]
    return insc

  @staticmethod 
  def many(otypes, labels, is_variable):
    insc = Inscription()
    insc._is_variable = is_variable
    insc._is_nu = False
    insc._object_types = otypes
    insc._labels = insc.mk_labels(labels)
    return insc

  @staticmethod 
  def nu(otype):
    insc = Inscription()
    insc._is_variable = False
    insc._is_nu = True
    insc._object_types = [otype]
    insc._labels = [insc.mk_label(otype.lower())]
    return insc

  def __str__(self):
    s = ""
    for l in self._labels:
      #s += ("\u03BD" if self._is_nu else "") + l + ","
      s += ("nu_" if self._is_nu else "") + l + ","
    return "(" + s[:-1] + ")"

  def pnml_string(self):
    s = ""
    for pair in zip(self._labels, self._object_types):
      l, otype = pair
      s += ("nu_" if self._is_nu else "") + l + ":" + otype + ","
    return s[:-1]


class Arc:
  def __init__(self, src, tgt, insc):
    self._source = src
    self._target = tgt
    self._inscription = insc
    self._is_variable = insc._is_variable

  def to_pnml(self, doc):
    xa = doc.createElement("arc")
    xa.setAttribute("source", str(self._source))
    xa.setAttribute("target", str(self._target))
    xa.setAttribute("inscription", self._inscription.pnml_string())
    return xa
  

class OPID: 
  id_count = 0

  def __init__(self):
    self._transitions = []
    self._places = []
    self._arcs = []
    self._creating_transitions = {} # map object typ to transition
    self._consuming_transitions = {} # map object type to transition

  @staticmethod
  def get_id():
    OPID.id_count += 1
    return OPID.id_count
  
  def sanity_check(self):
    self._object_types = set([ t for p in self._places for t in p._color ])
    fail = False
    msg = ""
    if not all(t in self._consuming_transitions for t in self._object_types):
      t = next(t for t in self._object_types if t not in self._consuming_transitions)
      msg = f"object type {t} has no consuming transition"
      fail = True
    if not all(t in self._creating_transitions for t in self._object_types):
      t = next(t for t in self._object_types if t not in self._creating_transitions)
      msg = f"object type {t} has no creating transition"
      fail = True
    if fail:
      print("Sanity check failed: "+msg)
      exit(2)

  def make_creating_transition(self, into):
    otype = into._color[0]
    id = OPID.get_id()
    t = Transition(id, "create "+otype, True)
    self._transitions.append(t)
    insc = Inscription.nu(otype)
    self._arcs.append(Arc(id, into._id, insc))
    self._creating_transitions[otype] = t

  def make_consuming_transition(self, outof):
    otype = outof._color[0]
    id = OPID.get_id()
    t = Transition(id, "consume "+otype, True)
    self._transitions.append(t)
    insc = Inscription.singleton(otype, False)
    self._arcs.append(Arc(outof._id, id, insc))
    self._consuming_transitions[otype] = t


  # implements the first translation proposed in the paper
  @staticmethod
  def from_ocpn_json(json, object_creation=True):
    opid = OPID()
    opid._name = json["name"]
    opid._has_object_creation = object_creation
    if "properties" in json:
      opid._properties = json["properties"] # arbitrarily structured json
      
    places = {}
    set_init_fin = not object_creation
    for p in json["places"]:
      place = Place(OPID.get_id(), p["name"], [p["objectType"]],
                    set_init_fin and p["initial"], set_init_fin and p["final"])
      places[p["name"]] = place
      if p["initial"]:
        opid.make_creating_transition(place)
      if p["final"]:
        opid.make_consuming_transition(place)
    transs = {}
    for t in json["transitions"]:
      trans = Transition(OPID.get_id(), t["label"], t["silent"])
      transs[t["name"]] = trans
    
    for a in json["arcs"]:
      srcname, tgtname = a["source"], a["target"]
      srcid = places[srcname]._id if srcname in places else transs[srcname]._id
      tgtid = places[tgtname]._id if tgtname in places else transs[tgtname]._id
      ot = (places[srcname] if srcname in places else places[tgtname])._color[0]
      arc = Arc(srcid, tgtid, Inscription.singleton(ot, a["variable"]))
      opid._arcs.append(arc)
    opid._transitions += transs.values()
    opid._places = list(places.values())
    opid.sanity_check()
    return opid

  def transition_types(self, t):
    ins = [ a._source for a in self._arcs if a._target == t._id ]
    outs = [ a._target for a in self._arcs if a._source == t._id ]
    places = [ p for p in self._places if p._id in (ins + outs) ]
    types = [ t for p in places for t in p._color ]
    return types

  def connect_transitions_to_link_place(self, one, many, link_place, ignore):

    def get_place_for(t, otype, pre = True): # get id of pre or post place of t
      if pre:
        ps = [a._source for a in self._arcs if a._target == t._id and \
          otype in a._inscription._object_types]
      else:
        ps = [a._target for a in self._arcs if a._source == t._id and \
          otype in a._inscription._object_types]
      return None if len(ps) == 0 else ps[0]
    
    for t in self._transitions:
      if (not set([one, many]).issubset(self.transition_types(t))) or \
        t._id in ignore:
        continue
      in_one = get_place_for(t, one, True)
      in_many = get_place_for(t, many, True)
      out_one = get_place_for(t, one, False)
      out_many = get_place_for(t, many, False)
      if None in [in_one, in_many, out_one, out_many]:
        print("Warning: transition '%s' ignored for types (%s,%s)" % \
          (t._label, many, one))
        continue
      print(" enforce many-to-one wrt %s-to-%s for %s" % (many, one, t._label))
      arcs = [a for a in self._arcs if a._source == in_many and a._target == t._id]
      if len(arcs) == 0:
        print(t._label, "no arc found")
      arc = arcs[0]
      if arc._inscription._is_variable:
        insc = Inscription.many([many, one], [many.upper(), one.lower()], True)
      else:
        insc = Inscription.many([many, one], [many.lower(), one.lower()], False)
      self._arcs.append(Arc(link_place._id, t._id, insc))
      self._arcs.append(Arc(t._id, link_place._id, insc))

  def add_many_to_one_syncs(self, many_one_types):
    for (many, one) in many_one_types:
      self.add_many_to_one_sync(many, one)

  def add_many_to_one_sync(self, many, one):
    linkname = "link %s-%s" % (many, one)
    link_place = Place(self.get_id(), "P"+linkname, [many, one])
    pb_many = Place(self.get_id(), "Pb "+many, [many])
    pb_one = Place(self.get_id(), "Pb "+one, [one])
    pa_many = Place(self.get_id(), "Pa "+many, [many])
    pa_one = Place(self.get_id(), "Pa "+one, [one])
    self._places += [link_place, pb_many, pb_one, pa_many, pa_one]
    link_trans = Transition(self.get_id(), "T"+linkname, True)
    ti_many = Transition(self.get_id(), "Ti "+many, True)
    ti_one = Transition(self.get_id(), "Ti "+one, True)
    self._transitions += [link_trans, ti_many, ti_one]
    insc_m = Inscription.singleton(many, is_variable=False)
    insc_o = Inscription.singleton(one, is_variable=False)
    insc_M = Inscription.singleton(many, is_variable=True)
    # connect Ti to Pb
    self._arcs.append(Arc(ti_many._id, pb_many._id, Inscription.nu(many)))
    self._arcs.append(Arc(ti_one._id, pb_one._id, Inscription.nu(one)))
    # connect Pb to link transition Tl
    self._arcs.append(Arc(pb_many._id, link_trans._id, insc_M))
    self._arcs.append(Arc(pb_one._id, link_trans._id, insc_o))
    # connect Tl to Pl and Pl to consuming transitions
    self._arcs.append(Arc(link_trans._id, link_place._id, 
      Inscription.many([many, one], [many.upper(), one.lower()], True)))
    consume_many = self._consuming_transitions[many]
    self._arcs.append(Arc(link_place._id, consume_many._id, 
      Inscription.many([many, one], [many.lower(), one.lower()], False)))
    # connect Tl to Pa
    self._arcs.append(Arc(link_trans._id, pa_many._id, insc_M))
    self._arcs.append(Arc(link_trans._id, pa_one._id, insc_o))
    # connect Pa to Te
    create_one = self._creating_transitions[one]
    self._creating_transitions[one] = ti_one
    create_many = self._creating_transitions[many]
    self._creating_transitions[many] = ti_many
    self._arcs.append(Arc(pa_one._id, create_one._id , insc_o))
    self._arcs.append(Arc(pa_many._id, create_many._id, insc_m))
    # replace inscription
    te_many = next(a for a in self._arcs if a._source == create_many._id)
    te_many._inscription = insc_m
    te_one = next(a for a in self._arcs if a._source == create_one._id)
    te_one._inscription = insc_o
    # add arcs to transitions that deal with both types
    ignore = [link_trans._id, consume_many._id]
    self.connect_transitions_to_link_place(one, many, link_place, ignore)

  def to_pnml(self):
    doc = xml.dom.minidom.parseString("<pnml/>")
    root = doc.documentElement
    #root.setAttribute("xes.version", "1849-2016")
    #root.setAttribute("xes.features", "nested-attributes")
    #root.setAttribute("xmlns", "http://www.xes-standard.org/")
    net = doc.createElement("net")
    root.appendChild(net)
    page = doc.createElement("page")
    net.appendChild(page)
    xname = doc.createElement("name")
    xtname = doc.createTextNode(self._name)
    xname.appendChild(xtname)
    page.appendChild(xname)
    for place in self._places:
      page.appendChild(place.to_pnml(doc))
    for t in self._transitions:
      page.appendChild(t.to_pnml(doc))
    for arc in self._arcs:
      page.appendChild(arc.to_pnml(doc))
    return root

  def to_dot(self, outdir, outname):
    g = nx.MultiDiGraph()
    g.add_nodes_from([p._id for p in self._places])
    g.add_nodes_from([t._id for t in self._transitions])
    g.add_edges_from([ (a._source, a._target) for a in self._arcs ])
    pos = nx.spring_layout(g)
    n = nx.draw_networkx_nodes(g, pos, node_size = 50)
    e = nx.draw_networkx_edges(g, pos, arrows=True)

    A = to_agraph(g) 
    A.node_attr['fontsize'] = "11"
    A.edge_attr['fontsize'] = "10"
    A.node_attr['fontname'] = "Arial"
    A.edge_attr['fontname'] = "Arial"
    A.edge_attr['arrowsize'] = "0.6"

    st = {}
    for a in self._arcs:
      (src,tgt) = (a._source, a._target)
      st[(src,tgt)] = 0 if (src,tgt) not in st else st[(src,tgt)] + 1
      edge = A.get_edge(src,tgt,st[(src,tgt)])
      edge.attr['label'] = str(a._inscription)
      edge.attr['penwidth'] = (2 if a._is_variable else 1)
    for p in self._places:
      n = A.get_node(p._id)
      n.attr['shape']='circle'
      n.attr['margin']="0.1,0.005"
      n.attr['label'] = p._name
      n.attr['height']="0.3"
      if p._is_final:
        n.attr['style']='filled'
        n.attr['fillcolor']='gray'
    for t in self._transitions:
      n = A.get_node(t._id)
      n.attr['shape']='box'
      n.attr['margin']="0.1,0.005"
      n.attr['label'] = t._label
      n.attr['height']="0.3"
      if t._is_silent:
        n.attr['style']='filled'
        n.attr['fillcolor']='black'

    A.layout('dot') 
    A.draw(outdir + outname + ".dot")  

