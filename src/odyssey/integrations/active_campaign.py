import requests
import json

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
    
    def check_contact_existence(self, user_id) -> bool:
        # check if user already exsists in active campaign system. 
        # Also checks to see if user is already in the active campaign list

        email = User.query.filter_by(user_id=user_id).one_or_none().email
        query = { 'email': email }
        url = self.url + 'contacts/?' + urlencode(query)

        response = requests.get(url, headers=self.request_header)
        data = json.loads(response.text)

        #contact exists, check if there is an db entry in UserActiveCampaign
        if data['meta']['total'] == '1':
            contact_id = data['contacts'][0]['id']
            ac_contact = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()

            #if None, create entry
            if not ac_contact:
                ac_contact = UserActiveCampaign(
                    user_id=user_id, 
                    active_campaign_id=contact_id
                )
                db.session.add(ac_contact)
                db.session.commit()

            #Check if contact is in list. 
            url = f"{self.url}/contacts/{contact_id}/contactLists"
            response = requests.get(url, headers=self.request_header)
            data = json.loads(response.text)

            in_list = False
            if len(data['contactLists']) > 0:
                for list in data['contactLists']:
                    if list['list'] == self.list_id:
                        in_list = True
            if not in_list:
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
            return True
        else:
            # Contact not in Active Campaigns
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
        contant_response = requests.post(url, json=payload, headers=self.request_header)
        data = json.loads(contant_response.text)
        contact_id = data['contact']['id']

        user_id = User.query.filter_by(email=email).one_or_none().user_id

        ac_contact = UserActiveCampaign(
            user_id=user_id, 
            active_campaign_id=contact_id, 
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
        list_response = requests.post(url, json=payload, headers=self.request_header)
        
        return contant_response, list_response

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
        
        return response

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

        return response

    def update_ac_contact_info(self, user_id, first_name=None, last_name=None, email=None):
        #Get active campaign contact id
        ac_id = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()
        if not ac_id:
            raise BadRequest('No active campaign contact found with provided user ID.')

        payload = {'contact': {}}

        if first_name:
            payload['contact']['firstName'] = first_name
        if last_name:
            payload['contact']['lastName'] = last_name
        if email:
            payload['contact']['email'] = email
        
        #Update contact info
        url = f'{self.url}/contacts/{ac_id.active_campaign_id}'
        
        response = requests.put(url, json=payload, headers=self.request_header)

        return response

    def delete_contact(self, user_id):
        ac_id = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()
        if not ac_id:
            raise BadRequest('No active campaign contact found with provided user ID.')

        #Delete contact info
        url = f'{self.url}/contacts/{ac_id.active_campaign_id}'
        response = requests.delete(url, headers=self.request_header)

        db.session.delete(ac_id)
        db.session.commit()

        return response
