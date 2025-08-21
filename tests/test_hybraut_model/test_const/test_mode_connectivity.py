import pytest
from hybraut_models.const import ModeConnectivity  # adjust import


class TestModeConnectivity:
    def test_enum_members_exist(self):
        assert ModeConnectivity.STRONG.name == "STRONG"
        assert ModeConnectivity.WEAK.name == "WEAK"
        assert ModeConnectivity.UNILATERAL.name == "UNILATERAL"
        assert ModeConnectivity.INCOMING.name == "INCOMING"
        assert ModeConnectivity.OUTGOING.name == "OUTGOING"
        assert ModeConnectivity.ISOLATED_OK.name == "ISOLATED_OK"
        assert ModeConnectivity.REACHABLE_FROM_START.name == "REACHABLE_FROM_START"
        assert ModeConnectivity.REACHABLE_TO_GOAL.name == "REACHABLE_TO_GOAL"

    @pytest.mark.parametrize(
        "connectivity, expected",
        [
            (
                ModeConnectivity.STRONG,
                "Every mode can reach every other mode via directed edges.",
            ),
            (
                ModeConnectivity.WEAK,
                "If directions are ignored, every mode is reachable from every other mode.",
            ),
            (
                ModeConnectivity.UNILATERAL,
                "For every pair of modes, at least one can reach the other directly.",
            ),
            (
                ModeConnectivity.INCOMING,
                "All modes have at least one inbound connection.",
            ),
            (
                ModeConnectivity.OUTGOING,
                "All modes have at least one outbound connection.",
            ),
            (
                ModeConnectivity.ISOLATED_OK,
                "Modes can be completely disconnected; no connectivity enforced.",
            ),
            (
                ModeConnectivity.REACHABLE_FROM_START,
                "Every mode must be reachable from a designated start mode.",
            ),
            (
                ModeConnectivity.REACHABLE_TO_GOAL,
                "Every mode must be able to reach a designated goal mode.",
            ),
        ],
    )
    def test_description_valid(self, connectivity, expected):
        assert ModeConnectivity.description(connectivity) == expected

    def test_description_invalid(self):
        class FakeConnectivity:
            pass

        fake = FakeConnectivity()
        assert ModeConnectivity.description(fake) == "Unknown connectivity type."


if __name__ == "__main__":
    pytest.main([__file__])
