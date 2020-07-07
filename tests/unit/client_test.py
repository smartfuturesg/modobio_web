
from odyssey.models.intake import ClientInfo

def test_new_client(test_client, init_database):
    """
    GIVEN a ClientInfo model
    WHEN a new client is created
    THEN check the model attributes and functionality
    """
    new_client = ClientInfo().query.first()
    assert new_client.email == 'test_this_client@gmail.com'
    assert new_client.get_medical_record_hash() == 'TC148FAC4'
    assert new_client.clientid == 1

    assert new_client.to_dict()

def test_client_search(test_client, init_database):
    """
    GIVEN a ClientInfo model
    WHEN the client database is searched
    THEN make sure the search seatures work as expected
    """
    page = 1
    per_page = 5
    data, _ = ClientInfo.all_clients_dict(ClientInfo.query.order_by(ClientInfo.lastname.asc()),
                                            page=page,per_page=per_page)

    assert len(data['items']) == 1
