# # !/usr/bin/env python3

# """
# test suite for the reset factory
# """

# from hybraut_factory.amdl.core.reset_factory import ResetFactory
# from hybraut_models.core import ResetRegistry, ResetWrapper
# import pytest
# from typing import Dict


# @pytest.fixture
# def sample_reset_name_and_cfg():
#     """returns a sample amdl with its configuration"""
#     reset_dict = (
#         "battery_level_reset",
#         {
#             "module": "hybraut_common_behaviours.resets.battery_level_reset",
#             "class_name": "BatteryLevelReset",
#             "configuration": {
#                 "low_battery_threshold": 30.0,
#                 "critical_battery_threshold": 5.0,
#                 "power_save_factor": 20.0,
#             },
#         },
#     )
#     return reset_dict


# @pytest.fixture
# def sample_reset_amdl():
#     """returns a sample amdl file for a reset"""
#     return {
#         "battery_level_reset": {
#             "module": "hybraut_common_behaviours.resets.battery_level_reset",
#             "class_name": "BatteryLevelReset",
#             "configuration": {
#                 "low_battery_threshold": 30.0,
#                 "critical_battery_threshold": 5.0,
#                 "power_save_factor": 20.0,
#             },
#         }
#     }


# def test_load_reset_wrapper_from_amdl(sample_reset_name_and_cfg):
#     reset_name, reset_cfg = sample_reset_name_and_cfg

#     reset_wrapper: ResetWrapper = ResetFactory.load_reset_wrapper_from_amdl(
#         reset_name, reset_cfg
#     )

#     assert isinstance(reset_wrapper, ResetWrapper)
#     assert reset_wrapper.get_name() == reset_name


# def test_register_reset_wrappers_from_amdl(sample_reset_amdl):
#     amdl = sample_reset_amdl

#     reset_registry: Dict[str, ResetWrapper] = (
#         ResetFactory.register_reset_wrappers_from_amdl(amdl)
#     )

#     assert reset_registry is not None

#     for reset_name, reset_wrapper in reset_registry.items():
#         print(reset_name)

#     assert True


# def test_load_reset_registry_from_amdl(sample_reset_amdl):
#     amdl = sample_reset_amdl

#     reset_registry: Dict[str, ResetWrapper] = (
#         ResetFactory.load_reset_registry_from_amdl(amdl)
#     )

#     assert isinstance(reset_registry, ResetRegistry)


# if __name__ == "__main__":
#     pytest.main([__file__])
