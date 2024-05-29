import ntpath
import os
import re
import time
import zipfile
from datetime import datetime

import read_market_web as wb
from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import wget
import insert_to_db as db

excel_name_file = "פירטי רישתות שיווק"
full_table = None
row = 1
column = 0
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def create_table():
    """
    Create dataFrame table
    :return: dataframe empty table
    """
    data = {'שם', 'גישה', 'URL', 'שם משתמש', 'סיסמא'}
    full_table = pd.DataFrame(columns=data)
    return full_table


def insert_value_to_table(table, name, valid, url, user_name=None, password=None):
    """
    Insert row of chain details to the dataFrame table
    :param table: dataframe type, name: chain name, valid: boolean if the url is valid
    :param url: of the chain web, user_name: if was needs user to login, password: if was needs user to login
    :return: dataframe table
    """
    print('Read ' + name + '...')
    data = {'שם': name, 'גישה': valid, 'URL': url, 'שם משתמש': user_name,
            'סיסמא': password}
    try:
        table = pd.concat([table, pd.DataFrame.from_records([data])])
    except Exception as e:
        print(e)
    return table


def check_valid_url(url):
    """
    Try to connect to the web chain
    :param url: of the chain web
    :return: True if valid, False if not
    """
    try:
        proxies = {'https': 'http://192.168.174.80:8080'}
        response = requests.get(url, verify=False)#, proxies=proxies,timeout=60)
    except requests.ConnectionError as exception:
        return False
    return True


def create_network_marketing_table(url):
    """
    Main function that create csv table that contains all chain details from
    "https://www.gov.il/he/departments/legalInfo/cpfta_prices_regulations"
    :param url: "שקיפות מחירים" url
    :return: Full csv table
    """
    driver = wb.load_page(url,'')
    time.sleep(5)
    page_source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_source, 'html.parser')
    table = soup.find("table")
    table_body = table.find("tbody")
    # traverse paragraphs from soup
    table = create_table()
    market = table_body.find_all("tr")
    for m in market:
        details = m.contents
        name = details[0].text
        link = details[1].find_all("a")
        url = []
        for l in link:
            url.append(l.get('href'))
            valid = check_valid_url(l.get('href'))
        user = details[2].text
        users = []
        if user != ' ':
            use = user.find("שם משתמש")
            user = user[use:]
            user = user.split("שם משתמש")
            for u in user:
                if 'פרטי' in u:
                    continue
                if "סיסמא" in u:
                    end = u.find("סיסמא")
                    u = u[:end]
                elif "ססמא" in u:
                    end = u.find("ססמא")
                    u = u[:end]
                u = re.sub('[:<\- =\xa0]', '', u)
                if u != '' and users is not None:
                    users.append(u)
            password = details[2].text
            pas = password.find("סיסמא")
            password = password[pas:]
            password = password.split("סיסמא")
            passwords = []
            for p in password:
                if p is not None and "אין צורך" not in p and "פרטי" not in p:
                    p = re.sub('[:<\- )=\xa0]', '', p)
                    p = re.sub('[\u0590-\u05FF]', '', p)
                    if p != '' and passwords is not None:
                        passwords.append(p)
                if "אין צורך" in p:
                    p = None
            table = insert_value_to_table(table, name, valid, url, users, passwords)
        else:
            table = insert_value_to_table(table, name, valid, url)
    table.to_csv('markets_list.csv', encoding="ISO-8859-8")
    return table
