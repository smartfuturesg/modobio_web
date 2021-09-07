import random
import hashlib
import base64
import requests

from odyssey.utils.constants import ALPHANUMERIC

def generate_encrypted_clinic_id(clinic_key,char_len=32):
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

def generate_sso(clinic_id, clinician_id, encrypted_clinic_id, encrypted_user_id, patient_id=None):
    encrypted_clinic_id_url = encrypted_clinic_id.replace('/','%2F')
    encrypted_clinic_id_url = encrypted_clinic_id_url.replace('+','%2B')            
    encrypted_user_id_url = encrypted_user_id.replace('/','%2F')
    encrypted_user_id_url = encrypted_user_id_url.replace('+','%2B')    
    URL = f'http://my.staging.dosespot.com/LoginSingleSignOn.aspx?SingleSignOnClinicId={clinic_id}&SingleSignOnUserId={clinician_id}&SingleSignOnPhraseLength=32&SingleSignOnCode={encrypted_clinic_id_url}&SingleSignOnUserIdVerify={encrypted_user_id_url}'
    if(patient_id):
        URL = URL+f'&PatientId={patient_id}'
    else:
        URL = URL+'&RefillsErrors=1'
    return URL

def get_access_token(clinic_id,encrypted_clinic_id,clinician_id,encrypted_user_id):
    payload = {'grant_type': 'password','Username':clinician_id,'Password':encrypted_user_id}
    res = requests.post('https://my.staging.dosespot.com/webapi/token',
                    auth=(clinic_id, encrypted_clinic_id),
                    data=payload)
    return res

