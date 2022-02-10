import logging
logger = logging.getLogger(__name__)

from flask import current_app
from odyssey.api.user.models import User
from odyssey.api.client.models import ClientInfo
from odyssey import db
import json

def build_ES_indices():
    es = current_app.elasticsearch
    if not es: return

    queries = []
    # clients = db.session.query(User, ClientInfo).filter_by(is_client=True, deleted=False).join(ClientInfo).order_by(User.lastname.asc(), User.firstname.asc()).all()
    clients = db.session.query(User).filter_by(is_client=True, deleted=False).order_by(User.lastname.asc(), User.firstname.asc()).all()    
    staff = db.session.query(User).filter_by(is_staff=True, deleted=False).order_by(User.lastname.asc(), User.firstname.asc()).all()
    queries.append(('clients',clients))
    queries.append(('staff', staff))

    #Create two(2) searchable indices (called "clients" and "staff") from query data
    def build_index(indexName:str, query:list):
        action = ''
        for user in query:
            payload = {}
            
            for field in user.__searchable__:
                payload[field] = str(getattr(user, field))        
            _id = user.user_id
            action = '{\"index\":{\"_index\":\"'f'{indexName}''\", \"_id\":'f'{_id}''}\n'f'{json.dumps(payload)}'
            yield action

    for queryName, query in queries:
        if len(query) != 0:
            es.bulk(operations=build_index(indexName=queryName, query=query), refresh=True)

#def update_user_dob(user_id:int, dob:str):
#    """
#    This function will be called when a dob(or anything) has been updated in 
#    the ClientInfo table.
#    It updates the dob field for the given user_id in the ES index
#    """
#    es = current_app.elasticsearch
#    if not es: return
#    
#    user = User.query.filter_by(user_id=user_id).one_or_none()
#    if user:
#        if str(user.dob) != dob:
#            update_body = {
#                "script":{
#                    "source":"ctx._source.dob = params.dob",
#                    "lang":"painless",
#                    "params":{"dob": f"{dob}"}
#                }
#            }
#            if user.is_client:
#                es.update(index="clients", id=user_id, body=update_body, refresh=True)
#            if user.is_staff:
#                es.update(index="staff", id=user_id, body=update_body, refresh=True)

            
def update_index(user:dict, new_entry:bool):
    """
    This function will be called when any change has 
    happened in the User table, 
    for example, if a new user is added 
    or if firstname, lastname, phone_number, email, dob or modobio_id are changed
    """
    es = current_app.elasticsearch
    if not es: return
    #updating index indexName when there's an event notification from 
    #listening to the db.
    
    _id = user['user_id']
    client = user['is_client']
    staff = user['is_staff']
    dob = None
    try: 
        dob = user['dob'].date()
    except:
        dob = user['dob']
    update_body = {
        "script":{
            "source":"ctx._source.firstname = params.firstname;\
                ctx._source.lastname = params.lastname;\
                ctx._source.phone_number = params.phone_number;\
                ctx._source.modobio_id = params.modobio_id;\
                ctx._source.email = params.email;\
                ctx._source.dob = params.dob;\
                ctx._source.user_id = params.user_id",
            "lang":"painless", 
            "params":{
                "firstname": f"{user['firstname']}",
                "lastname": f"{user['lastname']}",
                "phone_number": f"{user['phone_number']}",
                "email": f"{user['email']}",
                "modobio_id": f"{user['modobio_id']}",
                "dob": f"{dob}" if dob else dob,
                "user_id": f"{_id}"}}}
    
    if new_entry:
        if client:
            payload = update_body['script']['params']
            body = '{\"index\":{\"_index\":\"clients\", \"_id\":'f'{_id}''}\n'f'{json.dumps(payload)}'
            es.bulk(body=body, refresh=True)
        
        if staff:
            payload = update_body['script']['params']
            body = '{\"index\":{\"_index\":\"staff\", \"_id\":'f'{_id}''}\n'f'{json.dumps(payload)}'
            es.bulk(body=body, refresh=True)

    else:
        if client:
            if not es.exists(index='clients', id=_id):
                payload = update_body['script']['params']
                body = '{\"index\":{\"_index\":\"clients\", \"_id\":'f'{_id}''}\n'f'{json.dumps(payload)}'
                es.bulk(body=body, refresh=True)
            es.update(index="clients", id=_id, body=update_body, refresh=True)
        
        if staff:
            if not es.exists(index='staff', id=_id):
                payload = update_body['script']['params']
                body = '{\"index\":{\"_index\":\"staff\", \"_id\":'f'{_id}''}\n'f'{json.dumps(payload)}'
                es.bulk(body= body, refresh=True)
            es.update(index="staff", id=_id, body=update_body, refresh=True)
        

def delete_from_index(user_id:int):
    """
    This function is called from DELETE user/<user_id>
    Once a user has been deleted, we will remove it from the ES indices to 
    ensure the user won't come up on a search.
    """
    es = current_app.elasticsearch
    if not es: return
    
    if es.exists(index='clients', id=user_id):
        es.delete(index='clients', id=user_id, refresh=True)
    
    if es.exists(index='staff', id=user_id):
        es.delete(index='staff', id=user_id, refresh=True)
