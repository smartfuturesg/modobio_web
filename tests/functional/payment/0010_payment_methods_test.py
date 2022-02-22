from flask.json import dumps

from odyssey.api.payment.models import PaymentMethods

from .data import payment_methods_data, test_booking

def test_payment_methods_post(test_client):
    
    #test with invalid card #, should raise 400
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['invalid_card']),
        content_type='application/json')

    assert response.status_code == 400

    #test with expired card, should raise 400
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['expired']),
        content_type='application/json')

    assert response.status_code == 400

    #test with valid card details
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data']),
        content_type='application/json')
    
    assert response.status_code == 201
    assert response.json['payment_type'] == 'VISA'
    assert response.json['is_default'] == True

    #test again with valid card details and set new card to default
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_2']),
        content_type='application/json')

    assert response.status_code == 201
    assert response.json['payment_type'] == 'MC'
    assert response.json['is_default'] == True

    # Test adding too many payment methods, should return 405 when attemping to add 6th payment
    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_3']),
        content_type='application/json')

    assert response.status_code == 201

    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_3']),
        content_type='application/json')

    assert response.status_code == 201

    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_3']),
        content_type='application/json')

    assert response.status_code == 201

    response = test_client.post(
        f'/payment/methods/{test_client.client_id}/',
        headers=test_client.client_auth_header,
        data=dumps(payment_methods_data['normal_data_3']),
        content_type='application/json')

    assert response.status_code == 400

def test_payment_methods_get(test_client):

    response = test_client.get(
        f'/payment/methods/{test_client.client_id}/',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 200
    assert len(response.json) == 5
    assert response.json[0]['expiration'] == '04/25'

def test_payment_methods_delete(test_client, test_booking):
    """
        deleting payment methods has some complex cases, see comments below
    """

    #When there are no future bookings involved with the payment method:
    """
        1) an invalid payment_id is provided (returns 204, but nothing is changed in the db)
    """
    #attempt to delete with invalid idx
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=999',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 204

    """
        2) a valid payment_id is provided (returns 204 and the method has its token and expiration
           date deleted)
    """
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=5',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 204

    response = test_client.get(
        f'/payment/methods/{test_client.client_id}/',
        headers = test_client.client_auth_header,
        content_type='application.json')

    assert response.status_code == 200
    assert len(response.json) == 4
    
    deleted = PaymentMethods.query.filter_by(idx=5).one_or_none()
    assert deleted.payment_id == None
    assert deleted.expiration == None

    # When there are future bookings involved with the payment method:
    
    #generate booking and set payment method to one that was added in post test
    test_booking.payment_method_id = 1
    
    """
        1) no replacement_id is provided (returns 400 with a message to include a replacement_id)    
    """
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=1',
        headers = test_client.client_auth_header,
        content_type='application.json')
    
    assert response.status_code == 400
    
    """
        2) an id that belong to another user's payment method or is deleted (missing payment_id/expiration)
           is given as the replacement_id (returns 400 with a message that the replacement_id must 
           belong to a payment method that belongs to the current user/be an active payment method)
    """
    #change payment method with idx 2 to belong to a different user
    other_user_method = PaymentMethods.query.filter_by(idx=2).one_or_none()
    other_user_method.user_id = test_client.staff_id
    
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=1&replacement_id=2',
        headers = test_client.client_auth_header,
        content_type='application.json')
    
    assert response.status_code == 400
    
    #try to use the payment method with idx 5 as the replacement, should fail because this method
    #was deleted in no booking attached test case 2 above
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=1&replacement_id=5',
        headers = test_client.client_auth_header,
        content_type='application.json')
    
    assert response.status_code == 400
    
    """        
        3) an id that belongs to one of the current user's payment methods is given as the replacement_id
           (returns 204 and all bookings associated with the deleted paymethod method have their payment
           method replaced with the payment method identified by payment_id)
    """
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=1&replacement_id=3',
        headers = test_client.client_auth_header,
        content_type='application.json')
    
    assert response.status_code == 204
    assert test_booking.payment_method_id == 3
    
    deleted = PaymentMethods.query.filter_by(idx=1).one_or_none()
    assert deleted.payment_id == None
    assert deleted.expiration == None
    
    """
        4) 0 is given as the replacement_id (returns 204 and all booking associated with the deleted 
            payment method are canceled)
    """
    response = test_client.delete(
        f'/payment/methods/{test_client.client_id}/?idx=3&replacement_id=0',
        headers = test_client.client_auth_header,
        content_type='application.json')
    
    assert response.status_code == 204
    assert test_booking.status == "Canceled"
    
    deleted = PaymentMethods.query.filter_by(idx=3).one_or_none()
    assert deleted.payment_id == None
    assert deleted.expiration == None