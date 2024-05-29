import os

import schedule
import time
import subprocess


def job():
    subprocess.run(["python", "D:/Price_transparency_work/price_transparency.py"])


os.chdir(r'D:/Price_transparency_work')

schedule.every().day.at("09:12").do(job)
schedule.every().day.at("11:46").do(job)
schedule.every().day.at("17:01").do(job)
schedule.every().day.at("19:31").do(job)
schedule.every().day.at("12:02").do(job)

while True:
    schedule.run_pending()
    time.sleep(10)
