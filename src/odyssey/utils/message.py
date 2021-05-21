import enum

import boto3

from botocore.exceptions import ClientError
from flask import current_app
from flask.json import dumps

from odyssey.api.notifications.models import NotificationsPushRegistration
from odyssey.utils.constants import PASSWORD_RESET_URL, REGISTRATION_PORTAL_URL

SUBJECTS = {"remote_registration_portal": "Modo Bio User Registration Portal", 
            "password_reset": "Modo bio password reset request - temporary link",
            "testing-bounce": "SES TEST EMAIL-BOUNCE",
            "testing-complaint": "SES TEST EMAIL-COMPLAINT",
            "testing-success": "SES TEST EMAIL",
            "account_deleted": "Modo Bio Account Deleted"
            }

def send_email_user_registration_portal(recipient, password, portal_id):
    """
    Email for sending users their registration link and login details
    That were createrd by a client services staff member
    """
    
    SUBJECT = SUBJECTS["remote_registration_portal"]
    
    SENDER = "Modo Bio no-reply <no-reply@modobio.com>"

    remote_registration_url = REGISTRATION_PORTAL_URL.format(portal_id)

    # route emails to AWS mailbox simulator when in dev environment
    if current_app.config['LOCAL_CONFIG'] and not recipient.endswith('sde.cz'):
        recipient = "success@simulator.amazonses.com"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Welcome to Modo Bio!\r\n"
                "Please visit your unique portal to complete your user registration:\n"
                f"1) Copy and paste this portal link into your browser {remote_registration_url}\n"
                "2) Enter your email and password to login:"
                f"\t email: {recipient}\n"
                f"\t password: {password}\n\n"
                "If you have any issues, please contact client services."
                )
                
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
    <h1>Welcome to Modo Bio!</h1>
    <p>Please visit your unique portal to complete your user registration:
    <br>1) Click on this link to be directed to your registration portal <a href={remote_registration_url}></a>
    <br> or copy and paste this portal link into your browser {remote_registration_url} 
    <br>2) Enter your email and password to login: 
    <br>     email: {recipient}
    <br>     password: {password}
    <br>
    <br>
    <br>If you have any issues, please contact client services.
    </body>
    </html>
    """     

    send_email_no_reply(subject=SUBJECT, recipient=recipient, body_text=BODY_TEXT, body_html=BODY_HTML)

def send_email_password_reset(recipient, reset_token):
    """
    Email for sending users password reset portal
    """
    
    SUBJECT = SUBJECTS["password_reset"]
    
    SENDER = "Modo Bio no-reply <no-reply@modobio.com>"

    reset_password_url = PASSWORD_RESET_URL.format(reset_token)

    # route emails to AWS mailbox simulator when in dev environment
    if current_app.config['LOCAL_CONFIG'] and not recipient.endswith('sde.cz'):
        recipient = "success@simulator.amazonses.com"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("You have requested to reset your password\r\n"
                "Please visit the secure portal below to reset your password:\n"
                f"{reset_password_url}\n\n"
                "If you have not requested to have your password reset, please contact your admin."
                )
                
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
    <h1>You have requested to reset your password</h1>
    <p>Please visit the secure portal below to reset your password:
    <br>{reset_password_url} 
    <br>If you have not requested to have your password reset, please contact your admin.
    </body>
    </html>
    """     

    send_email_no_reply(subject=SUBJECT, recipient=recipient, body_text=BODY_TEXT, body_html=BODY_HTML)

def send_email_delete_account(recipient, deleted_account):
    """
    Email for notifying users of account deletion
    """
    
    SUBJECT = SUBJECTS["account_deleted"]
    
    SENDER = "Modo Bio no-reply <no-reply@modobio.com>"

    # route emails to AWS mailbox simulator when in dev environment
    if current_app.env == "development":
        recipient = "success@simulator.amazonses.com"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("The the account with email: "f"{deleted_account} has been deleted.\n"
                "If you have not requested to delete your account, please contact your admin."
                )
                
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
    <h1>Account Deleted</h1>
    <p>The account with email: {deleted_account} has been deleted.
    <br>If you have not requested to delete your account, please contact your admin.
    </body>
    </html>
    """     

    send_email_no_reply(subject=SUBJECT, recipient=recipient, body_text=BODY_TEXT, body_html=BODY_HTML)

def send_test_email(subject="testing-success", recipient="success@simulator.amazonses.com"):
    """
        Use the AWS mailbox simulator to test different scenarios: success, bounce, complaint
    """

    SENDER = "Modo Bio no-reply <no-reply@modobio.com>"

    # testing scenarios
    if "simulator.amazonses.com" not in recipient:
        pass
    elif subject == "testing-success":
        recipient="success@simulator.amazonses.com"
    elif subject == "testing-bounce":
        recipient = "bounce@simulator.amazonses.com" 
    elif subject == "testing-complaint":
        recipient = "complaint@simulator.amazonses.com" 
    
    RECIPIENT = recipient

    # The subject line for the email.
    SUBJECT = SUBJECTS.get(subject, None)

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                "This email was sent with Amazon SES using the "
                "AWS SDK for Python (Boto)."
                )
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
    <h1>Amazon SES Test (SDK for Python)</h1>
    <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
        <a href='https://aws.amazon.com/sdk-for-python/'>
        AWS SDK for Python (Boto)</a>.</p>
    </body>
    </html>
    """          
    send_email_no_reply(subject=SUBJECT,recipient=RECIPIENT, body_text=BODY_TEXT, body_html=BODY_HTML)


