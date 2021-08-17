import random
import hashlib
import base64
import requests

ALPHANUMERIC = "ABCDFGHJKLMNPQRSTVWXYZ0123456789"
clinic_key = 'WKUSNMSUQ5TUKFYCNSDC744YYMX3QSSH'
# Arnold Bays Clinician ID
clinician_id = '227295'

# TEst Clinician ID
# clinician_id = '229645'

# Steve Admin ID
# clinician_id = '229187'

# Steve Thach Clinician ID
# clinician_id = '230178'

# Jack Williams CLinician ID
# clinician_id = '229332'

char_len = 32
clinic_id = '30871'

def generate_encrypted_clinic_id(clinic_key,char_len):
    """
    This function generates an encrypted clinic key for DoseSpot
    
    Reference: 
    
    DoseSpot RESTful API Guide 
    Section 2.3.1 
    """
    rand_phrase = "".join([random.choice(ALPHANUMERIC) for i in range(char_len)])

    temp_str = rand_phrase + clinic_key

    encoded_str = temp_str.encode('utf-8')

    hash512 = hashlib.sha512(encoded_str).digest()

    encrypted_str = base64.b64encode(hash512).decode()

    while encrypted_str[-1] == '=':
        encrypted_str = encrypted_str[:-1]

    return rand_phrase+encrypted_str

def generate_encrypted_user_id(rand_phrase,clinic_key,clinician_id):
    """
    This function generates an encrypted user_id for DoseSpot
    
    Reference: 
    
    DoseSpot RESTful API Guide 
    Section 2.3.1 
    """    
    temp_str = clinician_id + rand_phrase + clinic_key
    encoded_str = temp_str.encode('utf-8')

    hash512 = hashlib.sha512(encoded_str).digest()

    encrypted_str = base64.b64encode(hash512).decode()

    while encrypted_str[-1] == '=':
        encrypted_str = encrypted_str[:-1]

    return encrypted_str

def generate_sso(clinic_id, clinician_id, encrypted_clinic_id_url, encrypted_user_id_url, patient_id=None):
    URL = f'http://my.staging.dosespot.com/LoginSingleSignOn.aspx?SingleSignOnClinicId={clinic_id}&SingleSignOnUserId={clinician_id}&SingleSignOnPhraseLength=32&SingleSignOnCode={encrypted_clinic_id_url}&SingleSignOnUserIdVerify={encrypted_user_id_url}'
    if(patient_id):
        URL = URL+f'&PatientId={patient_id}'
    else:
        URL = URL+'&RefillsErrors=1'
    return URL


encrypted_clinic_id = generate_encrypted_clinic_id(clinic_key,char_len)
encrypted_clinic_id_url = encrypted_clinic_id.replace('/','%2F')
encrypted_clinic_id_url = encrypted_clinic_id_url.replace('+','%2B')
encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_key,clinician_id)
encrypted_user_id_url = encrypted_user_id.replace('/','%2F')
encrypted_user_id_url = encrypted_user_id_url.replace('+','%2B')

clinician_sso_URL = generate_sso(clinic_id, clinician_id, encrypted_clinic_id_url, encrypted_user_id_url)

patient_id = '18048851'
patient_portal_URL = generate_sso(clinic_id, clinician_id, encrypted_clinic_id_url, encrypted_user_id_url,patient_id=patient_id)

print()
print(clinician_sso_URL)
print()
print(patient_portal_URL)
print()
def get_access_token(clinic_id,encrypted_clinic_id,clinician_id,encrypted_user_id):
    payload = {'grant_type': 'password','Username':clinician_id,'Password':encrypted_user_id}
    res = requests.post('https://my.staging.dosespot.com/webapi/token',
                    auth=(clinic_id, encrypted_clinic_id),
                    data=payload)
    return res

res = get_access_token(clinic_id,encrypted_clinic_id,clinician_id,encrypted_user_id)
breakpoint()
access_token = res.json()['access_token']
print(access_token)

# --------------------------------------------------------------------------------------------------

import random
import hashlib
import base64
import requests

ALPHANUMERIC = "ABCDFGHJKLMNPQRSTVWXYZ0123456789"
clinic_key = 'WKUSNMSUQ5TUKFYCNSDC744YYMX3QSSH'

# Steve Admin ID
clinician_id = '229187'
char_len = 32
clinic_id = '30871'

def generate_encrypted_clinic_id(clinic_key,char_len):
    """
    This function generates an encrypted clinic key for DoseSpot
    
    Reference: 
    
    DoseSpot RESTful API Guide 
    Section 2.3.1 
    """
    rand_phrase = "".join([random.choice(ALPHANUMERIC) for i in range(char_len)])

    temp_str = rand_phrase + clinic_key

    encoded_str = temp_str.encode('utf-8')

    hash512 = hashlib.sha512(encoded_str).digest()

    encrypted_str = base64.b64encode(hash512).decode()

    while encrypted_str[-1] == '=':
        encrypted_str = encrypted_str[:-1]

    return rand_phrase+encrypted_str

