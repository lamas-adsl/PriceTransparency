import configparser
import glob
import logging
import pandas as pd
from ast import literal_eval

import requests

import network_marketing
import create_folder_per_market as f
import insert_to_db as db
from datetime import datetime, date, timedelta
import ntpath
import time
import traceback
import os
BASE_PATH = os.getcwd()
config = configparser.ConfigParser()
config.read("config.ini")

# ==========================================================================================================================
# Application that running on every chains that shown in
# "https://www.gov.il/he/departments/legalInfo/cpfta_prices_regulations"
# and downloads all PriceFull and Promofull zips that was upload in this day.
# ==========================================================================================================================

def internet_on():
    try:
        req = requests.head('http://www.google.com/', timeout=2)
        # HTTP errors are not raised by default, this statement does that
        req.raise_for_status()
        return True
    except requests.HTTPError as e:
        print("Checking internet connection failed, status code {0}.".format(
            e.response.status_code))
        db.add_to_table('dbo.InsertLogException', 'FAILED', f'internet connection failed on: {str(e)}', datetime.now(), datetime.now())
    except requests.ConnectionError:
        print("No internet connection available.")
        db.add_to_table('dbo.InsertLogException', 'FAILED', f'No internet connection available', datetime.now(), datetime.now())
        return False


def main():
    internet_on()
    print('START!')
    start = datetime.now()
    global excel_table
    excel_table = pd.DataFrame()
    try:
        excel_table = network_marketing.create_network_marketing_table(
            "https://www.gov.il/he/departments/legalInfo/cpfta_prices_regulations")
        # insert to DB runtimes table row that was shown that we start scraping
        db.add_to_table('dbo.insertruntimes', "0000000000000", datetime.now(), 'NULL', 0)
        time.sleep(10)
    except Exception as e:
        end = datetime.now()
        # insert to DB runtimes table row that was shown that we finish (fail) the scraping
        db.add_to_table('dbo.insertruntimes', "9999999999999", 'NULL', end, 0)
        # insert to DB logException table row with description on the exception
        db.add_to_table('dbo.InsertLogException', 'FAILED',
                        type(e).__name__+" at line "+str(e.__traceback__.tb_lineno)+" of "+ntpath.basename(__file__)+": "+str(e),
                        start, end)
    try:
        if excel_table.empty:
            excel_table = pd.read_csv('./markets_list.csv', encoding='ISO-8859-8', converters={'URL': literal_eval})
            excel_table['שם משתמש'] = excel_table['שם משתמש'].apply(lambda x: literal_eval(x) if type(x) is str else None)
            excel_table['סיסמא'] = excel_table['סיסמא'].apply(lambda x: literal_eval(x) if type(x) is str else None)
        f.get_url_market(excel_table)
    except Exception as e:
        db.add_to_table('dbo.InsertLogException', 'FAILED',
                        type(e).__name__ + " at line " + str(e.__traceback__.tb_lineno) + " of " + ntpath.basename(
                            __file__) + ": " + str(e),
                        start, end)
    try:
        db.add_to_table('dbo.insertruntimes', "9999999999999", 'NULL', datetime.now(),0)
        date_n = f.zip_all_chains()
    except Exception as e:
        end = datetime.now()
        db.add_to_table('dbo.insertruntimes', "9999999999999", 'NULL', end, 0)
        db.add_to_table('dbo.InsertLogException', 'FAILED', type(e).__name__+" at line "+str(e.__traceback__.tb_lineno)+" of "+ntpath.basename(__file__)+": "+str(e), start, end)


if __name__ == "__main__":
    try:
        logging.basicConfig(filename=f'logs.txt', level=logging.INFO)
        main()

    except:
        logging.error(f'---------------- EXCEPTION ---------------- {datetime.now()}')
        logging.error(traceback.format_exc())
