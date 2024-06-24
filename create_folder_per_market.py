import os
import time
from pyunpack import Archive
import insert_to_db as db
import item_schema
import read_market_web as web
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import configparser
import ntpath
import shutil
import download_stores

BASE_PATH = os.getcwd()
DATE = str(datetime.today().strftime('%d-%m-%Y_%H-%M-%S'))
DATE_ZIP = str(datetime.today().strftime('%d-%m-%Y_%H-%M-%S'))
config = configparser.ConfigParser()
config.read("config.ini")


def zip_all_chains():
    """
    Create zip folder that contains all downloads from this day.
    :return:
    """
    location = config.get("others", "LocationToSaveZip")
    os.chdir(location)
    shutil.make_archive(os.path.join(location, DATE_ZIP), 'zip', os.path.join(BASE_PATH, DATE))
    shutil.rmtree(os.path.join(BASE_PATH, DATE))
    return DATE


def extract(path):
    """
    Get folder and extract all gz zips and remove the zips
    :param path: location of the folder of the .gz zips
    :return:
    """
    # Show location of the files
    os.chdir(path)
    time.sleep(8)
    list_of_files = list(filter(lambda x: '.gz' in x, os.listdir(path)))
    for f in list_of_files:
        if '.crdownload' in f:
            time.sleep(10)
            list_of_files = list(filter(lambda x: '.gz' in x, os.listdir(path)))
            continue
        Archive(f).extractall('.')
        os.remove(os.path.join(path, f))
    if os.path.exists(os.path.join(path, 'extracted')):
        os.remove(os.path.join(path, 'extracted'))


def extract_folder(path):
    p = Path(path)
    os.chdir(p.parent)
    folder = os.path.basename(path)
    Archive(folder).extractall('.')
    if ".xml" in path:
        return path[:-3]
    return path[:-2] + 'xml'


def create_folder(name):
    """
    Create folder per chain with the chain name
    :param name: of the chain
    :return: the name of the chain that was created
    """
    os.chdir(os.path.join(BASE_PATH, DATE))
    name = name.replace('"', '')
    name = name.replace('.', ' ')
    name = name.rstrip()
    if not os.path.exists(os.path.join(BASE_PATH, DATE, name)):
        os.mkdir(os.path.join(BASE_PATH, DATE, name))
    else:
        i = 1
        while os.path.exists(os.path.join(BASE_PATH, DATE, name + '_' + str(i))):
            i = i + 1
        os.mkdir(os.path.join(BASE_PATH, DATE, name + '_' + str(i)))
        name = name + '_' + str(i)
    return name


def copy_zips(base, dest):
    """
    Copy all (zips in the) folder from the source to the destination
    :param base: path of the source (For example: downloads)
    :param dest: path of the destination (For example: chain folder)
    :return: num of folders that was downloaded
    """
    time.sleep(5)
    for i in os.listdir(base):
        if '(' in i:
            os.remove(os.path.join(base, i))
            continue
        shutil.copy(os.path.join(base, i), dest)
        os.remove(os.path.join(base, i))
    return len(os.listdir(dest))


def clean_duplicate_folders(folder):
    for i in list(filter(lambda x: '(' in x, os.listdir(folder))):
        os.remove(os.path.join(folder, i))


