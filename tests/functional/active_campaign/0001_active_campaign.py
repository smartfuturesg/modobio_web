import json
from odyssey.integrations.active_campaign import ActiveCampaign
from odyssey.api.user.models import User, UserActiveCampaign, UserActiveCampaignTags

# Test Active Campaign operations on staff client.
# Operations: 
    # Create Contact
    # Create Tag
    # Remove Tag
    # Update contact name
    # Update contact email
    # Delete Contact

def test_create_contact(test_client):
    ac = ActiveCampaign()

    #create contact
    user =  User.query.filter_by(user_id=test_client.staff_id).one_or_none()
    contact_response, list_response = ac.create_contact(user.email, user.firstname, user.lastname)
    data = json.loads(contact_response.text)
    
    #assert contact was added to Active Campaign and stored in db
    assert contact_response.status_code == 201
    ac_contact = UserActiveCampaign.query.filter_by(user_id=test_client.staff_id).one_or_none()
    assert ac_contact.user_id == test_client.staff_id
    assert ac_contact.active_campaign_id == int(data['contact']['id'])

    #Assert contact was created in correct list
    data = json.loads(list_response.text)
    assert list_response.status_code == 201
    assert data['contactList']['list'] == ac.list_id

def test_create_tag(test_client):
    ac = ActiveCampaign()

    #create tag
    user =  User.query.filter_by(user_id=test_client.staff_id).one_or_none()
    response = ac.add_tag(user.user_id, 'Persona - Client')
    data = json.loads(response.text) 

    assert response.status_code == 201
    ac_tag = UserActiveCampaignTags.query.filter_by(user_id=user.user_id, tag_name='Persona - Client').one_or_none()
    assert ac_tag.tag_id == int(data['contactTag']['id'])

def test_remove_tag(test_client):
    ac = ActiveCampaign()

    #remove tag
    user =  User.query.filter_by(user_id=test_client.staff_id).one_or_none()
    response = ac.remove_tag(user.user_id, 'Persona - Client')
    data = json.loads(response.text) 

    assert response.status_code == 200
    ac_tag = UserActiveCampaignTags.query.filter_by(user_id=user.user_id, tag_name='Persona - Client').one_or_none()
    assert ac_tag == None

def test_update_contact_name(test_client):
    ac = ActiveCampaign()

    #update name
    user =  User.query.filter_by(user_id=test_client.staff_id).one_or_none()
    response = ac.update_ac_contact_info(user.user_id, 'Update', 'Name', 'updated@email.com')
    data = json.loads(response.text) 

    assert response.status_code == 200
    assert data['contact']['firstName'] == 'Update'
    assert data['contact']['lastName'] == 'Name'
    assert data['contact']['email'] == 'updated@email.com'


def test_delete_contact(test_client):
    ac = ActiveCampaign()
    
    #delete contact
    ac_contact = UserActiveCampaign.query.filter_by(user_id=test_client.staff_id).one_or_none()
    response = ac.delete_contact(ac_contact.user_id)

    #assert Contact was deleted and removed from db
    assert response.status_code == 200
    ac_contact = UserActiveCampaign.query.filter_by(user_id=test_client.staff_id).one_or_none()
    assert ac_contact == None