import os.path
import subprocess
import time
import zipfile
import wget
from glob import glob
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium.webdriver.chrome.service import Service
import insert_to_db as db
from get_chrome_driver import GetChromeDriver


BASE_PATH = r'D:\Price_transparency_work'

def get_chrome_version():
    try:
        result = subprocess.check_output(['wmic', 'datafile', 'where',
                                          r'name="C:\Program Files\Google\Chrome\Application\chrome.exe"',
                                          'get', 'Version', '/value'])
        version = result.decode().strip().split('=')[1]
        return version
    except Exception as e:
        print("Error occurred:", e)
        return None


def load_page(url, download_file, path = BASE_PATH):
    """
    Load the url for scraping, configur the wedDriver and load the url.
    :param url: chain web page
    :return: web driver
    """
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--disable-extensions")
    prefs = {
        'profile.default_content_setting_values.automatic_downloads': 1,
        'safebrowsing.enabled': True
    }
    options.add_experimental_option('prefs', prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    try:
        service = Service()
        driver = webdriver.Chrome(options=options, service=service)
        driver.execute_cdp_cmd('Page.setDownloadBehavior', {'behavior': 'allow', 'downloadPath': download_file})
        driver.get(url)
    except WebDriverException as driver_exception:
        try:
            get_driver = GetChromeDriver()
            print(get_driver.stable_version())
            try:
                os.remove(os.path.join(path, 'chromedriver_old.exe'))
                os.rename(os.path.join(path, 'chromedriver.exe'), os.path.join(path, 'chromedriver_old.exe'))
            except:
                pass
            get_driver.download_stable_version(extract=True, output_path=path)
            driver = webdriver.Chrome(options=options, executable_path=os.path.join(path, 'chromedriver.exe'))
            driver.get(url)
        except:
            chrome_version = get_chrome_version()
            url_chrome = f'https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/win64/chromedriver-win64.zip'
            latest_driver_zip = wget.download(url_chrome, os.path.join(path, 'chromedriver.zip'))
            os.remove(os.path.join(path, 'chromedriver_old.exe'))
            os.rename(os.path.join(path, 'chromedriver.exe'),  os.path.join(path, 'chromedriver_old.exe'))
            zip_obj = zipfile.ZipFile(latest_driver_zip, 'r')
            zip_obj.extractall(path)
            zip_obj.close()
            os.remove(latest_driver_zip)
            driver = webdriver.Chrome(chrome_options=options,
                                      executable_path=os.path.join(path, 'chromedriver.exe'))
            driver.get(url)
    return driver


def login_with_user_and_pass(driver, url, user, password):
    """
    Login with username and password in order to become to the chain web of the downloads
    :param driver: wed driver, user: chain username, password: chain password
    :return: the new url of the chain web
    """
    time.sleep(3)
    driver.find_element(By.XPATH,"//*[@type='text']").send_keys(user)
    driver.find_element(By.XPATH,"//*[@type='password']").send_keys(password)
    driver.find_element(By.XPATH,"//*[@type='submit']").click()
    time.sleep(3)
    return driver.current_url


def select_to_current_chain(driver, name, f=0):
    """
    In the part of the chains need to select in drop down list the current chain,
    here find the dropdown and if found, select to the current chain
    :param driver: wed driver
    :param name: of the current chain
    :return:
    """
    try:
        net_list = driver.find_elements(By.XPATH, '//*/select[@id="MainContent_chain"]/option')
        for i, v in enumerate(net_list):
            if v.text in name or ('ברקת' in name and 'ברקת' in v.text) or ('כהן' in name and 'כהן' in v.text):
                if i + 1 < len(net_list) and v.text == net_list[i + 1].text:
                    v = net_list[i + f]
                    f = 1 if f == 0 else 0
                v.click()
                driver.execute_script("arguments[0].click()", WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_btnSearch"]'))))
                time.sleep(3)
                return f
    except:
        return


def select_to_price_or_promo_full(driver, part):
    """
    In "סופר פארם" and "שופרסל" needs to select the type we want to see.
    here check if contains dropdown with promofull/pricefull option, if found select to them.
    :param driver: web driver, part: flag that tell we downloaded the PriceFull and now need to select PromoFull
    :return: flag if we need to select again for PromoFull.
    """
    try:
        if part:
            driver.find_element(By.XPATH, '//*/select/option[contains(text(),"PromosFull") or contains(text(),"PromoFull")]').click()
            part = False
            time.sleep(5)
        else:
            driver.find_element(By.XPATH, '//*/select/option[contains(text(),"PricesFull") or contains(text(),"PriceFull")]').click()
            part = True
        time.sleep(10)
    except:
        part = False
    return part


def get_button_type(driver, name, c=0):
    """
    Every chain went start to read the page code, try to find how call butten in this page- 'button' or 'a'
    :param driver: web driver, name: name of chain
    :return: the type that the button call, and the first button
    """
    try:
        button = driver.find_element(By.XPATH, '//*/table/tbody/tr/td/button')
        type = 'button'
    except:
        try:
            button = driver.find_element(By.XPATH, '//*/table/tbody/tr/td/a')
            type = 'a'
        except NoSuchElementException:
            if c < 3:
                time.sleep(8)
                select_to_current_chain(driver=driver, name=name)
                type, button = get_button_type(driver=driver, name=name, c=c+1)
    return type, button


def download_wait(path_to_downloads):
    seconds = 0
    while seconds < 40 and glob(fr'{path_to_downloads}\*.crdownload'):
        time.sleep(1)
        seconds += 1
    return seconds


def end_page():
    pass


def read_new_zips(driver, name, f=0, part=False, download_path=None, url=None):
    """
    Base function that call to other functions. in the chain page, select to the current chain if was needs,
    select to promo/price if was needs, get the current type of button, go to the first button that need to download,
    in 'יינות הביתן' select to the current folder that become to the chain download page, navigate to next page when was needs,
    and click every button to download.
    Every exception was written in sql in "LogExceptions" table
    :param driver: webdriver, name: name of the current chain, part: flag if in the middle of the downloads
    :return:
    """
    start_time = datetime.now()
    try:
        time.sleep(5)
        f = select_to_current_chain(driver=driver, name=name, f=f)
        part = select_to_price_or_promo_full(driver=driver, part=part)
        type, first_button = get_button_type(driver=driver, name=name)
        rows = driver.find_elements(By.TAG_NAME, 'tr')
        i = 1
        if first_button.text == '' or first_button.text == 'Parent Directory':
            buttons = driver.find_elements(By.XPATH, '//*/table/tbody/tr/td/'+type)
            while first_button.text == '' or first_button.text == 'Parent Directory':
                first_button = buttons[i]
                i += 1
        if ".gz" not in first_button.text and 'הורדה' not in first_button.text:
            if 'Stores' in first_button.text:
                return
            links = driver.find_elements(By.XPATH,'//*/table/tbody/tr/td[contains(text(), "'+datetime.today().strftime('%Y-%m-%d')+'")]/parent::tr/td/'+type)
            for l in links:
                if 'ncr' not in l.text and l.text != '':
                    l.click()
                    read_new_zips(driver=driver, name=name, download_path=download_path, url=url)
                    return
        index = 1
        x = 0
    except Exception as e:
        end_time = datetime.now()
        db.add_to_table('dbo.InsertLogException', 'FAILED', "The "+name+" chain failed in Exception: "+str(e)+" in URL: "+ url, start_time,
                        end_time)
        return
    while x < len(rows):
        try:
            try:
                if 'שופרסל' in name:
                    print(f'Rows number: {len(rows)}, index number: {x}')
                line = driver.find_element(By.XPATH, '//*/table/tbody/tr[' + str(x + index) + ']')
                if rows[x].text != line.text:
                    index = 0
                    try:
                        driver.find_element(By.XPATH, '//*/table/tbody/tr[' + str(x + index) + ']')
                    except:
                        x += 2
                        index = -1
                        continue
            except IndexError:
                try:
                    if 'שופרסל' in name:
                        time.sleep(3)
                        download_wait(download_path)
                        driver.find_element(By.XPATH, '//*[text()=">"]').click()
                        time.sleep(10)
                        print(f'--Next 1--')
                    else:
                        driver.find_element(By.XPATH, '//*/table/tbody/tr/td/' + type + '[text()=">"]').click()
                    x = 0
                except:
                    if part:
                        read_new_zips(driver=driver, name=name, download_path=download_path, part=part, url=url)
                    else:
                        download_wait(download_path)
                        return
            except:
                x += 1
                continue
            if rows[x].text.find(str((datetime.today()).strftime('-%Y%m%d'))) != -1 and rows[x].text.find("Full") != -1 and rows[x].text.find("StoresFull") == -1:
                if 'נתיב החסד' in name:
                    if not driver.find_element(By.XPATH, '//*/table/tbody/tr[' + str(x + index) + ']/td/' + type).get_attribute('href').endswith('gz'):
                        x += 1
                        continue

                driver.execute_script("arguments[0].click()", WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*/table/tbody/tr[' + str(x + index) + ']/td/' + type))))
                x += 1
                if 'שופרסל' in name:
                    time.sleep(1)
                if x == len(rows):
                    try:
                        if 'שופרסל' in name:
                            time.sleep(3)
                            download_wait(download_path)
                            driver.find_element(By.XPATH, '//*[text()=">"]').click()
                            time.sleep(10)
                            print(f'--Next 2--')
                        else:
                            download_wait(download_path)
                            driver.find_element(By.XPATH, '//*[text()=">"]').click()
                        x = 0
                        index = 1
                        rows = driver.find_elements(By.TAG_NAME, 'tr')
                        if len(rows) < 1:
                            print('Find 0 rows, try again')
                            rows = driver.find_elements(By.TAG_NAME, 'tr')
                    except:
                        if part:
                            read_new_zips(driver=driver, name=name, download_path=download_path, part=part, url=url)
                        else:
                            download_wait(download_path)
                            return
            else:
                if x == len(rows)-1:
                    try:
                        if 'שופרסל' in name:
                            time.sleep(3)
                            download_wait(download_path)
                            driver.find_element(By.XPATH, '//*[text()=">"]').click()
                            time.sleep(10)
                            print(f'--Next 3--')
                        else:
                            download_wait(download_path)
                            driver.find_element(By.XPATH, '//*[text()=">"]').click()
                        x = 0
                        index = 1
                        rows = driver.find_elements(By.TAG_NAME,'tr')
                    except:
                        if part:
                            read_new_zips(driver=driver, name=name, download_path=download_path, part=part, url=url)
                        else:
                            download_wait(download_path)
                            return f
                else:
                    x += 1
                    continue
        except Exception as e:
            end_time = datetime.now()
            try:
                db.add_to_table('dbo.InsertLogException', 'FAILED', "Failed on button "+rows[x].text+" on Exception: "+str(e),
                                start_time,
                                end_time)
            except Exception as eee:
                db.add_to_table('dbo.InsertLogException', 'FAILED',
                                "Failed on button, on Exception: " + str(e),
                                start_time,
                                end_time)
            x += 1
            continue


def close_driver(driver):
    """
    Close the chrome and the driver when finish downloading per chain
    :param driver: web driver
    :return:
    """
    driver.close()
