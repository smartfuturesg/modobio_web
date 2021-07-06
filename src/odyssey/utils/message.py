import enum
import pathlib

import boto3

from dataclasses import dataclass

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
    if current_app.config['DEV'] and not recipient.endswith('sde.cz'):
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
    if current_app.config['DEV'] and not recipient.email.endswith('sde.cz'):
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
    if current_app.config['DEV'] and not recipient.endswith('sde.cz'):
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
    if current_app.config['DEV']:
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
    send_email(subject=SUBJECT,recipient=RECIPIENT, body_text=BODY_TEXT, body_html=BODY_HTML)


def send_email(subject=None, recipient="success@simulator.amazonses.com", body_text=None, body_html=None, sender="no-reply@modobio.com"):

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

@dataclass
class EndpointARN:
    """ AWS Resource Number (ARN) for SNS application platforms and endpoints.

    This class takes a string representation of an ARN and parses it into endpoint
    parameters. Each parameter can be set individually. When the ARN is accessed
    it will reflect the changed parameters.

    Examples
    --------

    The primary function of this class is to change Apple push notification
    endpoints into corresponding Apple VoIP endpoints.

        >>> ep = EndpointARN('arn:aws:sns:us-west-1:393511634479:endpoint/APNS_SANDBOX/ModoBioClient/848daccf-0944-3593-bde0-7c6a9f227c47')
        >>> ep.channel
        APNS_SANDBOX
        >>> ep.is_voip
        False
        >>> ep.is_voip = True
        >>> ep.channel
        APNS_VOIP_SANDBOX
        >>> ep.arn
        arn:aws:sns:us-west-1:393511634479:endpoint/APNS_VOIP_SANDBOX/ModoBioClient/848daccf-0944-3593-bde0-7c6a9f227c47

    It is also possible to convert a platform application into an endpoint (if the device
    UUID is known), or vice versa.

        >>> ep.is_app
        False
        >>> ep.is_app = True
        >>> ep.arn
        arn:aws:sns:us-west-1:393511634479:app/APNS_VOIP_SANDBOX/ModoBioClient
    """

    prefix: str='arn'
    """ The prefix of the ARN, always the literal string "arn".

    :type: str
    :default: "arn"
    """

    main: str='aws'
    """ The main part of the ARN, always the literal string "aws".

    :type: str
    :default: "aws"
    """

    resource: str=''
    """ The resource part of the ARN, the name of the AWS resource this ARN belongs to.

    :type: str
    :default: *empty string*
    """

    region: str=''
    """ The region part of the ARN, the AWS region this ARN operates in.

    :type: str
    :default: *empty string*
    """

    account_id: str=''
    """ The account ID part of the ARN, the account number of the user this ARN belongs to.

    :type: str
    :default: *empty string*
    """

    type: str=''
    """ The type part of SNS endpoint, either "app" for Platform Application, or "endpoint" for an Endpoint.

    :type: str
    :default: *empty string*
    """

    label: str=''
    """ The label part of the ARN. This is usually set to the name of the app receiving the push notifications.

    :type: str
    :default: *empty string*
    """

    device: str=''
    """ The device part of the ARN, a UUID generated by AWS when the device endpoint was created.

    :type: str
    :default: *empty string*
    """

    is_app: bool=False
    """ Whether this is an application platform. If not, this is a device endpoint.

    :type: bool
    :default: False
    """

    is_voip: bool=False
    """ Whether or not the ARN represents a VoIP application platform or endpoint.

    :type: bool
    :default: False
    """

    is_sandbox: bool=False
    """ Whether or not the ARN represents a sandboxed (development, testing) application platform or endpoint.

    :type: bool
    :default: False
    """

    def __init__(self, arn: str=''):
        """ Instantiate an EndpointARN from an ARN string.

        Keyword Arguments
        -----------------
        arn : str
            The ARN string to parse.
        """
        self._channel = ''
        self.arn = arn

    @property
    def arn(self) -> str:
        """ Returns the ARN as a string.

        Returns
        -------
        str
            The ARN as a string.
        """
        device = ''
        if not self.is_app:
            device = f'/{self.device}'

        return (f'{self.prefix}:{self.main}:{self.resource}:{self.region}:{self.account_id}:'
                f'{self.type}/{self.channel}/{self.label}{device}')

    @arn.setter
    def arn(self, arn: str):
        """ Extract endpoint parameters from an ARN string.

        Parameters
        ----------
        arn : str
            The ARN as a string.
        """
        if not arn:
            return

        aws_part, sns_part = arn.rsplit(':', maxsplit=1)
        self.prefix, self.main, self.resource, self.region, self.account_id = aws_part.split(':')
        self.is_app = sns_part.startswith('app')

        if self.is_app:
            self.type, self.channel, self.label = sns_part.split('/')
        else:
            self.type, self.channel, self.label, self.device = sns_part.split('/')

    @property
    def channel(self) -> str:
        """ Returns the push notification channel.

        Returns
        -------
        str
            The channel of the platform application or endpoint.
        """
        channel = self._channel
        if channel == 'APNS':
            if self.is_voip:
                channel += '_VOIP'
            if self.is_sandbox:
                channel += '_SANDBOX'
        return channel

    @channel.setter
    def channel(self, channel: str):
        """ Extract endpoint setting from the channel.

        Parameters
        ----------
        channel : str
            The channel name.
        """
        if channel.startswith('APNS'):
            self._channel = 'APNS'
            if '_VOIP' in channel:
                self.is_voip = True
            if '_SANDBOX' in channel:
                self.is_sandbox = True
        else:
            self._channel = channel

    def __str__(self):
        return self.arn


