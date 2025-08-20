import pytest
from hybraut_models.const import UrgencyEnums

def test_eager_description():
    expected = "Transition must occur immediately when enabled — time cannot pass."
    assert UrgencyEnums.urgency_descriptions(UrgencyEnums.EAGER) == expected

def test_lazy_description():
    expected = "Transition may occur at any time after it's enabled — time can pass."
    assert UrgencyEnums.urgency_descriptions(UrgencyEnums.LAZY) == expected

def test_delayed_description():
    expected = "Transition can occur only after a specific delay or guard condition."
    assert UrgencyEnums.urgency_descriptions(UrgencyEnums.DELAYED) == expected

def test_invalid_description():
    class FakeUrgency:
        pass

    expected = "Invalid Urgency Type"
    assert UrgencyEnums.urgency_descriptions(FakeUrgency()) == expected


if __name__ == '__main__':
    pytest.main([__file__])