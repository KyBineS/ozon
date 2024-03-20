import time

from telebot import TeleBot, types
from requests import Session

from config import TOKEN
from db import DataBase
from proxies import check_proxy


bot = TeleBot(TOKEN)

keyboard = types.InlineKeyboardMarkup()
show_status = types.InlineKeyboardButton(text="Показать статус", callback_data="show_status")
stop_start = types.InlineKeyboardButton(text="Остановить/Запустить", callback_data="stop_start")
add_url = types.InlineKeyboardButton(text="Добавить ссылку", callback_data="add_url")
show_urls = types.InlineKeyboardButton(text="Показать ссылки", callback_data="show_urls")
delete_url = types.InlineKeyboardButton(text="Удалить ссылки", callback_data="delete_url")
show_history = types.InlineKeyboardButton(text="Показать историю", callback_data="show_history")
keyboard.row(show_status, stop_start)
keyboard.row(add_url, show_urls)
keyboard.row(delete_url)
keyboard.row(show_history)

def get_message():
    db = DataBase()
    status_bot = db.get_status_bot()
    if status_bot:
        message = f'Статус бота: Работает'
    else:
        message = f'Статус бота: Отдыхает'
    return message


@bot.message_handler(commands=['start'])
def start(message):
    db = DataBase()
    telegram_ids = db.get_telegram_ids()
    if str(message.chat.id) not in telegram_ids:
        db.add_telegram_id(str(message.chat.id))
    message_ = get_message()
    r = bot.send_message(message.chat.id, message_, reply_markup=keyboard)
    db.update_main_message_id(str(message.chat.id), str(r.message_id))


@bot.message_handler(content_types=['document'])
def handle_document(message):
    db = DataBase()
    try:
        if message.document.mime_type == 'text/plain':
            db.delete_proxies()
            file_info = bot.get_file(message.document.file_id)
            proxies = bot.download_file(file_info.file_path).decode('utf-8').split('\n')
            for proxy in proxies:
                proxy = proxy.strip().replace('\n', '')
                if check_proxy(proxy):
                    db.add_proxy(proxy)
                else:
                    bot.send_message(message.chat.id, f'Прокси не рабочий\n{proxy}')
        else:
            bot.reply_to(message, 'Пожалуйста, отправьте только текстовый файл в формате .txt')

    except Exception as e:
        print(e)
        bot.reply_to(message, 'Произошла ошибка при обработке файла.')
    finally:
        message_ = get_message()
        main_message_id = db.get_main_message_id(str(message.chat.id))
        if main_message_id:
            bot.delete_message(message.chat.id, int(main_message_id))
        r = bot.send_message(message.chat.id, message_, reply_markup=keyboard)
        db.update_main_message_id(str(message.chat.id), str(r.message_id))


