import os
from colav_hybrid_automaton.automaton._internal.utils import load_yml
from ament_index_python.packages import get_package_share_directory
import subprocess

state_diagram_save_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'assets', 'diagrams')

def generate_mermaid_automaton_chart(automaton_name, automaton_data):
    """
    Generate a Mermaid state diagram from automaton data.
    
    Args:
        automaton_name (str): Name of the automaton
        automaton_data (dict): Automaton configuration data
        
    Returns:
        list: Lines of Mermaid diagram code
    """
    mermaid = []
    
    # Header
    mermaid.append("stateDiagram-v2")
    mermaid.append(f"    %% {automaton_name} State Diagram")
    mermaid.append("")
    
    # Extract data
    init_mode = automaton_data.get('initial_mode', '')
    goal_modes = automaton_data.get('goal_modes', [])
    modes = automaton_data.get('modes', {})
    transitions = automaton_data.get('transitions', {})
    
    # Initial state
    if init_mode:
        mermaid.append("    %% Initial Mode")
        mermaid.append(f"    [*] --> {init_mode}")
        mermaid.append("")
    
    # Modes with notes
    if modes:
        mermaid.append("    %% Modes")
        for mode_key, mode_data in modes.items():
            mode_index = mode_data.get('index', '')
            invariants = mode_data.get('invariants', '')
            dynamics = mode_data.get('dynamics', '')
            
            # State definition
            mermaid.append(f"    {mode_key} : {mode_index}.{mode_key}")
            
            # Add note if there's invariant or dynamics info
            if invariants or dynamics:
                mermaid.append(f"    note left of {mode_key}")
                mermaid.append(f"        =====================")
                mermaid.append(f"        <b>{mode_index}.{mode_key}</b>") 
                mermaid.append(f"        =====================")
                mermaid.append(f"        <b>description</b>: {mode_data.get('description', '')}")
                if invariants:
                    mermaid.append(f"        <b>invariant</b>: {invariants}")
                if dynamics:
                    mermaid.append(f"        <b>dynamics</b>: {dynamics}")
                mermaid.append("    end note")
            
            mermaid.append("")
    
    # Transitions
    if transitions:
        mermaid.append("    %% Transitions")
        for transition_key, transition_data in transitions.items():
            origin_modes = transition_data.get('origin_modes', [])
            origin_priorities = transition_data.get('origin_priorities', [])
            target_mode = transition_data.get('target_mode', '')
            guard = transition_data.get('guard', '')
            reset = transition_data.get('reset', 'null')

            # Skip if no target mode
            if not target_mode:
                continue
            
            for idx, origin_mode in enumerate(origin_modes):
                # Get priority for this origin mode (default to 0 if not available)
                priority = origin_priorities[idx] if idx < len(origin_priorities) else 0
                
                # Create transition label
                transition_label = f"<b>{priority}.{transition_key}</b>  [<b>guard</b> = {guard}, <b>reset</b> = {reset}]"
                
                # Append transition line to Mermaid diagram
                mermaid.append(f"    {origin_mode} --> {target_mode} : {transition_label}")
    
    # Goal modes
    if goal_modes:
        mermaid.append("    %% Goal Modes")
        for goal_mode in goal_modes:
            mermaid.append(f"    {goal_mode} --> [*]")
        mermaid.append("")
    
    return mermaid


def save_mermaid_diagram(mermaid_lines, filename="famd_state_diagram.mmd"):
    """
    Save Mermaid diagram lines to a file.
    
    Args:
        mermaid_lines (list): Lines of Mermaid diagram code
        filename (str): Output filename (can be full path or just filename)
    """
    try:
        # Get absolute path for clarity
        abs_path = os.path.join(state_diagram_save_path, filename)
        
        with open(abs_path, "w", encoding="utf-8") as file:
            file.write("\n".join(mermaid_lines))
        
        print(f"Mermaid diagram saved to: {abs_path}")
        print(f"Current working directory: {os.getcwd()}")
        
    except IOError as e:
        print(f"Error saving file: {e}")

def mermaid_to_png(mmd_file, output_file):
    """Convert Mermaid file to PNG using mermaid-cli"""
    try:
        # Requires @mermaid-js/mermaid-cli to be installed globally
        # npm install -g @mermaid-js/mermaid-cli
        result = subprocess.run([
            'mmdc', 
            '-i', mmd_file, 
            '-o', output_file,
            '-t', 'neutral',  # theme
            '-b', 'white'     # background color
        ], capture_output=True, text=True, check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False


        
def main():
    """Main execution function."""
    try:
        # Get package directory and load automaton data
        package_name = 'colav_hybrid_automaton'
        pkg_share_directory = get_package_share_directory(package_name)
        config_path = os.path.join(pkg_share_directory, 'automaton', 'config', 'colav-famd.yml')
        
        # Load automaton data
        automaton_data = load_yml(config_path)
        
        # Generate Mermaid diagram
        mermaid_lines = generate_mermaid_automaton_chart("COLAV FAMD", automaton_data)
        
        # Print to console
        print("Generated Mermaid Diagram:")
        print("-" * 40)
        for line in mermaid_lines:
            print(line)
        print("-" * 40)
        
        # Save to file (you can specify a full path here)
        output_filename = f"{automaton_data['automaton_name']}.famd.mmd"  # or "/path/to/your/desired/location/famd_state_diagram.mmd"
        save_mermaid_diagram(mermaid_lines, output_filename)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()