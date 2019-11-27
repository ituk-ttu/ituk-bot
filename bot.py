import os
from telegram.ext import Updater, CommandHandler, CallbackContext
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging
import requests
import re

from telegram.update import Update

SCOPES = ['https://www.googleapis.com/auth/calendar']
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def add_to_calender(update: Update, context: CallbackContext):
    print(f"Adding to calendar: ", context.args)
    if update.effective_chat.id == -386179704 or update.effective_chat.id == 142217903:
        email = context.args[0]
        if re.fullmatch(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            rule = {
                'scope': {
                    'type': 'user',
                    'value': email,
                },
                'role': 'reader'
            }
            credentials = service_account.Credentials.from_service_account_file(filename="credentials.json", scopes=SCOPES)

            service = build('calendar', 'v3', credentials=credentials)
            service.acl().insert(calendarId=os.environ["CALENDAR_KEY"], body=rule).execute()

            context.bot.send_message(update.effective_chat.id, f"Successfully added to calendar email: { context.args[0]}")
        else:
            context.bot.send_message(update.effective_chat.id, "Email is not valid")
    else:
        context.bot.send_message(update.effective_chat.id, "You are not allowed to do it here!")


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def get_food_name(food_item):
    return food_item["nameEst"]


def get_food_price(food_item):
    price_item = food_item["prices"][-1]
    price = str(price_item["priceValue"]) + "€"

    if price_item["modifierName"]:
        price += " " + str(price_item["modifierName"])

    return price


def get_provider_name(item):
    return item[0]["provider"]["name"]


def create_menu_string(provider_id):
    contents = requests.get(f"https://fuud.raimondlu.me/api/v1/FoodItem/provider/{provider_id}").json()

    if len(contents) == 0:
        return "No menu found!"

    menu_string = f"Tänane {get_provider_name(contents)} menüü:\n"

    for item in contents:
        menu_string += get_food_name(item) + " - " + get_food_price(item) + "€\n"

    return menu_string


def send_bitstop(update: Update, context: CallbackContext):
    context.bot.send_message(update.effective_chat.id, create_menu_string(1))


def send_daily(update: Update, context: CallbackContext):
    context.bot.send_message(update.effective_chat.id, create_menu_string(2))


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    updater = Updater(os.environ["API_KEY"], use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # # Add command handler to start the payment invoice
    dp.add_handler(CommandHandler("add_to_calendar", add_to_calender, pass_args=True))
    dp.add_error_handler(error)
    dp.add_handler(CommandHandler('bitstop', send_bitstop))
    dp.add_handler(CommandHandler('daily', send_daily))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
