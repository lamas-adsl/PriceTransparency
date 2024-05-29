import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
import requests
import read_market_web as web


def get_row_to_click(driver, str_xpath):
    driver.execute_script("arguments[0].click()", WebDriverWait(driver, 0).until(
        EC.element_to_be_clickable((By.XPATH, str_xpath))))


def select_current_item(driver):
    try:
        driver.find_element(By.XPATH,
                            '//*/select/option[contains(text(),"מחסנים")or contains(text(),"סניפים")or contains(text(),"Stores")]').click()
        get_row_to_click(driver, str_xpath='//*[@type="button" or @type="submit"]')
        time.sleep(2)
    except:
        pass


def download_stores(driver, full_name):
    select_current_item(driver)
    d = date.today().strftime("-%Y%m%d")
    try:
        typ, first_button = web.get_button_type(driver)
        str_xpath = f'//*/tr[./td[contains(text(),"Store") and contains(text(),"{d}")]]/td/{typ}'
        get_row_to_click(driver, str_xpath)
    except:
        try:
            str_xpath = f'//*/tr[./td[./{typ}[contains(text(),"Store")and contains(text(),"{d}")]]]/td/{typ}[./span]'
            try:
                get_row_to_click(driver, str_xpath)
            except:
                yesterday = (date.today() + timedelta(days=-1)).strftime("-%Y%m%d")
                str_xpath = str_xpath.replace(d, yesterday)
                get_row_to_click(driver, str_xpath)
            dowload_click = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Download')
            [dowload.click() for dowload in dowload_click]
        except:
            try:
                """
                Option to access two types of websites with the same code
                """
                rows = WebDriverWait(driver, 0).until(
                    EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, 'Stores')))
                rows_name_and_url = [(row.text.replace(' ', ''), row.get_attribute('href')) for row in rows if d in row.text][0]
                driver.get(url=rows_name_and_url[1])
                with open(f'{full_name}\\sel{rows_name_and_url[0]}', "w", encoding='utf-8') as stores:
                    stores.write(driver.find_element(By.TAG_NAME, "body").text.partition('\n')[-1])
            except:
                print(driver.current_url)
    web.download_wait(full_name)
    return
