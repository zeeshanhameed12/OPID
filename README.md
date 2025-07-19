# OPID
Object Centric Petrinet With Identifier <br>
Althogh OCPNs describe how objects
of di!erent types flow through the process and co-participate
in events, they do not provide mechanisms for tracking the identity of
objects and their relationships, making the synchronization of objects
ambiguous.  We aim to identify the class of object-centric executions with stable many-to-one relationships that can provide mechanisms
for tracking the identity of objects and their relationships.
The transformation of OCPN to OPID consist of following four major stps: <br> First, we consider arbitrary executions, showing how to map
an OCPN into an equivalent OPID that retains the same ambiguity in dealing with object identity and relationships. Second, we formalize stable many-to-one relationships on pairs of object types, formally capturing that whenever two objects of those types co-participate in an event, they form a stable relationship
that is never altered during the execution. Third, we provide an encoding that,
given an input OCPN and stable relationships, produces a corresponding OPID
in which the identity of objects is tracked, and stable relationships are established
and used in synchronization points. Finally, we show that, while the so-obtained
OPID is more restrictive than the original OCPN, they are indeed identical when
restricting only to executions with stable relationships.

# OPID Net Generation and Visualization Tool

This repository provides a two-stage tool for generating and visualizing Object-Centric Petri Nets (OPID Nets) from event logs. The tool is implemented in Python and uses the Graphviz package for visualization.

---

## 🛠 How to Use the Tool

The tool operates in two main stages:

1. **OPID Net Generation**  
   - The first stage processes an event log and generates an OPID Net.
   - The resulting OPID Net is stored in JSON format for further analysis and visualization.

2. **Visualization**  
   - The second stage reads the generated JSON file and visualizes the OPID Net using the [Graphviz](https://graphviz.org/) package.

---

## ⚙️ Assumptions

This tool assumes a **many-to-one synchronization model** between object types. Given two object types `(T1, T2)`:

- `T1` is always treated as the **many-type**.
- `T2` is always treated as the **one-type**.

### Example  
For object types like `(wheel, frame)`, the tool assumes:
- `wheel` → many-type
- `frame` → one-type  
This is based on the assumption that a single frame can have multiple wheels.

**Important**:
- When specifying object type pairs, always list the many-type first.
- The silent transition that consumes tokens from the link place at the end of the process should correspond to the many-type object.

---

## 🧩 Versions

### Version 1
- **Scripts**:
  - `OPID_FI_v1.py`: Generates the OPID Net.
  - `view_OPID_FI_v1.py`: Visualizes the generated OPID Net.
- **Behavior**:
  - Accepts multiple object type pairs.
  - Produces a **single, unified OPID Net**.
  - Includes all specified pairs as well as all other object types found in the event log.
  - Provides a **combined view** of the entire model.

### Version 2
- **Scripts**:
  - `OPID_FI_v2.py`: Generates the OPID Net.
  - `view_OPID_FI_v2.py`: Visualizes the generated OPID Net.
- **Behavior**:
  - Accepts multiple object type pairs.
  - Generates **separate OPID Nets** for each pair.
  - Excludes all other object types in the event log not explicitly specified.
  - Offers a **modular and focused view** for each object type pair.

---

## 📦 Requirements

The following packages are required to run the tool:

```bash
pm4py
graphviz

