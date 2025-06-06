import pm4py
ocel = pm4py.read_ocel2_xml("selfocel.xml")


# see the ocel
print(ocel)


#print(objects)
# number of object types in ocel and their names
object_types = pm4py.ocel_get_object_types(ocel)
print("Number of object types in OCEL:", len(object_types))
print("Object types in OCEL:", object_types)
print("--------------------------------")
print(ocel.objects)
print("---------------------------------")
Object_types_and_counts = ocel.objects["ocel:type"].value_counts()
print( Object_types_and_counts)
print("---------------------------------")
print(ocel.events)
print("---------------------------------")
activity_types_and_counts = ocel.events["ocel:activity"].value_counts()

print("Number of occurrences of each activity type in OCEL:", activity_types_and_counts)

print("---------------------------------")

obta = pm4py.ocel_object_type_activities(ocel) # get the activities of each object type
print("the activities of each object type in the OCEL are:")
print(obta)     
print("---------------------------------")

objectInterectionSummary = pm4py.ocel_objects_interactions_summary(ocel)
print("the relationship between the objects in the OCEL are:")  
print(objectInterectionSummary)
print("---------------------------------")
obj_activ_relations = ocel.relations # get all the relations in the OCEL
print(" the relationship between the objects and events in the OCEL are:")  
print(obj_activ_relations)
print("---------------------------------")
summary = pm4py.ocel_objects_summary(ocel) # get the summary of the objects
print("The objects summary provides a table that reports each object along with the list of related activities, the start/end timestamps of the object's lifecycle, the lifecycle's duration, and related objects in the interaction graph")
print((summary))
print("---------------------------------")



object_type_to_filter = "handle"  # Change this to your desired object type

# Filter OCEL by object types

filtered_ocel = pm4py.filtering.filter_ocel_object_types(ocel, [object_type_to_filter, "frame"])
print("Object type to filter:", filtered_ocel)
print("---------------------------------")



"""filtered_ocel = pm4py.filter_ocel_object_types(ocel, ['handle'], positive=False)
print("Filtered OCEL for object type:", object_type_to_filter)
print(filtered_ocel)"""
print("---------------------------------")
# new ocel without the filtered object type

# filtered ocel




