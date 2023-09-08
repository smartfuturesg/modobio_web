import base64
import logging
import secrets
from datetime import time, timedelta
from math import ceil

import boto3
from boto3.dynamodb.conditions import Key
from dateutil import parser
from flask import current_app, jsonify, request
from flask_accepts import accepts, responds
from flask_restx import Namespace
from requests_oauthlib import OAuth2Session
from sqlalchemy import select
from sqlalchemy.sql import text
from werkzeug.exceptions import BadRequest, Unauthorized

from odyssey import mongo
from odyssey.api.wearables.models import *
from odyssey.api.wearables.schemas import *
from odyssey.integrations.active_campaign import ActiveCampaign
from odyssey.integrations.terra import TerraClient
from odyssey.tasks.tasks import deauthenticate_terra_user
from odyssey.utils.auth import token_auth
from odyssey.utils.base.resources import BaseResource
from odyssey.utils.constants import (
    START_TIME_TO_THREE_HOUR_TIME_BLOCKS,
    THREE_HOUR_TIME_BLOCK_START_TIMES_LIST,
    WEARABLE_DEVICE_TYPES,
    WEARABLES_TO_ACTIVE_CAMPAIGN_DEVICE_NAMES,
)
from odyssey.utils.json import JSONProvider
from odyssey.utils.misc import (
    create_wearables_filter_query,
    date_range,
    date_validator,
    iso_string_to_iso_datetime,
    lru_cache_with_ttl,
)
from odyssey.utils.mongo_queries import (
    sleep_durations_aggregation,
    resting_hr_aggregation,
    steps_aggregation
)

logger = logging.getLogger(__name__)

#########################
#
# V1 of the Wearables API
#
#########################

ns = Namespace("wearables", description="Endpoints for registering wearable devices.")


