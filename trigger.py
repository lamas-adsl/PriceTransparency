import configparser
import os
import schedule
import time
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, body, to_email):
    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")
    from_email, app_password = config.get('EMAIL', 'ADDRESS'), config.get('EMAIL', 'APP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = from_email, to_email, subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, app_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")


def job():
    try:
        subprocess.run(["python", "D:/Price_transparency_work/price_transparency.py"])
        # raise ValueError("An error occurred in the program")
    except Exception as e:
        print(f'Error: {e}')
        send_email('Program Failure Notification', str(e), 'RachelL@cbs.gov.il')
        send_email('Program Failure Notification', str(e), 'EstherL@cbs.gov.il')


os.chdir(r'D:/Price_transparency_work')

schedule.every().day.at("09:12").do(job)
schedule.every().day.at("17:01").do(job)
schedule.every().day.at("19:31").do(job)
schedule.every().day.at("12:02").do(job)

while True:
    schedule.run_pending()
    time.sleep(10)
