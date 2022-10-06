import requests
import json
from sqlalchemy import true

from werkzeug.exceptions import BadRequest

from flask import current_app
from urllib.parse import urlencode
from odyssey import db
from odyssey.api.user.models import User, UserActiveCampaign, UserActiveCampaignTags


class ActiveCampaign:
    """ Active Campaign integration class"""

    def __init__(self):
        self.url = current_app.config.get('ACTIVE_CAMPAIGN_BASE_URL')
        self.api_key = current_app.config.get('ACTIVE_CAMPAIGN_API_KEY')
        self.request_header = {
            "accept": "application/json",
            "Api-Token": self.api_key
        }
        ac_list = current_app.config.get('ACTIVE_CAMPAIGN_LIST')
        self.list_id = self.get_list_id(ac_list)

    def get_list_id(self, ac_list):
        #Returns the list id where contacts will be stored

        url = f'{self.url}/lists'
        response = requests.get(url, headers=self.request_header)
        data = json.loads(response.text)

        for list in data['lists']:
            if list['stringid'] == ac_list:
                return list['id'] 

    def check_contact_existence(self, email) -> bool:
        #check if email exsists in active campaign
        query = { 'email': email }
        url = self.url + 'contacts/?' + urlencode(query)

        response = requests.get(url, headers=self.request_header)
        data = json.loads(response.text)

        #contact exists, check if there is an db entry in UserActiveCampaign
        if data['meta']['total'] == '1':
            ac_contact = UserActiveCampaign.query.filter_by(email=email).one_or_none()
            #if None, create entry
            if not ac_contact:
                user_id = User.query.filter_by(email=email).one_or_none().user_id
                ac_contact = UserActiveCampaign(
                    user_id=user_id, 
                    active_campaign_id=data['contacts'][0]['id'], 
                    email=email
                )
                db.session.add(ac_contact)
                db.session.commit()

            return True
        else:
            # Contact not in Active Campaign
            return False

    def create_contact(self, email, first_name, last_name):
        #create contact and save contact id
        url = f'{self.url}/contacts'
        payload = {
            'contact': {
                'email': email, 
                'firstName': first_name,
                'lastName': last_name
            }
        }
        response = requests.post(url, json=payload, headers=self.request_header)
        data = json.loads(response.text)
        contact_id = data['contact']['id']

        user_id = User.query.filter_by(email=email).one_or_none().user_id

        ac_contact = UserActiveCampaign(
            user_id=user_id, 
            active_campaign_id=contact_id, 
            email=email
        )
        db.session.add(ac_contact)
        db.session.commit()

        #add contact to list
        url = f'{self.url}/contactLists'
        payload = {
            "contactList": {
                "list": self.list_id,
                "contact": contact_id,
                "status": 1    # '1': Set active to list, '2': unsubscribe from list
            }
        }
        response = requests.post(url, json=payload, headers=self.request_header)

    
    def add_tag(self, user_id, tag_name):  
        #Get tag id from tag name
        query = { 'search': tag_name }
        url = self.url + 'tags/?' + urlencode(query)

        response = requests.get(url, headers=self.request_header)
        data = json.loads(response.text)
        if data['meta']['total'] == '0':
            raise BadRequest('No tag found with the provided name.')
        
        tag_id = data['tags'][0]['id']

        #Get active campaign contact id
        ac_id = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()
        if not ac_id:
            raise BadRequest('No active campaign contact found with provided user ID.')

        #Add tag to contact
        url = f'{self.url}/contactTags'
        payload = {
            "contactTag": {
                "contact": ac_id.active_campaign_id,
                "tag": tag_id
            }
        }

        response = requests.post(url, json=payload, headers=self.request_header)
        data = json.loads(response.text)
        tag_id = data['contactTag']['id']

        #Check if tag already exists with user, if not store to db
        tag = UserActiveCampaignTags.query.filter_by(user_id=user_id, tag_name=tag_name).one_or_none()
        if not tag:
            tag = UserActiveCampaignTags(user_id=user_id, tag_id=tag_id, tag_name=tag_name)
            db.session.add(tag)
            db.session.commit()

    def remove_tag(self, user_id, tag_name):
        #Get tag from db
        tag = UserActiveCampaignTags.query.filter_by(user_id=user_id, tag_name=tag_name).one_or_none()
        if not tag:
            raise BadRequest('Tag not associated with user.')

        #Remove tag
        url = f'{self.url}/contactTags/{tag.tag_id}'
        response = requests.delete(url, headers=self.request_header)
        
        db.session.delete(tag)
        db.session.commit()

    def update_ac_contact_name(self, user_id, first_name, last_name):
        #Get active campaign contact id
        ac_id = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()
        if not ac_id:
            raise BadRequest('No active campaign contact found with provided user ID.')

        #Update contact info
        url = f'{self.url}/contacts/{ac_id.active_campaign_id}'
        payload = {
            "contact": {
                "firstName": first_name,
                "lastName": last_name
            }
        }
        response = requests.put(url, json=payload, headers=self.request_header)

    def update_ac_email_contact(self, user_id, email):
        #Get active campaign contact id
        ac_id = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()
        if not ac_id:
            raise BadRequest('No active campaign contact found with provided user ID.')

        #Update email address
        url = f'{self.url}/contacts/{ac_id.active_campaign_id}'
        payload = {
            "contact": {
                "email": email,
            }
        }
        response = requests.put(url, json=payload, headers=self.request_header)
