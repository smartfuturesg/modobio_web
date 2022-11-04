from datetime import date
import requests
import json

from flask import current_app
from urllib.parse import urlencode
from odyssey import db
from odyssey.api.user.models import User, UserActiveCampaign, UserActiveCampaignTags, UserSubscriptions

import logging
logger = logging.getLogger(__name__)
class ActiveCampaign:
    """ Active Campaign integration class"""

    def __init__(self):
        self.url = current_app.config.get('ACTIVE_CAMPAIGN_BASE_URL')
        logger.info(f'ACTIVE_CAMPAIGN_BASE_URL: {self.url}')
        self.api_key = current_app.config.get('ACTIVE_CAMPAIGN_API_KEY')
        logger.info(f'ACTIVE_CAMPAIGN_API_KEY: {self.url[-4:]}')
        self.request_header = {
            "accept": "application/json",
            "Api-Token": self.api_key
        }
        ac_list = current_app.config.get('ACTIVE_CAMPAIGN_LIST')
        logger.info(f'ACTIVE_CAMPAIGN_LIST {ac_list}')
        self.list_id = self.get_list_id(ac_list)
        logger.info('Active Campaign initialization complete.')

    def get_list_id(self, ac_list):
        #Returns the list id where contacts will be stored

        url = f'{self.url}/lists'
        response = requests.get(url, headers=self.request_header)
        data = json.loads(response.text)

        for list in data['lists']:
            if list['stringid'] == ac_list:
                logger.info(f'Found list {ac_list} with list ID {list["id"]}')
                return list['id']   

        logger.error(f'No list ID found of {ac_list} found.')
    
    def check_contact_existence(self, user_id) -> bool:
        # check if user already exsists in active campaign system. 
        # Also checks to see if user is already in the active campaign list
        # Returns True if contact exists and False if not

        email = User.query.filter_by(user_id=user_id).one_or_none().email
        query = { 'email': email }
        url = self.url + 'contacts/?' + urlencode(query)

        response = requests.get(url, headers=self.request_header)
        data = json.loads(response.text)

        #contact exists, check if there is an db entry in UserActiveCampaign
        if data['meta']['total'] == '1':
            logger.info(f'Active campagign contact exisits for {email}')
            contact_id = data['contacts'][0]['id']
            ac_contact = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()

            #if None, create db entry
            if not ac_contact:
                logger.info(f'Creating UserActiveCampaign db entry for already exisiting user {email}.')
                ac_contact = UserActiveCampaign(
                    user_id=user_id, 
                    active_campaign_id=contact_id
                )
                db.session.add(ac_contact)
                db.session.commit()

            # User already exists as a contact, check to see if they have been marked as a prospect. 
            # If so change this adds a tag of "Converted-Clients".
            self.convert_prosect(user_id, contact_id)  

            #Check if contact is in active campaign list. 
            url = f"{self.url}/contacts/{contact_id}/contactLists"
            response = requests.get(url, headers=self.request_header)
            data = json.loads(response.text)

            in_list = False
            if len(data['contactLists']) > 0:
                for x in data['contactLists']:
                    if x['list'] == self.list_id:    #Contact is already created and in list
                        logger.info('Active Campaign contact exists in targeted list.')
                        in_list = True 
            if not in_list:
                #add contact to list
                logger.info('Adding existing active campaign contact to list.')
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
            # Returns false if contact not in Active Campaigns
            logger.info(f'No contact in Active Campaign with the email: {email}')
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
        logger.info(f'Contact Create response code: {contant_response.status_code}')
        logger.info(f'Contact Create response  {contant_response.text}')

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
        logger.info(f'Add contact to list response code: {list_response.status_code}')  
        logger.info(f'Contact Create response  {list_response.text}')

        return contant_response, list_response

    def add_tag(self, user_id, tag_name):  
        #Get tag id from tag name
        query = { 'search': tag_name }
        url = self.url + 'tags/?' + urlencode(query)

        response = requests.get(url, headers=self.request_header)
        data = json.loads(response.text)
        if data['meta']['total'] == '0':
            logger.error('No tag found with the provided name.')
            return
        
        tag_id = data['tags'][0]['id']

        #Get active campaign contact id
        ac_id = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()
        if not ac_id:
            logger.error('No active campaign contact found with provided user ID.')
            return

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

            logger.info(f'Added Active Campaign tag: {tag_name} to user with user_id: {user_id}')
        return response

    def remove_tag(self, user_id, tag_name):
        #Get tag from db
        tag = UserActiveCampaignTags.query.filter_by(user_id=user_id, tag_name=tag_name).one_or_none()
        if not tag:
            logger.error('Tag not associated with user.')
            return

        #Remove tag
        url = f'{self.url}/contactTags/{tag.tag_id}'
        response = requests.delete(url, headers=self.request_header)
        
        db.session.delete(tag)
        db.session.commit()

        logger.info(f'Removed Active Campaign tag: {tag_name} from user with user_id: {user_id}')
        return response

    def update_ac_contact_info(self, user_id, first_name=None, last_name=None, email=None):
        #Get active campaign contact id
        ac_id = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()
        if not ac_id:
            logger.error('No active campaign contact found with provided user ID.')
            return
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

        logger.info(f'Update Active Campaign contact information status code: {response.status_code}') 
        logger.info(f'Update Active Campaign contact information error: {response.text}')
        return response

    def delete_contact(self, user_id):
        #Delete contact from active campaign
        ac_id = UserActiveCampaign.query.filter_by(user_id=user_id).one_or_none()
        if not ac_id:
            logger.error('No active campaign contact found with provided user ID.')
            return

        #Delete contact info
        url = f'{self.url}/contacts/{ac_id.active_campaign_id}'
        response = requests.delete(url, headers=self.request_header)

        db.session.delete(ac_id)
        db.session.commit()

        return response

    def add_age_group_tag(self, user_id):
        #Gets users age and adds to age group
        dob = User.query.filter_by(user_id=user_id).one_or_none().dob
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < 25:
            return self.add_tag(user_id, 'Age 25 -')
        elif age >= 25 and age < 45:
            return self.add_tag(user_id, 'Age 25-44')
        elif age >= 45 and age < 64:
            return self.add_tag(user_id, 'Age 45-64')
        elif age >= 64:
            return self.add_tag(user_id, 'Age 64+')
    
    def add_user_subscription_type(self, user_id):
        #Remove old subscription tags if any
        subscription_tags = UserActiveCampaignTags.query.filter(
            UserActiveCampaignTags.user_id == user_id, UserActiveCampaignTags.tag_name.contains('Subscription')).all()
        if subscription_tags:
            for tag in subscription_tags:
                self.remove_tag(user_id, tag.tag_name)

        #Get subscription type and add tag based off subsctipyon type
        client_sub = UserSubscriptions.query.filter_by(user_id=user_id, is_staff=False).order_by(UserSubscriptions.idx.desc()).first()
        if client_sub:
            if client_sub.subscription_status == 'unsubscribed':   #Unsubscribed
                return self.add_tag(user_id, 'Subscription - None')
            elif client_sub.subscription_type_id == 2:             #Monthly Subscription ID from LookupTable
                return self.add_tag(user_id, 'Subscription - Month')
            elif client_sub.subscription_type_id == 3:             #Yearly Subscrioption ID from LookupTable
                return self.add_tag(user_id, 'Subscription - Annual')

    def convert_prosect(self, user_id, ac_contact_id):
        #Checks if contact is marked as a "prospect" and converts them to "Converted - Clients"
        user = User.query.filter_by(user_id=user_id).one_or_none()

        #Get the ids of the 'Prospect' tags stored in Active Campaign
        query = { 'search': 'prospect' }
        url = self.url + 'tags/?' + urlencode(query)
        response = requests.get(url, headers=self.request_header)
        data = json.loads(response.text)
        prospect_tag_ids = data['tags']

        if data['meta']['total'] == '0':
            logger.error('No tag found with the provided name.')
            return
        
        #Get the tags associated with the user. 
        url = f'{self.url}/contacts/{ac_contact_id}/contactTags' 
        response = requests.get(url, headers=self.request_header)
        data = json.loads(response.text)
        user_tags = data['contactTags']

        #Check if user has 'Prospect' tags on account
        has_prospect_tag = False
        for user_tag in user_tags:
            for tag_id in prospect_tag_ids:
                #User has some tag of 'Prospect' 
                if tag_id['tag'] != 'Prospect - Provider' and user_tag['tag'] == tag_id['id']:
                    has_prospect_tag = True
                #Disregard operation because user has tag of 'Prospect - Provider'
                elif tag_id['tag'] == 'Prospect - Provider' and user_tag['tag'] == tag_id['id']:
                    return
                
        if has_prospect_tag and user.is_client:
            return self.add_tag(user_id, 'Converted - Client')