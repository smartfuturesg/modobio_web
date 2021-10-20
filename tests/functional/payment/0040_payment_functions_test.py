from flask.json import dumps
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

    #charge booking using test endpoint ($99.00)

    #should succeed

    #create new booking to charge

    #charge booking using test endpoint ($99.05)

    #should fail, check that booking is cancelled

    #create new booking to charge

    #charge booking using test endpoint ($99.10)

    #should fail, check that booking is cancelled and partial payment is voided

def test_void(test_client):
    #create booking to charge

    #charge booking using test endpoint ($99.00)

    #should succeed

    #void payment using test endpoint

    #should succeed

def test_refund(test_client):
    #create booking to charge

    #charge booking using test endpoint ($99.00)

    #should succeed

    #refund payment for full amount

    #should succeed

    #create new booking to charge

    #charge booking using test endpoint ($99.00)

    #should succeed

    #refund for more than full amount using test endpoint ($100.00)

    #should fail

    #refund first payment that has already been refunded in full

    #should fail