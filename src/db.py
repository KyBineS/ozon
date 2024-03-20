import logging
import time
from datetime import datetime, timedelta

from psycopg2 import connect, Error
from psycopg2.extras import DictCursor

from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE


def send_request_db_read(query: str, params: tuple | list = ()):
    response = {'status': bool, 'message': str}
    try:
        with connect(host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USER, password=POSTGRES_PASSWORD,
                     database=POSTGRES_DATABASE) as connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                result = cursor.fetchall()
                response['status'] = True
                response['message'] = result
                return response
    except Error as error:
        response['status'] = False
        response['message'] = error
        logging.error(error)
        return response


def send_request_db_write(query: str, params: tuple | list = (), id_bool=False):
    response = {'status': bool, 'message': str}
    try:
        with connect(host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USER, password=POSTGRES_PASSWORD,
                     database=POSTGRES_DATABASE) as connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                connection.commit()
                if id_bool:
                    last_id = cursor.lastrowid
        if id_bool:
            response['status'] = True
            response['message'] = last_id
            return response
        response['status'] = True
        response['message'] = 'Writed'
        return response
    except Error as error:
        response['status'] = False
        response['message'] = error
        return response


class DataBase:
    def __init__(self):
        pass

    def add_url_attack(self, url):
        query = f'INSERT INTO urls(url) VALUES(%s)'
        params = (url,)
        send_request_db_write(query, params)

    def get_urls_attack(self):
        urls = []
        query = f'SELECT * FROM urls'
        r = send_request_db_read(query)
        if r['status']:
            for i in r['message']:
                urls.append(i[1])
        return urls

    def delete_url_attack(self, url):
        query = f'DELETE FROM urls WHERE url = %s'
        params = (url,)
        send_request_db_write(query, params)

    def add_history(self, url):
        query = 'INSERT INTO history(date, url) VALUES(%s, %s)'
        date_now = datetime.now() + timedelta(hours=3)
        date_now_str = date_now.strftime("%Y-%m-%d %H:%M:%S")
        params = (date_now_str, url)
        send_request_db_write(query, params)

    def get_history(self):
        urls = []
        query = f'SELECT * FROM history'
        r = send_request_db_read(query)
        if r['status']:
            for i in r['message']:
                urls.append(f'{i[1]} {i[2]}')
        return urls

    def get_telegram_ids(self):
        query = f'SELECT * FROM telegram_ids'
        response = send_request_db_read(query)
        telegram_ids = []
        if response['status']:
            for i in response['message']:
                telegram_ids.append(i[1])
        return telegram_ids

    def add_telegram_id(self, telegram_id):
        query = 'INSERT INTO telegram_ids(telegram_id) VALUES (%s)'
        params = (telegram_id,)
        send_request_db_write(query, params)

    def update_main_message_id(self, telegram_id, message_id):
        query = f'UPDATE telegram_ids SET main_message_id = %s WHERE telegram_id = %s'
        params = (message_id, telegram_id,)
        send_request_db_write(query, params)

    def get_main_message_id(self, telegram_id):
        query = f'SELECT main_message_id FROM telegram_ids WHERE telegram_id = %s'
        params = (telegram_id,)
        r = send_request_db_read(query, params)
        if r['status']:
            return r['message'][0][0]
        else:
            return False

    def get_status_bot(self):
        query = f'SELECT status FROM statuses'
        r = send_request_db_read(query)
        return r['message'][0][0]

    def switch_status(self):
        status = self.get_status_bot()
        query = f'UPDATE statuses SET status = %s'
        if status:
            params = (0,)
        else:
            params = (1,)
        send_request_db_write(query, params)

    def add_proxy(self, proxy):
        query = f'INSERT INTO proxies (proxy) VALUES (%s)'
        params = (proxy,)
        send_request_db_write(query, params)

    def delete_proxy(self, proxy):
        query = f'DELETE FROM proxies WHERE proxy = %s'
        params = (proxy,)
        send_request_db_write(query, params)

    def delete_proxies(self):
        query = f'DELETE FROM proxies'
        send_request_db_write(query)

    def get_proxies(self):
        proxies = []
        query = f'SELECT * FROM proxies'
        response = send_request_db_read(query)
        if response['status']:
            for i in response['message']:
                proxies.append(i[1])
        return proxies

