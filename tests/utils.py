""" Utility funcitons for testing. """

import base64

def login(test_client, user, password='password') -> dict:
    """ Login user, return header with token.
    
    Parameters
    ----------
    test_client : :class:`Flask.app.test_client`
        The :class:`Flask.app.test_client` object that runs the tests.

    user : :class:`~odyssey.api.user.models.User`
        User model instance, can be staff or client.

    password : str
        Optional password for user, defaults to "password".

    Returns
    -------
    dict
        Authorization header with the access token for user.
    """
    creds = base64.b64encode(f'{user.email}:{password}'.encode('utf-8')).decode('utf-8')
    header = {'Authorization': f'Basic {creds}'}

    url = 'client'
    if user.is_staff:
        url = 'staff'
    elif user.is_provider:
        url = 'provider'

    response = test_client.post(
        f'/{url}/token/',
        headers=header,
        content_type='application/json')

    token = response.json.get('token')
    return {'Authorization': f'Bearer {token}'}
