import pytest

from odyssey.integrations.wheel import Wheel

@pytest.mark.skip("needs wheel credentials")
def test_clinician_roster_request(test_client):
    """
    Bring up the clinician roster from the sandbox environment
    """

    wheel = Wheel()

    full_roster = wheel.physician_roster()

    assert len(full_roster) == 4