def generate_encrypted_user_id(rand_phrase,clinic_key,clinician_id):
    """
    This function generates an encrypted user_id for DoseSpot
    
    Reference: 
    
    DoseSpot RESTful API Guide 
    Section 2.3.1 
    """    
    temp_str = clinician_id + rand_phrase + clinic_key
    encoded_str = temp_str.encode('utf-8')

    hash512 = hashlib.sha512(encoded_str).digest()

    encrypted_str = base64.b64encode(hash512).decode()

    while encrypted_str[-1] == '=':
        encrypted_str = encrypted_str[:-1]

    return encrypted_str

def generate_sso(clinic_id, clinician_id, encrypted_clinic_id_url, encrypted_user_id_url, patient_id=None):
    URL = f'http://my.staging.dosespot.com/LoginSingleSignOn.aspx?SingleSignOnClinicId={clinic_id}&SingleSignOnUserId={clinician_id}&SingleSignOnPhraseLength=32&SingleSignOnCode={encrypted_clinic_id_url}&SingleSignOnUserIdVerify={encrypted_user_id_url}'
    if(patient_id):
        URL = URL+f'&PatientId={patient_id}'
    else:
        URL = URL+'&RefillsErrors=1'
    return URL


encrypted_clinic_id = generate_encrypted_clinic_id(clinic_key,char_len)
encrypted_clinic_id_url = encrypted_clinic_id.replace('/','%2F')
encrypted_clinic_id_url = encrypted_clinic_id_url.replace('+','%2B')
encrypted_user_id = generate_encrypted_user_id(encrypted_clinic_id[:22],clinic_key,clinician_id)
encrypted_user_id_url = encrypted_user_id.replace('/','%2F')
encrypted_user_id_url = encrypted_user_id_url.replace('+','%2B')

clinician_sso_URL = generate_sso(clinic_id, clinician_id, encrypted_clinic_id_url, encrypted_user_id_url)

# patient_id = '18048851'
# patient_portal_URL = generate_sso(clinic_id, clinician_id, encrypted_clinic_id_url, encrypted_user_id_url,patient_id=patient_id)

# print()
# print(clinician_sso_URL)
# print()
# print(patient_portal_URL)
# print()
def get_access_token(clinic_id,encrypted_clinic_id,clinician_id,encrypted_user_id):
    payload = {'grant_type': 'password','Username':clinician_id,'Password':encrypted_user_id}
    res = requests.post('https://my.staging.dosespot.com/webapi/token',
                    auth=(clinic_id, encrypted_clinic_id),
                    data=payload)
    return res

res = get_access_token(clinic_id,encrypted_clinic_id,clinician_id,encrypted_user_id)

access_token = res.json()['access_token']

def create_clinician(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    # payload = {'Prefix': '',
    #            'FirstName': 'Steve',
    #            'MiddleName': '',
    #            'LastName': 'Thach',
    #            'Suffix': '',
    #            'DateOfBirth': '1995-06-13',
    #            'Gender': 1,
    #            'Email':'',
    #            'Address1': '123 test ave',
    #            'Address2': '',
    #            'City':'Mesa',
    #            'State':'AZ',
    #            'ZipCode':'85212',
    #            'PhoneAdditional1':'',
    #            'PhoneAdditional2':'',
    #            'PhoneAdditionalType1':'',
    #            'PhoneAdditionalType2':'',
    #            'PrimaryPhone': '4803107597',
    #            'PrimaryPhoneType': 1,
    #            'Weight': '',
    #            'WeightMetric': '',
    #            'NonDoseSpotMedicalRecordNumber':'',
    #            'Active': True,
    #            'Encounter': ''}

    # min_payload = {'Prefix': '',
    #            'FirstName': 'Steve',
    #            'MiddleName': '',
    #            'LastName': 'Thach',
    #            'Suffix': '',
    #            'DateOfBirth': '1995-06-13',
    #            'Gender': 1,
    #            'Email':'',
    #            'Address1': '123 test ave',
    #            'Address2': '',
    #            'City':'Mesa',
    #            'State':'AZ',
    #            'ZipCode':'85212',
    #            'PhoneAdditional1':'',
    #            'PhoneAdditional2':'',
    #            'PrimaryPhone': '4803107597',
    #            'PrimaryPhoneType': 1,
    #            'NonDoseSpotMedicalRecordNumber':'',
    #            'Active': True,
    #            'Encounter': ''}
    min_payload = {'FirstName': 'Clinician',
               'LastName': 'clin1',
               'DateOfBirth': '1995-06-13',
               'Gender': 1,
               'Address1': '123 test ave',
               'City':'Mesa',
               'State':'AZ',
               'ZipCode':'85212',
               'PrimaryPhone': '4803107597',
               'PrimaryPhoneType': 1,
               'PrimaryFax': '4803107597',
               'ClinicianRoleType': 1,
               'NPINumber': '1296336567'
               }                
    res = requests.post('https://my.staging.dosespot.com/webapi/api/clinicians',
                    headers=headers,
                    data=min_payload)
    
    return res

res = create_clinician(access_token)
print(res.json())
breakpoint()
