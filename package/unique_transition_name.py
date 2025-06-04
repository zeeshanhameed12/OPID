def get_transition_name(transition):
    """
    Get a unique name for a transition, ensuring it is not already used.
    If the transition is silent, assign a unique name based on its ID.
    """

    global silent_map, used_transition_names, transitions_json
    if transition.label:
        return str(transition.label)
    else:
        if transition in silent_map:
            return silent_map[transition]
        # If not seen before, create a new entry for this silent transition
        base_name = transition.name if transition.name is not None else "tau"
        silent_name = base_name
        # Ensure the chosen name is unique among all transition names used so far
        counter = 0
        while silent_name in used_transition_names:
                counter += 1
                silent_name = f"{base_name}_{counter}"
        silent_map[transition] = silent_name
        used_transition_names.add(silent_name)
        transitions_json.append({
                "name": silent_name,
                "label": silent_name,  # for silent transitions, we use the name as the label placeholder
                "silent": True,
                "properties": {}
            })
        return silent_name