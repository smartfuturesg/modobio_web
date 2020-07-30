from odyssey.models.intake import ClientInfo
from odyssey.api.errors import UserNotFound



def check_client_existence(clientid):
    client = ClientInfo.query.filter_by(clientid=clientid).one_or_none()
    if not client:
        raise UserNotFound(clientid)
