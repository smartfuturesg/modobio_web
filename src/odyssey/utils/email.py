import boto3
from botocore.exceptions import ClientError
from flask import current_app

from odyssey.utils.constants import PASSWORD_RESET_URL, REGISTRATION_PORTAL_URL

SUBJECTS = {"remote_registration_portal": "Modo Bio User Registration Portal", 
            "password_reset": "Modo bio password reset request - temporary link",
            "testing-bounce": "SES TEST EMAIL-BOUNCE",
            "testing-complaint": "SES TEST EMAIL-COMPLAINT",
            "testing-success": "SES TEST EMAIL"
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
    if current_app.env == "development" and not recipient.endswith('sde.cz'):
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
    if current_app.env == "development" and not recipient.endswith('sde.cz'):
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