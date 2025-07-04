import yaml
from typing import Tuple, List, Dict
from collections import defaultdict

class FAMDValidator:
    def __init__(self, famd: yaml) -> None:
        """Initialize validator with FAMD content."""
        self.famd = famd
        self.errors = []
        self.warnings = []

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """Run complete validation and return results."""
        try:
            self.errors = []
            self.warnings = []
            
            # Core validation checks
            self._validate_structure()
            self._validate_modes()
            self._validate_transitions()
            self._validate_guards()
            self._validate_resets()
            self._validate_invariants()
            self._validate_dynamics()
            self._validate_states()
            self._validate_references()
            
            is_valid = len(self.errors) == 0
            return is_valid, self.errors, self.warnings
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {str(e)}")
            return False, self.errors, self.warnings

    def _validate_structure(self):
        """Validate basic FAMD structure."""
        required_sections = ['states', 'modes', 'transitions', 'guards', 
                        'resets', 'invariants', 'dynamics', 'initial_mode']
        
        for section in required_sections:
            if section not in self.famd:
                self.errors.append(f"Missing required section: {section}")

    def _validate_modes(self):
        """Validate mode definitions."""
        if 'modes' not in self.famd:
            return
        
        modes = self.famd['modes']
        mode_names = set()
        
        for mode_index, mode_def in modes.items():
            # Check required fields
            required_fields = ['name', 'description', 'dynamics', 'invariants', 'transitions']
            for field in required_fields:
                if field not in mode_def:
                    self.errors.append(f"Mode with index '{mode_index}' missing required field: {field}")
            
            # Check for duplicate names
            if 'name' in mode_def:
                name = mode_def['name']
                if name in mode_names:
                    self.errors.append(f"Duplicate mode name '{name}' found in mode with index '{mode_index}'")
                mode_names.add(name)
            
            # Validate transition priorities within each mode
            self._validate_mode_transition_priorities(mode_index, mode_def)

    def _validate_mode_transition_priorities(self, mode_name: str, mode_def: Dict):
        """Validate transition priorities within a mode."""
        if 'transitions' not in mode_def:
            return
            
        transitions = mode_def['transitions']
        priorities = []
        
        if not transitions == []:
            for idx, transition in enumerate(transitions):
                transition_key =  next(iter(transition))
                if 'priority' in transition[transition_key]:
                    priority = transition[transition_key]['priority']
                    priorities.append((priority,transition_key))
            
            # Check for duplicate priorities
            priority_counts = defaultdict(list)
            for priority, trans_name in priorities:
                priority_counts[priority].append(trans_name)
            
            for priority, trans_names in priority_counts.items():
                if len(trans_names) > 1:
                    self.errors.append(
                        f"Mode '{mode_name}' has duplicate priority {priority} "
                        f"for transitions: {', '.join(trans_names)}"
                    )

    def _validate_transitions(self):
        """Validate transition definitions."""
        if 'transitions' not in self.famd:
            return
            
        transitions = self.famd['transitions']
        if not transitions == []:
            for trans_name, trans_def in transitions.items():
                # Check required fields
                required_fields = ['origin_modes', 'target_mode', 'guard']
                for field in required_fields:
                    if field not in trans_def:
                        self.errors.append(f"Transition '{trans_name}' missing required field: {field}")
                
                # Validate origin_modes and origin_priorities alignment
                if 'origin_modes' in trans_def and 'origin_priorities' in trans_def:
                    modes = trans_def['origin_modes']
                    priorities = trans_def['origin_priorities']
                    
                    if len(modes) != len(priorities):
                        self.errors.append(
                            f"Transition '{trans_name}': origin_modes ({len(modes)}) and "
                            f"origin_priorities ({len(priorities)}) must have same length"
                        )
                
                # Check that target_mode exists
                if 'target_mode' in trans_def:
                    target = trans_def['target_mode']
                    if 'modes' in self.famd and target not in self.famd['modes']:
                        self.errors.append(f"Transition '{trans_name}' targets non-existent mode: {target}")
                
                # Check that origin_modes exist
                if 'origin_modes' in trans_def:
                    for origin_mode in trans_def['origin_modes']:
                        if 'modes' in self.famd and origin_mode not in self.famd['modes']:
                            self.errors.append(
                                f"Transition '{trans_name}' references non-existent origin mode: {origin_mode}"
                            )

    def _validate_guards(self):
        """Validate guard definitions."""
        if 'guards' not in self.famd:
            return
            
        guards = self.famd['guards']
        
        for guard_name, guard_def in guards.items():
            # Check required fields
            required_fields = ['module', 'class_name', 'description', 'state_inputs', 'configuration']
            for field in required_fields:
                if field not in guard_def:
                    self.errors.append(f"Guard '{guard_name}' missing required field: {field}")
            
            # Validate state_inputs reference existing states
            if 'state_inputs' in guard_def:
                self._validate_state_references(guard_name, guard_def['state_inputs'], 'guard')

    def _validate_resets(self):
        """Validate reset definitions."""
        if 'resets' not in self.famd:
            return
            
        resets = self.famd['resets']
        
        for reset_name, reset_def in resets.items():
            # Check required fields
            required_fields = ['module', 'class_name', 'description', 'state_inputs', 'reset_targets', 'configuration']
            for field in required_fields:
                if field not in reset_def:
                    self.errors.append(f"Reset '{reset_name}' missing required field: {field}")
            
            # Validate state references
            if 'state_inputs' in reset_def:
                self._validate_state_references(reset_name, reset_def['state_inputs'], 'reset')
            if 'state_outputs' in reset_def:
                self._validate_state_references(reset_name, reset_def['state_outputs'], 'reset')

    def _validate_invariants(self):
        """Validate invariant definitions."""
        if 'invariants' not in self.famd:
            return
            
        invariants = self.famd['invariants']
        
        for inv_name, inv_def in invariants.items():
            # Check required fields
            required_fields = ['module', 'class_name', 'description', 'state_inputs', 'configuration']
            for field in required_fields:
                if field not in inv_def:
                    self.errors.append(f"Invariant '{inv_name}' missing required field: {field}")
            
            # Validate state_inputs if present
            if 'state_inputs' in inv_def:
                self._validate_state_references(inv_name, inv_def['state_inputs'], 'invariant')

    def _validate_dynamics(self):
        """Validate dynamics definitions."""
        if 'dynamics' not in self.famd:
            return

        dynamics = self.famd['dynamics']
        
        for dyn_name, dyn_def in dynamics.items():
            # Required top-level fields
            required_fields = ['module', 'class_name', 'state_inputs', 'dynamic_outputs']
            for field in required_fields:
                if field not in dyn_def:
                    self.errors.append(f"Dynamics '{dyn_name}' missing required field: '{field}'")

            # Validate state_inputs
            if 'state_inputs' in dyn_def:
                self._validate_state_references(dyn_name, dyn_def['state_inputs'], 'dynamic')

            # Validate dynamic_outputs
            if 'dynamic_outputs' in dyn_def:
                dyn_out = dyn_def['dynamic_outputs']
                names = dyn_out.get('dynamic_parameter_names', [])
                types = dyn_out.get('dynamic_parameter_value_types', [])
                metrics = dyn_out.get('dynamic_parameter_metrics', [])

                if not (len(names) == len(types) == len(metrics)):
                    self.errors.append(
                        f"Dynamics '{dyn_name}' has mismatched lengths in dynamic_outputs: "
                        f"{len(names)} names, {len(types)} types, {len(metrics)} metrics"
                    )

    def _validate_states(self):
        """Validate state definitions."""
        if 'states' not in self.famd:
            return
            
        states = self.famd['states']
        
        for state_name, state_def in states.items():
            # Check required fields
            required_fields = ['topic', 'type']
            for field in required_fields:
                if field not in state_def:
                    self.errors.append(f"State '{state_name}' missing required field: {field}")
            
            # Validate type structure
            if 'type' in state_def:
                type_def = state_def['type']
                if not isinstance(type_def, dict) or 'pkg' not in type_def or 'msg' not in type_def:
                    self.errors.append(f"State '{state_name}' type must have 'pkg' and 'msg' fields")

    def _validate_state_references(self, component_name: str, state_list: List[str], component_type: str):
        """Validate that referenced states exist."""
        if 'states' not in self.famd:
            return
            
        available_states = set(self.famd['states'].keys())
        
        for state_ref in state_list:
            if state_ref not in available_states:
                self.errors.append(
                    f"{component_type.title()} '{component_name}' references non-existent state: {state_ref}"
                )

    def _validate_references(self):
        """Validate cross-references between components."""
        # Check that modes reference existing dynamics and invariants
        if 'modes' in self.famd:
            for mode_name, mode_def in self.famd['modes'].items():
                # Check dynamics reference
                if 'dynamics' in mode_def:
                    dyn_ref = mode_def['dynamics']
                    if 'dynamics' in self.famd and 'dynamic_classes' in self.famd['dynamics']:
                        if dyn_ref not in self.famd['dynamics']['dynamic_classes']:
                            self.errors.append(
                                f"Mode '{mode_name}' references non-existent dynamics: {dyn_ref}"
                            )
                
                # Check invariants reference
                if 'invariants' in mode_def:
                    inv_ref = mode_def['invariants']
                    for invariant in mode_def['invariants']:
                        if invariant not in self.famd['invariants']:
                            self.errors.append(
                                f"Mode '{mode_name}' references non-existent invariant: {inv_ref}"
                            )
                
                # Check transition references
                if 'transitions' in mode_def:
                    if not mode_def['transitions'] == []:
                        for transition in mode_def['transitions']:
                            if not any(list(transition.keys())[0] in t for t in mode_def['transitions']):
                                self.errors.append(
                                    f"Mode '{mode_name}' references non-existent transition: {trans_name}"
                                )
        
        # Check that transitions reference existing guards and resets
        if 'transitions' in self.famd:
            for trans_name, trans_def in self.famd['transitions'].items():
                # Check guard reference
                if 'guard' in trans_def:
                    guard_ref = trans_def['guard']
                    if 'guards' in self.famd and guard_ref not in self.famd['guards']:
                        self.errors.append(
                            f"Transition '{trans_name}' references non-existent guard: {guard_ref}"
                        )
                
                # Check reset reference
                if 'reset' in trans_def and trans_def['reset'] is not None:
                    reset_ref = trans_def['reset']
                    if 'resets' in self.famd and reset_ref not in self.famd['resets']:
                        self.errors.append(
                            f"Transition '{trans_name}' references non-existent reset: {reset_ref}"
                        )
        
        # Check initial_mode reference
        if 'initial_mode' in self.famd:
            init_mode = self.famd['initial_mode']
            if 'modes' in self.famd and init_mode not in self.famd['modes']:
                self.errors.append(f"initial_mode references non-existent mode: {init_mode}")
        
        # Check goal_modes references
        if 'goal_modes' in self.famd:
            for goal_mode in self.famd['goal_modes']:
                if 'modes' in self.famd and goal_mode not in self.famd['modes']:
                    self.errors.append(f"goal_modes references non-existent mode: {goal_mode}")

    def print_validation_report(self):
        """Print a formatted validation report."""
        print("=" * 60)
        print("COLAV Hybrid Automaton FAMD Structure Validation Report")
        print("=" * 60)
        
        if not self.errors and not self.warnings:
            print("✅ VALIDATION PASSED - No issues found!")
            return
        
        if self.errors:
            print(f"\n❌ ERRORS FOUND ({len(self.errors)}):")
            print("-" * 40)
            for i, error in enumerate(self.errors, 1):
                print(f"{i:2d}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            print("-" * 40)
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i:2d}. {warning}")
        
        print("\n" + "=" * 60)
        if self.errors:
            print("❌ STRUCTURE VALIDATION FAILED - Please fix the errors above")
        else:
            print("✅ STRUCTURE VALIDATION PASSED - Only warnings found")