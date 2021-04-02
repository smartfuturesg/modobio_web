"""
Hasura gives us flexibility to authorize user access through special claims embedded in our JWTs. 
These claims should summarize a user’s level of access when requesting a resource from our database. 
Currently we use a combination of a 4 interworking resource access systems:

1. Context-based access: 
    We have client and staff users who will access both their own resources and those of other users.
2. Role-based access (staff): 
    Staff members may only view and manipulate data which falls under their purview. 
    Ex. doctors may only access medical-specific resources while physical trainers may have no access 
    or restricted access to client medical data. 
3. User-specific access:
    Clients must specify whether another user should be able to see their data. 
    Currently this is implemented through the clinical care team system, but we expect to build 
    a similar system in the future where clients must explicitly give access of their resources to 
    specific staff members.
4. Table-level access (clinical care team): 
    Clients are given the option to specify which data they will grant a member of their care team access to. 
    Care team members may be other users. 

Permissions can be applied to a table in hasura by editing the `permissions` area of a table's metadata.
In yaml format, these permissions look like:
"select_permissions": [
        {
          "role": "client",
          "permission": {
            "columns": [
              "created_at",
              "updated_at",
              "user_id",
              "modobio_id"
            ],
            "filter": {
              "user_id": {
                "_eq": "X-Hasura-User-Id"
              }
            }
          }

Broken down here

    - the type of request. Must be one of:
        - select_permissions
        - insert_permissions
        - update_permissions

    - role: the user type the user is making the request from. In our cases, this is ('staff', or 'client')
    - permission: consists of two fields which control which columns and rows are accessible
        - columns: which columns are accessible
        - filter: controls the rows that are returned. If none of the filter requirements are met, no data is returned.

""""


##
# Clients accessing their own data
# user_id and client_user_id may be present in these tables
# All 'Client' tables
##

def client_default_select_permission(columns, insert, filter_by_id_column='user_id'):
    """
    Covers select permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables'
    and accessed from a client context
    """
    permission =  {
        'role': 'client', 
        'permission': {
            'columns': columns,
            'filter': {
                filter_by_id_column : { "_eq": "X-Hasura-User-Id"}
            }
        }
     } 

    #TODO add clinical care team scenario

    return permission
    
def client_default_update_permission(columns, insert, filter_by_id_column='user_id'):
    """
    Covers insert and update permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables'
    and accessed from a client context.

    user_id is automatically set to user_id
    """

    permission =  {
        'role': 'client', 
        'permission': {
            'columns': columns,
            'check': {
              'user_id': {
                '_eq': 'X-Hasura-User-Id'
              }
            },
            'set': {
              'user_id': 'X-Hasura-User-Id'
            }
        }
     }

    if 'reporter_id' in columns:
        permission['permission']['set']['reporter_id'] =  'X-Hasura-User-Id' 

    return permission


            




# Select permissions


# insert permissions





