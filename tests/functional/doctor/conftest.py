import pytest

from odyssey.api.doctor.models import MedicalBloodTests, MedicalBloodTestResults


@pytest.fixture(scope='function')
def blood_tests(test_client):
    """ Generate bloodtest entries """

    blood_test_1 = MedicalBloodTests(
        user_id=test_client.client_id,
        notes='test2',
        date='2020-01-01',
        was_fasted=True,
        reporter_id = test_client.staff_id
    )

    blood_test_2 = MedicalBloodTests(
        user_id=test_client.client_id,
        notes='test2',
        date='2020-02-02',
        was_fasted=True,
        reporter_id = test_client.staff_id
    )
        
    test_client.db.session.add_all([blood_test_1, blood_test_2])

    test_client.db.session.flush()

    bloodtest_results_1 = MedicalBloodTestResults(
        test_id=blood_test_1.test_id,
        modobio_test_code='CBC001',
        result_value = 10,
        evaluation = "Normal",
        age = 30,
    )
    
    bloodtest_results_2 = MedicalBloodTestResults(
        test_id=blood_test_2.test_id,
        modobio_test_code='CBC002',
        result_value = 10,
        evaluation = "Normal",
        age = 30,
    )
    
    test_client.db.session.add_all([bloodtest_results_1, bloodtest_results_2])
    test_client.db.session.commit()

    yield blood_test_1, blood_test_2

    MedicalBloodTestResults.query.filter_by(test_id=blood_test_1.test_id).delete()
    MedicalBloodTestResults.query.filter_by(test_id=blood_test_2.test_id).delete()

    MedicalBloodTests.query.filter_by(user_id=blood_test_1.test_id).delete()

    test_client.db.session.commit()