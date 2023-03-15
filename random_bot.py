from datetime import datetime
import datetime
import json
import requests
import sqlite3
import random
import time

from telegram.ext import Updater, MessageHandler, CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler


apikey = ""
secret_token = ''
conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()


def db_table_val(chat_name, user_name, user_surname, username, user_id):
    try:
        cursor.execute(f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{chat_name}';""")
        cursor.execute(f'INSERT INTO {chat_name} (user_id, user_name, user_surname, username, best_stat, pidr_stat) VALUES ( ?, ?, ?, ?, 0, 0)', (user_id, user_name, user_surname, username))
        conn.commit()
    except:
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {chat_name}(
            user_id INT UNIQUE,
            user_name TEXT,
            user_surname TEXT,
            username TEXT,
            best_stat INT,
            pidr_stat INT,
            time TEXT);
            """)
        cursor.execute(f'INSERT INTO {chat_name} (user_id, best_stat, pidr_stat, time) VALUES ( 1, 0, 0, 0);')
        cursor.execute(f'INSERT INTO {chat_name} (user_id, best_stat, pidr_stat, time) VALUES ( 2, 0, 0, 0);')
        cursor.execute(f'INSERT INTO {chat_name} (user_id, user_name, user_surname, username, best_stat, pidr_stat) VALUES ( ?, ?, ?, ?, 0, 0)', (user_id, user_name, user_surname, username))
        conn.commit()
        
def add_result_in_bd(chat_name, user_id, best_stat, pidr_stat):
    now_time = datetime.date.today()
    if best_stat:
        cursor.execute(f'UPDATE {chat_name} SET time = "{now_time}" WHERE user_id = 2;')
        cursor.execute(f'UPDATE {chat_name} SET best_stat = best_stat + 1 WHERE user_id = "{user_id}";')
        conn.commit()
    elif pidr_stat:
        cursor.execute(f'UPDATE {chat_name} SET time = "{now_time}" WHERE user_id = 1;')
        cursor.execute(f'UPDATE {chat_name} SET pidr_stat = pidr_stat + 1 WHERE user_id = "{user_id}";')
        conn.commit()
        
def del_whitespaces(chat_name):
    try:
        chat_name = chat_name.replace(" ", "")
        return chat_name
    except:
        return chat_name
    
def check_username(user_id, chat_name):
    cursor.execute(f'SELECT username, user_name FROM {chat_name} WHERE user_id == {user_id};')
    result = cursor.fetchall()
    if result[0][0] is None:
        return False
    else:
        return True
    

def reg_customer(update, context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Хах, а ты смельчак @{}'.format(update.message.from_user.username)
    )
    try:
        chat_name = del_whitespaces(chat_name=update.message.chat.title)
        user_id = update.message.from_user.id
        us_name = update.message.from_user.first_name
        us_sname = update.message.from_user.last_name
        username = update.message.from_user.username
        db_table_val(chat_name=chat_name, user_name=us_name, user_surname=us_sname, username=username, user_id=user_id)
        context.bot.send_message(
            chat_id=chat.id,
            text='И теперь ты в моей базе Красавчиков и Пидоров 🤗'
        )
    except:
        context.bot.send_message(
            chat_id=chat.id,
            text='Но ты и так в моей базе Красавчиков и Пидоров'
        )
  
def found_pidr(update, context):
    now_time = datetime.date.today()
    chat_name = del_whitespaces(chat_name=update.message.chat.title)
    cursor.execute(f'SELECT time FROM {chat_name} WHERE user_id = 1;')
    check_time = cursor.fetchone()
    if str(now_time) != str(check_time[0]):
        cursor.execute(f'SELECT username, user_name, user_id FROM {chat_name} WHERE user_id != 1 AND user_id != 2;')
        all_results = cursor.fetchall()
        one_result = random.choice(all_results)
        add_result_in_bd(chat_name=chat_name, user_id=one_result[2], pidr_stat=True, best_stat=False)
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s" % ("find", apikey))
        gif = json.loads(r.content)
        i = random.randint(0, 15)
        res = gif["results"][i]["url"]
        context.bot.send_message(chat_id=update.effective_chat.id, text=res)
        time.sleep(2)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Пидо-пидо-пидо три')
        time.sleep(2)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Пидо-пидо-пидо два')
        time.sleep(2)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Пидо-пидо-пидо раз')
        time.sleep(2)
        if check_username(one_result[2], chat_name):
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'@{one_result[0]} расчехляй свой ШОКО-ГЛАЗ')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'{one_result[1]} расчехляй свой ШОКО-ГЛАЗ')
    else:
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s" % ("goodbye", apikey))
        gif = json.loads(r.content)
        i = random.randint(0, 15)
        res = gif["results"][i]["url"]
        context.bot.send_message(chat_id=update.effective_chat.id, text=res)
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Возвращайся завтра дружок')

def stat_pidr(update, context):
    chat_name = del_whitespaces(chat_name=update.message.chat.title)
    cursor.execute(f'SELECT username, pidr_stat, user_name FROM {chat_name} WHERE user_id != 1 AND user_id != 2;')
    all_results = cursor.fetchall()
    result = ""
    i = 1
    for row in all_results:
        if row[0] is None:
            result = result + f'{i}' + ") " + f'{row[2]}' + "  --->  " + f'{row[1]} раз(а)' + "\n"
        else:
            result = result + f'{i}' + ") " + f'{row[0]}' + "  --->  " + f'{row[1]} раз(а)' + "\n"
        i += 1
    context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'🏳️‍🌈👨➕👨🟰❤️🏳️‍🌈\nА вот и список пидорков подъехал:\n\n{result}'
        )
    
def found_best(update, context):
    now_time = datetime.date.today()
    chat_name = del_whitespaces(chat_name=update.message.chat.title)
    cursor.execute(f'SELECT time FROM {chat_name} WHERE user_id = 2;')
    check_time = cursor.fetchone()
    if str(now_time) != str(check_time[0]):
        chat_name = del_whitespaces(chat_name=update.message.chat.title)
        cursor.execute(f'SELECT username, user_name, user_id FROM {chat_name} WHERE user_id != 1 AND user_id != 2;')
        all_results = cursor.fetchall()
        one_result = random.choice(all_results)
        add_result_in_bd(chat_name=chat_name, user_id=one_result[2], pidr_stat=False, best_stat=True)
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s" % ("best", apikey))
        gif = json.loads(r.content)
        i = random.randint(0, 15)
        res = gif["results"][i]["url"]
        context.bot.send_message(chat_id=update.effective_chat.id, text=res)
        time.sleep(2)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Свет мой, зеркальце! скажи')
        time.sleep(2)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Да всю правду доложи:')
        time.sleep(2)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Кто на свете всех милее,')
        time.sleep(2)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Всех румяней и белее?')
        time.sleep(2)
        if check_username(one_result[2], chat_name):
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ты @{one_result[0]}, конечно, спору нет!')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ты {one_result[1]}, конечно, спору нет!')
    else:
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s" % ("goodbye", apikey))
        gif = json.loads(r.content)
        i = random.randint(0, 15)
        res = gif["results"][i]["url"]
        context.bot.send_message(chat_id=update.effective_chat.id, text=res)
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Возвращайся завтра дружок')

def stat_best(update, context):
    chat_name = del_whitespaces(chat_name=update.message.chat.title)
    cursor.execute(f'SELECT username, best_stat, user_name FROM {chat_name} WHERE user_id != 1 AND user_id != 2;')
    all_results = cursor.fetchall()
    result = ""
    i = 1
    for row in all_results:
        if row[0] is None:
            result = result + f'{i}' + ") " + f'{row[2]}' + "  --->  " + f'{row[1]} раз(а)' + "\n"
        else:
            result = result + f'{i}' + ") " + f'{row[0]}' + "  --->  " + f'{row[1]} раз(а)' + "\n"
        i += 1
    context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'🍾🏆🥇🥈🥉🎉\nВот они лучшие самцы\самки на свете:\n\n{result}'
        )

def donate_msg(update, context):
    r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s" % ("donate", apikey))
    gif = json.loads(r.content)
    i = random.randint(0, 15)
    res = gif["results"][i]["url"]
    context.bot.send_message(chat_id=update.effective_chat.id, text=res)
    time.sleep(2)
    context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='https://www.donationalerts.com/r/greenpandorik'
        )
    time.sleep(2)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Можно кинуть криптовалюту USDT на этот кошелёк ⬇️')
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'0x4f0f7a5fac8bfe0527140e99e6cb4f37a6cfac7a')
    
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"I don't understand you 😕❓🚪")

def new_members(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Не забудьте написать команду\n/reg\nЧтобы зарегистрироваться в моей базе 😈")

def main():
    updater = Updater(token=secret_token)
    updater.dispatcher.add_handler(CommandHandler('reg', reg_customer, run_async= True))
    updater.dispatcher.add_handler(CommandHandler('pidor', found_pidr, run_async= True))
    updater.dispatcher.add_handler(CommandHandler('pidorstatistic', stat_pidr, run_async= True))
    updater.dispatcher.add_handler(CommandHandler('best', found_best, run_async= True))
    updater.dispatcher.add_handler(CommandHandler('beststatistic', stat_best, run_async= True))
    updater.dispatcher.add_handler(CommandHandler('donate', donate_msg, run_async= True))
    updater.dispatcher.add_handler(MessageHandler(Filters.regex(r'@bestorpidrofday_bot') & (~Filters.command), echo))
    updater.dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_members))
    # updater.dispatcher.add_handler(MessageHandler(filters.Entity (MENTION), unknown_msg, run_async= True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()