def get_branch_zips(content, folder_name, user_name=None, password=None, f=0):
    """
    Scraping function that login to chain page, download the folders and close the chrome page when finished.
    copy the download folder to specific folder. and insert the exception to logException table when fails.
    :param content: url of the chain
    :param folder_name: of the chain
    :param user_name: if was needs for login
    :param password: if was needs for login
    :param f: flag if there are two chain in this web
    :return:
    """
    start_time = datetime.now()
    url = content
    trying = 0
    while trying < 10:
        try:
            name = create_folder(folder_name)
            full_name = os.path.join(BASE_PATH, DATE, name)
            driver = web.load_page(url, full_name, os.path.join(BASE_PATH, DATE))
            if 'login' in url or user_name is not None:
                web.login_with_user_and_pass(driver, url, user_name, password)
            break
        except Exception as e:
            if trying < 9:
                trying = trying + 1
                continue
            end_time = datetime.now()
            db.add_to_table('dbo.InsertLogException', 'FAILED',
                            "The " + folder_name + " chain failed in Exception: " + str(e)+" in URL: "+content, start_time, end_time)
            if e == 'maximum recursion depth exceeded while calling a Python object':
                return
            return None
    f = web.read_new_zips(driver=driver, name=name, part=f, url=url)
    web.download_wait(full_name)
    clean_duplicate_folders(name)
    num_of_folders = len(os.listdir(name))

    try:
        download_stores.download_stores(driver=driver, full_name=full_name)
    except Exception as e:
        pass

    try:
        driver.close()
        time.sleep(3)
        chain_id = os.listdir(full_name)[0].split('-')[0][9:]
        if (db.select_from_table('dbo.selectchainbycode', int(chain_id))).rowcount == 0:
            list_prices = list(filter(lambda x: 'Price' in x, os.listdir(full_name)))
            path = extract_folder(os.path.join(BASE_PATH, DATE, name, list_prices[0]))
            item = item_schema.create_schema(path)
            was_inserted = db.add_to_table('dbo.insertchaincode', int(chain_id), name, item.get_name_package(), os.path
                                           .join(BASE_PATH, folder_name), '/' + item.root + '/' + item.chain_code,
                                           '/' + item.root + '/' + item.store_code,
                                           '/' + item.root + '/' + item.branch_code)
        end_time = datetime.now()
        db.add_to_table('dbo.insertruntimes', int(chain_id), start_time, end_time, int(num_of_folders))
        date_to_read = datetime.strptime(DATE[:10], "%d-%m-%Y").strftime("%Y-%m-%d")
        db.add_to_table('dbo.InsertProcessDetails', int(chain_id), date_to_read,
                        os.path.join(config.get("others", "LocationToSaveZip"), date_to_read, name), start_time,
                        end_time, int(num_of_folders))
        return f
    except Exception as e:
        db.add_to_table('dbo.InsertLogException', 'FAILED',
                        "Faild in " + folder_name + ", The Exception is: " + type(e).__name__ + " at line " + str(
                            e.__traceback__.tb_lineno) + " of " + ntpath.basename(__file__) + ": " + str(
                            e) + ", continue to the next chain!", start_time, datetime.now())
        print('Failed in ' + folder_name + ', The Exception is: ' + e.__str__() + ' continue to the next chain!')
        return f


def get_url_market(table):
    """
    Base function that scraping the chains
    The function reads the "markets_list.csv" loop every row and trigger the scraping on the chain page.
    every iteration all the downloads folders save on folder with the current time in specific folder per chain name.
    :param table: csv file with all chains details
    :return:
    """
    if not os.path.exists(os.path.join(BASE_PATH, DATE)):
        os.mkdir(os.path.join(BASE_PATH, DATE))
    i =0
    for u in table.iterrows():
        url = u[1]['URL']
        user = u[1]['שם משתמש']
        passowrd = u[1]['סיסמא']
        folder_name = u[1]['שם']
        if len(url) > 1:
            for i, ur in enumerate(url):
                folder_name = f"{str(u[1]['שם']).strip()}_{chr(ord('A') + i)}"
                per_passowrd = ''
                try:
                    if user[i] is not None:
                        per_user = user[i]
                except:
                    per_user = None
                try:
                    if passowrd is not None:
                        if len(passowrd) < 1:
                            per_passowrd = ''
                        else:
                            per_passowrd = passowrd[i]
                except:
                    per_passowrd = ''
                get_branch_zips(content=ur, folder_name=folder_name, user_name=per_user, password=per_passowrd)
        else:
            f = get_branch_zips(content=url[0], folder_name=folder_name, user_name=user, password=passowrd)
            if f == 1:
                get_branch_zips(content=url[0], folder_name=folder_name, user_name=user, password=passowrd, f=1)


def parse_to_table():
    """
    Parse the attributes of the xmls per chain.
    :return:
    """
    execl_path = os.path.join(os.getcwd(), 'xml_parse.xlsx')
    writer = pd.ExcelWriter(execl_path, engine='xlsxwriter')
    path = os.path.join(BASE_PATH, DATE)
    for f in os.listdir(path):
        folder = os.listdir(os.path.join(BASE_PATH, f))[0]
        db.parse_xml_to_pandas(os.path.join(path, f, folder), f, writer)
    writer.close()
