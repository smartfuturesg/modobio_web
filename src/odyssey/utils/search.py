import json
import logging

import elasticsearch
from flask import current_app

from odyssey import db
from odyssey.api.user.models import User

logger = logging.getLogger(__name__)


def build_es_indices():
    es = current_app.elasticsearch
    if not es:
        # TODO: throw some kind of error or something?
        return

    queries = []
    # clients = db.session.query_data(User, ClientInfo).filter_by(is_client=True, deleted=False).join(
    # ClientInfo).order_by(User.lastname.asc(), User.firstname.asc()).all()
    clients = (
        db.session.query(User).filter_by(is_client=True, deleted=False).order_by(
            User.lastname.asc(), User.firstname.asc()
        ).all()
    )
    staff = (
        db.session.query(User).filter_by(is_staff=True, deleted=False).order_by(
            User.lastname.asc(), User.firstname.asc()
        ).all()
    )
    queries.append(('clients', clients))
    queries.append(('staff', staff))

    # Create two(2) searchable indices (called "clients" and "staff") from query_data
    def build_index(index_name: str, query_data: list):
        for user in query_data:
            payload = {}

            for field in user.__searchable__:
                payload[field] = str(getattr(user, field))

            _id = user.user_id

            action = (
                '{"index":{"_index":"'
                f'{index_name}'
                '", "_id":'
                f'{_id}'
                '}}\n'
                f'{json.dumps(payload)}'
            )

            yield action

    for queryName, query in queries:
        if len(query) != 0:
            # Elasticsearch 8.0 requires all arguments to be named parameters.
            if elasticsearch.__version__[0] >= 8:
                es.bulk(
                    operations=build_index(index_name=queryName, query_data=query),
                    refresh=True,
                )
            else:
                # But it's not backwards compatible.
                es.bulk(
                    build_index(index_name=queryName, query_data=query),
                    refresh=True,
                )


# def update_user_dob(user_id:int, dob:str):
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


def update_index(user: dict, new_entry: bool):
    """
    This function will be called when any change has
    happened in the User table,
    for example, if a new user is added
    or if firstname, lastname, phone_number, email, dob or modobio_id are changed
    """
    es = current_app.elasticsearch
    if not es:
        return
    # updating index indexName when there's an event notification from
    # listening to the db.

    _id = user['user_id']
    client = user['is_client']
    staff = user['is_staff']

    try:
        dob = user['dob'].date()
    except:
        dob = user['dob']

    update_body = {
        'script': {
            'source': (
                'ctx._source.firstname = params.firstname;           '
                ' ctx._source.lastname = params.lastname;           '
                ' ctx._source.phone_number = params.phone_number;           '
                ' ctx._source.modobio_id = params.modobio_id;           '
                ' ctx._source.email = params.email;            ctx._source.dob'
                ' = params.dob;            ctx._source.user_id ='
                ' params.user_id'
            ),
            'lang': 'painless',
            'params': {
                'firstname': f"{user['firstname']}",
                'lastname': f"{user['lastname']}",
                'phone_number': f"{user['phone_number']}",
                'email': f"{user['email']}",
                'modobio_id': f"{user['modobio_id']}",
                'dob': f'{dob}' if dob else dob,
                'user_id': f'{_id}',
            },
        }
    }

    if new_entry:  # in all usages as of 12/01/2022 new_entry is always False
        if client:
            payload = update_body['script']['params']
            body = ('{"index":{"_index":"clients", "_id":'
                    f'{_id}'
                    '}\n'
                    f'{json.dumps(payload)}')
            es.bulk(body=body, refresh=True)

        if staff:  # What about if client and staff both???
            payload = update_body['script']['params']
            body = ('{"index":{"_index":"staff", "_id":'
                    f'{_id}'
                    '}\n'
                    f'{json.dumps(payload)}')
            es.bulk(body=body, refresh=True)

    else:
        if client:
            if not es.exists(index='clients', id=_id):
                es.index(
                    index='clients',
                    id=_id,
                    document=update_body['script']['params'],
                )
            es.update(index='clients', id=_id, body=update_body, refresh=True)
        if staff:
            if not es.exists(index='staff', id=_id):
                es.index(
                    index='staff',
                    id=_id,
                    document=update_body['script']['params'],
                )
            es.update(index='staff', id=_id, body=update_body, refresh=True)


def delete_from_index(user_id: int):
    """
    This function is called from DELETE user/<user_id>
    Once a user has been deleted, we will remove it from the ES indices to
    ensure the user won't come up on a search.
    """
    es = current_app.elasticsearch
    if not es:
        return

    if es.exists(index='clients', id=user_id):
        es.delete(index='clients', id=user_id, refresh=True)

    if es.exists(index='staff', id=user_id):
        es.delete(index='staff', id=user_id, refresh=True)
