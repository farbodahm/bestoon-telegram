# -*- coding: utf-8 -*-

import telebot
import sqlite3
import requests
import json

from config import *

bot = telebot.TeleBot(TOKEN)
dbconnect = sqlite3.connect(DB_NAME, check_same_thread=False)
command = dbconnect.cursor()
user_input = {}

##Uncomment if you want log:
#import logging
#logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "این ربات یه کلاینت برای سایت bestoon.ir هستش \
که میتونید باهاش دخل و خرجتون رو ذخیره کنید.\
 البته شدیدا زیر توسعه هستش و داره بهتر و بهتر میشه.\
 و البته این بات هم نسخه بتا هستش و بزودی کامل میشه :)\
\n \
برای استفاده از این بات باید\
 توکنی که از سایت بستون.آی‌آر گرفتید رو به بات بدید تا بتونید\
 باهاش دخل و خرجتون رو ذخیره کنید.\
 اگه هنوز توکنتون رو نگرفتید میتونید از اینجا بگیرید:\
\n \
http://bestoon.ir/accounts/register/ \
بعد از این که توکنتون رو گرفتید \
 دستور /token \
رو برام بفرستید \
")

@bot.message_handler(commands=['token'])
def wait_for_token(message):
    #wait for user response
    msg = bot.reply_to(message, "لطفا توکن ۴۸ رقمی خود را که از سایت دریافت کرده اید وارد نمایید:")
    bot.register_next_step_handler(msg, register_token)
def register_token(message):
    user_token = str(message.text.encode('utf-8'))
    uid = str(message.from_user.id)
    #validate token
    if len(user_token) == 48:
        #get user token from Db if there is one!
        cursor = command.execute("SELECT token from user WHERE uid='{}'".format(uid))
        for row in cursor:
            user_token_db = row[0]
        try:
            user_token_db
        except NameError:
            user_token_db = None
        #insert user token to DB
        if user_token_db == None:
            command.execute("INSERT INTO user ('uid', 'token') VALUES ('{}', '{}')".format(uid, user_token))
            dbconnect.commit()
            bot.reply_to(message, "توکن شما با موفقیت ذخیره شد.\
اکنون میتوانید دخل و خرج خود را حساب کنید\
\n \
برای ثبت دخل پیام /income \
و برای ثبت خرج پیام /expense \
رو برام ارسال کنید :) \
")
        else:
            bot.reply_to(message, "توکن شما قبلا ذخیره شده است. میتوانید دخل و خرج خود را حساب کنید")
    else:
        bot.reply_to(message, "توکن نامعتبر است!")


@bot.message_handler(commands=['income'])
def income(message):
    uid = str(message.from_user.id)
    #get user token from DB
    cursor = command.execute("SELECT token from user WHERE uid='{}'".format(uid))
    for row in cursor:
        user_token = row[0]
    try:
        user_token
    except NameError:
        user_token = None
    if user_token != None:
        user_input['token'] = user_token
        #wait for user amount
        msg = bot.reply_to(message,"چند تومان درآمد داشتید؟")
        bot.register_next_step_handler(msg, get_income_amount)
    else:
        bot.reply_to(message,"ابتدا شما باید توکن خود را ثبت کنید!")
def get_income_amount(message):
    user_input['amount'] = message.text.encode('utf-8')
    #wait for user message
    msg = bot.reply_to(message, "چه توضیحی برای این درآمد دارید؟")
    bot.register_next_step_handler(msg, get_income_text)
def get_income_text(message):
    text = message.text.encode('utf-8')
    token = user_input['token']
    amount = user_input['amount']
    #sendind data to site
    payload = { "token":"{}".format(token), "amount":"{}".format(amount), "text":"{}".format(text) }
    request = requests.post("{}submit/income/".format(URL), data=payload, headers=HEADER)
    #send response to user
    if request.status_code == 200:
        bot.reply_to(message, "درآمد شما با موفقیت ذخیره شد!")
    else:
        bot.reply_to(message, "متاسفانه هنگام ثبت درآمد شما مشکلی پیش آمد! عیب نداره اگه میخوای دوباره امتحان کن :)")

@bot.message_handler(commands=['expense'])
def expense(message):
    uid = str(message.from_user.id)
    #get user token from db
    cursor = command.execute("SELECT token from user WHERE uid='{}'".format(uid))
    for row in cursor:
        user_token = row[0]
    try:
        user_token
    except NameError:
        user_token = None
    if user_token != None:
        user_input['token'] = user_token
        #wait for user amount
        msg = bot.reply_to(message,"چند تومان خرج کردید؟")
        bot.register_next_step_handler(msg, get_expense_amount)
    else:
        bot.reply_to(message,"ابتدا شما باید توکن خود را ثبت کنید!")
def get_expense_amount(message):
    user_input['amount'] = message.text.encode('utf-8')
    msg = bot.reply_to(message, "توضیح برای این خرج چی هستش؟")
    #wait for user message
    bot.register_next_step_handler(msg, get_expene_text)
def get_expene_text(message):
    text = message.text.encode('utf-8')
    token = user_input['token']
    amount = user_input['amount']
    #sendind data to site
    payload = { "token":"{}".format(token), "amount":"{}".format(amount), "text":"{}".format(text) }
    request = requests.post("{}submit/expense/".format(URL), data=payload, headers=HEADER)
    #send response to user
    if request.status_code == 200:
        bot.reply_to(message," خرج شما ثبت شد!")
    else:
        bot.reply_to(message, "متاسفانه هنگام ثبت خرج شما مشکلی پیش آمد! عیب نداره اگه میخوای دوباره امتحان کن :)")

@bot.message_handler(commands=['stat'])
def getstat(message):
    uid = str(message.from_user.id)
    #get user token from DB
    cursor = command.execute("SELECT token from user WHERE uid='{}'".format(uid))
    for row in cursor:
        user_token = row[0]
    try:
        user_token
    except NameError:
        user_token = None
    if user_token != None:
        user_input['token'] = user_token
        #sending request to site
        payload = { "token":"{}".format(user_token) }
        PostRequest = requests.post("{}q/generalstat/".format(URL), data=payload, headers=HEADER)
        #get data from site
        PostResponse = PostRequest.content
        PostResponse = json.loads(PostResponse)
        expense = PostResponse['expense']
        expense_amount_sum = expense['amount__sum']
        expense_amount_count = expense['amount__count']
        income = PostResponse['income']
        income_amount_sum = income['amount__sum']
        income_amount_count = income['amount__count']
        bot.reply_to(message,"\
            درآمد: \n \
            مجموع: {} تومان \n \
            تعداد: {} عدد \n \
            خرج:\n \
            مجموع: {} تومان \n \
            تعداد: {} عدد \n \
        ".format(income_amount_sum, income_amount_count, expense_amount_sum, expense_amount_count))
    else:
        bot.reply_to(message,"ابتدا شما باید توکن خود را ثبت کنید!")
bot.polling(True)
