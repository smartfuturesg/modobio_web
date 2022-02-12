import pytest

from odyssey import db
from odyssey.api.user.models import User

from tests.utils import login

@pytest.fixture(scope='module')
def client_services(test_client):
    """ Log in as a staff member user **with** client_services role. """
    cs = db.session.query(User).filter_by(email='client_services@modobio.com').one_or_none()
    cs.auth_header = login(test_client, cs, password='123')

    return cs

@pytest.fixture(scope='module')
def not_client_services(test_client):
    """ Log in as a staff member user **without** client_services role.
    
    Cannot use ``test_client.staff`` for this purpose, since staff has all roles,
    including the client_services role.
    """
    sa = db.session.query(User).filter_by(email='admin@modobio.com').one_or_none()
    sa.auth_header = login(test_client, sa, password='123')

    return sa
