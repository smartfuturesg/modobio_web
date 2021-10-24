from flask.json import dumps, loads

from odyssey import db
from odyssey.api.payment.models import PaymentHistory
from odyssey.api.telehealth.models import TelehealthBookingStatus

from .data import generate_test_booking
"""
This payment tests all InstaMed functions in accordance to InstaMed required test cases.

These are:
Sale with approval (sale ending in $.00)
Sale with decline (sale ending in $.05)
Sale with partial approval (sale ending in $.10)
Void on same day
Refund full amount
Refund more than full amount (should fail)
Refund after full amount has been refunded (should fail)
"""
def test_sale(test_client):
    #create a booking to charge
    booking = generate_test_booking(test_client)
    db.session.add(booking)
    db.session.flush()

    #charge booking using test endpoint ($99.00)
    response = test_client.post(
        '/payment/test/charge/',
        headers=test_client.staff_auth_header,
        data=dumps({'booking_id': booking.idx}),
        content_type='application/json')

    #should succeed
    res = loads(response.data)
    assert response.status_code == 200
    assert res['TransactionStatus'] == "C"
    assert booking.charged

    db.session.delete(booking)
    db.session.flush()

    #create new booking to charge
    booking = generate_test_booking(test_client)
    booking.consult_rate = 99.05
    db.session.add(booking)
    db.session.flush()

    #charge booking using test endpoint ($99.05)
    response = test_client.post(
        '/payment/test/charge/',
        headers=test_client.staff_auth_header,
        data=dumps({'booking_id': booking.idx}),
        content_type='application/json')

    #should fail, check that booking is cancelled
    res = loads(response.data)
    assert res['TransactionStatus'] == "D"
    assert booking.status == 'Canceled'
    assert booking.charged

    statuses = TelehealthBookingStatus().query.filter_by(booking_id=booking.idx).all()
    for status in statuses:
        db.session.delete(status)
    db.session.delete(booking)
    db.session.flush()

    #create new booking to charge
    booking = generate_test_booking(test_client)
    booking.consult_rate = 99.10
    db.session.add(booking)
    db.session.flush()

    #charge booking using test endpoint ($99.10)
    response = test_client.post(
        '/payment/test/charge/',
        headers=test_client.staff_auth_header,
        data=dumps({'booking_id': booking.idx}),
        content_type='application/json')

    #should fail, check that booking is canceled and partial payment is voided
    res = loads(response.data)
    assert res['TransactionStatus'] == "C"
    assert res['PartialApprovalAmount'] == 99
    assert res['IsPartiallyApproved'] == True
    assert booking.status == 'Canceled'
    assert booking.charged

    statuses = TelehealthBookingStatus().query.filter_by(booking_id=booking.idx).all()
    for status in statuses:
        db.session.delete(status)
    db.session.delete(booking)
    db.session.flush()

def test_void(test_client):
    #create booking to charge
    booking = generate_test_booking(test_client)
    db.session.add(booking)
    db.session.flush()

    #charge booking using test endpoint ($99.00)
    response = test_client.post(
        '/payment/test/charge/',
        headers=test_client.staff_auth_header,
        data=dumps({'booking_id': booking.idx}),
        content_type='application/json')

    #should succeed
    res = loads(response.data)
    assert response.status_code == 200
    assert res['TransactionStatus'] == "C"
    assert booking.charged

    #void payment using test endpoint
    response = test_client.post(
        '/payment/test/void/',
        headers=test_client.staff_auth_header,
        data=dumps({'booking_id': booking.idx}),
        content_type='application/json')

    #should succeed
    assert response.status_code == 200

    statuses = TelehealthBookingStatus().query.filter_by(booking_id=booking.idx).all()
    for status in statuses:
        db.session.delete(status)
    db.session.delete(booking)
    db.session.commit()

def test_refund(test_client):
    #create booking to charge
    booking1 = generate_test_booking(test_client)
    booking1.consult_rate = 99.00
    db.session.add(booking1)
    db.session.flush()

    #charge booking using test endpoint ($99.00)
    response = test_client.post(
        '/payment/test/charge/',
        headers=test_client.staff_auth_header,
        data=dumps({'booking_id': booking1.idx}),
        content_type='application/json')

    #should succeed
    res = loads(response.data)
    assert response.status_code == 200
    assert res['TransactionStatus'] == "C"
    assert booking1.charged

    #refund payment for full amount
    data1 = {
        'amount': 99.00,
        'transaction_id': PaymentHistory.query.filter_by(booking_id=booking1.idx).one_or_none().transaction_id
    }

    response = test_client.post(
        '/payment/test/refund/',
        headers=test_client.staff_auth_header,
        data=dumps(data1),
        content_type='application/json')

    #should succeed
    assert response.status_code == 200

    #create new booking to charge
    booking2 = generate_test_booking(test_client)
    booking2.consult_rate = 99.00
    db.session.add(booking2)
    db.session.flush()

    #charge booking using test endpoint ($99.00)
    response = test_client.post(
        '/payment/test/charge/',
        headers=test_client.staff_auth_header,
        data=dumps({'booking_id': booking2.idx}),
        content_type='application/json')

    #should succeed
    assert response.status_code == 200

    #refund for more than full amount using test endpoint ($100.00)
    data2 = {
        'amount': 100.00,
        'transaction_id': PaymentHistory.query.filter_by(booking_id=booking2.idx).one_or_none().transaction_id
    }

    response = test_client.post(
        '/payment/test/refund/',
        headers=test_client.staff_auth_header,
        data=dumps(data2),
        content_type='application/json')

    #should fail
    assert response.status_code == 400

    #refund first payment that has already been refunded in full
    response = test_client.post(
        '/payment/test/refund/',
        headers=test_client.staff_auth_header,
        data=dumps(data1),
        content_type='application/json')

    #should fail
    assert response.status_code == 400

    statuses = TelehealthBookingStatus().query.filter_by(booking_id=booking1.idx).all()
    for status in statuses:
        db.session.delete(status)
    statuses = TelehealthBookingStatus().query.filter_by(booking_id=booking2.idx).all()
    for status in statuses:
        db.session.delete(status)
    db.session.delete(booking1)
    db.session.delete(booking2)
    db.session.flush()