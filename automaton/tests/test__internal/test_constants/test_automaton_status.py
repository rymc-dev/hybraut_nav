from colav_proto.constants import AutomatonStatusEnum as ProtoAutomatonStatusEnum
from automaton._internal.constants import HybridAutomatonStatusEnum as PythonHybridAutomatonStatusEnum
from hybrid_automaton_interfaces.msg import HybridAutomatonStatus as ROSHybridAutomatonStatus
import pytest


@pytest.mark.parametrize(
        "python_status_enum, ros_status_enum, proto_status_enum",
        [
            (
                PythonHybridAutomatonStatusEnum.INITIALIZING,
                ROSHybridAutomatonStatus.STATUS_INITIALIZING,
                ProtoAutomatonStatusEnum.INITIALIZING
            ),
            (
                PythonHybridAutomatonStatusEnum.ACTIVE_MODE,
                ROSHybridAutomatonStatus.STATUS_ACTIVE_MODE,
                ProtoAutomatonStatusEnum.ACTIVE_MODE
            ),
            (
                PythonHybridAutomatonStatusEnum.TRANSITIONING,
                ROSHybridAutomatonStatus.STATUS_TRANSITIONING,
                ProtoAutomatonStatusEnum.TRANSITIONING
            ),
            (
                PythonHybridAutomatonStatusEnum.COMPLETED,
                ROSHybridAutomatonStatus.STATUS_COMPLETED,
                ProtoAutomatonStatusEnum.COMPLETED
            ),
            (
                PythonHybridAutomatonStatusEnum.DEACTIVATING,
                ROSHybridAutomatonStatus.STATUS_DEACTIVATING,
                ProtoAutomatonStatusEnum.DEACTIVATING
            ),
            (
                PythonHybridAutomatonStatusEnum.ERROR,
                ROSHybridAutomatonStatus.STATUS_ERROR,
                ProtoAutomatonStatusEnum.ERROR
            ),

        ]
)
def test_automaton_state_enum_comprehensive(python_status_enum: PythonHybridAutomatonStatusEnum, ros_status_enum: ROSHybridAutomatonStatus, proto_status_enum: ProtoAutomatonStatusEnum):
    assert python_status_enum.value == ros_status_enum
    assert python_status_enum.value == proto_status_enum.value
