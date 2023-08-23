import pytest
from flask.json import dumps, loads

from odyssey import db
from odyssey.api.notifications.models import Notifications
from odyssey.api.payment.models import PaymentHistory
from odyssey.api.telehealth.models import TelehealthBookingStatus

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


@pytest.mark.skip("payment disabled until instamed is replaced")
def test_sale_success(test_client, test_booking):
    # charge booking using test endpoint ($99.00)
    response = test_client.post(
        "/payment/test/telehealth-charge/",
        headers=test_client.staff_auth_header,
        data=dumps({"booking_id": test_booking.idx}),
        content_type="application/json",
    )

    # should succeed
    res = loads(response.data)
    assert response.status_code == 200
    assert res["TransactionStatus"] == "C"
    assert test_booking.charged


@pytest.mark.skip("payment disabled until instamed is replaced")
def test_sale_deny(test_client, test_booking):
    # charge booking using test endpoint ($99.05)
    test_booking.consult_rate = 99.05
    response = test_client.post(
        "/payment/test/telehealth-charge/",
        headers=test_client.staff_auth_header,
        data=dumps({"booking_id": test_booking.idx}),
        content_type="application/json",
    )

    # bring up client's notifications
    notifications = (
        Notifications.query.filter_by(
            user_id=test_booking.client_user_id, notification_type_id=5
        )
        .order_by(Notifications.notification_id.desc())
        .all()
    )

    # should fail, check that booking is cancelled
    res = loads(response.data)
    assert len(notifications) == 1  # payment failed notification
    assert res["TransactionStatus"] == "D"
    assert test_booking.status == "Canceled"
    assert not test_booking.charged

    statuses = (
        TelehealthBookingStatus().query.filter_by(booking_id=test_booking.idx).all()
    )
    for status in statuses:
        db.session.delete(status)
    db.session.commit()


@pytest.mark.skip("payment disabled until instamed is replaced")
def test_sale_partial(test_client, test_booking):
    # charge booking using test endpoint ($99.10)
    test_booking.consult_rate = 99.10
    response = test_client.post(
        "/payment/test/telehealth-charge/",
        headers=test_client.staff_auth_header,
        data=dumps({"booking_id": test_booking.idx}),
        content_type="application/json",
    )

    # bring up client's notifications
    notifications = (
        Notifications.query.filter_by(
            user_id=test_booking.client_user_id, notification_type_id=5
        )
        .order_by(Notifications.notification_id.desc())
        .all()
    )

    assert len(notifications) == 2  # includes notification from test_sale_deny
    # should fail, check that booking is canceled and partial payment is voided
    assert response.status_code == 400
    assert test_booking.status == "Canceled"
    assert not test_booking.charged

    statuses = (
        TelehealthBookingStatus().query.filter_by(booking_id=test_booking.idx).all()
    )
    for status in statuses:
        db.session.delete(status)
    db.session.commit()


@pytest.mark.skip("payment disabled until instamed is replaced")
def test_void(test_client, test_booking):
    # charge booking using test endpoint ($99.00)
    response = test_client.post(
        "/payment/test/telehealth-charge/",
        headers=test_client.staff_auth_header,
        data=dumps({"booking_id": test_booking.idx}),
        content_type="application/json",
    )

    # should succeed
    res = loads(response.data)
    assert response.status_code == 200
    assert res["TransactionStatus"] == "C"
    assert test_booking.charged

    # void payment using test endpoint
    response = test_client.post(
        "/payment/test/void/",
        headers=test_client.staff_auth_header,
        data=dumps({"booking_id": test_booking.idx}),
        content_type="application/json",
    )

    # should succeed
    assert response.status_code == 200

    statuses = (
        TelehealthBookingStatus().query.filter_by(booking_id=test_booking.idx).all()
    )
    for status in statuses:
        db.session.delete(status)
    db.session.commit()


@pytest.mark.skip("payment disabled until instamed is replaced")
def test_refund(test_client, test_booking):
    # charge booking using test endpoint ($99.00)
    response = test_client.post(
        "/payment/test/telehealth-charge/",
        headers=test_client.staff_auth_header,
        data=dumps({"booking_id": test_booking.idx}),
        content_type="application/json",
    )

    # should succeed
    res = loads(response.data)
    assert response.status_code == 200
    assert res["TransactionStatus"] == "C"
    assert test_booking.charged

    # refund payment for full amount
    data1 = {
        "refund_amount": "99.00",
        "payment_id": PaymentHistory.query.filter_by(
            idx=test_booking.payment_history_id
        )
        .one_or_none()
        .idx,
        "refund_reason": "Test refund functionality",
    }

    response = test_client.post(
        f"/payment/refunds/{test_client.client_id}/",
        headers=test_client.staff_auth_header,
        data=dumps(data1),
        content_type="application/json",
    )

    # should succeed
    assert response.status_code == 201

    # refund payment that has already been refunded in full
    response = test_client.post(
        f"/payment/refunds/{test_client.client_id}/",
        headers=test_client.staff_auth_header,
        data=dumps(data1),
        content_type="application/json",
    )

    # should fail
    assert response.status_code == 400

    statuses = (
        TelehealthBookingStatus().query.filter_by(booking_id=test_booking.idx).all()
    )
    for status in statuses:
        db.session.delete(status)
    db.session.commit()


@pytest.mark.skip("payment disabled until instamed is replaced")
def test_refund_too_much(test_client, test_booking):
    # charge booking using test endpoint ($99.00)
    response = test_client.post(
        "/payment/test/telehealth-charge/",
        headers=test_client.staff_auth_header,
        data=dumps({"booking_id": test_booking.idx}),
        content_type="application/json",
    )

    # should succeed
    assert response.status_code == 200

    # refund for more than full amount using test endpoint ($100.00)
    data2 = {
        "refund_amount": "100.00",
        "payment_id": PaymentHistory.query.filter_by(
            idx=test_booking.payment_history_id
        )
        .one_or_none()
        .idx,
        "refund_reason": "Test refund functionality",
    }

    response = test_client.post(
        f"/payment/refunds/{test_client.client_id}/",
        headers=test_client.staff_auth_header,
        data=dumps(data2),
        content_type="application/json",
    )

    # should fail
    assert response.status_code == 400

    statuses = (
        TelehealthBookingStatus().query.filter_by(booking_id=test_booking.idx).all()
    )
    for status in statuses:
        db.session.delete(status)
    db.session.commit()


@pytest.mark.skip("payment disabled until instamed is replaced")
def test_payment_history(test_client):
    """
    Test the response to payment/transaction-history (GET)

    Relies on the transactions previously made with test_client.client_id
    """

    response = test_client.get(
        f"/payment/transaction-history/{test_client.client_id}/",
        headers=test_client.client_auth_header,
        content_type="application/json",
    )

    assert response.status_code == 200
    assert (
        response.json["items"][0]["transaction_descriptor"]
        == "Telehealth-MedicalDoctor-20mins"
    )