def send_email_no_reply(subject=None, recipient="success@simulator.amazonses.com", body_text=None, body_html=None):

    # The character encoding for the email.
    CHARSET = "UTF-8"
    # Create a new SES resource and specify a region.
    AWS_REGION = "us-east-2"
    
    client = boto3.client('ses', region_name=AWS_REGION)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source="no-reply@modobio.com"
        )
       
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


##############################################################
#
# Push notifications
#

def _load_sns():
    """ Loads the AWS Simple Notification Service (SNS).

    Loads the boto3 SNS resource with some guards against being in
    an unsupported region.

    Returns
    -------
    sns : boto3.resources.factory.sns.ServiceResource
        The loaded boto3 resource.

    channel_app : dict
        A dict mapping the channel names to the platform applications, e.g.
        {'APNS': sns.PlatformApplication(arn='arn:aws:.../APNS/...'),
         'APNS_VOIP': sns.PlatformApplication(arn='arn:aws:.../APNS_VOIP/...')}

    Raises
    ------
    ClientError
        In case of boto3 load failure.
    """
    sns = boto3.resource('sns')

    try:
        apps = list(sns.platform_applications.all())
    except ClientError as err:
        if ('Error' in err.response
            and 'Message' in err.response['Error']
            and 'not supported in this region' in err.response['Error']['Message']):
            # SNS Push notifications are not available in current region.
            region = current_app.config['AWS_SNS_REGION']
            sns = boto3.resource('sns', region_name=region)
            apps = list(sns.platform_applications.all())
        else:
            # Some other error
            raise err

    channel_app = {app.arn.split('/')[1]: app for app in apps}

    return sns, channel_app

push_platforms = {
    'apple': 'APNS',
    'android': 'FCM',
    'debug': 'DEBUG/LOG'}

def register_device(
    device_token: str,
    device_os: str,
    device_description: str,
    current_endpoint: str=None
) -> str:
    """ Register a device for push notifications.

    Parameters
    ----------
    device_token : str
        The device token (called registration ID on Android) obtained from the OS to allow
        push notifications.

    device_os : str
        Which platform to register with. Currently supported: "apple", "android", or "debug".

    device_description : str
        Additional data stored with the device_token in the AWS SNS endpoint. Max length 2048.

    current_endpoint : str
        Current endpoint ARN, which may or may not be active.

    Returns
    -------
    str
        Endpoint ARN registered for this device.

    Raises
    ------
    ValueError
        On incorrect platform or device_description too long.
    """
    # Some info and explanation:
    #
    # https://docs.aws.amazon.com/sns/latest/dg/mobile-push-send.html
    #
    # ARN = string representation of resources on AWS
    # Platform Application = endpoint for a single platform channel.
    #   example arn:aws:sns:us-west-1:393511634479:app/APNS_SANDBOX/ApplePushNotification-Dev
    # Endpoint = endpoint for a single device within a channel.
    #   example arn:aws:sns:us-west-1:393511634479:endpoint/APNS_SANDBOX/
    #           ApplePushNotification-Dev/147a664a-2ca9-3109-91e6-1986d3f0d52a
    #
    # TODO: make use of endpoint params UserID and ChannelID

    if device_os not in push_platforms:
        raise ValueError('Device OS must be one of: {}'.format(', '.join(push_platforms.keys())))

    if len(device_description) > 2048:
        raise ValueError('Device description must be less than 2048 characters long.')

    # Not a real endpoint
    if device_os == 'debug':
        return push_platforms[device_os]

    sns, channel_app = _load_sns()

    if current_endpoint:
        # Check if current endpoint is still good, delete if not.
        endpoint = sns.PlatformEndpoint(arn=current_endpoint)
        try:
            endpoint.load()
        except (NotFoundException, InvalidParameterException):
            # Endpoint was deleted or has different parameters.
            endpoint.delete()
        else:
            if endpoint.attributes['Enabled'] == 'false':
                # Endpoint was disabled, delete.
                endpoint.delete()
            else:
                # Current endpoint still good
                return current_endpoint

    channel = push_platforms[device_os]

    if device_os == 'apple':
        # Apple has a separate channel for VoIP notifications.
        voip_channel = 'APNS_VOIP'

        # Apple also has separate channels for development.
        # TODO: fix this after ticket NRV-1838 is done.
        if current_app.env == 'development':
            channel += '_SANDBOX'
            voip_channel += '_SANDBOX'

        voip_app = channel_app[voip_channel]
        voip_endpoint = voip_app.create_platform_endpoint(
                Token=device_token,
                CustomUserData=device_description)

    app = channel_app[channel]
    endpoint = app.create_platform_endpoint(
            Token=device_token,
            CustomUserData=device_description)

    return endpoint.arn

