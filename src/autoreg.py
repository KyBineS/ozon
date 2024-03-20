import logging
import json
import os
import time

from faker import Faker
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException

from db import DataBase
from proxies import load_proxy_selenium, get_random_proxy
from utils import get_webdriver
from flaresolverr_service import _evil_logic
from onlinesim import OnlineSim
from config import API_KEY

reg_xpath = '//*[@id="stickyHeader"]/div[3]/div[1]'
iframe_xpath = '//*[@id="authFrame"]'
input_number_xpath = '//*[@id="layoutPage"]/div[1]/div/div/div[4]/div/div/div[1]/label/div/div/input'
button_sms_xpath = '//*[@id="layoutPage"]/div[1]/div/div/div[5]/div[2]/div[2]/a'
input_code_xpath = '//*[@id="layoutPage"]/div[1]/div/div/div[4]/div[1]/label/div/div/input'
buy_selector = '#layoutPage > div.b2 > div.xd7 > div > div.container.b6 > div:nth-child(5) > div.d4.c9 > div > section > div.u1b > div.bs9.bu2 > button'
accept_xpath = '//*[@id="layoutPage"]/div[1]/div/div/div[5]/label[1]'
accept_selector = '#layoutPage > div > div > div > div:nth-child(5) > label'
accept_name = 'персональных данных'
sign_xpath = '//*[@id="layoutPage"]/div[1]/div/div/div[4]/button'
enter_xpath = '//*[@id="layoutPage"]/div[1]/div/div/div[5]/button'
change_xpath = '//*[@id="layoutPage"]/div[1]/div/section/div/div[1]/div/div[2]/div[3]/button'
name_xpath = '//*[@id="firstName"]'
surname_xpath = '//*[@id="lastName"]'
save_xpath = '/html/body/div[3]/div/div[2]/div/div/div/div/div[2]/button[2]'


db = DataBase()


def load_json(name_file):
    with open(name_file, 'r') as file:
        cookies = json.loads(file.read())
    return cookies


def wait_sms(online_sim, tzid, attempt=0):
    while True:
        code = online_sim.get_code(tzid)
        time.sleep(5)
        attempt += 1
        if code:
            return code
        if attempt > 10:
            return False


def write_json(name_file, selenium_cookies):
    cookies = []
    for i in selenium_cookies:
        cookies.append({i['name']: i['value']})
    with open(name_file, 'w') as file:
        file.write(json.dumps(cookies))


def main(proxy=None):
    if proxy:
        proxy_sel = load_proxy_selenium(proxy)
        driver, display = get_webdriver(proxy_sel)
    else:
        driver, display = get_webdriver()
    url = 'https://www.ozon.ru'
    _evil_logic(driver, url)
    time.sleep(10)
    driver.refresh()
    try:
        WebDriverWait(driver, 20).until(
            presence_of_element_located((By.XPATH, reg_xpath)))
    except TimeoutException:
        logging.info(f'timeout. {proxy}')
        display.stop()
        driver.quit()
        return False
    logging.info('Browser ready')
    driver.find_element(By.XPATH, reg_xpath).click()
    logging.info('click reg')
    try:
        WebDriverWait(driver, 20).until(
            presence_of_element_located((By.XPATH, iframe_xpath)))
    except TimeoutException:
        logging.info(f'not view iframe')
        driver.find_element(By.XPATH, reg_xpath).click()
        logging.info('click reg')
        try:
            WebDriverWait(driver, 20).until(
                presence_of_element_located((By.XPATH, iframe_xpath)))
        except TimeoutException:
            logging.info(f'not view iframe')
            display.stop()
            driver.quit()
            return False
    iframe = driver.find_element(By.XPATH, iframe_xpath)
    driver.switch_to.frame(iframe)
    online_sim = OnlineSim(API_KEY)
    number, tzid = online_sim.get_number()
    logging.info(number)
    try:
        WebDriverWait(driver, 20).until(
            presence_of_element_located((By.XPATH, input_number_xpath)))
    except TimeoutException:
        logging.info(f'not view input number')
        display.stop()
        driver.quit()
        return False
    driver.find_element(By.XPATH, input_number_xpath).send_keys(number)
    driver.find_element(By.XPATH, enter_xpath).click()
    logging.info('enter number')
    try:
        WebDriverWait(driver, 40).until(
            presence_of_element_located((By.XPATH, accept_xpath)))
    except TimeoutException:
        logging.info(f'timeout. {proxy}')
        display.stop()
        driver.quit()
        return False
    driver.execute_script(f"document.querySelector('{accept_selector}').click()")
    try:
        WebDriverWait(driver, 30).until(
            presence_of_element_located((By.XPATH, button_sms_xpath)))
    except TimeoutException:
        logging.info(f'timeout. {proxy}')
        display.stop()
        driver.quit()
        return False
    driver.find_element(By.XPATH, button_sms_xpath).click()
    logging.info('enter get sms')
    code = wait_sms(online_sim, tzid)
    if not code:
        try:
            WebDriverWait(driver, 70).until(
                presence_of_element_located((By.XPATH, button_sms_xpath)))
            driver.find_element(By.XPATH, button_sms_xpath).click()
            logging.info('enter get sms')
        except TimeoutException:
            pass
    code = wait_sms(online_sim, tzid)
    if not code:
        return False
    driver.find_element(By.XPATH, input_code_xpath).send_keys(code)
    logging.info('enter code')
    time.sleep(20)
    driver.find_element(By.XPATH, sign_xpath).click()
    logging.info('login ready')

    time.sleep(20)
    selenium_cookies = driver.get_cookies()
    write_json(f'cookies/{number}.json', selenium_cookies)

    driver.get('https://www.ozon.ru/ozonid')
    try:
        WebDriverWait(driver, 20).until(
            presence_of_element_located((By.XPATH, change_xpath)))
    except TimeoutException:
        logging.info(f'timeout. {proxy}')
        display.stop()
        driver.quit()
        return False
    driver.find_element(By.XPATH, change_xpath).click()
    try:
        WebDriverWait(driver, 20).until(
            presence_of_element_located((By.XPATH, name_xpath)))
    except TimeoutException:
        logging.info(f'timeout. {proxy}')
        display.stop()
        driver.quit()
        return False
    f = Faker('ru_RU')
    surname, name, _ = f.name().split(' ')
    driver.find_element(By.XPATH, name_xpath).send_keys(name)
    driver.find_element(By.XPATH, surname_xpath).send_keys(f'{surname}\n')
    time.sleep(4)
    driver.get('https://www.ozon.ru')
    time.sleep(2)
    write_json(f'cookies/{number}.json', selenium_cookies)


def run():
    log_level = 'INFO'
    logger_format = '%(asctime)s %(levelname)-8s ReqId %(thread)s %(message)s'
    logging.basicConfig(
        format=logger_format,
        level=log_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    while True:
        proxy = get_random_proxy()
        names_file = os.listdir('cookies')
        if len(names_file) < 10:
            main(proxy)
        time.sleep(10)


if __name__ == '__main__':
    run()
