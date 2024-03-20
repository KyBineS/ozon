import pickle
import asyncio

from celery import Celery

import telegram_autobuy

from config import REDIS_URL, REDIS_URL_RESULT_BACKEND
from aim_market import AimMarket
from db import DataBase

celery = Celery('tasks', broker=REDIS_URL, result_backend=REDIS_URL_RESULT_BACKEND)


@celery.task
def buy_product(aim_market, buy_products):
    aim_market = pickle.loads(aim_market)
    db = DataBase()
    field_ids = list(map(lambda x: x['id'], buy_products))
    r = aim_market.buy_products(field_ids)
    if r:
        print(f'Buy: {field_ids}')
        telegram_ids = db.get_telegram_ids()
        for product in buy_products:
            db.add_product_buy(product['id'], product['name'], product['price'])
            message = f'Куплен предмет: <b>{product["name"]}</b> - <b>{product["price"]}$</b>'
            for telegram_id in telegram_ids:
                try:
                    telegram_autobuy.bot.send_message(telegram_id, message, parse_mode='HTML')
                except:
                    pass
        return True
    print(f'Not buy: {field_ids}')
    return False