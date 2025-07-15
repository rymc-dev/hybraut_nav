# import os
# from colav_hybrid_automaton.automaton._internal.factory.hybrid_automaton_factory import hybrid_automaton_registry
# from colav_hybrid_automaton.automaton._internal.utils import load_yml
# from ament_index_python.packages import get_package_share_directory

# package_name = 'colav_hybrid_automaton'
# pkg_share_dir = get_package_share_directory(package_name)

# default_config_path = os.path.join(pkg_share_dir, 'automaton', 'config', 'colav-famd.yml')

# def test_hybrid_automaton_registry_comprehensive():
#     config = load_yml(default_config_path)

#     result = hybrid_automaton_registry(config)

#     print (f"Result: {result}")

#     assert isinstance(result, dict), "Result should be a dictionary"
#     assert 'states' in result, "Result should contain 'states' key"
#     assert 'transitions' in result, "Result should contain 'transitions' key"
#     assert 'guards' in result, "Result should contain 'guards' key"
#     assert 'resets' in result, "Result should contain 'resets' key"
#     assert 'dynamics' in result, "Result should contain 'dynamics' key"
#     assert 'invariants' in result, "Result should contain 'invariants' key"
#     assert 'modes' in result, "Result should contain 'modes' key"
#     assert 'goal_modes' in result, "Result should contain 'goal_modes' key"
#     assert 'initial_mode' in result, "Result should contain 'initial_mode' key"
#     assert 'parameters' in result, "Result should contain 'parameters' key"

#     # validate states
#     assert 'agent_state' in result['states'], "States should contain 'agent_state'"
#     assert 'topic' in result['states']['agent_state'], "States should contain 'agent_state'"
#     assert 'type' in result['states']['agent_state'], "States should contain 'agent_state'"
#     assert 'params' in result['states']['agent_state'], "States should contain 'agent_state'"
#     # assert '/state/agent' ==  result['states']['agent_state']['topic'], "States should contain 'agent_state'"

#     assert 'obstacles_state' in result['states'], "States should contain 'obstacles_state'"
#     assert 'topic' in result['states']['obstacles_state'], "States should contain 'obstacles_state'"
#     assert 'type' in result['states']['obstacles_state'], "States should contain 'obstacles_state'"
#     assert 'params' in result['states']['obstacles_state'], "States should contain 'obstacles_state'"

#     assert 'unsafe_set_state' in result['states'], "States should contain 'unsafe_set_state'"
#     assert 'topic' in result['states']['unsafe_set_state'], "States should contain 'unsafe_set_state'"
#     assert 'type' in result['states']['unsafe_set_state'], "States should contain 'unsafe_set_state'"
#     assert 'params' in result['states']['unsafe_set_state'], "States should contain 'unsafe_set_state'"

#     assert 'waypoints_state' in result['states'], "States should contain 'waypoints_state'"
#     assert 'topic' in result['states']['waypoints_state'], "States should contain 'waypoints_state'"
#     assert 'type' in result['states']['waypoints_state'], "States should contain 'waypoints_state'"
    