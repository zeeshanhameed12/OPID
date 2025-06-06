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

