""" Default permissions for Hasura GraphQL.

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

"""
# These tables should remain inaccessible in Hasura
STAFF_SELECT_ONLY = (
    "StaffRecentClients",
    "User",
    "ClientInfo",
    "StaffRoles",
    "StaffOperationalTerriories",
)
NO_UPDATE_FIELDS = [
    "user_id",
    "created_at",
    "updated_at",
    "is_staff",
    "is_client",
    "role",
    "idx",
    "modobioId",
]
NO_INSERT_FIELDS = [item for item in NO_UPDATE_FIELDS if item not in ["user_id"]]
NO_DELETE_FIELDS = NO_UPDATE_FIELDS

##
# Clients accessing their own data or accessing staff profile data
# user_id and client_user_id may be present in these tables
# All 'Client' tables
# TODO: permission for clinical care team members
##


def client_default_select_permission(columns):
    """
    Covers select permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables'
    and accessed from a client context
    """
    permission = {"role": "client", "permission": {"columns": columns, "filter": {}}}

    # TODO add clinical care team scenario
    if "user_id" in columns:
        permission["permission"].update(
            {"filter": {"user_id": {"_eq": "X-Hasura-User-Id"}}}
        )
    elif "client_user_id" in columns:
        permission["permission"].update(
            {"filter": {"client_user_id": {"_eq": "X-Hasura-User-Id"}}}
        )

    return permission


def client_default_update_permission(columns):
    """
    Covers update permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables'
    and accessed from a client context.

    users may not alter user_id columns
    """
    permission = {
        "role": "client",
        "permission": {
            "columns": [column for column in columns if column not in NO_UPDATE_FIELDS],
            "filter": {},
        },
    }

    if "user_id" in columns:
        permission["permission"]["filter"].update(
            {"user_id": {"_eq": "X-Hasura-User-Id"}}
        )
    elif "client_user_id" in columns:
        permission["permission"]["filter"].update(
            {"client_user_id": {"_eq": "X-Hasura-User-Id"}}
        )

    return permission


def client_default_insert_permission(columns):
    """
    Covers insert and update permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables'
    and accessed from a client context.

    user_id is automatically set to uid (a.k.a 'X-Hasura-User-Id') found in the payload of the access token
    """
    permission = {
        "role": "client",
        "permission": {
            "columns": [column for column in columns if column not in NO_UPDATE_FIELDS],
            "check": {},
            "set": {},
        },
    }

    if "reporter_id" in columns:
        permission["permission"]["set"].update({"reporter_id": "X-Hasura-User-Id"})

    if "user_id" in columns:
        permission["permission"]["check"].update(
            {"user_id": {"_eq": "X-Hasura-User-Id"}}
        )
        permission["permission"]["set"].update({"user_id": "X-Hasura-User-Id"})
    elif "client_user_id" in columns:
        permission["permission"]["check"].update(
            {"client_user_id": {"_eq": "X-Hasura-User-Id"}}
        )
        permission["permission"]["set"].update({"client_user_id": "X-Hasura-User-Id"})

    return permission


def client_default_delete_permission(columns):
    """
    Covers delete permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables'
    and accessed from a client context.

    user_id is automatically set to uid (a.k.a 'X-Hasura-User-Id') found in the payload of the access token
    """
    permission = {
        "role": "client",
        "permission": {
            "columns": [column for column in columns if column not in NO_DELETE_FIELDS],
            "check": {},
            "set": {},
        },
    }

    if "user_id" in columns:
        permission["permission"].update(
            {"filter": {"user_id": {"_eq": "X-Hasura-User-Id"}}}
        )
    elif "client_user_id" in columns:
        permission["permission"].update(
            {"filter": {"client_user_id": {"_eq": "X-Hasura-User-Id"}}}
        )

    return permission


##
# Staff accessing their own data or client's data
# user_id and client_user_id may be present in these tables
##
def staff_default_select_permission(columns, filtered=True):
    """
    Covers select permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables'
    and accessed from a staff context

    Staff may view all client data but may only view their own staff accounts.

    when filtered = True, the permission sets the filter to allow only rows where the user_id is
    equal to the user_id of the request (found from JWT)
    """
    permission = {"role": "staff", "permission": {"columns": columns, "filter": {}}}

    if filtered and "user_id" in columns:
        permission["permission"].update(
            {"filter": {"user_id": {"_eq": "X-Hasura-User-Id"}}}
        )
    elif filtered and "staff_user_id" in columns:
        permission["permission"].update(
            {"filter": {"staff_user_id": {"_eq": "X-Hasura-User-Id"}}}
        )

    return permission


def staff_default_update_permission(columns, filtered=True):
    """
    Covers update permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables', 'Staff', 'System'
    and accessed from a staff context

    Staff may view all client data but may only view their own staff accounts.

    when filtered = True, the permission sets the filter to allow only rows where the user_id is
    equal to the user_id of the request (found from JWT)
    """
    permission = {
        "role": "staff",
        "permission": {
            "columns": [column for column in columns if column not in NO_UPDATE_FIELDS],
            "filter": {},
        },
    }

    if filtered and "user_id" in columns:
        permission["permission"].update(
            {"filter": {"user_id": {"_eq": "X-Hasura-User-Id"}}}
        )

    if "reporter_id" in columns:
        permission["permission"].update({"set": {"reporter_id": "X-Hasura-User-Id"}})

    return permission


def staff_default_insert_permission(columns, filtered=True):
    """
    Covers insert and update permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables'
    and accessed from a staff context.

    user_id must be submitted

    TODO (4.1.21): we have not yet worked out which tables can be editied by staff on behalf of clients
    When we do have this in order, these permissions must be updated
    """
    permission = {
        "role": "staff",
        "permission": {
            "columns": [column for column in columns if column not in NO_INSERT_FIELDS],
            "check": {},
        },
    }

    if "reporter_id" in columns:
        permission["permission"].update({"set": {"reporter_id": "X-Hasura-User-Id"}})

    if filtered and "user_id" in columns:
        permission["permission"].update(
            {"check": {"user_id": {"_eq": "X-Hasura-User-Id"}}}
        )

    return permission


def staff_default_delete_permission(columns, filtered=True):
    """
    Covers delete permisisons for most tables prefixed with
    'Client', 'Medical', 'User', 'PT', 'Trainer', 'Telehealth', 'Wearables'
    and accessed from a staff context.

    user_id must be submitted.
    """
    permission = {
        "role": "staff",
        "permission": {
            "columns": [column for column in columns if column not in NO_DELETE_FIELDS],
            "check": {},
        },
    }

    if filtered and "user_id" in columns:
        permission["permission"].update(
            {"filter": {"user_id": {"_eq": "X-Hasura-User-Id"}}}
        )
    elif filtered and "staff_user_id" in columns:
        permission["permission"].update(
            {"filter": {"staff_user_id": {"_eq": "X-Hasura-User-Id"}}}
        )

    return permission


##
# Unfiltered select access for lookup and system variable tables
##
def default_unfiltered_select_permission(columns, user_type):
    """
    Both client and staff permissions for accessing lookup tables
    """
    permission = {"role": user_type, "permission": {"columns": columns, "filter": {}}}

    return permission
