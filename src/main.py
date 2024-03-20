import logging
import json
import os
import random
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException

from db import DataBase
from proxies import load_proxy_selenium, get_random_proxy
from utils import get_webdriver
from flaresolverr_service import _evil_logic

auth_xpath = '//*[@id="stickyHeader"]/div[3]/div[1]'
add_cart_xpath = '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div[2]/div/div[4]/div/div/div[1]/div/div/div/div[1]/button'
add_cart_xpath_2 = '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div[2]/div/div[5]/div/div/div[1]/div/div/div/div[1]/button'
add_cart_xpath_3 = '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[4]/div/div/div[1]/div/div/div/div[1]/button'
cart_selector = '#stickyHeader > div.jd1 > a:nth-child(4)'
select_count_xpath = '//*[@id="layoutPage"]/div[1]/div/div/div[2]/div[4]/div[1]/div/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div/input'
buy_xpath = '//*[@id="layoutPage"]/div[1]/div/div/div[2]/div[4]/div[2]/div/section/div[1]/div[1]/button'
buy_all_xpath = '//*[@id="layoutPage"]/div[1]/div[3]/div/div/div[2]/div[3]/div/section/div[1]/div[1]/button'

reload_selector = '.q-checkbox__label.q-anchor--skip'

db = DataBase()


def load_json(name_file):
    with open(name_file, 'r') as file:
        cookies = json.loads(file.read())
    return cookies


def main(cookies, target_urls, name_file, proxy=None):
    if proxy:
        proxy_sel = load_proxy_selenium(proxy)
        driver, display = get_webdriver(proxy_sel)
    else:
        driver, display = get_webdriver()
    url = 'https://www.ozon.ru'
    _evil_logic(driver, url)
    time.sleep(20)
    driver.refresh()
    for cookie in cookies:
        for key, value in cookie.items():
            driver.add_cookie({'name': key, 'value': value})
    logging.info('Add cookies')
    for target_url in target_urls:
        driver.get(target_url)
        try:
            WebDriverWait(driver, 20).until(
                presence_of_element_located((By.XPATH, auth_xpath)))
        except TimeoutException:
            logging.info(f'timeout. {proxy}')
            display.stop()
            driver.quit()
            return False

        logging.info('Browser ready')
        try:
            WebDriverWait(driver, 5).until(
                presence_of_element_located((By.XPATH, add_cart_xpath)))
            driver.find_element(By.XPATH, add_cart_xpath).click()
        except TimeoutException:
            try:
                WebDriverWait(driver, 5).until(
                    presence_of_element_located((By.XPATH, add_cart_xpath_2)))
                driver.find_element(By.XPATH, add_cart_xpath_2).click()
            except TimeoutException:
                try:
                    WebDriverWait(driver, 5).until(
                        presence_of_element_located((By.XPATH, add_cart_xpath_3)))
                    driver.find_element(By.XPATH, add_cart_xpath_3).click()
                except TimeoutException:
                    logging.info(f'No product')
                    continue

        logging.info('add to card')
        time.sleep(2)
        driver.get('https://www.ozon.ru/cart')
        try:
            WebDriverWait(driver, 100).until(
                presence_of_element_located((By.XPATH, select_count_xpath)))
        except TimeoutException:
            logging.info(f'timeout. {proxy}')
            display.stop()
            driver.quit()
            return False
        driver.find_element(By.XPATH, select_count_xpath).send_keys('10000\n')
        time.sleep(3)
        driver.find_element(By.XPATH, buy_xpath).click()
        driver.get(
            'https://www.ozon.ru/gocheckout/delivery?ab_reason=failed_to_set_address&fr=t&map_reason=no_addresses&pv=0')
        driver.get(
            'https://www.ozon.ru/gocheckout/delivery?azimuth=1.002523679888&bdm=f&haad=f&map_reason=no_addresses&msid=13542e36-0811-48f4-8a98-26248f9d86f2&nfr=t&pid=5&pp=400507&pv=0&pxlw=1015.000000&said=2&sie=t&slat=55.75222&slong=37.615559&ssv=%D0%A2%D1%80%D0%BE%D0%B8%D1%86%D0%BA%D0%B0%D1%8F+%D1%83%D0%BB%D0%B8%D1%86%D0%B0&tab=pp')
        time.sleep(10)
        try:
            WebDriverWait(driver, 20).until(
                presence_of_element_located(
                    (By.XPATH, '//*[@id="layoutPage"]/div[1]/div/div/div[1]/div/div/div/div[2]/button')))
        except TimeoutException:
            os.remove(name_file)
            display.stop()
            driver.quit()
            return False
        driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div/div/div[1]/div/div/div/div[2]/button').click()
        try:
            WebDriverWait(driver, 20).until(
                presence_of_element_located(
                    (By.XPATH, buy_all_xpath)))
        except TimeoutException:
            logging.info(f'timeout. {proxy}')
            display.stop()
            driver.quit()
            return False
        driver.find_element(By.XPATH, buy_all_xpath).click()
        time.sleep(10)
        db.add_history(target_url)
        return True


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
        status = db.get_status_bot()
        target_urls = db.get_urls_attack()
        names_file = os.listdir('cookies')
        if names_file and status and target_urls:
            name_file = f'cookies/{random.choice(names_file)}'
            logging.info(name_file)
            cookies = load_json(name_file)
            main(cookies, target_urls, name_file, proxy)
        time.sleep(10)


if __name__ == '__main__':
    run()