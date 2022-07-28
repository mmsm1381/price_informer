from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton


class TelegramMessageHandler:
    MARKETS, PLANS, SETTINGS, CONNECT_WITH_US, SELECTING_ACTION = map(chr, range(5))

    @classmethod
    def start(cls, update, context):
        update: Update
        message = 'به ربات قیمت لحظه ای تبدیل خوش آمدید'
        buttons = [
            [
                KeyboardButton(text="💵 بازار‌‌ها", callback_data=str(cls.MARKETS)),
                KeyboardButton(text="📌استراتژي‌ها", callback_data=str(cls.PLANS)),
            ],
            [KeyboardButton(text="⚙️ تنظیمات", callback_data=str(cls.SETTINGS)),
             KeyboardButton(text="☎️ ارتباط‌با‌ما", callback_data=str(cls.CONNECT_WITH_US))
             ]
        ]
        keyboard = ReplyKeyboardMarkup(buttons)
        update.message.reply_text(text=message, reply_markup=keyboard)
        return cls.SELECTING_ACTION

    @classmethod
    def market_menu(cls, update, context):
        buttons = [
            [
                KeyboardButton(text="📃 مشاهده همه بازار‌های موجود", callback_data=str(cls.MARKETS)),
                KeyboardButton(text="🔎 مشاهده قیمت لحظه ای ارز‌ها", callback_data=str(cls.MARKETS)),
            ],
            [KeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data=str(cls.MARKETS)),
             ]
        ]
        keyboard = ReplyKeyboardMarkup(buttons)
        update.message.reply_text(text="fkhdgjr")
        update.callback_query.answer()
        update.callback_query.edit_message(reply_markup=keyboard)
        return cls.MARKETS

    @classmethod
    def show_market_list(cls, update, context):
        message = 'مارکت ها '
        update.message.reply_text(message)

    @classmethod
    def stop(cls, update, context):
        update.message.reply_text("Okay, bye.")


class Bot:

    def __init__(self, bot_token):
        self.bot = Updater(bot_token, use_context=True)
        self.dispatcher = self.bot.dispatcher

    def start_polling(self):
        # markets_handler = ConversationHandler(
        #     entry_points=[CallbackQueryHandler(TelegramMessageHandler.market_menu,
        #                                        pattern="^"+str(TelegramMessageHandler.MARKETS) + "$")],
        #     fallbacks=[CommandHandler('stop', TelegramMessageHandler.stop)], states={})
        handlers = [
            CallbackQueryHandler(TelegramMessageHandler.market_menu,
                                 pattern="^" + str(TelegramMessageHandler.MARKETS) + "$")
        ]

        start_handler = ConversationHandler(entry_points=[CommandHandler('start', TelegramMessageHandler.start)],
                                            states={
                                                TelegramMessageHandler.SELECTING_ACTION: handlers
                                            }, fallbacks=[CommandHandler('stop', TelegramMessageHandler.stop)])

        self.dispatcher.add_handler(start_handler)
        self.bot.start_polling()
        self.bot.idle()


price_bot_informer = Bot(bot_token="5285202877:AAHytsXfkZS4SX4qXzk9sPCwWLcy-fWmBCw")

if __name__ == '__main__':
    price_bot_informer.start_polling()