def unregister_device(endpoint_arn: str):
    """ Delete endpoint.

    Parameters
    ----------
    endpoint_arn : str
        ARN of the endpoint to be deleted.
    """
    sns, channel_app = _load_sns()

    channel = endpoint_arn.split('/')[1]
    if channel.startswith('APNS'):
        # Apple has a separate channel for VoIP notifications.
        voip_channel = 'APNS_VOIP'

        # Apple also has separate channels for development.
        if channel.endswith('_SANDBOX'):
            voip_channel += '_SANDBOX'

        # There must be a better way to get an endpoint
        # given an platform application and a channel name.
        voip_app = channel_app[voip_channel]
        uuid = endpoint_arn.split('/')[-1]
        voip_arn = f'{voip_app.arn}/{uuid}'.replace('app', 'endpoint')

        endpoint = sns.PlatformEndpoint(arn=voip_arn)
        endpoint.delete()

    # Won't fail if endpoints don't exist.
    endpoint = sns.PlatformEndpoint(arn=endpoint_arn)
    endpoint.delete()

apple_tmpl = {
    'aps': {
        'alert': {
            'title': None,
            'body': None,
            'title-loc-key': None,
            'title-loc-args': None,
            'action-loc-key': None,
            'loc-key': None,
            'loc-args': None,
            'launch-image': None},
        'sound': None,
        'category': None,
        'thread-id': None,
        'badge': None,
        'content-available': None}}
"""
Template for Apple Push Notifications.

This template can be used for all types of push notifications to the Apple channel,
_except_ VoIP notification. See :attr:`apple_voip_tmpl` for that.

To use this template, simply import this template, set any keys you want to use, and
submit it as the `content` parameter of :func:`push_notification`. Any key set to
``None`` (the default), will be removed from the template before sending.

Custom keys can be added anywhere in the dict, but typically the ``aps`` root key and
all its nested keys are defined by Apple. Most likely you'll want to add custom keys
to the root of the template, at the same level as ``aps``.

For more information on Apple specific keys, see
https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/PayloadKeyReference.html#//apple_ref/doc/uid/TP40008194-CH17-SW1

- aps (dict): root key of Apple specific payload keys.
    - alert (dict): keys for a standard user alert message.
        * title (str): [required] title of the message.
        * body (str): [required] the actual message.
        * title-loc-key (str): a key that looks up the translation (localization) of the title in Localizable.strings.
        * title-loc-args (list(str)): a list of strings that replace formatting specifiers in the translated title.
        * action-loc-key (str): a key that looks up the translation or alternate text of the "View" button.
        * loc-key (str): a key that looks up the translation (localization) of the body in Localizable.strings.
        * loc-args (list(str)): a list of strings that replace formatting specifiers in the translated body.
        * launch-image (str): filename of image to show while app is loading from background.
    - badge (int): set app badge to this number; 0 removes badge.
    - sound (str): filename of custom sound to play when push notification arrives.
- custom key (any): add any custom keys to the root of this template.

Title and body are required **only if** alert is included. If you want to only set a badge, or only
include custom keys, then do _not_ set alert. If alert if included, then title and body must also
be set.

Not included in this template are:
- content-available: this will be set by choosing NotificationType.background.
- thread-id (str): app-specific identifier for grouping notifications (not used at the moment).
- category (str): custom actions directly from notification center (not used at the moment), see https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/SupportingNotificationsinYourApp.html#//apple_ref/doc/uid/TP40008194-CH4-SW26
"""

