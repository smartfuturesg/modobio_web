
import time 

from flask.json import dumps

# from .data import (
#     telehealth_staff_general_availability_1_post_data,
#     telehealth_staff_general_availability_2_post_data,
#     telehealth_staff_general_availability_bad_3_post_data,
#     telehealth_staff_general_availability_bad_4_post_data,
#     telehealth_staff_general_availability_bad_5_post_data,
#     telehealth_staff_general_availability_bad_6_post_data,
#     telehealth_staff_general_availability_bad_7_post_data
# )

def test_get_1_client_select_time(test_client, init_database, client_auth_header, staff_auth_header):
    """
    GIVEN a api end point for clients to select their appointment times
    WHEN the '/telehealth/client/time-select/' resource  is requested (GET)
    THEN check the response is valid
    """
    for header in (staff_auth_header, client_auth_header):
        response = test_client.get('/telehealth/client/time-select/1/',
                                    headers=header, 
                                    content_type='application/json')
        
        # queue order should be 4, 1, 3, 2, 5
        assert response.status_code == 200
        assert [response.json['queue'][0]['target_date'],response.json['queue'][0]['priority']] == ['2025-01-02T02:00:00',False]
        assert [response.json['queue'][1]['target_date'],response.json['queue'][1]['priority']] == ['2025-01-05T02:00:00',False]
        assert [response.json['queue'][2]['target_date'],response.json['queue'][2]['priority']] == ['2025-02-05T02:00:00',False]
        assert [response.json['queue'][3]['target_date'],response.json['queue'][3]['priority']] == ['2025-03-05T02:00:00',False]
        assert [response.json['queue'][4]['target_date'],response.json['queue'][4]['priority']] == ['2025-04-05T02:00:00',False]
        assert response.json['total_queue'] == 5