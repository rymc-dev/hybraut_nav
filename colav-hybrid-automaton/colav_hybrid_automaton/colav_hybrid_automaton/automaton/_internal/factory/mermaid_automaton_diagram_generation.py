from colav_hybrid_automaton.automaton._internal.utils import load_yml
from ament_index_python.packages import get_package_share_directory
import os

package_name = 'colav_hybrid_automaton'
pkg_share_directory = get_package_share_directory(package_name)

def generate_mermaid_automaton_chart(automaton_name, automaton_data):
    mermaid = ["stateDiagram-v2"]
    mermaid.append(f"# {automaton_name} FAMD State Diagram")
    init_mode = automaton_data.get('initial_mode', '')
    goal_modes = automaton_data.get('goal_modes', {})
    mode_keys = list(automaton_data.get('modes', {}).keys())
    mode_idx = [automaton_data['modes'][key]['index'] for key in mode_keys]

    mermaid.append("    %% Initial Mode")
    mermaid.append("    [*] --> " + init_mode + ": initial_mode") 
    
    mermaid.append("    %% Modes")
    for idx, mode_key in enumerate(mode_keys):
        mermaid.append(f"    {mode_key}: {mode_idx[idx]}.{mode_key}")
        mermaid.append("")
        mermaid.append(f"    note left of {mode_key}")
        mermaid.append(f"      invariant: {automaton_data.get('modes')[mode_key]['invariants']}")
        mermaid.append(f"      dynamics: {automaton_data.get('modes')[mode_key]['dynamics']}")
        mermaid.append(f"    end note")
    
    # transitions
    transitions = automaton_data.get('transitions', {})
    mermaid.append("    %% Transitions")
    for transition_key, transition in transitions.items():
        for idx, origin_mode in enumerate(transition.get('origin_modes', [])):
            origin_mode = origin_mode
            target_mode = f"{transition.get('target_mode', '')}"
            priority = transition.get('origin_priorities', [])[idx] if 'origin_priorities' in transition else 0
            # guard = transition.get('guard', '')
            # reset = transition.get('reset', '')
            
            # If target_mode is not specified, skip this transition
            if not target_mode:
                continue
            
            # Format the transition string
            transition_str = f"    {origin_mode} --> {target_mode}: {priority}.{transition_key}"
            mermaid.append(transition_str)

    mermaid.append("    # Goal Modes")
    for goal_mode in goal_modes:
        mermaid.append(f"    {goal_mode} --> [*]: goal_reached")

    mermaid.append("    # Transitions")

    

    


     # Start state

    
    # transitions = 
    

    # for mode in modes:
    #     mermaid.append(f"    state {mode} {{")
    #     mode_data = automaton_data.get('modes', {}).get(mode, {})
    #     transitions = mode_data.get('transitions', {})

    #     # If transitions is a dict, get keys; otherwise return an empty list
    #     transition_keys = list(transitions.keys()) if isinstance(transitions, dict) else []
    #     for transition_key in transition_keys:
    #         transition = automaton_data['transitions'][transition_key]
    #         target_mode = transition.get('target_mode')
    #         guard = transition.get('guard', '')
    #         reset = transition.get('reset', '')
    #         mermaid.append(f"        [{guard}] --> {target_mode} : {reset}")
        
        
    # mermaid.append("    }")

    return mermaid


if __name__ == '__main__':
    automaton_data = load_yml(os.path.join(pkg_share_directory, 'automaton', 'config', 'colav-famd.yml'))
    mermaid = generate_mermaid_automaton_chart("colav famd", automaton_data)
    print (mermaid)
    with open("famd_state_diagram.mmd", "w") as file:
        for line in mermaid:
            file.write(line + "\n")