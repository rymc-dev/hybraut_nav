# from colav_proto.constants import AutomatonStatusEnum as ProtoAutomatonStatusEnum
# from automaton.constants import HybridAutomatonStatusEnum as PythonHybridAutomatonStatusEnum
# from hybrid_automaton_interfaces.msg import HybridAutomatonStatus as ROSHybridAutomatonStatus
# import pytest


# @pytest.mark.parametrize(
#         "python_status_enum, ros_status_enum, proto_status_enum",
#         [
#             (
#                 PythonHybridAutomatonStatusEnum.INITIALIZING,
#                 ROSHybridAutomatonStatus.INITIALIZING,
#                 ProtoAutomatonStatusEnum.INITIALIZING
#             ),
#         ]
# )
# def test_automaton_state_enum_comprehensive(python_status_enum: PythonHybridAutomatonStatusEnum, ros_status_enum: ROSHybridAutomatonStatus, proto_status_enum: ProtoAutomatonStatusEnum):
#     assert python_status_enum.value == ros_status_enum
#     assert python_status_enum.value == proto_status_enum.value
