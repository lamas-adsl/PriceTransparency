import configparser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, body, to_email):
    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")
    from_email, app_password = config.get('EMAIL', 'ADDRESS'), config.get('EMAIL', 'APP_PASSWORD')

    html_body = f"""
    <html>
      <head></head>
      <body>
        <p style="color: red;">{body}</p>
      </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = from_email, to_email, subject
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, app_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")


try:
    x = 5 / 0
    # raise ValueError("An error occurred in the program")
except Exception as e:
    print(f'Error: {e}')
    send_email('Hi from python', f'NOTHING exept {e.__str__()}', 'EstherL@cbs.gov.il')
