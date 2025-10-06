# # !/usr/bin/env python3
# """
# a test suite for testing invariants factory
# """

# from hybraut_factory.amdl.core.invariant_factory import InvariantFactory
# from hybraut_models.core.invariants import InvariantWrapper, InvariantRegistry
# import pytest
# from typing import List


# @pytest.fixture
# def sample_invariant_name_and_cfg():
#     return (
#         "timeout_invariant",
#         {
#             "module": "hybraut_common_behaviours.invariants",
#             "class_name": "TimeoutInvariant",
#             "configuration": {"timeout_sec": 10.0, "entry_time": 1.0},
#         },
#     )


# @pytest.fixture
# def sample_invariants_amdl():
#     return {
#         "timeout_invariant": {
#             "module": "hybraut_common_behaviours.invariants",
#             "class_name": "TimeoutInvariant",
#             "configuration": {"timeout_sec": 10.0, "entry_time": 1.0},
#         },
#         "trivial_invariant": {
#             "module": "hybraut_common_behaviours.invariants",
#             "class_name": "TrivialInvariant",
#         },
#     }


# def test_load_invariant_from_amdl(sample_invariant_name_and_cfg):
#     """
#     test to ensure that the invariant factory works as expected
#     """
#     invariant_name, invariant_cfg = sample_invariant_name_and_cfg
#     invariant: InvariantWrapper = InvariantFactory.load_invariant_from_amdl(
#         invariant_name, invariant_cfg
#     )

#     assert invariant.get_invariant_name() == invariant_name
#     assert invariant.get_initialization_configuration() == invariant_cfg.get(
#         "configuration", {}
#     )


# def test_register_invariants_from_amdl(sample_invariants_amdl):
#     """Test to ensure that the registration of invariants works as expected"""
#     invariants_amdl = sample_invariants_amdl
#     registered_invariants: List[InvariantWrapper] = (
#         InvariantFactory.register_invariants_from_amdl(invariants_amdl)
#     )

#     assert len(registered_invariants) == len(invariants_amdl)
#     for invariant_name, invariant_wrapper in registered_invariants.items():
#         assert invariant_name in invariants_amdl
#         assert isinstance(invariant_wrapper, InvariantWrapper)
#         assert invariant_wrapper.get_invariant_name() in invariants_amdl
#         assert invariant_wrapper.get_initialization_configuration() == invariants_amdl[
#             invariant_wrapper.get_invariant_name()
#         ].get("configuration", {})
#     assert True


# def test_load_invariant_registry_from_amdl(
#     sample_invariants_amdl,
# ):
#     """
#     test loading the invariant registry from amdl
#     """
#     amdl = sample_invariants_amdl
#     registry: InvariantRegistry = InvariantFactory.load_invariant_registry_from_amdl(
#         amdl
#     )

#     assert isinstance(registry, InvariantRegistry)
#     assert registry.get_num_invariants() == 2
#     assert registry.get_invariant_names() == list(sample_invariants_amdl.keys())
#     for invariant_name in registry.get_invariant_names():
#         invariant = registry.get_invariant_by_name(invariant_name)
#         assert invariant is not None and isinstance(invariant, InvariantWrapper)
#         assert invariant.get_invariant_name() == invariant_name
#         assert invariant.get_initialization_configuration() == amdl[invariant_name].get(
#             "configuration", {}
#         )


# if __name__ == "__main__":
#     pytest.main([__file__])