@bot.message_handler()
def update_token_and_add_filter(message):
    db = DataBase()
    telegram_ids = db.get_telegram_ids()
    if str(message.chat.id) in telegram_ids:
        if message.text.startswith('Add'):
            url = message.text
            url = url.replace('Add ', '')
            db.add_url_attack(url)
            message_ = get_message()
            main_message_id = db.get_main_message_id(str(message.chat.id))
            if main_message_id:
                bot.delete_message(message.chat.id, int(main_message_id))
            r = bot.send_message(message.chat.id, message_, reply_markup=keyboard)
            db.update_main_message_id(str(message.chat.id), str(r.message_id))

        elif message.text.startswith('Delete'):
            url = message.text
            url = url.replace('Delete ', '')
            db.delete_url_attack(url)
            message_ = get_message()
            main_message_id = db.get_main_message_id(str(message.chat.id))
            if main_message_id:
                bot.delete_message(message.chat.id, int(main_message_id))
            r = bot.send_message(message.chat.id, message_, reply_markup=keyboard)
            db.update_main_message_id(str(message.chat.id), str(r.message_id))

        elif message.text.startswith('AProxy'):
            proxy = message.text
            proxy = proxy.replace('AProxy ', '')
            if check_proxy(proxy):
                db.add_proxy(proxy)
                message_ = get_message()
                main_message_id = db.get_main_message_id(str(message.chat.id))
                if main_message_id:
                    bot.delete_message(message.chat.id, int(main_message_id))
                r = bot.send_message(message.chat.id, message_, reply_markup=keyboard)
                db.update_main_message_id(str(message.chat.id), str(r.message_id))
            else:
                bot.send_message(message.chat.id, f'Прокси не рабочий\n{proxy}')

        elif message.text.startswith('DProxy'):
            proxy = message.text
            proxy = proxy.replace('DProxy ', '')
            db.delete_proxy(proxy)
            message_ = get_message()
            main_message_id = db.get_main_message_id(str(message.chat.id))
            if main_message_id:
                bot.delete_message(message.chat.id, int(main_message_id))
            r = bot.send_message(message.chat.id, message_, reply_markup=keyboard)
            db.update_main_message_id(str(message.chat.id), str(r.message_id))
    else:
        bot.send_message(message.chat.id, 'Пошл вон отсюда')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    db = DataBase()
    telegram_ids = db.get_telegram_ids()
    if str(call.message.chat.id) in telegram_ids:
        main_message_id = db.get_main_message_id(str(call.message.chat.id))
        if call.data == 'stop_start':
            bot.edit_message_text("Делаем", call.message.chat.id, int(main_message_id), reply_markup=keyboard)
            db.switch_status()
            message_ = get_message()
            bot.edit_message_text(message_, call.message.chat.id, int(main_message_id), reply_markup=keyboard)

        elif call.data == 'show_status':
            message_ = get_message()
            bot.edit_message_text(message_, call.message.chat.id, int(main_message_id), reply_markup=keyboard)

        elif call.data == 'add_url':
            bot.edit_message_text('Формат ввода: Add Ссылка', call.message.chat.id, int(main_message_id), reply_markup=keyboard)

        elif call.data == 'show_urls':
            urls = db.get_urls_attack()
            if urls:
                urls.insert(0, 'Ссылки:\n')
                message_products = '\n'.join(urls)
                bot.edit_message_text(message_products, call.message.chat.id, int(main_message_id), reply_markup=keyboard)
            else:
                bot.edit_message_text('Нет ссылок', call.message.chat.id, int(main_message_id), reply_markup=keyboard)
                time.sleep(2)
                message_ = get_message()
                bot.edit_message_text(message_, call.message.chat.id, int(main_message_id), reply_markup=keyboard)

        elif call.data == 'show_history':
            history = db.get_history()
            if len(history) > 10:
                history = history[:10]
            if history:
                history.insert(0, 'История:\n')
                message_products = '\n'.join(history)
                bot.edit_message_text(message_products, call.message.chat.id, int(main_message_id), reply_markup=keyboard)
            else:
                bot.edit_message_text('Нет истории', call.message.chat.id, int(main_message_id), reply_markup=keyboard)
                time.sleep(2)
                message_ = get_message()
                bot.edit_message_text(message_, call.message.chat.id, int(main_message_id), reply_markup=keyboard)

        elif call.data == 'delete_url':
            urls = db.get_urls_attack()
            if urls:
                urls.insert(0, 'Вводите: Delete https://lorem.ru\n')
                message_products = '\n'.join(urls)
                bot.edit_message_text(message_products, call.message.chat.id, int(main_message_id), reply_markup=keyboard)

        elif call.data == 'show_proxy':
            proxies = db.get_proxies()
            if proxies:
                proxies.insert(0, 'Прокси\n')
                message_proxies = '\n'.join(proxies)
                bot.edit_message_text(message_proxies, call.message.chat.id, int(main_message_id),
                                      reply_markup=keyboard)
            else:
                bot.edit_message_text('Нет прокси', call.message.chat.id, int(main_message_id),
                                      reply_markup=keyboard)
                time.sleep(1)
                message_ = get_message()
                bot.edit_message_text(message_, call.message.chat.id, int(main_message_id), reply_markup=keyboard)

        elif call.data == 'add_proxy':
            bot.edit_message_text('Формат ввода: AProxy login:password@ip:port', call.message.chat.id,
                                  int(main_message_id), reply_markup=keyboard)

        elif call.data == 'delete_proxy':
            proxies = db.get_proxies()
            if proxies:
                proxies.insert(0, 'Формат ввода: DProxy login:password@ip:port\n')
                message_proxies = '\n'.join(proxies)
                bot.edit_message_text(message_proxies, call.message.chat.id, int(main_message_id),
                                      reply_markup=keyboard)


if __name__ == '__main__':
    bot.infinity_polling()
