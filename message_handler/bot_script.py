from django.conf import settings
from enum import Enum

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from message_handler import models as message_handler_models
from price_collector import models as price_collector_models


class TelegramMessageHandler:
    ONLINE_PRICE, SELECTING_ACTION, MARKETS = map(chr, range(3))

    @classmethod
    def start(cls, update, context):
        update: Update
        message = 'به بات قیمت لحظه ای تبدیل خوش آمدید'
        _, created = message_handler_models.Subscriber.objects.get_or_create(chat_id=update.message.chat_id,
                                                                             defaults={'active': True})
        buttons = [
            [
                InlineKeyboardButton(text="بازار ها",
                                     callback_data=str(TelegramMessageHandler.MARKETS)),
            ],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        if created:
            update.message.reply_text(message)
        else:
            message = 'منو'
            update.message.reply_text(text=message, reply_markup=keyboard)

    @classmethod
    def menu(cls, update, context):
        # show menu
        pass

    @classmethod
    def show_market_list(cls, update, context):
        message = ''
        for market in price_collector_models.Market.objects.all():
            message += f"🟢 {market.first_currency_symbol}_{market.second_currency_symbol} :\n"
        update.message.reply_text(message)

    @classmethod
    def stop(cls, update, context):
        update.message.reply_text("Okay, bye.")


class Bot:

    def __init__(self, bot_token):
        self.bot = Updater(bot_token, use_context=True)
        self.dispatcher = self.bot.dispatcher

    def start_polling(self):
        selection_handlers = [
            # add_member_conv,
            CallbackQueryHandler(TelegramMessageHandler.show_market_list,
                                 pattern="^" + str(TelegramMessageHandler.MARKETS) + "$"),
            # CallbackQueryHandler(adding_self, pattern="^" + str(ADDING_SELF) + "$"),
            # CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
        ]

        start_handler = ConversationHandler(entry_points=[CommandHandler('start', TelegramMessageHandler.start)],
                                            states={
                                                TelegramMessageHandler.SELECTING_ACTION: selection_handlers
                                            }, fallbacks=[CommandHandler('stop', TelegramMessageHandler.stop)])

        self.dispatcher.add_handler(start_handler)
        self.bot.start_polling()
        self.bot.idle()


price_bot_informer = Bot(bot_token=settings.BOT_TOKEN)