class PushNotificationPlatform(enum.Enum):
    """ Enumerates push notification platforms and maps them to channels. """
    apple = 'APNS'
    android = 'FCM'
    debug = 'arn:aws::::app/DEBUG/LOG'


class PushNotificationType(enum.Enum):
    """ Enumerates the type of push notification that can be send. """
    alert = 'A standard notification with a title and a body.'
    background = 'Trigger the app to reload data in the background.'
    badge = 'ONLY set the app badge to the specified number, no alert.'
    voip = 'A notification that will trigger a VoIP call.'


class PushNotification:
    """ A class for handling push notifications.

    To send push notifications, first register a device with :meth:`register_device`. Once
    one or more devices are registered, a push notification can be send. Select which type
    of notification to send (see :class:`PushNotificationType`). Then use one of the
    templates in this class as a starting point for the content of the notification. Finally,
    use :meth:`send` to send a notification to all devices registered to the user.

    To create the contents of a notification, start with one of the templates below and set
    any keys you want to use. Any key set to ``None`` (the default), will be removed from
    the template before sending.

    Custom keys can be added anywhere in the dict, but typically the ``aps`` root key and
    all its nested keys are defined by Apple. Most likely you'll want to add custom keys
    to the root of the template, at the same level as ``aps``.

    For more information on Apple specific keys, see
    https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/PayloadKeyReference.html#//apple_ref/doc/uid/TP40008194-CH17-SW1

    Glossary
    --------

    A short overview of terms used in setting up and sending push notifications using the
    AWS SNS platform. For more info on AWS SNS, see https://docs.aws.amazon.com/sns/latest/dg/mobile-push-send.html

    .. glossary::

        ARN
            String representation of resources on AWS

        Platform Application
            A channel as registered with a push notification provider, e.g. Apple APNS, or Android FCM.

        Endpoint
            Endpoint for a single device within a channel. Messages send to an endpoint will be send to just that device.

        Topic
            A collection of endpoints. Each device/endpoint has to subscribe to the topic. Topics can be used for general messages to all users, e.g. tip of the day, network outages, general updates.

    Attributes
    ----------
    apple_alert_tmpl : dict
        This template can be used to send alert messages to Apple devices. ::

            {'aps': {
                'alert': {
                    'title': str,
                    'body': str,
                    'title-loc-key': str,
                    'title-loc-args': [str],
                    'action-loc-key': str,
                    'loc-key': str,
                    'loc-args': [str],
                    'launch-image': str},
                'category': str,
                'thread-id': str,
                'badge': int,
                'sound': str},
             'custom': dict}

        :aps: root key of Apple specific payload keys.
        :alert: keys for a standard user alert message.
        :title: **[required]** title of the message.
        :body: **[required]** the actual message.
        :title-loc-key: a key that looks up the translation (localization) of the title in Localizable.strings.
        :title-loc-args: a list of strings that replace formatting specifiers in the translated title.
        :action-loc-key: a key that looks up the translation or alternate text of the "View" button.
        :loc-key: a key that looks up the translation (localization) of the body in Localizable.strings.
        :loc-args: a list of strings that replace formatting specifiers in the translated body.
        :launch-image: filename of image to show while app is loading from background.
        :badge: set app badge to this number; 0 removes badge.
        :sound: filename of custom sound to play when push notification arrives.
        :thread-id: [*not used*] app-specific identifier for grouping notifications.
        :category: [*not used*] custom actions directly from notification center.
        :custom: add any custom keys to the root of this template.

    apple_background_tmpl : dict
        This template can be used to trigger a background update in the app. The notification
        may contain custom keys, but nothing else besides "content-available" in the "aps" dict. ::

            {'aps': {
                'content-available': 1},
             'custom': dict}

        :content-available: **[required]** must be set to 1.

    apple_badge_tmpl : dict
        This template can be used to set the app badge to a specific number. Badge may also be
        combined with "alert", see :attr:`apple_alert_tmpl`. Use this template to ONLY send a
        badge number update. ::

            {'aps': {
                'badge': int,
                'sound': str},
             'custom': dict}

        :badge: **[required]** set app badge to this number; 0 removes badge.
        :sound: filename of custom sound to play when push notification arrives.

    apple_voip_tmpl : dict
        This template can be used to initiate a VoIP call. The contents of this template
        are not dictated by Apple, it does not use the ``aps`` root key. ::

            {'aps': {},
             'type': 'incoming-call',
             'data': {
                'booking_id': int,
                'booking_description': str,
                'staff_id': int,
                'staff_first_name': str,
                'staff_middle_name': str,
                'staff_last_name': str,
                'staff_profile_picture: str},
             'custom': dict}

        :aps: must be present, but empty; entries in ``aps`` are ignored.
        :type: do not change this, it must be the literal string "incoming-call".
        :data: VoIP specific information.
        :booking_id: ID of the Twilio video call room.
        :booking_description: reason for the call.
        :staff_id: staff member who is initiating the call.
        :staff_first_name: first name of the staff member.
        :staff_middle_name: middle name of the staff member.
        :staff_last_name: last name of the staff member.
        :staff_profile_picture: profile picture url of the staff member.

    sns : boto3.Resource
        The active connection with AWS SNS through :mod:`boto3`.

    channel_platapp : dict
        Maps channel names to platform applications for all platform applications on SNS.
    """

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
        'aps': {'content-available': 1}}

    apple_badge_tmpl = {
        'aps': {
            'badge': None,
            'sound': None}}

    apple_voip_tmpl = {
        'aps': {},
        'type': 'incoming-call',
        'data': {
            'booking_id': None,
            'booking_description': None,
            'staff_id': None,
            'staff_first_name': None,
            'staff_middle_name': None,
            'staff_last_name': None,
            'staff_profile_picture': None}}

    def __init__(self):
        """ Initiate the push notification system.

        Loads the AWS Simple Notification Service (SNS) as part of initialization process.
        """
        region = current_app.config['AWS_SNS_REGION']
        self.sns = boto3.resource('sns', region_name=region)

        apps = list(self.sns.platform_applications.all())
        self.channel_platapp = {EndpointARN(app.arn).channel: app for app in apps}

    def register_device(
        self,
        device_token: str,
        device_platform: PushNotificationPlatform,
        device_info: dict={},
        current_endpoint: str=None,
        voip: bool=False
    ) -> str:
        """ Register a device for push notifications.

        Parameters
        ----------
        device_token : str
            The device token (called registration ID on Android) obtained from the OS to allow
            push notifications.

        device_platform : str or PushNotificationPlatform
            Which platform to register with. Currently supported: "apple", "android", or "debug".

        Keyword Arguments
        -----------------
        device_info : dict
            Additional data stored with the device_token in the AWS SNS endpoint.
            Max length after conversion to JSON: 2048.

        current_endpoint : str
            ARN of existing endpoint for this device token, which may or may not be active.

        voip : bool
            Whether or not this device token is for a VoIP channel. Only used by Apple devices,
            ignored by Android devices.

        Returns
        -------
        str
            Endpoint ARN registered for this device.

        Raises
        ------
        ValueError
            On incorrect platform or device_description too long.
        """

        if isinstance(device_platform, str):
            device_platform = PushNotificationPlatform[device_platform]

        # Not a real endpoint
        if device_platform == PushNotificationPlatform.debug:
            return device_platform.value

        if current_endpoint:
            # Check if current endpoint is still good, delete if not.
            endpoint = self.sns.PlatformEndpoint(arn=current_endpoint)
            try:
                endpoint.load()
            except (self.sns.meta.client.exceptions.NotFoundException,
                    self.sns.meta.client.exceptions.InvalidParameterException):
                # Endpoint was deleted or has different parameters.
                endpoint.delete()
            else:
                if endpoint.attributes['Enabled'] == 'false':
                    # Endpoint was disabled, delete.
                    endpoint.delete()
                else:
                    # Current endpoint still good
                    return current_endpoint

        device_description = dumps(device_info)
        if len(device_description) > 2048:
            raise ValueError('Device info as JSON must be less than 2048 characters long.')

        channel = device_platform.value

        if device_platform == PushNotificationPlatform.apple:
            # Apple has a separate channel for VoIP notifications.
            if voip:
                channel += '_VOIP'

            # Apple also has separate channels for development.
            if current_app.config['DEV']:
                channel += '_SANDBOX'

        app = self.channel_platapp[channel]
        try:
            new_endpoint = app.create_platform_endpoint(
                Token=device_token,
                CustomUserData=device_description)
        # Boto3 errors are incredibly stupid. You cannot import them, they are generated on the fly.
        except self.sns.meta.client.exceptions.InvalidParameterException as err:
            # "Endpoint xxx already exists with the same Token, but different attributes."
            # This happens when the database was cleared, but the endpoints still exist on AWS.
            #
            # The offending arn is in the error message somewhere,
            # but we'll have to do some ugly parsing to get to it.
            msg = err.response['Error']['Message'].split()
            for m in msg:
                if m.startswith('arn:'):
                    # Make sure this is a device endpoint, don't want to accidentally delete App Platform.
                    old_arn = EndpointARN(arn=m)
                    if not old_arn.is_app:
                        old_endpoint = self.sns.PlatformEndpoint(arn=old_arn.arn)
                        old_endpoint.delete()

                        # Now try again
                        new_endpoint = app.create_platform_endpoint(
                            Token=device_token,
                            CustomUserData=device_description)

                        break

        return new_endpoint.arn

    def unregister_device(self, arn: str):
        """ Delete endpoint.

        Parameters
        ----------
        arn : str
            ARN of the device endpoint to be deleted.
        """
        # Won't fail if endpoint doesn't exist.
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
            Content of the push notification. See the templates in this class
            for a place to start.

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
            arn = EndpointARN(device.arn)
            if arn.channel.startswith('APNS'):
                message = self._send_apple(device, notification_type, content)
            elif arn.channel == 'FCM':
                message = self._send_android(device, notification_type, content)
            elif arn.channel == 'DEBUG':
                message = self._send_log(notification_type, content)
            else:
                raise UnknownError(f'Unknown push notification channel {arn.channel} for user {user_id}')

        return message

    def _send_apple(self, device, notification_type: PushNotificationType, content: dict) -> dict:
        """ Send a push notification to an Apple device.

        Do not call this function directly, use :meth:`send` instead.
        """
        # Check content and convert to JSON.
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

        # Where to send it to?
        if notification_type == PushNotificationType.voip:
            endp = EndpointARN(device.voip_arn)
        else:
            endp = EndpointARN(device.arn)

        # Message needs a special attribute to tell SNS what type it is.
        # SNS can tell by some heuristic, but doesn't always get it right.
        push_type = notification_type.name
        if notification_type == PushNotificationType.badge:
            push_type = PushNotificationType.alert.name

        message_attr = {
            'AWS.SNS.MOBILE.APNS.PUSH_TYPE': {
                'DataType': 'String',
                'StringValue': push_type}}

        message = {endp.channel: processed}

        endpoint = self.sns.PlatformEndpoint(arn=endp.arn)

        # Yes, the message got dumped twice in one day. Ouch!
        response = endpoint.publish(
            TargetArn=endp.arn,
            Message=dumps(message),
            MessageStructure='json',
            MessageAttributes=message_attr)

        return message

    def _send_android(self, device, notification_type: PushNotificationType, content: dict) -> dict:
        """ Send a push notification to an Android device.

        Do not call this function directly, use :meth:`send` instead.
        """
        return content

    def _send_log(self, notification_type: PushNotificationType, content: dict) -> dict:
        """ Send a push notification to a debug log.

        Do not call this function directly, use :math:`send` instead.
        """
        print(content)
        return content