@ns.route("/<int:user_id>/")
@ns.doc(params={"user_id": "User ID number"})
class WearablesEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "staff"), resources=("wearable_data",)
    )
    @responds(schema=WearablesSchema, status_code=200, api=ns)
    def get(self, user_id):
        """Wearable device information for client ``user_id`` in response to a GET request.

        This endpoint returns information on which wearables a client has. For
        each supported wearable device, two keys exist in the returned dictionary:
        ``has_<device_name>`` to indicate whether or not the client has this device,
        and ``registered_<device_name>`` to indicate whether or not the registration
        of the wearable device with Modo Bio was completed successfully.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        wearables = Wearables.query.filter_by(user_id=user_id).one_or_none()

        return wearables

    @token_auth.login_required(user_type=("client",))
    @accepts(schema=WearablesSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """Create new wearables information for client ``user_id`` in reponse to a POST request.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict.
        """
        request.parsed_obj.user_id = user_id
        db.session.add(request.parsed_obj)
        db.session.commit()

    @token_auth.login_required(user_type=("client",))
    @accepts(schema=WearablesSchema, api=ns)
    @responds(status_code=204, api=ns)
    def put(self, user_id):
        """Update wearables information for client ``user_id`` in reponse to a PUT request.

        Parameters
        ----------
        user_id : int
            User ID number.
        """
        query = Wearables.query.filter_by(user_id=user_id)
        data = WearablesSchema().dump(request.parsed_obj)
        query.update(data)
        db.session.commit()


@ns.route("/oura/auth/<int:user_id>/")
@ns.doc(params={"user_id": "User ID number"})
class WearablesOuraAuthEndpoint(BaseResource):
    @token_auth.login_required(user_type=("client",))
    @responds(schema=WearablesOAuthGetSchema, status_code=200, api=ns)
    def get(self, user_id):
        """Oura OAuth2 parameters to initialize the access grant process.

        Use these parameters to initiate the OAuth2 access grant process with
        Oura. You must replace the value for ``redirect_uri`` with a
        valid redirect URI. The redirect URI must match the URI registered
        with Oura.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict containing:
            - url
            - client_id
            - redirect_uri (must be replaced with actual URI)
            - response_type (literal word 'code')
            - state
            - scope (space separated string of scopes)
        """
        info = Wearables.query.filter_by(user_id=user_id).one_or_none()
        if not info:
            raise BadRequest(
                f"user_id {user_id} not found in Wearables table. "
                "Connect to POST /wearables first."
            )

        state = secrets.token_urlsafe(24)

        # Store state in database
        oura = WearablesOura.query.filter_by(user_id=user_id).one_or_none()

        if not oura:
            oura = WearablesOura(
                user_id=user_id, oauth_state=state, wearable_id=info.idx
            )
            db.session.add(oura)
        else:
            oura.oauth_state = state
        db.session.commit()

        url = current_app.config["OURA_AUTH_URL"]
        client_id = current_app.config["OURA_CLIENT_ID"]
        scope = current_app.config["OURA_SCOPE"]

        return {
            "url": url,
            "client_id": client_id,
            "redirect_uri": "replace-this",
            "response_type": "code",
            "scope": scope,
            "state": state,
        }

    @token_auth.login_required(user_type=("client",))
    @accepts(schema=WearablesOAuthPostSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """Oura OAuth2 access grant code exchange.

        Post OAuth2 parameters here after user clicks 'allow' on the Oura homepage.
        This endpoint will reach out to Oura for the second part of the OAuth2
        process, exchanging the grant code for an access token and a refresh token.

        Parameters
        ----------
        code : str
            Access grant code.

        state : str
            State code, must be the same code as received from `GET /wearables/oura/auth`.

        redirect_uri : str
            The redirect URI used to come back to the frontend app after the user clicked
            'allow' on the Oura homepage. Must be registered with Oura.

        scope : str
            The scopes the user actually selected when clicking 'allow'. Space separated
            string of scopes. Required for Oura.
        """
        oura = WearablesOura.query.filter_by(user_id=user_id).one_or_none()
        if not oura:
            raise BadRequest(
                f"user_id {user_id} not found in WearablesOura table. "
                "Connect to GET /wearables/oura/auth first."
            )

        if request.parsed_obj["state"] != oura.oauth_state:
            raise BadRequest("OAuth state changed between requests.")

        # Oura ring returns selected scope with redirect.
        # Not requiring email or personal
        minimal_scope = set(current_app.config["OURA_SCOPE"].split())
        scope = set(request.parsed_obj.get("scope", "").split())

        if scope.intersection(minimal_scope) != minimal_scope:
            msg = "You must agree to share at least: {}.".format(
                ", ".join(minimal_scope)
            )
            raise BadRequest(msg)

        # Exchange access grant code for access token
        client_id = current_app.config["OURA_CLIENT_ID"]
        client_secret = current_app.config["OURA_CLIENT_SECRET"]
        token_url = current_app.config["OURA_TOKEN_URL"]

        oauth_session = OAuth2Session(
            client_id,
            state=request.parsed_obj["state"],
            redirect_uri=request.parsed_obj["redirect_uri"],
        )
        try:
            oauth_reply = oauth_session.fetch_token(
                token_url,
                code=request.parsed_obj["code"],
                include_client_id=True,
                client_secret=client_secret,
            )
        except Exception as e:
            raise BadRequest(f"Error while exchanging grant code for access token: {e}")

        # Everything was successful
        oura.access_token = oauth_reply["access_token"]
        oura.refresh_token = oauth_reply["refresh_token"]
        oura.token_expires = datetime.utcnow() + timedelta(
            seconds=oauth_reply["expires_in"]
        )
        oura.oauth_state = None
        oura.wearable.has_oura = True
        oura.wearable.registered_oura = True

        db.session.commit()

    @token_auth.login_required(user_type=("client",))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        """Revoke Oura OAuth2 data sharing permissions.

        Parameters
        ----------
        user_id : str
            Modo Bio user ID.
        """
        oura = WearablesOura.query.filter_by(user_id=user_id).one_or_none()

        if oura:
            oura.access_token = None
            oura.refresh_token = None
            oura.wearable.registered_oura = False
            db.session.commit()


@ns.route("/fitbit/auth/<int:user_id>/")
@ns.doc(params={"user_id": "User ID number"})
class WearablesFitbitAuthEndpoint(BaseResource):
    @token_auth.login_required(user_type=("client",))
    @responds(schema=WearablesOAuthGetSchema, status_code=200, api=ns)
    def get(self, user_id):
        """Fitbit OAuth2 parameters to initialize the access grant process.

        Use these parameters to initiate the OAuth2 access grant process with
        Fitbit. You must replace the value for ``redirect_uri`` with a
        valid redirect URI. The redirect URI must match the URI registered
        with Fitbit.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        dict
            JSON encoded dict containing:
            - url
            - client_id
            - redirect_uri (must be replaced with actual URI)
            - response_type (literal word 'code')
            - state
            - scope (space separated string of scopes)
        """
        info = Wearables.query.filter_by(user_id=user_id).one_or_none()
        if not info:
            raise BadRequest(
                f"user_id {user_id} not found in Wearables table. "
                "Connect to POST /wearables first."
            )

        state = secrets.token_urlsafe(24)

        # Store state in database
        fitbit = WearablesFitbit.query.filter_by(user_id=user_id).one_or_none()

        if not fitbit:
            fitbit = WearablesFitbit(
                user_id=user_id, oauth_state=state, wearable_id=info.idx
            )
            db.session.add(fitbit)
        else:
            fitbit.oauth_state = state
        db.session.commit()

        url = current_app.config["FITBIT_AUTH_URL"]
        client_id = current_app.config["FITBIT_CLIENT_ID"]
        scope = current_app.config["FITBIT_SCOPE"]

        return {
            "url": url,
            "client_id": client_id,
            "redirect_uri": "replace-this",
            "response_type": "code",
            "scope": scope,
            "state": state,
        }

    @token_auth.login_required(user_type=("client",))
    @accepts(schema=WearablesOAuthPostSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """Fitbit OAuth2 access grant code exchange.

        Post OAuth2 parameters here after user clicks 'allow' on the Fitbit homepage.
        This endpoint will reach out to Fitbit for the second part of the OAuth2
        process, exchanging the grant code for an access token and a refresh token.

        Parameters
        ----------
        code : str
            Access grant code.

        state : str
            State code, must be the same code as received from `GET /wearables/fitbit/auth`.

        redirect_uri : str
            The redirect URI used to come back to the frontend app after the user clicked
            'allow' on the Fitbit homepage. Must be registered with Fitbit.

        scope : str
            The scopes the user actually selected when clicking 'allow'. Space separated
            string of scopes. Ignored for Fitbit.
        """
        fitbit = WearablesFitbit.query.filter_by(user_id=user_id).one_or_none()
        if not fitbit:
            raise BadRequest(
                f"user_id {user_id} not found in WearablesFitbit table. "
                "Connect to GET /wearables/fitbit/auth first."
            )

        if request.parsed_obj["state"] != fitbit.oauth_state:
            raise BadRequest("OAuth state changed between requests.")

        # Exchange access grant code for access token
        client_id = current_app.config["FITBIT_CLIENT_ID"]
        client_secret = current_app.config["FITBIT_CLIENT_SECRET"]
        token_url = current_app.config["FITBIT_TOKEN_URL"]

        # Fitbit requires client ID and client secret as basic auth in header.
        auth_str = base64.urlsafe_b64encode(
            f"{client_id}:{client_secret}".encode("utf-8")
        ).decode("utf-8")

        oauth_session = OAuth2Session(
            client_id,
            state=request.parsed_obj["state"],
            redirect_uri=request.parsed_obj["redirect_uri"],
        )
        try:
            oauth_reply = oauth_session.fetch_token(
                token_url,
                code=request.parsed_obj["code"],
                include_client_id=True,
                client_secret=client_secret,
                headers={"Authorization": f"Basic {auth_str}"},
            )
        except Exception as e:
            raise BadRequest(f"Error while exchanging grant code for access token: {e}")

        # Fitbit sends errors in body with a 200 response.
        if not oauth_reply.get("success", True):
            msg = oauth_reply["errors"][0]["message"]
            raise BadRequest(f"fitbit.com returned error: {msg}")

        # Not requiring location, settings, or social
        minimal_scope = set(current_app.config["FITBIT_SCOPE"].split())
        scope = set(oauth_reply.get("scope", []))

        if scope.intersection(minimal_scope) != minimal_scope:
            msg = "You must agree to share at least: {}.".format(
                ", ".join(minimal_scope)
            )
            raise BadRequest(msg)

        # Everything was successful
        fitbit.access_token = oauth_reply["access_token"]
        fitbit.refresh_token = oauth_reply["refresh_token"]
        fitbit.token_expires = datetime.utcnow() + timedelta(
            seconds=oauth_reply["expires_in"]
        )
        fitbit.oauth_state = None
        fitbit.wearable.has_fitbit = True
        fitbit.wearable.registered_fitbit = True

        db.session.commit()

    @token_auth.login_required(user_type=("client",))
    @responds(status_code=204, api=ns)
    def delete(self, user_id):
        """Revoke Fitbit OAuth2 data sharing permissions.

        Parameters
        ----------
        user_id : str
            Modo Bio user ID.
        """
        fitbit = WearablesFitbit.query.filter_by(user_id=user_id).one_or_none()

        if fitbit:
            fitbit.access_token = None
            fitbit.refresh_token = None
            fitbit.wearable.registered_fitbit = False
            db.session.commit()


@ns.route("/freestyle/activate/<int:user_id>/")
@ns.doc(params={"user_id": "User ID number"})
class WearablesFreeStyleActivateEndpoint(BaseResource):
    @token_auth.login_required(user_type=("client",))
    @responds(schema=WearablesFreeStyleActivateSchema, status_code=200, api=ns)
    def get(self, user_id):
        """Returns CGM activation timestamp for client ``user_id`` in reponse to a GET request.

        Time data on the CGM sensor is stored as minutes since activation and as full
        timestamps in the database. Time data must be converted before it can be
        uploaded to the database, using the activation timestamp retrieved in this GET
        request.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        str
            JSON encoded, ISO 8601 formatted datetime string.
        """
        cgm = WearablesFreeStyle.query.filter_by(user_id=user_id).one_or_none()

        return cgm

    @token_auth.login_required(user_type=("client",))
    @accepts(schema=WearablesFreeStyleActivateSchema, api=ns)
    @responds(status_code=201, api=ns)
    def post(self, user_id):
        """Set new activation timestamp for client ``user_id`` in response to POST request.

        When a new CGM is activated, the activation timestamp must be stored in the database.

        Parameters
        ----------
        user_id : int
            User ID number.

        timestamp : str
            ISO 8601 formatted datetime string.
        """
        cgm = WearablesFreeStyle.query.filter_by(user_id=user_id).one_or_none()

        if not cgm:
            info = Wearables.query.filter_by(user_id=user_id).one_or_none()
            if not info:
                info = Wearables(user_id=user_id)
                db.session.add(info)
                db.session.flush()

            cgm = WearablesFreeStyle(
                user_id=user_id, wearable_id=info.idx, wearable=info
            )
            db.session.add(cgm)

        cgm.activation_timestamp = request.parsed_obj.activation_timestamp
        cgm.wearable.has_freestyle = True
        cgm.wearable.registered_freestyle = True
        db.session.commit()


@ns.route("/freestyle/<int:user_id>/")
@ns.doc(params={"user_id": "User ID number"})
class WearablesFreeStyleEndpoint(BaseResource):
    @token_auth.login_required(user_type=("client",))
    @responds(schema=WearablesFreeStyleSchema, status_code=200, api=ns)
    def get(self, user_id):
        """Return FreeStyle CGM data for client ``user_id`` in reponse to a GET request.

        Parameters
        ----------
        user_id : int
            User ID number.

        Returns
        -------
        str
            JSON encoded dictionary
        """
        cgm = WearablesFreeStyle.query.filter_by(user_id=user_id).one_or_none()

        return cgm

    @token_auth.login_required(user_type=("client",))
    @accepts(schema=WearablesFreeStyleSchema, api=ns)
    @responds(status_code=204, api=ns)
    def patch(self, user_id):
        """Add CGM data for client ``user_id`` in reponse to a PATCH request.

        Parameters
        ----------
        user_id : int
            User ID number.
        """
        cgm = WearablesFreeStyle.query.filter_by(user_id=user_id).one_or_none()

        if not cgm:
            msg = (
                f"FreeStyle Libre for client {user_id} has not yet been" " activated. "
            )
            msg += f"Send a POST request to /wearables/freestyle/activate/ first."
            raise BadRequest(msg)

        if cgm.activation_timestamp != request.parsed_obj.activation_timestamp:
            msg = (
                "Activation timestamp"
                f" {request.parsed_obj.activation_timestamp} does not "
            )
            msg += "match current activation timestamp" f" {cgm.activation_timestamp}. "
            msg += f"Send a GET request to /wearables/freestyle/activate/ first."
            raise BadRequest(msg)

        tstamps = request.parsed_obj.timestamps
        glucose = request.parsed_obj.glucose

        if len(tstamps) != len(glucose):
            raise BadRequest("Data arrays not equal length.")

        if not tstamps:
            return

        if len(tstamps) != len(set(tstamps)):
            raise BadRequest("Duplicate timestamps in data.")

        # Sort data
        if tstamps != sorted(tstamps):
            temp = sorted(zip(tstamps, glucose))
            tstamps = []
            glucose = []
            for t, g in temp:
                formatted_timestamp = parser.parse(t).replace(tzinfo=None).isoformat()
                tstamps.append(formatted_timestamp)
                glucose.append(g)

        # Find index where new data starts
        n = 0
        if cgm.timestamps:
            while n < len(tstamps) and tstamps[n] <= cgm.timestamps[-1]:
                n += 1

        # No new data
        if n == len(tstamps):
            return

        # Concatenate new array values to previous values, removing duplicates.
        # {array_name}.copy() is used here because sqlalchemy ARRAY fields are
        # immutable, so we need to make a new copy of the previous values in order
        # to concatenate the new values and remove the duplicates
        if cgm.glucose:
            glucose_copy = cgm.glucose.copy()
            glucose_copy.extend(x for x in glucose[n:] if x not in glucose_copy)
            glucose_update = glucose_copy
        else:
            glucose_update = glucose[n:]

        if cgm.timestamps:
            tstamps_copy = cgm.timestamps.copy()
            tstamps_copy.extend(x for x in tstamps[n:] if x not in tstamps_copy)
            tstamps_update = tstamps_copy
        else:
            tstamps_update = tstamps[n:]

        cgm.update(dict(glucose=glucose_update, timestamps=tstamps_update))
        db.session.commit()


@ns.route("/data/<string:device_type>/<int:user_id>/")
@ns.doc(
    params={
        "user_id": "User ID number",
        "device_type": "fitbit, applewatch, oura, freestyle",
        "start_date": "(optional) iso formatted date. start of date range",
        "end_date": "(optional) iso formatted date. end of date range",
    }
)
class WearablesData(BaseResource):
    @token_auth.login_required(
        user_type=("client", "staff"), resources=("wearable_data",)
    )
    @responds(status_code=200, api=ns)
    def get(self, user_id, device_type):
        """Retrieve wearables data from dynamodb.

        Parameters
        ----------
        user_id : int
            User ID number

        device_type : str
            only the data from one device per request.

        Returns
        -------
        dict
            The requested wearables data.
        """

        # connect to dynamo
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(current_app.config["WEARABLES_DYNAMO_TABLE"])

        # validate device_type request
        if device_type not in WEARABLE_DEVICE_TYPES:
            raise BadRequest(f"wearable device type, {device_type}, not supported")

        # configure date range expression
        # Four cases:
        #   - both start and end date provided: return data for date range
        #   - only start date specified: return start_date + WEARABLE_DATA_DEFAULT_RANGE_DAYS
        #   - only end date specified: return end_date - WEARABLE_DATA_DEFAULT_RANGE_DAYS
        #   - no dates specified: return last WEARABLE_DATA_DEFAULT_RANGE_DAYS days of data
        start_date = (
            date_validator(request.values.get("start_date"))
            if request.values.get("start_date")
            else None
        )
        end_date = (
            date_validator(request.values.get("end_date"))
            if request.values.get("end_date")
            else None
        )
        if start_date and end_date:
            date_condition = Key("date").between(start_date, end_date)
        elif start_date:
            end_date = (
                (
                    datetime.fromisoformat(start_date)
                    + timedelta(
                        days=current_app.config["WEARABLE_DATA_DEFAULT_RANGE_DAYS"]
                    )
                )
                .date()
                .isoformat()
            )
            date_condition = Key("date").between(start_date, end_date)
        elif end_date:
            start_date = (
                (
                    datetime.fromisoformat(end_date)
                    - timedelta(
                        days=current_app.config["WEARABLE_DATA_DEFAULT_RANGE_DAYS"]
                    )
                )
                .date()
                .isoformat()
            )
            date_condition = Key("date").between(start_date, end_date)
        else:
            start_date = (
                (
                    datetime.now()
                    - timedelta(
                        days=current_app.config["WEARABLE_DATA_DEFAULT_RANGE_DAYS"]
                    )
                )
                .date()
                .isoformat()
            )
            end_date = datetime.now().date().isoformat()
            date_condition = Key("date").gte(start_date)

        # make reqeust for data
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id) & date_condition,
            FilterExpression=Key("wearable").eq(device_type),
        )

        payload = {
            "start_date": start_date,
            "end_date": end_date,
            "total_items": len(response.get("Items", [])),
            "items": [],
        }

        # only provide the data that is required
        payload["items"] = response.get("Items", [])

        return jsonify(payload)


#########################
#
# V2 of the Wearables API
#
#########################

# V2 is the terra integration. It is namespaced into v2, which will eventually be
# the v2/ prefix for the entire API once we reach v2.0.0. Once that is reached,
# fold this v2 into that.
#

import requests
import terra
from terra.api.api_responses import (
    HOOK_RESPONSE,
    HOOK_TYPES,
    USER_DATATYPES,
    ConnectionErrorHookResponse,
    RequestCompletedHookResponse,
    RequestProcessingHookResponse,
)

ns_v2 = Namespace(
    "wearables", description="Endpoints for registering wearable devices."
)

# Fix mistakes in terra-python wrappers:
# - misspelled connexion_error instead of connection_error (v0.0.7)
# - request_processing was replaced by large_request_processing (v0.0.7)
# - request_completed was replaced by large_request_sending (v0.0.7)
# - permission_change is undocumented, seems come be in response to scope change (v0.0.7)
HOOK_TYPES.add("connection_error")
HOOK_RESPONSE["connection_error"] = ConnectionErrorHookResponse

HOOK_TYPES.add("large_request_processing")
HOOK_RESPONSE["large_request_processing"] = RequestProcessingHookResponse

HOOK_TYPES.add("large_request_sending")
HOOK_RESPONSE["large_request_sending"] = RequestCompletedHookResponse

HOOK_TYPES.add("permission_change")

MIDNIGHT = time(0)
ONE_WEEK = timedelta(weeks=1)
THIRTY_DAYS = timedelta(days=30)
WAY_BACK_WHEN = datetime(2010, 1, 1)

WEBHOOK_RESPONSES = HOOK_TYPES.copy()
WEBHOOK_RESPONSES.update(set(USER_DATATYPES))


@lru_cache_with_ttl(maxsize=1, ttl=86400)
def supported_wearables() -> dict:
    """Get the list of supported wearables from Terra.

    Terra's API provides a list of supported wearable devices. This function fetches that
    list and caches the result. It is updated once per day.

    The wearable devices are split into two lists, "providers" (web API based devices) and
    "sdk_providers" (SDK based devices). Each entry has an enum name (used in the API) and
    a display name.

    The display names are generated from the enum names, with an exception list for those
    cases where simply lower-casing is not sufficient. By having a "default translation"
    from enum name to display name plus a list of exceptions, any newly supported devices
    returned from Terra's API are automatically included. Exceptions can later be added
    to the list.

    Returns
    -------
    dict
        Dictionary with two keys "providers" and "sdk_providers". The values are dictionaries
        with enum names as keys and display names as values.
    """
    tc = TerraClient()
    response = tc.list_providers()
    tc.status(response, raise_on_error=False)

    # List of display names that cannot be generated by simply capitalizing the enum names.
    exceptions = {
        "APPLE": "Apple HealthKit",
        "CONCEPT2": "Concept 2",
        "EIGHT": "Eight Sleep",
        "FREESTYLELIBRE": "Freestyle Libre",
        "FREESTYLELIBRESDK": "Freestyle Libre (SDK)",
        "GOOGLE": "Google Fit",
        "GOOGLEFIT": "Google Fit (SDK)",
        "IFIT": "iFit",
        "OMRONUS": "Omron",
        "TEMPO": "Tempo Fit",
        "TRAININGPEAKS": "Training Peaks",
        "WEAROS": "Wear OS",
    }

    # These devices are not supported at the moment.
    # That's a business decision, there is no technical reason not to support them.
    # Simply remove them from this list to start supporting them.
    suppressed = {
        "BIOSTRAP",
        "BRYTONSPORT",
        "CARDIOMOOD",
        "CONCEPT2",
        "CRONOMETER",
        "CYCLINGANALYTICS",
        "EATTHISMUCH",
        "EIGHT",
        "FATSECRET",
        "FINALSURGE",
        "FREESTYLELIBRESDK",
        "HAMMERHEAD",
        "HUAWEI",
        "IFIT",
        "INBODY",
        "KETOMOJOEU",
        "KETOMOJOUS",
        "KOMOOT",
        "LEZYNE",
        "LIVEROWING",
        "MOXY",
        "MYFITNESSPAL",
        "NOLIO",
        "NUTRACHECK",
        "OMRON",
        "PELOTON",
        "PUL",
        "REALTIME",
        "RENPHO",
        "RIDEWITHGPS",
        "ROUVY",
        "STRAVA",
        "TECHNOGYM",
        "TEMPO",
        "TODAYSPLAN",
        "TRAINASONE",
        "TRAINERROAD",
        "TRAININGPEAKS",
        "TRAINXHALE",
        "TREDICT",
        "TRIDOT",
        "UNDERARMOUR",
        "VELOHERO",
        "VIRTUAGYM",
        "WAHOO",
        "WEAROS",
        "WGER",
        "WHOOP",
        "XERT",
        "XOSS",
        "ZWIFT",
    }

    result = {}
    for provider_type in ("providers", "sdk_providers"):
        subresult = {}
        for provider in getattr(response.parsed_response, provider_type):
            if provider in suppressed:
                continue
            if provider in exceptions:
                subresult[provider] = exceptions[provider]
            else:
                subresult[provider] = provider.capitalize()
        result[provider_type] = subresult

    return result


def parse_wearable(wearable: str) -> str:
    """Parse wearable path parameter.

    Clean up path parameter and check against list of supported devices.
    Cleaning up consists of converting to all-caps and removing spaces.

    Parameters
    ----------
    wearable : str
        Name of the wearable.

    Returns
    -------
    str
        Name of the wearable "cleaned up". Cleaning up consists of converting to
        all-caps and removing spaces.

    Raises
    ------
    :class:`werkzeug.exceptions.BadRequest`
        Raised when the wearable (after cleaning up), is not found in the list
        of supported wearable devices, see :func:`supported_wearables`.
    """
    wearable_clean = wearable.upper().replace(" ", "")
    supported = supported_wearables()
    if (
        wearable_clean in supported["providers"]
        or wearable_clean in supported["sdk_providers"]
    ):
        return wearable_clean
    raise BadRequest(f"Unknown wearable {wearable}")


@ns_v2.route("")
class WearablesV2Endpoint(BaseResource):
    @token_auth.login_required
    @responds(schema=WearablesV2ProvidersGetSchema, api=ns_v2)
    def get(self):
        """Get a list of all supported wearable devices."""
        return {
            "providers": {
                "COROS": "Coros",
                "DEXCOM": "Dexcom",
                "FITBIT": "Fitbit",
                "FREESTYLELIBRE": "Freestyle Libre",
                "GARMIN": "Garmin",
                "GOOGLE": "Google Fit",
                "OMRONUS": "Omron",
                "OURA": "Oura",
                "POLAR": "Polar",
                "SUUNTO": "Suunto",
                "WITHINGS": "Withings",
            },
            "sdk_providers": {
                "GOOGLEFIT": "Google Fit (SDK)",
                "APPLE": "Apple HealthKit",
                "SAMSUNG": "Samsung",
            },
        }


@ns_v2.route("/<int:user_id>")
class WearablesV2UserEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "provider"), resources=("wearable_data",)
    )
    @responds(schema=WearablesV2UserGetSchema, status_code=200, api=ns_v2)
    def get(self, user_id):
        """Get a list of wearable devices registered to this user."""
        # user_id = self.check_user(uid, user_type='client').user_id

        wearables = (
            db.session.execute(select(WearablesV2.wearable).filter_by(user_id=user_id))
            .scalars()
            .all()
        )

        return {"wearables": wearables}


@ns_v2.route("/<int:user_id>/<wearable>")
class WearablesV2DataEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "provider"), resources=("wearable_data",)
    )
    @ns_v2.doc(
        params={
            "start_date": (
                "Start of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp."
            ),
            "end_date": (
                "End of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp."
            ),
            "query_specification": (
                "Specifies the wearable data fields that gets returned. Parsed"
                " as a array. Use the same key to pass multiple values."
            ),
        }
    )
    @responds(schema=WearablesV2UserDataGetSchema, status_code=200, api=ns_v2)
    def get(self, user_id, wearable):
        """
        Gets the wearable data stored for an user.
        Allows to specify the specific fields of data to be returned.

        Path Parameters
        ---------------
        user_id : int
            User ID number.
        wearable: str
            wearable used to measure blood glucose data

        Query Parameters
        ----------------
        start_date : str
            Start of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date - 7 days if not specified
        end_date: str
            End of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date if not specified
        query_specification: str
            The specific field or object in the 'data' object to be returned. Ex. (data.daily.heart_rate_data)
            Request multiple values by using multiple 'query_specification' params along with the value.

        Returns
        -------
        dict
        """

        wearable = parse_wearable(wearable)

        # Gets start and end date ranges. Defaults to one week if one or none is provided
        start_date, end_date = date_range(
            start_time=request.args.get("start_date"),
            end_time=request.args.get("end_date"),
            time_range=timedelta(weeks=1),
        )

        query_specification = request.args.getlist("query_specification", str)
        query = create_wearables_filter_query(
            user_id, wearable, start_date, end_date, query_specification
        )
        data = mongo.db.wearables.find(query[0], projection=query[1])

        return {"results": list(data)}

    @token_auth.login_required(user_type=("client",))
    @accepts(schema=WearablesV2UserAuthUrlInputSchema, api=ns_v2)
    @responds(schema=WearablesV2UserAuthUrlSchema, status_code=201, api=ns_v2)
    def post(self, user_id, wearable):
        """Register a new wearable device for this user."""
        # user_id = self.check_user(uid, user_type='client').user_id
        wearable = parse_wearable(wearable)

        # API based providers
        if wearable in supported_wearables()["providers"]:
            # For local testing, set the redirect urls to something like http://localhost/xyz
            # When you copy the URL into a browser and allow access, Terra will redirect back
            # to localhost. It will give an error in the browser, but the URL in the address
            # bar will have all the relevant information.

            # These URL schemes are registered with Apple and Google.
            # TODO: remove this when the following paths are verified to work
            # redirect_url_scheme = 'com.modobio.ModoBioClient'
            # if request.parsed_obj['platform'] == 'android':
            #     # Somebody was not paying attention when registering for Android.
            #     redirect_url_scheme = redirect_url_scheme.lower()

            # TODO: when frontend adds success and failure views, fill in these paths
            success_path = "modobio://setup_success"
            failure_path = "modobio://setup_failure"

            tc = TerraClient()
            response = tc.generate_authentication_url(
                resource=wearable,
                auth_success_redirect_url=success_path,
                auth_failure_redirect_url=failure_path,
                reference_id=user_id,
            )
            tc.status(response)

            # Not stored in the database at this point.
            # Registration is only complete when client follows the link to the provider.
            # The response of that action comes in through the webhook and will be stored.

            return response.parsed_response

        # SDK based providers
        else:
            # Functionality not in terra-python (v0.0.7), use requests.
            url = f"{terra.constants.BASE_URL}/auth/generateAuthToken"
            headers = {
                "accept": "application/json",
                "dev-id": current_app.config["TERRA_DEV_ID"],
                "x-api-key": current_app.config["TERRA_API_KEY"],
            }

            response = requests.post(url, headers=headers)
            response_json = response.json()

            status = response_json.pop("status", "error")
            if status != "success":
                raise BadRequest(f"Terra replied: {response_json}")

            # Same as for API based providers, nothing stored in the database at this point.
            # Registration is only complete when frontend calls initConnection() with token.
            # The response of that action comes in through the webhook and will be stored.

            return response_json

    @token_auth.login_required(user_type=("client",))
    @responds(status_code=204, api=ns_v2)
    def delete(self, user_id, wearable):
        """Revoke access for this wearable device."""
        # user_id = self.check_user(uid, user_type='client').user_id
        wearable = parse_wearable(wearable)

        user_wearable = db.session.get(WearablesV2, (user_id, wearable))

        # Don't error on non-existant users, delete is idempotent
        if not user_wearable:
            logger.debug(
                f"Nothing to delete for user {user_id} and wearable {wearable}"
            )
            return

        deauthenticate_terra_user(user_id, wearable_obj=user_wearable, delete_data=True)


@ns_v2.route("/sync/<int:user_id>")
class WearablesV2ResyncEndpoint(BaseResource):
    @ns_v2.doc(params={"wearable": "The wearable device to resync"})
    @token_auth.login_required(
        user_type=("client", "staff"), staff_role=("community_manager",)
    )
    @responds(status_code=200, api=ns_v2)
    def get(self, user_id):
        """
        Resync data for a wearable device.

        If no wearable is specified, resync all wearables for this user.
        A resync will first request all data from the last 7 days and
        then request data from WAY_BACK_WHEN up to 7 days ago.
        Each wearable can be resynced once every 24 hours.

        Parameters
        ----------
        user_id : int
            The user ID of the user to resync data for.

        Query Parameters
        ----------------
        wearable : str, optional
            The wearable device to resync. If not specified, all wearables
        """

        wearables_query = WearablesV2().query.filter_by(user_id=user_id)

        if "wearable" in request.args:
            wearable = parse_wearable(request.args["wearable"])
            wearables_query = wearables_query.filter_by(wearable=wearable)

        wearables = wearables_query.all()

        tc = TerraClient()

        now = datetime.utcnow()
        twenty_four_hours_ago = now - timedelta(hours=24)
        seven_days_ago = now - timedelta(days=7)

        for wearable in wearables:
            if (
                wearable.last_sync_date != None
                and wearable.last_sync_date > twenty_four_hours_ago
            ):
                continue

            terra_user = tc.from_user_id(wearable.terra_user_id)
            tc.get_terra_data(terra_user, seven_days_ago, now)
            tc.get_terra_data(terra_user, WAY_BACK_WHEN, seven_days_ago)
            wearable.last_sync_date = datetime.utcnow()
            db.session.commit()

        return


@ns_v2.route("/terra")
class WearablesV2TerraWebHookEndpoint(BaseResource):
    @accepts(api=ns_v2)
    def post(self):
        """Webhook for incoming notifications from Terra."""
        # Override JSON handling for this request.
        request.json_module = JSONProvider()

        tc = TerraClient()

        # For testing without TERRA_API_SECRET or the need to sign every request,
        # use the next line instead of the try-except block.
        # response = terra.api.api_responses.TerraWebhookResponse(request.get_json(), dtype='hook')

        try:
            response = tc.handle_flask_webhook(request)
        except KeyError:
            # This happens when terra-signature is not present in the request header.
            raise Unauthorized

        if not response:
            # This happens when terra-signature was present in the header, but wrong.
            # Most likely because TERRA_API_SECRET does not match.
            raise Unauthorized

        tc.status(response, raise_on_error=False)

        if response.dtype not in WEBHOOK_RESPONSES:
            logger.error(
                f'Terra webhook response with unknown type "{response.dtype}".'
                f" Full message: {response.json}"
            )
        elif response.dtype == "auth":
            # Completion of new wearable registration for user,
            # or reauthentication by existing user.
            tc.auth_response(response)
        elif response.dtype == "user_reauth":
            # Terra sends both auth and user_reauth in response
            # to reauthentication. Only need one, ignore this one.
            pass
        elif response.dtype == "permission_change":
            # Undocumented response. Seems to be in response to OAuth scope change.
            pass
        elif response.dtype == "deauth":
            # User revoked access through our API. Nothing else to do.
            pass
        elif response.dtype in ("access_revoked", "connection_error"):
            # User revoked access through wearable provider.
            tc.access_revoked_response(response)
        elif response.dtype == "google_no_datasource":
            # uh, ok
            pass
        elif response.dtype in (
            "request_processing",
            "request_completed",
            "large_request_processing",
            "large_request_sending",
        ):
            # Terra is letting us know that they're working on it. Great.
            pass
        elif response.dtype in USER_DATATYPES:
            tc.store_data(response)


@ns_v2.route("/calculations/blood-glucose/<int:user_id>/<string:wearable>")
class WearablesV2BloodGlucoseCalculationEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "provider"), resources=("wearable_data",)
    )
    @ns_v2.doc(
        params={
            "start_date": (
                "Start of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
            "end_date": (
                "End of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
        }
    )
    @responds(
        schema=WearablesV2BloodGlucoseCalculationOutputSchema,
        status_code=200,
        api=ns_v2,
    )
    def get(self, user_id, wearable):
        """Get calculated values related to blood glucose wearable data.

        This route will return all calculated values related to blood glucose data for a particular user_id, wearable, and timestamp range.

        Path Parameters
        ----------
        user_id : int
            User ID number.
        wearable: str
            wearable used to measure blood glucose data

        Query Parameters
        ----------
        start_date : str
            Start of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date - 7 days if not specified
        end_date: str
            End of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date if not specified

        Returns
        -------
        dict
            JSON encoded dict containing:
            - user_id
            - wearable
            - average_glucose - mg/dL
            - standard_deviation
            - glucose_management_indicator - percentage
            - glucose_variability - percentage
        """

        wearable = parse_wearable(wearable)

        # Default dates
        end_date = datetime.utcnow()
        start_date = end_date - ONE_WEEK

        if request.args.get("start_date") and request.args.get("end_date"):
            start_date = iso_string_to_iso_datetime(request.args.get("start_date"))
            end_date = iso_string_to_iso_datetime(request.args.get("end_date"))
        elif request.args.get("start_date") or request.args.get("end_date"):
            raise BadRequest("Provide both or neither start_date and end_date.")

        # Calculate Average Glucose
        # Begin with defining each stage of the pipeline

        # Filter documents on user_id, wearable, and date range
        stage_match_user_id_and_wearable = {
            "$match": {
                "user_id": user_id,
                "wearable": wearable,
                "timestamp": {
                    "$gte": start_date - timedelta(days=1),
                    "$lte": end_date,
                },
            }
        }

        # Unwind the blood_glucose_samples array so that we can operate on each individual sample
        stage_unwind_blood_glucose_samples = {
            "$unwind": "$data.body.glucose_data.blood_glucose_samples"
        }

        # Filter on the timestamp of each blood glucose sample
        stage_match_date_range = {
            "$match": {
                "data.body.glucose_data.blood_glucose_samples.timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                }
            }
        }

        # Group all of these documents together and calculate average glucose and standard deviation for the group
        stage_group_average_and_std_dev = {
            "$group": {
                "_id": None,
                "average_glucose": {
                    "$avg": "$data.body.glucose_data.blood_glucose_samples.blood_glucose_mg_per_dL"
                },
                "standard_deviation": {
                    "$stdDevSamp": "$data.body.glucose_data.blood_glucose_samples.blood_glucose_mg_per_dL"
                },
            }
        }

        # Add field for GMI and calculate it. Calculated as 3.31 + 0.02392 x (mean glucose in mg/dL)
        stage_add_gmi = {
            "$addFields": {
                "glucose_management_indicator": {
                    "$add": [
                        {"$multiply": ["$average_glucose", 0.02392]},
                        3.31,
                    ]
                }
            }
        }

        # Add field for glucose variability and calculate it. Calculated as 100 * (Standard Deviation / Mean Glucose)
        stage_add_glucose_variability = {
            "$addFields": {
                "glucose_variability": {
                    "$multiply": [
                        100,
                        {
                            "$divide": [
                                "$standard_deviation",
                                "$average_glucose",
                            ]
                        },
                    ]
                }
            }
        }

        # Round values
        stage_round_values = {
            "$project": {
                "average_glucose": {"$round": ["$average_glucose", 0]},
                "standard_deviation": {"$round": ["$standard_deviation", 1]},
                "glucose_management_indicator": {
                    "$round": ["$glucose_management_indicator", 1]
                },
                "glucose_variability": {"$round": ["$glucose_variability", 1]},
            }
        }

        # Assemble pipeline
        pipeline = [
            stage_match_user_id_and_wearable,
            stage_unwind_blood_glucose_samples,
            stage_match_date_range,
            stage_group_average_and_std_dev,
            stage_add_gmi,
            stage_add_glucose_variability,
            stage_round_values,
        ]

        # MongoDB pipelines return a cursor
        cursor = mongo.db.wearables.aggregate(pipeline)
        document_list = list(cursor)
        data = {}

        # We need to grab the document that we want from that cursor so we can format the data in a payload
        if document_list:
            data = document_list[0]

        # Build and return payload
        payload = {
            "user_id": user_id,
            "wearable": wearable,
            "average_glucose": data.get("average_glucose"),
            "standard_deviation": data.get("standard_deviation"),
            "glucose_management_indicator": data.get("glucose_management_indicator"),
            "glucose_variability": data.get("glucose_variability"),
        }

        return payload


@ns_v2.route(
    "/calculations/blood-glucose/cgm/time-in-ranges/<int:user_id>/<string:wearable>"
)
class WearablesV2BloodGlucoseTimeInRangesCalculationsEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "provider"), resources=("wearable_data",)
    )
    @ns_v2.doc(
        params={
            "start_date": (
                "Start of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
            "end_date": (
                "End of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
        }
    )
    @responds(
        schema=WearablesV2BloodGlucoseTimeInRangesOutputSchema,
        status_code=200,
        api=ns_v2,
    )
    def get(self, user_id, wearable):
        """
        Calculates time in ranges for CGM data for a specified date range.

        Path Parameters
        ---------------
        user_id : int
            User ID number.
        wearable: str
            wearable used to measure blood glucose data

        Query Parameters
        ----------------
        start_date : str
            Start of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date - 7 days if not specified
        end_date: str
            End of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date if not specified

        Returns
        -------
        dict
        """
        payload = {}
        wearable = parse_wearable(wearable)

        # Gets start and end dates ranges. Defaults to 30 days if one or none is provided
        start_date, end_date = date_range(
            start_time=request.args.get("start_date"),
            end_time=request.args.get("end_date"),
            time_range=timedelta(days=30),
        )

        # Filter documents on user_id, wearable
        stage_match_user_id_and_wearable = {
            "$match": {
                "user_id": user_id,
                "wearable": wearable,
                "timestamp": {
                    "$gte": start_date - timedelta(days=1),
                    "$lte": end_date,
                },
            }
        }

        # Project out glucose samples to filter start and end time precisely on samples timestamps
        stage_project_bp_samples = {
            "$project": {
                "_id": 0,
                "samples": "$data.body.glucose_data.blood_glucose_samples",
            }
        }
        # Unwind the blood_glucose_samples array so that we can operate on each individual sample
        stage_unwind_bp_samples = {"$unwind": {"path": "$samples"}}

        # Filter on the timestamp of each blood glucose sample
        stage_match_date_range_bp_samples = {
            "$match": {"samples.timestamp": {"$gte": start_date, "$lte": end_date}}
        }

        # Runs multiple stages. Groups samples in buckets by glucose range,
        # gets the total count of glucose samples, and creates array of just
        # samples timestamps.
        stage_facet = {
            "$facet": {
                "samples_buckets": [
                    {
                        "$bucket": {
                            "groupBy": "$samples.blood_glucose_mg_per_dL",
                            "boundaries": [0, 54, 70, 181, 251, 10000],
                            "output": {"count": {"$sum": 1}},
                        }
                    }
                ],
                "total_count": [{"$count": "total_count"}],
                "reading_timestamps": [
                    {"$project": {"timestamp": "$samples.timestamp"}}
                ],
            }
        }

        # In case there are buckets that dont get filled from samples, this stage aligns the arrays
        # so that there are always the same number of buckets to make calculations from.
        # Also carries over the ID and count of any previously filled buckets
        stage_align_buckets = {
            "$addFields": {
                "samples_buckets": {
                    "$map": {
                        "input": [0, 54, 70, 181, 251],
                        "as": "i",
                        "in": {
                            "_id": "$$i",
                            "count": {
                                "$cond": [
                                    {
                                        "$eq": [
                                            {
                                                "$indexOfArray": [
                                                    "$samples_buckets._id",
                                                    "$$i",
                                                ]
                                            },
                                            -1,
                                        ]
                                    },
                                    0,
                                    {
                                        "$arrayElemAt": [
                                            "$samples_buckets.count",
                                            {
                                                "$indexOfArray": [
                                                    "$samples_buckets._id",
                                                    "$$i",
                                                ]
                                            },
                                        ]
                                    },
                                ]
                            },
                        },
                    }
                }
            }
        }

        # Projects facet data to new document.
        # Sorts samples buckets and samples timestamps in accending order.
        stage_project_facet_data = {
            "$project": {
                "samples_sorted": {
                    "$sortArray": {"input": "$samples_buckets", "sortBy": 1}
                },
                "timestamp_sorted": {
                    "$sortArray": {"input": "$reading_timestamps", "sortBy": 1}
                },
                "total_samples": "$total_count",
            }
        }

        # Starts calculations get percentages of total time in glucose ranges
        stage_calculate_percentages = {
            "$addFields": {
                "total_time_in_min": {
                    "$dateDiff": {
                        "startDate": {
                            "$arrayElemAt": ["$timestamp_sorted.timestamp", 0]
                        },
                        "endDate": {
                            "$arrayElemAt": ["$timestamp_sorted.timestamp", -1]
                        },
                        "unit": "minute",
                    }
                },
                "very_low_percentage": {
                    "$round": [
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {
                                            "$arrayElemAt": [
                                                "$samples_sorted.count",
                                                0,
                                            ]
                                        },
                                        {
                                            "$arrayElemAt": [
                                                "$total_samples.total_count",
                                                0,
                                            ]
                                        },
                                    ]
                                },
                                100,
                            ]
                        },
                        0,
                    ]
                },
                "low_percentage": {
                    "$round": [
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {
                                            "$arrayElemAt": [
                                                "$samples_sorted.count",
                                                1,
                                            ]
                                        },
                                        {
                                            "$arrayElemAt": [
                                                "$total_samples.total_count",
                                                0,
                                            ]
                                        },
                                    ]
                                },
                                100,
                            ]
                        },
                        0,
                    ]
                },
                "target_range_percentage": {
                    "$round": [
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {
                                            "$arrayElemAt": [
                                                "$samples_sorted.count",
                                                2,
                                            ]
                                        },
                                        {
                                            "$arrayElemAt": [
                                                "$total_samples.total_count",
                                                0,
                                            ]
                                        },
                                    ]
                                },
                                100,
                            ]
                        },
                        0,
                    ]
                },
                "high_percentage": {
                    "$round": [
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {
                                            "$arrayElemAt": [
                                                "$samples_sorted.count",
                                                3,
                                            ]
                                        },
                                        {
                                            "$arrayElemAt": [
                                                "$total_samples.total_count",
                                                0,
                                            ]
                                        },
                                    ]
                                },
                                100,
                            ]
                        },
                        0,
                    ]
                },
                "very_high_percentage": {
                    "$round": [
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {
                                            "$arrayElemAt": [
                                                "$samples_sorted.count",
                                                4,
                                            ]
                                        },
                                        {
                                            "$arrayElemAt": [
                                                "$total_samples.total_count",
                                                0,
                                            ]
                                        },
                                    ]
                                },
                                100,
                            ]
                        },
                        0,
                    ]
                },
            }
        }

        # Finally use calculated percentages to calculate total time in minutes
        stage_project_total_percentages_and_times = {
            "$project": {
                "very_low_percentage": "$very_low_percentage",
                "low_percentage": "$low_percentage",
                "target_range_percentage": "$target_range_percentage",
                "high_percentage": "$high_percentage",
                "very_high_percentage": "$very_high_percentage",
                "very_low_total_time": {
                    "$round": [
                        {
                            "$multiply": [
                                {"$divide": ["$very_low_percentage", 100]},
                                "$total_time_in_min",
                            ]
                        }
                    ]
                },
                "low_total_time": {
                    "$round": [
                        {
                            "$multiply": [
                                {"$divide": ["$low_percentage", 100]},
                                "$total_time_in_min",
                            ]
                        }
                    ]
                },
                "target_range_total_time": {
                    "$round": [
                        {
                            "$multiply": [
                                {"$divide": ["$target_range_percentage", 100]},
                                "$total_time_in_min",
                            ]
                        }
                    ]
                },
                "high_total_time": {
                    "$round": [
                        {
                            "$multiply": [
                                {"$divide": ["$high_percentage", 100]},
                                "$total_time_in_min",
                            ]
                        }
                    ]
                },
                "very_high_total_time": {
                    "$round": [
                        {
                            "$multiply": [
                                {"$divide": ["$very_high_percentage", 100]},
                                "$total_time_in_min",
                            ]
                        }
                    ]
                },
            }
        }

        # Build pipeline
        time_in_ranges_pipeline = [
            stage_match_user_id_and_wearable,
            stage_project_bp_samples,
            stage_unwind_bp_samples,
            stage_match_date_range_bp_samples,
            stage_facet,
            stage_align_buckets,
            stage_project_facet_data,
            stage_calculate_percentages,
            stage_project_total_percentages_and_times,
        ]

        cursor = mongo.db.wearables.aggregate(time_in_ranges_pipeline)
        results = list(cursor)

        payload = {
            "user_id": user_id,
            "wearable": wearable,
            "results": results[0],
        }

        return payload


@ns_v2.route(
    "/calculations/blood-glucose/cgm/percentiles/<int:user_id>/<string:wearable>"
)
class WearablesV2BloodGlucoseCalculationEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "provider"), resources=("wearable_data",)
    )
    @ns_v2.doc(
        params={
            "start_date": (
                "Start of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
            "end_date": (
                "End of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
            "increment_mins": "bin sizes in minutes",
        }
    )
    @responds(
        schema=WearablesV2CGMPercentilesOutputSchema,
        status_code=200,
        api=ns_v2,
    )
    def get(self, user_id, wearable):
        """
        Calculates binned percentiles of CGM data for a specified date range. The glucose
        samples are grouped by time they are taken in a 24 hour day.

        Path Parameters
        ---------------
        user_id : int
            User ID number.
        wearable: str
            wearable used to measure blood glucose data

        Query Parameters
        ----------------
        start_date : str
            Start of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date - 7 days if not specified
        end_date: str
            End of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date if not specified

        Returns
        -------
        dict
        """

        wearable = parse_wearable(wearable)

        start_date, end_date = date_range(
            start_time=request.args.get("start_date"),
            end_time=request.args.get("end_date"),
            time_range=timedelta(weeks=2),
        )
        increments = request.args.get("increment_mins", 15, type=int)

        boundaries = [i * increments for i in range(ceil(1440 / increments) + 1)]
        boundaries[-1] = 1440  # last index must be 1440

        # Filter documents on user_id, wearable, and date range
        stage_1_match_user_id_and_wearable = {
            "$match": {
                "user_id": user_id,
                "wearable": wearable,
                "timestamp": {
                    "$gte": start_date - timedelta(days=1),
                    "$lte": end_date,
                },
            }
        }

        # bring just the glucose samples up
        stage_2_project_glucose_sample_only = {
            "$project": {
                "_id": 0,
                "samples": "$data.body.glucose_data.blood_glucose_samples",
            }
        }

        # unwind the samples
        stage_3_unwind = {"$unwind": "$samples"}

        # project the timestamp and glucose sample into their own fields
        stage_4_project_samples_parse_timestamp = {
            "$project": {
                "timestamp": "$samples.timestamp",
                "sample": "$samples.blood_glucose_mg_per_dL",
                "24hr_minute": {
                    "$add": [
                        {"$multiply": [{"$hour": "$samples.timestamp"}, 60]},
                        {"$minute": "$samples.timestamp"},
                    ]
                },
            }
        }

        # match on sample timestamp
        stage_5_match_on_samples = {
            "$match": {
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                }
            }
        }

        # bucket by minute in 24 hr day
        stage_6_bucket = {
            "$bucket": {
                "groupBy": "$24hr_minute",
                "boundaries": boundaries,
                "output": {
                    "count": {"$sum": 1},
                    "avg_glucose": {"$avg": "$sample"},
                    "samples": {"$push": "$sample"},
                },
            }
        }
        # sort samples in each bucket
        stage_7_sort_samples = {
            "$project": {
                "samplesSorted": {"$sortArray": {"input": "$samples", "sortBy": 1}},
                "count": {"$toInt": "$count"},
                "avg_glucose": 1,
            },
        }

        stage_8_calculate_percentiles = {
            "$project": {
                "minute": "$_id",
                "_id": 0,
                "count": 1,
                "avg_glucose_mg_per_dL": {"$round": ["$avg_glucose", 2]},
                "min": {"$round": [{"$arrayElemAt": ["$samplesSorted", 0]}, 2]},
                "max": {"$round": [{"$arrayElemAt": ["$samplesSorted", -1]}, 2]},
                "percentile_5th": {
                    "$round": [
                        {
                            "$arrayElemAt": [
                                "$samplesSorted",
                                {
                                    "$cond": {
                                        "if": {
                                            "$gt": [
                                                {
                                                    "$round": {
                                                        "$subtract": [
                                                            {
                                                                "$multiply": [
                                                                    "$count",
                                                                    0.05,
                                                                ]
                                                            },
                                                            1,
                                                        ]
                                                    }
                                                },
                                                0,
                                            ]
                                        },
                                        "then": {
                                            "$round": [
                                                {
                                                    "$subtract": [
                                                        {
                                                            "$multiply": [
                                                                "$count",
                                                                0.05,
                                                            ]
                                                        },
                                                        1,
                                                    ]
                                                },
                                                0,
                                            ]
                                        },
                                        "else": 0,
                                    }
                                },
                            ]
                        },
                        2,
                    ]
                },
                "percentile_25th": {
                    "$round": [
                        {
                            "$arrayElemAt": [
                                "$samplesSorted",
                                {
                                    "$cond": {
                                        "if": {
                                            "$gt": [
                                                {
                                                    "$round": {
                                                        "$subtract": [
                                                            {
                                                                "$multiply": [
                                                                    "$count",
                                                                    0.25,
                                                                ]
                                                            },
                                                            1,
                                                        ]
                                                    }
                                                },
                                                0,
                                            ]
                                        },
                                        "then": {
                                            "$round": [
                                                {
                                                    "$subtract": [
                                                        {
                                                            "$multiply": [
                                                                "$count",
                                                                0.25,
                                                            ]
                                                        },
                                                        1,
                                                    ]
                                                },
                                                0,
                                            ]
                                        },
                                        "else": 0,
                                    }
                                },
                            ]
                        },
                        2,
                    ]
                },
                "percentile_50th": {
                    "$round": [
                        {
                            "$arrayElemAt": [
                                "$samplesSorted",
                                {
                                    "$round": [
                                        {
                                            "$subtract": [
                                                {
                                                    "$multiply": [
                                                        "$count",
                                                        0.50,
                                                    ]
                                                },
                                                1,
                                            ]
                                        },
                                        0,
                                    ]
                                },
                            ]
                        },
                        2,
                    ]
                },
                "percentile_75th": {
                    "$round": [
                        {
                            "$arrayElemAt": [
                                "$samplesSorted",
                                {
                                    "$round": [
                                        {
                                            "$subtract": [
                                                {
                                                    "$multiply": [
                                                        "$count",
                                                        0.75,
                                                    ]
                                                },
                                                1,
                                            ]
                                        },
                                        0,
                                    ]
                                },
                            ]
                        },
                        2,
                    ]
                },
                "percentile_95th": {
                    "$round": [
                        {
                            "$arrayElemAt": [
                                "$samplesSorted",
                                {
                                    "$round": [
                                        {
                                            "$subtract": [
                                                {
                                                    "$multiply": [
                                                        "$count",
                                                        0.95,
                                                    ]
                                                },
                                                1,
                                            ]
                                        },
                                        0,
                                    ]
                                },
                            ]
                        },
                        2,
                    ]
                },
            }
        }

        cursor = mongo.db.wearables.aggregate(
            [
                stage_1_match_user_id_and_wearable,
                stage_2_project_glucose_sample_only,
                stage_3_unwind,
                stage_4_project_samples_parse_timestamp,
                stage_5_match_on_samples,
                stage_6_bucket,
                stage_7_sort_samples,
                stage_8_calculate_percentiles,
            ]
        )

        data = list(cursor)

        # Build and return payload
        payload = {
            "user_id": user_id,
            "start_time": start_date,
            "end_time": end_date,
            "wearable": wearable,
            "data": data,
            "bin_size_mins": increments,
        }

        return payload


@ns_v2.route("/calculations/blood-pressure/variation/<int:user_id>/<string:wearable>")
class WearablesV2BloodPressureVariationCalculationEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "provider"), resources=("wearable_data",)
    )
    @ns_v2.doc(
        params={
            "start_date": (
                "Start of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
            "end_date": (
                "End of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
        }
    )
    @responds(
        schema=WearablesV2BloodPressureVariationCalculationOutputSchema,
        status_code=200,
        api=ns_v2,
    )
    def get(self, user_id, wearable):
        """Get calculated blood pressure wearable data.

        This route will return the average for blood pressure readings from a start to end date for a particular
        user_id and wearable.

        Path Parameters
        ----------
        user_id : int
            User ID number.
        wearable: str
            wearable used to measure blood pressure data

        Query Parameters
        ----------
        start_date : str
            Start of specified date range
            Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)
            Default will be current date - 7 days if not specified
        end_date: str
            End of specified date range
            Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)
            Default will be current date if not specified

        Returns
        -------
        dict
            JSON encoded dict containing:
            - user_id
            - wearable
            - diastolic_bp_avg
            - systolic_bp_avg
            - pulse_avg
            - diastolic_standard_deviation
            - systolic_standard_deviation
            - pulse_standard_deviation
            - diastolic_bp_coefficient_of_variation
            - systolic_bp_coefficient_of_variation
            - pulse_coefficient_of_variation
        """

        wearable = parse_wearable(wearable)

        # Default dates
        end_date = datetime.utcnow() + timedelta(seconds=2)
        start_date = end_date - THIRTY_DAYS

        if request.args.get("start_date") and request.args.get("end_date"):
            start_date = iso_string_to_iso_datetime(request.args.get("start_date"))
            end_date = iso_string_to_iso_datetime(request.args.get("end_date"))
        elif request.args.get("start_date") or request.args.get("end_date"):
            raise BadRequest("Provide both or neither start_date and end_date.")
        """Calculate Average Blood Pressures"""
        # Define each stage of the pipeline
        # Filter documents on user_id, wearable, and date range
        stage_match_user_id_and_wearable = {
            "$match": {
                "user_id": user_id,
                "wearable": wearable,
                "timestamp": {  # search just outside of range to make sure we get objects that encompass the start_date
                    "$gte": start_date - timedelta(days=1),
                    "$lte": end_date,
                },
            }
        }

        # Unwind the bp samples array so that we can operate on each individual sample
        stage_unwind_blood_pressure_samples = {
            "$unwind": "$data.body.blood_pressure_data.blood_pressure_samples"
        }

        # Filter now again at the sample level to round out objects that overlap the tips of the desired range
        stage_match_date_range = {
            "$match": {
                "data.body.blood_pressure_data.blood_pressure_samples.timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            }
        }

        # Group all of these documents together and calculate average pressures and standard deviations for the group
        stage_group_pressure_average_and_std_dev = {
            "$group": {
                "_id": None,
                "diastolic_bp_avg": {
                    "$avg": "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp"
                },
                "systolic_bp_avg": {
                    "$avg": "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp"
                },
                "diastolic_standard_deviation": {
                    "$stdDevSamp": "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp"
                },
                "systolic_standard_deviation": {
                    "$stdDevSamp": "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp"
                },
            }
        }

        # Add field for coefficient_of_variation and calculate it. Calculated as stdDev / mean(average)
        stage_add_coefficient_of_variation = {
            "$addFields": {
                "diastolic_bp_coefficient_of_variation": {
                    "$multiply": [
                        100,
                        {
                            "$divide": [
                                "$diastolic_standard_deviation",
                                "$diastolic_bp_avg",
                            ]
                        },
                    ]
                },
                "systolic_bp_coefficient_of_variation": {
                    "$multiply": [
                        100,
                        {
                            "$divide": [
                                "$systolic_standard_deviation",
                                "$systolic_bp_avg",
                            ]
                        },
                    ]
                },
            },
        }

        # Round values
        stage_round_values = {
            "$project": {
                "diastolic_bp_avg": {"$round": ["$diastolic_bp_avg", 0]},
                "systolic_bp_avg": {"$round": ["$systolic_bp_avg", 0]},
                "diastolic_standard_deviation": {
                    "$round": ["$diastolic_standard_deviation", 0]
                },
                "systolic_standard_deviation": {
                    "$round": ["$systolic_standard_deviation", 0]
                },
                "diastolic_bp_coefficient_of_variation": {
                    "$round": ["$diastolic_bp_coefficient_of_variation", 0]
                },
                "systolic_bp_coefficient_of_variation": {
                    "$round": ["$systolic_bp_coefficient_of_variation", 0]
                },
            }
        }

        # Assemble pipeline
        pipeline = [
            stage_match_user_id_and_wearable,
            stage_unwind_blood_pressure_samples,
            stage_match_date_range,
            stage_group_pressure_average_and_std_dev,
            stage_add_coefficient_of_variation,
            stage_round_values,
        ]

        # MongoDB pipelines return a cursor
        cursor = mongo.db.wearables.aggregate(pipeline)
        document_list = list(cursor)
        data = {}

        # We need to grab the document that we want from that cursor so we can format the data in a payload
        if document_list:
            data = document_list[0]

        # Build the second pipeline for pulse data
        # Unwind the bpm data array so that we can operate on each individual sample
        stage_unwind_bpm_samples = {
            "$unwind": ("$data.body.heart_data.heart_rate_data.detailed.hr_samples")
        }

        stage_match_date_range_bpm = {
            "$match": {
                "data.body.heart_data.heart_rate_data.detailed.hr_samples.timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            }
        }

        stage_group_pressure_average_and_std_dev_bpm = {
            "$group": {
                "_id": None,
                "bpm_avg": {
                    "$avg": "$data.body.heart_data.heart_rate_data.detailed.hr_samples.bpm"
                },
                "bpm_standard_deviation": {
                    "$stdDevSamp": "$data.body.heart_data.heart_rate_data.detailed.hr_samples.bpm"
                },
            }
        }

        stage_add_coefficient_of_variation_bpm = {
            "$addFields": {
                "bpm_coefficient_of_variation": {
                    "$multiply": [
                        100,
                        {
                            "$divide": [
                                "$bpm_standard_deviation",
                                "$bpm_avg",
                            ]
                        },
                    ]
                },
            },
        }

        stage_round_values_bpm = {
            "$project": {
                "bpm_avg": {"$round": ["$bpm_avg", 0]},
                "bpm_standard_deviation": {"$round": ["$bpm_standard_deviation", 0]},
                "bpm_coefficient_of_variation": {
                    "$round": ["$bpm_coefficient_of_variation", 0]
                },
            }
        }

        # Run the second pipeline for pulse data
        pipeline2 = [
            stage_match_user_id_and_wearable,
            stage_unwind_bpm_samples,
            stage_match_date_range_bpm,
            stage_group_pressure_average_and_std_dev_bpm,
            stage_add_coefficient_of_variation_bpm,
            stage_round_values_bpm,
        ]
        cursor2 = mongo.db.wearables.aggregate(pipeline2)
        document_list2 = list(cursor2)
        data2 = {}

        if document_list2:
            data2 = document_list2[0]

        # Build and return payload
        payload = {
            "user_id": user_id,
            "wearable": wearable,
            "diastolic_bp_avg": data.get("diastolic_bp_avg"),
            "systolic_bp_avg": data.get("systolic_bp_avg"),
            "diastolic_standard_deviation": data.get("diastolic_standard_deviation"),
            "systolic_standard_deviation": data.get("systolic_standard_deviation"),
            "diastolic_bp_coefficient_of_variation": data.get(
                "diastolic_bp_coefficient_of_variation"
            ),
            "systolic_bp_coefficient_of_variation": data.get(
                "systolic_bp_coefficient_of_variation"
            ),
            "pulse_avg": data2.get("bpm_avg"),
            "pulse_standard_deviation": data2.get("bpm_standard_deviation"),
            "pulse_coefficient_of_variation": data2.get("bpm_coefficient_of_variation"),
        }

        return payload


@ns_v2.route(
    "/calculations/blood-pressure/30-day-hourly/<int:user_id>/<string:wearable>"
)
class WearablesV2BloodPressureCalculationEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "provider"), resources=("wearable_data",)
    )
    @ns_v2.doc(
        params={
            "start_date": (
                "Start of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
            "end_date": (
                "End of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
        }
    )
    @responds(
        schema=WearablesV2BloodPressureCalculationOutputSchema,
        status_code=200,
        api=ns_v2,
    )
    def get(self, user_id, wearable):
        """Get calculated values related to hourly blood pressure wearable data.

        This route will return hourly blood pressure data for a particular user_id, wearable, and timestamp range with the default date being the previous 30 days.
        The data is grouped into 8 time blocks with each being 3 hours long (0-3, 3-6, 6-9, etc...). See below for exact calculations being returned.

        Path Parameters
        ----------
        user_id : int
            User ID number.
        wearable: str
            wearable used to measure blood pressure data

        Query Parameters
        ----------
        start_date : str
            Start of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date - 30 days if not specified
        end_date: str
            End of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date if not specified

        Returns
        -------
        dict
            JSON encoded dict containing:
            - user_id
            - wearable
            - block_one - Data for the first time block - (0-3)
            - block_two - Data for the second time block - (3-6)
            - block_three - Data for the third time block - (6-9)
            - block_four - Data for the fourth time block - (9-12)
            - block_five - Data for the fifth time block - (12-15)
            - block_six - Data for the sixth time block - (15-18)
            - block_seven - Data for the seventh time block - (18-21)
            - block_eight - Data for the eighth time block - (21-24)

            Each time block will be a dict containing:
            - total_bp_readings - Number of blood pressure readings
            - total_pulse_readings - Number of heart rate readings
            - average_systolic - average systolic value in mmHg
            - average_diastolic - average diastolic value in mmHg
            - min_systolic - Min systolic value
            - min_diastolic - Min diastolic value
            - max_systolic - Max systolic value
            - max_diastolic - Max diastolic value
            - average_pulse - average pulse value in bpm
        """

        payload = {}
        wearable = parse_wearable(wearable)

        # Default dates
        end_date = datetime.utcnow()
        start_date = end_date - THIRTY_DAYS

        if request.args.get("start_date") and request.args.get("end_date"):
            start_date = iso_string_to_iso_datetime(request.args.get("start_date"))
            end_date = iso_string_to_iso_datetime(request.args.get("end_date"))
        elif request.args.get("start_date") or request.args.get("end_date"):
            raise BadRequest("Provide both or neither start_date and end_date.")

        # Stages for blood pressure calculations

        # Filter documents on user_id, wearable
        stage_match_user_id_and_wearable = {
            "$match": {
                "user_id": user_id,
                "wearable": wearable,
                "timestamp": {  # search just outside of range to make sure we get objects that encompass the start_date
                    "$gte": start_date - timedelta(days=1),
                    "$lte": end_date,
                },
            }
        }

        # Unwind the blood_pressure_samples array so that we can operate on each individual sample
        stage_unwind_bp_samples = {
            "$unwind": "$data.body.blood_pressure_data.blood_pressure_samples"
        }

        # Filter on the timestamp of each blood pressure sample
        stage_match_date_range_bp = {
            "$match": {
                "data.body.blood_pressure_data.blood_pressure_samples.timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                }
            }
        }

        # Add the hour field so that we can group all samples based on the hour they were taken
        stage_add_hour_bp = {
            "$addFields": {
                "hour": {
                    "$hour": "$data.body.blood_pressure_data.blood_pressure_samples.timestamp"
                }
            }
        }

        # Place documents in buckets by time block. Each time block is three hours long starting with 0-3 and ending with 21-24
        # After that, calculate total readings, averages, min, and max
        stage_bucket_and_calculate_bp = {
            "$bucket": {
                "groupBy": "$hour",
                "boundaries": THREE_HOUR_TIME_BLOCK_START_TIMES_LIST,
                "output": {
                    "total_bp_readings": {"$sum": 1},
                    "average_systolic": {
                        "$avg": "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp"
                    },
                    "average_diastolic": {
                        "$avg": "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp"
                    },
                    "min_systolic": {
                        "$min": "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp"
                    },
                    "min_diastolic": {
                        "$min": "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp"
                    },
                    "max_systolic": {
                        "$max": "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp"
                    },
                    "max_diastolic": {
                        "$max": "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp"
                    },
                },
            }
        }

        # Round averages
        stage_round_averages_bp = {
            "$project": {
                "total_bp_readings": "$total_bp_readings",
                "average_systolic": {"$round": ["$average_systolic", 0]},
                "average_diastolic": {"$round": ["$average_diastolic", 0]},
                "min_systolic": "$min_systolic",
                "min_diastolic": "$min_diastolic",
                "max_systolic": "$max_systolic",
                "max_diastolic": "$max_diastolic",
            }
        }

        # Stages for pulse - making another call because the location of the pulse data is nested in another part of the Terra schema

        # Unwind the hr_samples array so that we can operate on each individual sample
        stage_unwind_hr_samples = {
            "$unwind": "$data.body.heart_data.detailed.hr_samples"
        }

        # Filter on the timestamp of each hr_sample
        stage_match_date_range_pulse = {
            "$match": {
                "data.body.heart_data.detailed.hr_samples.timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                }
            }
        }

        # Add the hour field so that we can group all samples based on the hour they were taken
        stage_add_hour_pulse = {
            "$addFields": {
                "hour": {
                    "$hour": ("$data.body.heart_data.detailed.hr_samples.timestamp")
                }
            }
        }

        # Place documents in buckets by time block. Each time block is three hours long starting with 0-3 and ending with 21-24
        # After that, calculate average and total readings
        stage_bucket_and_calculate_pulse = {
            "$bucket": {
                "groupBy": "$hour",
                "boundaries": THREE_HOUR_TIME_BLOCK_START_TIMES_LIST,
                "output": {
                    "average_pulse": {
                        "$avg": "$data.body.heart_data.detailed.hr_samples.bpm"
                    },
                    "total_pulse_readings": {"$sum": 1},
                },
            }
        }

        # Round averages
        stage_round_averages_pulse = {
            "$project": {
                "total_pulse_readings": "$total_pulse_readings",
                "average_pulse": {"$round": ["$average_pulse", 0]},
            }
        }

        # Build blood pressure pipeline
        blood_pressure_pipeline = [
            stage_match_user_id_and_wearable,
            stage_unwind_bp_samples,
            stage_match_date_range_bp,
            stage_add_hour_bp,
            stage_bucket_and_calculate_bp,
            stage_round_averages_bp,
        ]

        # Build pulse pipeline
        pulse_pipeline = [
            stage_match_user_id_and_wearable,
            stage_unwind_hr_samples,
            stage_match_date_range_pulse,
            stage_add_hour_pulse,
            stage_bucket_and_calculate_pulse,
            stage_round_averages_pulse,
        ]

        # Store blood pressure data

        # MongoDB pipelines return a cursor
        cursor = mongo.db.wearables.aggregate(blood_pressure_pipeline)
        bp_document_list = list(cursor)

        # Loop through each document (time block bucket) and add blood pressuredata for that time block to the payload
        if bp_document_list:
            for doc in bp_document_list:
                time_block = START_TIME_TO_THREE_HOUR_TIME_BLOCKS[doc.get("_id")]
                time_block_data = {
                    "total_bp_readings": doc.get("total_bp_readings"),
                    "average_systolic": doc.get("average_systolic"),
                    "average_diastolic": doc.get("average_diastolic"),
                    "min_systolic": doc.get("min_systolic"),
                    "min_diastolic": doc.get("min_diastolic"),
                    "max_systolic": doc.get("max_systolic"),
                    "max_diastolic": doc.get("max_diastolic"),
                }
                payload[time_block] = time_block_data

        # Store pulse data

        # MongoDB pipelines return a cursor
        cursor = mongo.db.wearables.aggregate(pulse_pipeline)
        pulse_document_list = list(cursor)

        # Loop through each document (time block bucket) and add pulse data for that time block to the payload
        if pulse_document_list:
            for doc in pulse_document_list:
                time_block = START_TIME_TO_THREE_HOUR_TIME_BLOCKS[doc.get("_id")]

                payload[time_block]["average_pulse"] = doc.get("average_pulse")
                payload[time_block]["total_pulse_readings"] = doc.get(
                    "total_pulse_readings"
                )

        # Add user_id and wearable to payload and return
        payload["user_id"] = user_id
        payload["wearable"] = wearable

        return payload


@ns_v2.route(
    "/calculations/blood-pressure/monitoring-statistics/<int:user_id>/<string:wearable>"
)
class WearablesV2BloodPressureMonitoringStatisticsCalculationEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "provider"), resources=("wearable_data",)
    )
    @ns_v2.doc(
        params={
            "start_date": (
                "Start of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            )
        }
    )
    @responds(
        schema=WearablesV2BloodPressureMonitoringStatisticsOutputSchema,
        status_code=200,
        api=ns_v2,
    )
    def get(self, user_id, wearable):
        """Get calculated values related to blood pressure monitoring statistics.

        This route will return 2 blocks of general blood pressure data and classification info given a user_id, wearable, and an optional start_date.
        The first block of data will always be from the start_date (default is current date minus 30 days) to the current date. The second block will always be over
        the same range (default 30 days) but will end at the given start_date and span X days (default 30) prior to that. For example, if the distance between start_date
        and the current date is 7 days, both blocks will give data for 7 day blocks. The first will contain data from current date minus 7 days to the current date and the
        second block will contain the 7 days prior to that. The length of blocks is determined by the delta between start_date and current date.

        Path Parameters
        ----------
        user_id : int
            User ID number.
        wearable: str
            wearable used to measure blood pressure data

        Query Parameters
        ----------
        start_date : str
            Start of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date - 30 days if not specified

        Returns
        -------
        dict
            JSON encoded dict containing:
            - user_id - User ID number
            - wearable - wearable used to measure blood pressure data
            - current_block - data for most recent block
            - prev_block - data for previous block

            Each block will be a dict containing:
            - start_date - start of time range
            - end_date - end of time range
            - general_data - general blood pressure data
            - classification_data - blood pressure classification data

            general_data will contain the following:
            - average_systolic - average systolic value in mmHg
            - average_diastolic - average diastolic value in mmHg
            - total_bp_readings - total number of blood pressure readings
            - total_pulse_readings - total number of pulse readings
            - average_pulse - average pulse in bpm
            - average_readings_per_day - average number of readings per day over the time period

            classification_data will contain the following:
            - normal - number of readings in the 'normal' range
            - elevated - number of readings in the 'elevated' range
            - hypertension_stage_1 - number of readings in the 'hypertension_stage_1' range
            - hypertension_stage_2 - number of readings in the 'hypertension_stage_2' range
            - hypertensive_crisis - number of readings in the 'hypertensive_crisis' range
            - normal_percentage - percentage of total readings that are in the 'normal' range
            - elevated_percentage - percentage of total readings that are in the 'elevated' range
            - hypertension_stage_1_percentage - percentage of total readings that are in the 'hypertension_stage_1' range
            - hypertension_stage_2_percentage - percentage of total readings that are in the 'hypertension_stage_2' range
            - hypertensive_crisis_percentage - percentage of total readings that are in the 'hypertensive_crisis' range

        """

        wearable = parse_wearable(wearable)

        # Default dates
        end_date = datetime.utcnow()
        start_date = end_date - THIRTY_DAYS
        days = 30

        # For this endpoint, we just allow the user to start_date because end_date will always be the current_date.
        # We will then return data for start_date -> current date and then start_date minus the delta between orginal start_date and current_date -> start_date
        if request.args.get("start_date"):
            start_date = iso_string_to_iso_datetime(request.args.get("start_date"))
            # Get time delta in days for average_readings_per_day calculation
            duration = end_date - start_date
            days = duration.days

        ### Stages for blood pressure monitoring statistics calculations ###

        # Filter documents on user_id, wearable, and current time block dates
        stage_match_user_id_and_wearable = {
            "$match": {
                "user_id": user_id,
                "wearable": wearable,
                "timestamp": {  # search just outside of range to make sure we get objects that encompass the start_date
                    "$gte": start_date - timedelta(days=1),
                    "$lte": end_date,
                },
            }
        }

        # Filter documents on user_id, wearable and prev time block dates
        stage_match_user_id_and_wearable_prev = {
            "$match": {
                "user_id": user_id,
                "wearable": wearable,
                "timestamp": {  # search just outside of range to make sure we get objects that encompass the start_date
                    "$gte": start_date - timedelta(days=days),
                    "$lte": start_date,
                },
            }
        }

        # Unwind the blood_pressure_samples array so that we can operate on each individual sample
        stage_unwind_bp_samples = {
            "$unwind": "$data.body.blood_pressure_data.blood_pressure_samples"
        }

        # Filter on the timestamp of each blood pressure sample
        stage_match_date_range_bp = {
            "$match": {
                "data.body.blood_pressure_data.blood_pressure_samples.timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                }
            }
        }

        # Filter on the timestamp of each blood pressure sample in prev time block
        stage_match_date_range_bp_prev = {
            "$match": {
                "data.body.blood_pressure_data.blood_pressure_samples.timestamp": {
                    "$gte": start_date - timedelta(days=days),
                    "$lte": start_date,
                }
            }
        }

        # Group all bp samples to calculate total, averages, min, and max
        stage_group_bp = {
            "$group": {
                "_id": None,
                "total_bp_readings": {"$sum": 1},
                "average_systolic": {
                    "$avg": "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp"
                },
                "average_diastolic": {
                    "$avg": "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp"
                },
                "min_systolic": {
                    "$min": "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp"
                },
                "min_diastolic": {
                    "$min": "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp"
                },
                "max_systolic": {
                    "$max": "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp"
                },
                "max_diastolic": {
                    "$max": "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp"
                },
            }
        }

        # Project those previous calculations and then calculate average_readings_per_day
        stage_project_bp = {
            "$project": {
                "average_readings_per_day": {
                    "$round": [{"$divide": ["$total_bp_readings", days]}, 1]
                },
                "total_bp_readings": "$total_bp_readings",
                "average_systolic": "$average_systolic",
                "average_diastolic": "$average_diastolic",
                "min_systolic": "$min_systolic",
                "min_diastolic": "$min_diastolic",
                "max_systolic": "$max_systolic",
                "max_diastolic": "$max_diastolic",
            }
        }

        ### Stages for blood pressure classification ###

        # Add classification field to samples
        stage_add_classification = {
            "$addFields": {
                "classification": {
                    "$switch": {
                        "branches": [
                            {
                                "case": {
                                    "$and": [
                                        {
                                            "$lt": [
                                                "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp",
                                                120,
                                            ]
                                        },
                                        {
                                            "$lt": [
                                                "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp",
                                                80,
                                            ]
                                        },
                                    ]
                                },
                                "then": "normal",
                            },
                            {
                                "case": {
                                    "$and": [
                                        {
                                            "$and": [
                                                {
                                                    "$gte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp",
                                                        120,
                                                    ]
                                                },
                                                {
                                                    "$lte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp",
                                                        129,
                                                    ]
                                                },
                                            ]
                                        },
                                        {
                                            "$lt": [
                                                "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp",
                                                80,
                                            ]
                                        },
                                    ]
                                },
                                "then": "elevated",
                            },
                            {
                                "case": {
                                    "$or": [
                                        {
                                            "$and": [
                                                {
                                                    "$gte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp",
                                                        130,
                                                    ]
                                                },
                                                {
                                                    "$lte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp",
                                                        139,
                                                    ]
                                                },
                                            ]
                                        },
                                        {
                                            "$and": [
                                                {
                                                    "$gte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp",
                                                        80,
                                                    ]
                                                },
                                                {
                                                    "$lte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp",
                                                        89,
                                                    ]
                                                },
                                            ]
                                        },
                                    ]
                                },
                                "then": "hypertension_stage_1",
                            },
                            {
                                "case": {
                                    "$or": [
                                        {
                                            "$and": [
                                                {
                                                    "$gte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp",
                                                        140,
                                                    ]
                                                },
                                                {
                                                    "$lte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp",
                                                        180,
                                                    ]
                                                },
                                            ]
                                        },
                                        {
                                            "$and": [
                                                {
                                                    "$gte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp",
                                                        90,
                                                    ]
                                                },
                                                {
                                                    "$lte": [
                                                        "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp",
                                                        120,
                                                    ]
                                                },
                                            ]
                                        },
                                    ]
                                },
                                "then": "hypertension_stage_2",
                            },
                            {
                                "case": {
                                    "$or": [
                                        {
                                            "$gt": [
                                                "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp",
                                                180,
                                            ]
                                        },
                                        {
                                            "$gt": [
                                                "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp",
                                                120,
                                            ]
                                        },
                                    ]
                                },
                                "then": "hypertensive_crisis",
                            },
                        ],
                        "default": None,
                    }
                }
            }
        }

        # Group by classification and pass total count forward
        stage_facet_classification = {
            "$facet": {
                "buckets": [
                    {
                        "$group": {
                            "_id": "$classification",
                            "count": {"$sum": 1},
                        }
                    }
                ],
                "total_count": [{"$count": "total_count"}],
            }
        }

        # Unwind new buckets
        stage_unwind_buckets = {"$unwind": "$buckets"}

        # Pass forward bucket and count to calculate percentage for each classification
        stage_project_classification = {
            "$project": {
                "percentage": {
                    "$multiply": [
                        {
                            "$round": [
                                {
                                    "$divide": [
                                        "$buckets.count",
                                        {
                                            "$arrayElemAt": [
                                                "$total_count.total_count",
                                                0,
                                            ]
                                        },
                                    ]
                                },
                                2,
                            ]
                        },
                        100,
                    ]
                },
                "bucket": "$buckets._id",
                "count": "$buckets.count",
            }
        }

        ### Stages for heart rate calculations ###

        # Unwind the hr_samples array so that we can operate on each individual sample
        stage_unwind_hr_samples = {
            "$unwind": "$data.body.heart_data.detailed.hr_samples"
        }

        # Filter on the timestamp of each hr_sample
        stage_match_date_range_pulse = {
            "$match": {
                "data.body.heart_data.detailed.hr_samples.timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                }
            }
        }

        # Filter on the timestamp of each prev hr_sample
        stage_match_date_range_pulse_prev = {
            "$match": {
                "data.body.heart_data.detailed.hr_samples.timestamp": {
                    "$gte": start_date - timedelta(days=days),
                    "$lte": start_date,
                }
            }
        }
        # Group all pulse and calculate total and average
        stage_group_pulse = {
            "$group": {
                "_id": None,
                "total_pulse_readings": {"$sum": 1},
                "average_pulse": {
                    "$avg": "$data.body.heart_data.detailed.hr_samples.bpm"
                },
            }
        }

        ### Current time block pipelines ###

        # Build bp pipeline
        pipeline = [
            stage_match_user_id_and_wearable,
            stage_unwind_bp_samples,
            stage_match_date_range_bp,
            stage_group_bp,
            stage_project_bp,
        ]

        # Build pulse pipeline
        pulse_pipeline = [
            stage_match_user_id_and_wearable,
            stage_unwind_hr_samples,
            stage_match_date_range_pulse,
            stage_group_pulse,
        ]

        # Build classification pipeline
        classification_pipeline = [
            stage_match_user_id_and_wearable,
            stage_unwind_bp_samples,
            stage_match_date_range_bp,
            stage_add_classification,
            stage_facet_classification,
            stage_unwind_buckets,
            stage_project_classification,
        ]

        ### Previous time block pipelines ###

        # Build prev bp pipeline
        prev_pipeline = [
            stage_match_user_id_and_wearable_prev,
            stage_unwind_bp_samples,
            stage_match_date_range_bp_prev,
            stage_group_bp,
            stage_project_bp,
        ]

        # Build prev pulse pipeline
        prev_pulse_pipeline = [
            stage_match_user_id_and_wearable_prev,
            stage_unwind_hr_samples,
            stage_match_date_range_pulse_prev,
            stage_group_pulse,
        ]

        # Build prev classification pipeline
        prev_classification_pipeline = [
            stage_match_user_id_and_wearable_prev,
            stage_unwind_bp_samples,
            stage_match_date_range_bp_prev,
            stage_add_classification,
            stage_facet_classification,
            stage_unwind_buckets,
            stage_project_classification,
        ]

        ### Add current time block data to payload ###

        # General bp data
        cursor = mongo.db.wearables.aggregate(pipeline)
        document_list = list(cursor)
        data = {}

        if document_list:
            data = document_list[0]

        # Build general bp info for payload
        payload = {"user_id": user_id, "wearable": wearable}

        # Add general info to current_block in the payload
        payload["current_block"] = {}
        payload["current_block"]["start_date"] = start_date
        payload["current_block"]["end_date"] = end_date
        payload["current_block"]["general_data"] = {}
        payload["current_block"]["general_data"]["average_systolic"] = data.get(
            "average_systolic"
        )
        payload["current_block"]["general_data"]["average_diastolic"] = data.get(
            "average_diastolic"
        )
        payload["current_block"]["general_data"]["min_systolic"] = data.get(
            "min_systolic"
        )
        payload["current_block"]["general_data"]["max_systolic"] = data.get(
            "max_systolic"
        )
        payload["current_block"]["general_data"]["min_diastolic"] = data.get(
            "min_diastolic"
        )
        payload["current_block"]["general_data"]["max_diastolic"] = data.get(
            "max_diastolic"
        )
        payload["current_block"]["general_data"]["total_bp_readings"] = data.get(
            "total_bp_readings"
        )
        payload["current_block"]["general_data"]["average_readings_per_day"] = data.get(
            "average_readings_per_day"
        )

        # Pulse data
        cursor = mongo.db.wearables.aggregate(pulse_pipeline)
        document_list = list(cursor)
        pulse_data = {}

        if document_list:
            pulse_data = document_list[0]

        # Add pulse data to current_block in the payload
        payload["current_block"]["general_data"]["average_pulse"] = pulse_data.get(
            "average_pulse"
        )
        payload["current_block"]["general_data"][
            "total_pulse_readings"
        ] = pulse_data.get("total_pulse_readings")

        # Systolic classifications
        cursor = mongo.db.wearables.aggregate(classification_pipeline)
        classification_document_list = list(cursor)

        if classification_document_list:
            payload["current_block"]["classification_data"] = {}
            for doc in classification_document_list:
                # Add classification data to current_block in the payload
                payload["current_block"]["classification_data"][
                    doc.get("bucket")
                ] = doc.get("count")
                payload["current_block"]["classification_data"][
                    doc.get("bucket") + "_percentage"
                ] = doc.get("percentage")

        ### Add previous time block data to payload ###

        # General bp data prev
        cursor = mongo.db.wearables.aggregate(prev_pipeline)
        document_list = list(cursor)
        data = {}

        if document_list:
            data = document_list[0]

        # Add general info to prev_block in the payload
        payload["prev_block"] = {}
        payload["prev_block"]["start_date"] = start_date - timedelta(days=days)
        payload["prev_block"]["end_date"] = start_date
        payload["prev_block"]["general_data"] = {}
        payload["prev_block"]["general_data"]["average_systolic"] = data.get(
            "average_systolic"
        )
        payload["prev_block"]["general_data"]["average_diastolic"] = data.get(
            "average_diastolic"
        )
        payload["prev_block"]["general_data"]["min_systolic"] = data.get("min_systolic")
        payload["prev_block"]["general_data"]["max_systolic"] = data.get("max_systolic")
        payload["prev_block"]["general_data"]["min_diastolic"] = data.get(
            "min_diastolic"
        )
        payload["prev_block"]["general_data"]["max_diastolic"] = data.get(
            "max_diastolic"
        )
        payload["prev_block"]["general_data"]["total_bp_readings"] = data.get(
            "total_bp_readings"
        )
        payload["prev_block"]["general_data"]["average_readings_per_day"] = data.get(
            "average_readings_per_day"
        )

        # Pulse data prev
        cursor = mongo.db.wearables.aggregate(prev_pulse_pipeline)
        document_list = list(cursor)
        pulse_data = {}

        if document_list:
            pulse_data = document_list[0]

        # Add pulse data to prev_block in the payload
        payload["prev_block"]["general_data"]["average_pulse"] = pulse_data.get(
            "average_pulse"
        )
        payload["prev_block"]["general_data"]["total_pulse_readings"] = pulse_data.get(
            "total_pulse_readings"
        )

        # Systolic classifications prev
        cursor = mongo.db.wearables.aggregate(prev_classification_pipeline)
        classification_document_list = list(cursor)

        if classification_document_list:
            payload["prev_block"]["classification_data"] = {}
            for doc in classification_document_list:
                # Add classification data to current_block in the payload
                payload["prev_block"]["classification_data"][
                    doc.get("bucket")
                ] = doc.get("count")
                payload["prev_block"]["classification_data"][
                    doc.get("bucket") + "_percentage"
                ] = doc.get("percentage")

        # Return completed payload
        return payload


@ns_v2.route(
    "/calculations/blood-pressure/daily-average/<int:user_id>/<string:wearable>"
)
class WearablesV2BloodPressureDailyAvgCalculationEndpoint(BaseResource):
    @token_auth.login_required(
        user_type=("client", "provider"), resources=("wearable_data",)
    )
    @ns_v2.doc(
        params={
            "start_date": (
                "Start of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
            "end_date": (
                "End of specified date range. Can be either ISO format date"
                " (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z)"
            ),
        }
    )
    @responds(
        schema=WearablesV2BloodPressureDailyAvgOutputSchema,
        status_code=200,
        api=ns_v2,
    )
    def get(self, user_id, wearable):
        """
        Accepts a date range and returns the daily average systolic, diastolic blood pressure, and heartrate at time of reading.

        Path Parameters
        ----------
        user_id : int
            User ID number.
        wearable: str
            wearable used to measure blood pressure data

        Query Parameters
        ----------
        start_date : str
            Start of specified date range - Can be either ISO format date (2023-01-01) or full ISO timestamp (2023-01-01T00:00:00Z).
            Default will be current date - 30 days if not specified

        Returns
        -------
        dict
            JSON encoded dict containing:
        """

        start_date, end_date = date_range(
            start_time=request.args.get("start_date"),
            end_time=request.args.get("end_date"),
            time_range=timedelta(days=30),
        )

        stage_1_match_user_id_and_wearable = {
            "$match": {
                "user_id": user_id,
                "wearable": wearable,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            }
        }

        stage_2_unwind_bp_data = {
            "$unwind": "$data.body.blood_pressure_data.blood_pressure_samples"
        }

        stage_3_group_by_date_take_bp_avgs = {
            "$group": {
                "_id": {"date": "$timestamp"},
                "systolic_bp_avg": {
                    "$avg": "$data.body.blood_pressure_data.blood_pressure_samples.systolic_bp"
                },
                "diastolic_bp_avg": {
                    "$avg": "$data.body.blood_pressure_data.blood_pressure_samples.diastolic_bp"
                },
                "bp_readings_count": {"$sum": 1},
                "hr_samples": {
                    "$first": "$data.body.heart_data.heart_rate_data.detailed.hr_samples"
                },
            }
        }

        stage_4_unwind_hr_data = {"$unwind": "$hr_samples"}

        stage_5_group_by_date_take_hr_avgs = {
            "$group": {
                "_id": {"date": "$_id.date"},
                "systolic_bp_avg": {"$first": {"$round": ["$systolic_bp_avg", 0]}},
                "diastolic_bp_avg": {"$first": {"$round": ["$diastolic_bp_avg", 0]}},
                "bp_readings_count": {"$first": "$bp_readings_count"},
                "hr_bpm_avg": {"$avg": "$hr_samples.bpm"},
                "hr_readings_count": {"$sum": 1},
            }
        }

        stage_6_sort_by_date = {"$sort": {"_id.date": 1}}

        stage_7_project = {
            "$project": {
                "_id": 0,
                "date": "$_id.date",
                "systolic_bp_avg": 1,
                "diastolic_bp_avg": 1,
                "bp_readings_count": 1,
                "hr_bpm_avg": {"$round": ["$hr_bpm_avg", 0]},
                "hr_readings_count": 1,
            }
        }

        pipeline = [
            stage_1_match_user_id_and_wearable,
            stage_2_unwind_bp_data,
            stage_3_group_by_date_take_bp_avgs,
            stage_4_unwind_hr_data,
            stage_5_group_by_date_take_hr_avgs,
            stage_6_sort_by_date,
            stage_7_project,
        ]

        cursor = mongo.db.wearables.aggregate(pipeline)

        document_list = list(cursor)

        payload = {
            "items": document_list,
            "total_items": len(document_list),
            "wearable": wearable,
        }

        return payload


@ns_v2.route("/data/dashboard/<int:user_id>")
class WearablesV2DataDashboardEndpoint(BaseResource):
    """Endpoint for retrieving data for the data dashboard"""

    def get(self, user_id):
        """
        Retrieve data for the data dashboard.
        This endpoint will return the following data:
            - Total sleep duration
            - Daily Steps
            - Daily Calories
            - Daily resting heart rate

        Path Parameters
        ---------------
        user_id : int
            User ID number.
        device: str
            TODO target device

        Returns
        -------
        dict
            JSON encoded dict containing:
            - total_sleep_duration - total sleep duration in hours
            - daily_steps - daily steps
            - daily_calories - daily calories
            - daily_resting_heart_rate - daily resting heart rate
        """
        start_date, end_date = date_range(
            start_time=request.args.get("start_date"),
            end_time=request.args.get("end_date"),
            time_range=timedelta(days=14),
        )

        device = request.args.get("device", "OURA")

        # mongo db query for sleep
        # this one will require an aggregation due to the complexity of sleep data
        # the data can get muddled with multiple sleep events and handling sleep
        # recordings which cross day boundaries
        # Notable points:
        # - sleep events are grouped on the day the sleep even ends
        # - sleep data is only returned for a day if there are sleep events that were not considered a nap
        # - total sleep duration is summed from all naps

        
        sleep_durations_query = sleep_durations_aggregation(user_id, device, start_date, end_date)
        resting_hr_query= resting_hr_aggregation(user_id, device, start_date, end_date)
        steps_query = steps_aggregation(user_id, device, start_date, end_date)


        sleep_durations_cursor = mongo.db.wearables.aggregate(sleep_durations_query)
        resting_hrs_cursor = mongo.db.wearables.aggregate(resting_hr_query)
        steps_cursor = mongo.db.wearables.aggregate(steps_query)

        # Initialize an empty dictionary to store the collated results
        collated_results = {}

        num_entries = 0
        asleep_duration_sum = 0
        in_bed_duration_sum = 0

        # Add result1 to the collated_results
        for entry in sleep_durations_cursor:
            date = entry["date"]
            del entry["date"]
            num_entries += 1
            asleep_duration_sum += entry["total_duration_asleep"]
            in_bed_duration_sum += entry["total_duration_in_bed"]
            if date not in collated_results:
                collated_results[date] = {}
            collated_results[date].update(entry)

        # Calculate the average sleep duration

        if num_entries > 0:
            avg_sleep_duration = asleep_duration_sum / num_entries
            avg_in_bed_duration = in_bed_duration_sum / num_entries

        # Add the hr_aggregation data to the collated_results
        # while looping through hr_aggregation, find the average resting heart rate
        hr_sum = 0
        hr_count = 0

        for entry in resting_hrs_cursor:
            date = entry["date"]
            hr_count += 1
            hr_sum += entry["resting_hr"]
            if date not in collated_results:
                collated_results[date] = {}
            collated_results[date]["resting_hr"] = entry["resting_hr"]

        # Calculate the average resting heart rate
        if hr_count == 0:
            avg_resting_hr = None
        else:
            avg_resting_hr = hr_sum / hr_count

        num_entries = 0
        steps_sum = 0
        distance_sum = 0

        for entry in steps_cursor:
            date = entry["date"]
            del entry["date"]
            num_entries += 1

            # convert total_distance_meters to feet
            entry["total_distance_feet"] = entry["total_distance_meters"] * 3.28084

            del entry["total_distance_meters"]

            steps_sum += entry["total_steps"]
            distance_sum += entry["total_distance_feet"]
            if date not in collated_results:
                collated_results[date] = {}
            collated_results[date].update(entry)

        # Calculate the average steps and distance
        if num_entries > 0:
            avg_steps = steps_sum / num_entries
            avg_distance = distance_sum / num_entries
        else:
            avg_steps = None
            avg_distance = None


        # breakpoint()
        # return the documents using json
        payload = {
            "daily_metrics": collated_results,
            "total_days": len(collated_results),
            "avg_resting_hr": avg_resting_hr,
            "avg_steps": avg_steps,
            "avg_distance_feet": avg_distance,
            "avg_sleep_duration": avg_sleep_duration,
            "avg_in_bed_duration": avg_in_bed_duration,
        }

        return payload
