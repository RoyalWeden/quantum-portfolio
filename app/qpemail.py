from app import config, mongodb
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

context = ssl.create_default_context()

def send_email(receiver_email, subject, message):
    with smtplib.SMTP_SSL(config['GMAIL_SMTP'], config['GMAIL_PORT'], context=context) as server:
        server.login(config['GMAIL_ADDRESS'], config['GMAIL_PASSWORD'])
        message["Subject"] = subject
        message["From"] = config['GMAIL_ADDRESS']
        message["To"] = receiver_email
        server.sendmail(config['GMAIL_ADDRESS'], receiver_email, message.as_string())

def verify_code_email(user):
    message = MIMEMultipart("alternative")
    code = mongodb.pass_decrypt(user['verification']['code'])
    url_uuid = str(user['verification']['uuid'])
    url_id = str(user['_id'])
    if config['FLASK_ENV'] == 'development':
        web_url = 'localhost:5000'
    elif config['FLASK_ENV'] == 'development':
        web_url = 'quantumportfolio.herokuapp.com'
    url = f'http://{web_url}/verify?a={url_uuid}&b={url_id}'
    text = f"""\
Hello,

To begin using your account and optimizing a quantum portfolio, please use the following \
verification code to verify your account at the url below within the next 10 minutes:

Code: {code}
URL: {url}

QuantumPortfolio
"""
    html = f"""\
<html>
    <body>
        <p>Hello,<br>
            To begin using your account and optimizing a quantum portfolio, please use the following 
            verification code to verify your account at the url below within the next 10 minutes:
            <br><br>
            <b>Code:</b> {code}<br>
            <b>URL:</b> {url}
        </p>
    </body>
</html>
"""
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    send_email(user['email'], 'QuantumPortfolio Account Verification', message)