apple_voip_tmpl = {
    'type': 'incoming-call',
    'data': {
        'room_id': None,
        'staff_id': None,
        'staff_first_name': None,
        'staff_middle_name': None,
        'staff_last_name': None,
        'booking_description': None}}
"""
Template for Apple Push Notification to initiate a VoIP call.

Apple VoIP push notifications are sent through a different channel than regular push
notifications. This special channel sends notifications straight to the app for
processing without the user needing to interact with the notification first. VoIP
push notifications also have higher priority and an incoming VoIP push notification
will launch the app even if in the background or not running at all.

To use this template, simply import this template, set any keys you want to use, and
submit it as the `content` parameter of :func:`push_notification`. Any key set to
``None`` (the default), will be removed from the template before sending.

The contents of this template are not dictated by Apple, only our app.

- type (str): do **not** change this, it must be the literal string "incoming-call".
- data (dict): VoIP specific information.
    * room_id (int): ID of the Twilio video call room.
    * staff_id (int): staff member who is initiating the call.
    * staff_first_name (str): first name of the staff member.
    * staff_middle_name (str): middle name of the staff member.
    * staff_last_name (str): last name of the staff member.
    * booking_description (str): reason for the call.
"""


class NotificationType(enum.Enum):
    alert = 'A standard notification with a title and a body.'
    background = 'Trigger the app to reload data in the background.'
    badge = 'ONLY set the app badge to the specified number, no alert.'
    voip = 'A notification that will trigger a VoIP call.'


def push_notification(user_id: int, notification_type: NotificationType, content: dict):
    """ Send a push notification to the user.

    Parameters
    ----------
    user_id : int
        User ID of User to send message to. Notification will be send to all
        registered devices for this user.

    notification_type : str or NotificationType(Enum)
        What type of notification (alert, background, badge, voip) to send.

    content : dict
        Content of the push notification. See the ``apple_tmpl`` and ``apple_voip_tmpl``
        notification templates for a place to start.
    """
    if isinstance(notification_type, str):
        notification_type = NotificationType[notification_type]

    registered = (
        NotificationsPushRegistration
        .query
        .filter_by(user_id=user_id)
        .all())

    for device in registered:
        channel = device.arn.split('/')[1]
        if channel.startswith('APSN'):
            msg = _apple_push_notification(device.arn, notification_type, content)
        elif channel == 'FCM':
            msg = _android_push_notificaton(device.arn, notification_type, content)
        elif channel == 'LOG':
            msg = _debug_push_notification(notification_type, content)
        else:
            raise UnknownError(f'Unknown push notification channel {channel} for user {user_id}')

    return msg

def _apple_push_notification(arn: str, notification_type: NotificationType, content: dict):
    """ Send a push notification to an Apple device.

    Do not call this function directly, use :func:`push_notification` instead.
    """
    # Check content. Don't error, just set defaults.
    if notification_type == NotificationType.alert:
        if 'aps' not in content:
            content['aps'] = {}
        if 'alert' not in content['aps']:
            content['aps']['alert']
        if 'title' not in content['aps']['alert']:
            content['aps']['alert']['title'] = 'Modo Bio'
        if 'body' not in content['aps']['alert']:
            content['aps']['alert']['body'] = 'A message from Modo Bio.'
    elif notification_type == NotificationType.background:
        if 'aps' in content:
            sound = content['aps'].get('sound', None)
        content['aps'] = {
            'content-available': 1,
            'sound': sound}
    elif notification_type == NotificationType.badge:
        if 'aps' not in content:
            content['aps'] = {}
        if 'badge' not in content['aps']:
            content['aps']['badge'] = 0
        content['aps'].pop('alert', None)
    else:
        content.pop('aps', None)
        content['type'] = 'incoming-call'

    channel = 'APSN'
    if notification_type == NotificationType.voip:
        channel = 'APSN_VOIP'
        arn.replace('APSN', 'APSN_VOIP')

    message = dumps({channel: content})

    sns, _ = _load_sns()
    endpoint = sns.PlatformEndpoint(arn)
    reponse = endpoint.publish(TargetArn=arn, Message=message)

    #TODO: do something based on response.
    return message

def _android_push_notification(arn: str, notification_type: NotificationType, content: dict):
    """ Send a push notification to an Android device.

    Do not call this function directly, use :func:`push_notification` instead.
    """
    pass

def _debug_push_notification(notification_type: NotificationType, content: dict):
    """ Send a push notification to a debug log.

    Do not call this function directly, use :func:`push_notification` instead.
    """
    print(content)
    return content
