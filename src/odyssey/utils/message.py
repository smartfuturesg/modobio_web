import enum
import pathlib

import boto3

from botocore.exceptions import ClientError
from flask import current_app
from flask.json import dumps
from marshmallow import ValidationError

from odyssey.api import api
from odyssey.api.notifications.models import NotificationsPushRegistration
from odyssey.api.notifications.schemas import (
    ApplePushNotificationAlertSchema,
    ApplePushNotificationBackgroundSchema,
    ApplePushNotificationBadgeSchema,
    ApplePushNotificationVoipSchema)
from odyssey.utils.constants import PASSWORD_RESET_URL, REGISTRATION_PORTAL_URL
from odyssey.utils.errors import UnknownError

SUBJECTS = {"remote_registration_portal": "Modo Bio User Registration Portal", 
            "password_reset": "Modo bio password reset request - temporary link",
            "testing-bounce": "SES TEST EMAIL-BOUNCE",
            "testing-complaint": "SES TEST EMAIL-COMPLAINT",
            "testing-success": "SES TEST EMAIL",
            "account_deleted": "Modo Bio Account Deleted",
            "email-verification": "Verify Your Modo Bio Email"
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

    send_email(subject=SUBJECT, recipient=recipient, body_text=BODY_TEXT, body_html=BODY_HTML)

def send_email_verify_email(recipient, token, code):
    """
    Email sent to verifiy a user's email address.
    """

    SUBJECT = SUBJECTS["email-verification"]

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (f'Hello {recipient.firstname},\r\n'
                'We are delighted to welcome you to Modo Bio.\n'
                'Email Verification\n'
                'For security purposes, we need to confirm your email address for your Modo Bio account. Please click the following link to verify your address:\n'
                f'{api.base_url}/user/email-verification/token/{token}/\n'
                'Or alternatively, enter the following 4 digit code on your mobile application:\n'
                f'{code}\n'
                'Please check that this email was sent from verify@modobio.com'
                )

    # Get HTML from file and insert recipient information
    HTML_FILE = pathlib.Path(current_app.static_folder) / 'email-verify.html'
    with open(HTML_FILE) as fh:
        BODY_HTML = fh.read()
        BODY_HTML = BODY_HTML.replace('[user-first-name]', recipient.firstname)
        BODY_HTML = BODY_HTML.replace('[verification-link]', f'{api.base_url}/user/email-verification/token/{token}/')
        BODY_HTML = BODY_HTML.replace('XXXX', str(code))

    # route emails to AWS mailbox simulator when in dev environment
    if current_app.config['LOCAL_CONFIG'] and not recipient.email.endswith('sde.cz'):
        send_email(subject=SUBJECT, recipient="success@simulator.amazonses.com", body_text=BODY_TEXT, body_html=BODY_HTML, sender="verify@modobio.com")
    else:
        send_email(subject=SUBJECT, recipient=recipient.email, body_text=BODY_TEXT, body_html=BODY_HTML, sender="verify@modobio.com")

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

    send_email(subject=SUBJECT, recipient=recipient, body_text=BODY_TEXT, body_html=BODY_HTML)

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

    send_email(subject=SUBJECT, recipient=recipient, body_text=BODY_TEXT, body_html=BODY_HTML)

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


def send_email(subject=None, recipient="success@simulator.amazonses.com", body_text=None, body_html=None):

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

class PushNotificationType(enum.Enum):
    alert = 'A standard notification with a title and a body.'
    background = 'Trigger the app to reload data in the background.'
    badge = 'ONLY set the app badge to the specified number, no alert.'
    voip = 'A notification that will trigger a VoIP call.'


class PushNotification:
    """ A class for handling push notifications.

    To send push notifications, first register a device with :meth:`register_device`. Once
    one or more devices are registered, a push notification can be send. Select which type
    of notification to send. Then use one of the corresponding templates in this class as
    a starting point for the content of the notification. Finally, use :meth:`send` to send
    a notification to all devices registered to the user.

    To create the contents of a notification, start with one of the templates below and set
    any keys you want to use. Any key set to ``None`` (the default), will be removed from
    the template before sending.

    Custom keys can be added anywhere in the dict, but typically the ``aps`` root key and
    all its nested keys are defined by Apple. Most likely you'll want to add custom keys
    to the root of the template, at the same level as ``aps``.

    For more information on Apple specific keys, see
    https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/PayloadKeyReference.html#//apple_ref/doc/uid/TP40008194-CH17-SW1

    Attributes
    ----------
    platforms : dict
        These major platforms are supported by our notification system. Also includes a debug
        "platform". This dict maps platforms to channel names.

    apple_alert_tmpl : dict
        This template can be used to send alert messages to Apple devices.

        - aps (dict): root key of Apple specific payload keys.
            - alert (dict): keys for a standard user alert message.
                - title (str): [required] title of the message.
                - body (str): [required] the actual message.
                - title-loc-key (str): a key that looks up the translation (localization) of the title in Localizable.strings.
                - title-loc-args (list(str)): a list of strings that replace formatting specifiers in the translated title.
                - action-loc-key (str): a key that looks up the translation or alternate text of the "View" button.
                - loc-key (str): a key that looks up the translation (localization) of the body in Localizable.strings.
                - loc-args (list(str)): a list of strings that replace formatting specifiers in the translated body.
                - launch-image (str): filename of image to show while app is loading from background.
            - badge (int): set app badge to this number; 0 removes badge.
            - sound (str): filename of custom sound to play when push notification arrives.
            - thread-id (str): [not used] app-specific identifier for grouping notifications.
            - category (str): [not used] custom actions directly from notification center.
        - custom key (any): add any custom keys to the root of this template.

    apple_background_tmpl : dict
        This template can be used to trigger a background update in the app.

        - aps (dict): root key of Apple specific payload keys.
            - content-available (int): [required] must be set to 1.
            - badge (int): set app badge to this number; 0 removes badge.
            - sound (str): filename of custom sound to play when push notification arrives.
        - custom key (any): add any custom keys to the root of this template.

    apple_badge_tmpl : dict
        This template can be used to set the app badge to a specific number.

        - aps (dict): root key of Apple specific payload keys.
            - badge (int): [required] set app badge to this number; 0 removes badge.
            - sound (str): filename of custom sound to play when push notification arrives.
        - custom key (any): add any custom keys to the root of this template.

    apple_voip_tmpl : dict
        This template can be used to initiate a VoIP call. The contents of this template
        are not dictated by Apple, it does not use the ``aps`` root key.

        - type (str): do **not** change this, it must be the literal string "incoming-call".
        - data (dict): VoIP specific information.
            - booking_id (int): ID of the Twilio video call room.
            - booking_description (str): reason for the call.
            - staff_id (int): staff member who is initiating the call.
            - staff_first_name (str): first name of the staff member.
            - staff_middle_name (str): middle name of the staff member.
            - staff_last_name (str): last name of the staff member.
    """

    platforms = {
        'apple': 'APNS',
        'android': 'FCM',
        'debug': 'DEBUG/LOG'}

    apple_alert_tmpl = {
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
            'category': None,
            'thread-id': None,
            'badge': None,
            'sound': None}}

    apple_background_tmpl = {
        'aps': {
            'content-available': 1,
            'badge': None,
            'sound': None}}

    apple_badge_tmpl = {
        'aps': {
            'badge': None,
            'sound': None}}

    apple_voip_tmpl = {
        'type': 'incoming-call',
        'data': {
            'booking_id': None,
            'booking_description': None,
            'staff_id': None,
            'staff_first_name': None,
            'staff_middle_name': None,
            'staff_last_name': None}}

    def __init__(self):
        """ Initiate the push notification system.

        Loads the AWS Simple Notification Service (SNS) as part of initialization process.
        """
        region = current_app.config['AWS_SNS_REGION']
        self.sns = boto3.resource('sns', region_name=region)

        apps = list(self.sns.platform_applications.all())
        self.channel_platapp = {app.arn.split('/')[1]: app for app in apps}

    def register_device(
        self,
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
        # TODO: make use of endpoint params UserID and ChannelID?

        if device_os not in self.platforms:
            raise ValueError('Device OS must be one of: {}'.format(', '.join(self.platforms.keys())))

        if len(device_description) > 2048:
            raise ValueError('Device description must be less than 2048 characters long.')

        # Not a real endpoint
        if device_os == 'debug':
            return self.platforms[device_os]

        if current_endpoint:
            # Check if current endpoint is still good, delete if not.
            endpoint = self.sns.PlatformEndpoint(arn=current_endpoint)
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

        channel = self.platforms[device_os]

        if device_os == 'apple':
            # Apple has a separate channel for VoIP notifications.
            voip_channel = 'APNS_VOIP'

            # Apple also has separate channels for development.
            # TODO: fix this after ticket NRV-1838 is done.
            if current_app.env == 'development':
                channel += '_SANDBOX'
                voip_channel += '_SANDBOX'

            voip_app = self.channel_platapp[voip_channel]
            voip_endpoint = voip_app.create_platform_endpoint(
                    Token=device_token,
                    CustomUserData=device_description)

        app = self.channel_platapp[channel]
        endpoint = app.create_platform_endpoint(
                Token=device_token,
                CustomUserData=device_description)

        return endpoint.arn

    def unregister_device(self, arn: str):
        """ Delete endpoint.

        Parameters
        ----------
        arn : str
            ARN of the device endpoint to be deleted.
        """
        channel = arn.split('/')[1]
        if channel.startswith('APNS'):
            # Apple has a separate channel for VoIP notifications.
            voip_channel = 'APNS_VOIP'

            # Apple also has separate channels for development.
            if channel.endswith('_SANDBOX'):
                voip_channel += '_SANDBOX'

            # There must be a better way to get an endpoint
            # given an platform application and a channel name.
            voip_app = self.channel_platapp[voip_channel]
            uuid = arn.split('/')[-1]
            voip_arn = f'{voip_app.arn}/{uuid}'.replace('app', 'endpoint')

            endpoint = self.sns.PlatformEndpoint(arn=voip_arn)
            endpoint.delete()

        # Won't fail if endpoints don't exist.
        endpoint = self.sns.PlatformEndpoint(arn=arn)
        endpoint.delete()

    def send(self, user_id: int, notification_type: PushNotificationType, content: dict) -> dict:
        """ Send a push notification to the user.

        Parameters
        ----------
        user_id : int
            User ID of User to send message to. Notification will be send to all
            registered devices for this user.

        notification_type : str or PushNotificationType(Enum)
            What type of notification (alert, background, badge, voip) to send.

        content : dict
            Content of the push notification. See the ``apple_tmpl`` and ``apple_voip_tmpl``
            notification templates for a place to start.

        Returns
        -------
        dict
            A dict with the channel name as key and the JSON encoded string of the message
            as it was sent to the registrered device(s) as value.

        Raises
        ------
        UnknownError
            If the user has no registered devices or if the device is registered with an
            unknown channel.
        """
        if isinstance(notification_type, str):
            notification_type = PushNotificationType[notification_type]

        registered = (
            NotificationsPushRegistration
            .query
            .filter_by(user_id=user_id)
            .all())

        if not registered:
            raise UnknownError(
                message=f'User {user_id} does not have any registered devices.'
                         'Connect with POST /notifications/push/register/{user_id}/ first.')

        for device in registered:
            channel = device.arn.split('/')[1]
            if channel.startswith('APNS'):
                message = self._send_apple(device.arn, notification_type, content)
            elif channel == 'FCM':
                message = self._send_android(device.arn, notification_type, content)
            elif channel == 'LOG':
                message = self._send_log(notification_type, content)
            else:
                raise UnknownError(f'Unknown push notification channel {channel} for user {user_id}')

        return message

    def _send_apple(self, arn: str, notification_type: PushNotificationType, content: dict) -> dict:
        """ Send a push notification to an Apple device.

        Do not call this function directly, use :meth:`send` instead.
        """
        # Check content. Don't error, just set defaults.
        if notification_type == PushNotificationType.alert:
            schema = ApplePushNotificationAlertSchema
        elif notification_type == PushNotificationType.background:
            schema = ApplePushNotificationBackgroundSchema
        elif notification_type == PushNotificationType.badge:
            schema = ApplePushNotificationBadgeSchema
        else:
            schema = ApplePushNotificationVoipSchema

        try:
            processed = schema().dumps(content)
        except ValidationError as err:
            raise UnknownError(message='\n'.join(err.messages))

        channel = arn.split('/')[1]
        uuid = arn.split('/')[-1]

        if notification_type == PushNotificationType.voip:
            if channel == 'APNS':
                channel = 'APNS_VOIP'
            elif channel == 'APNS_SANDBOX':
                channel = 'APNS_VOIP_SANDBOX'

        app = self.channel_platapp[channel]
        correct_arn = f'{app.arn}/{uuid}'.replace('app', 'endpoint')

        message = {channel: processed}

        endpoint = self.sns.PlatformEndpoint(arn=correct_arn)
        # Yes, the message got dumped twice in one day. Ouch!
        response = endpoint.publish(TargetArn=correct_arn, Message=dumps(message))

        return message

    def _send_android(self, arn: str, notification_type: PushNotificationType, content: dict) -> dict:
        """ Send a push notification to an Android device.

        Do not call this function directly, use :meth:`send` instead.
        """
        pass

    def _send_log(self, notification_type: PushNotificationType, content: dict) -> dict:
        """ Send a push notification to a debug log.

        Do not call this function directly, use :math:`send` instead.
        """
        print(content)
        return content
