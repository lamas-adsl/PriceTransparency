import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
import read_market_web as web


def get_rows_to_download(driver, str_xpath):
    return WebDriverWait(driver, 0).until(EC.presence_of_all_elements_located((By.XPATH, str_xpath)))


def select_current_item(driver):
    try:
        s = driver.find_element(By.XPATH,
                            '//*/select/option[contains(text(),"מחסנים")or contains(text(),"סניפים")or contains(text(),"Stores")]')
        s.click()
        s = WebDriverWait(driver, 0).until(EC.element_to_be_clickable((By.XPATH, '//*[@type="button" or @type="submit"]')))
        s.click()
    except:
        pass


def download_stores(driver, full_name):
    select_current_item(driver=driver)
    d = datetime.today().strftime("-%Y%m%d")
    driver.implicitly_wait(4)
    try:
        typ, first_button = web.get_button_type(driver=driver, name='')
        str_xpath = f'//*/tr[./td[contains(text(),"Store") and contains(text(),"{d}")]]/td/{typ}'
        rows = get_rows_to_download(driver=driver, str_xpath=str_xpath)
        [row.click() for row in rows]
    except:
        try:
            str_xpath = f'//*/tr[./td[./{typ}[contains(text(),"Store")and contains(text(),"{d}")]]]/td/{typ}[./span]'
            try:
                rows = get_rows_to_download(driver=driver, str_xpath=str_xpath)
            except:
                yesterday = (date.today() + timedelta(days=-1)).strftime("-%Y%m%d")
                str_xpath = str_xpath.replace(d, yesterday)
                rows = get_rows_to_download(driver=driver, str_xpath=str_xpath)
            [row.click() for row in rows]
            download_click = driver.find_elements(By.PARTIAL_LINK_TEXT, 'Download')
            [download.click() for download in download_click]
        except:
            try:
                """
                Option to access two types of websites with the same code
                """
                rows = WebDriverWait(driver, 0).until(EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, 'Stores')))
                dict_rows_text_and_url = {row.text.replace(' ', ''): row.get_attribute('href') for row in rows if d in row.text}
                for name, url in dict_rows_text_and_url.items():
                    driver.get(url=url)
                    with open(f'{full_name}\\sel{name}', "w", encoding='utf-8') as stores:
                        stores.write(driver.find_element(By.TAG_NAME, "body").text.partition('\n')[-1])
                    time.sleep(1)
            except:
                print(driver.current_url)
    web.download_wait(full_name)
    return

