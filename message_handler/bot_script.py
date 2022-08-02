from django.conf import settings
import logging
from enum import Enum

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove

from message_handler import models as message_handler_models
from price_collector import models as price_collector_models
from price_collector.redis import TREDIS

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramMessageHandler:
    MARKETS, PLANS, SETTINGS, CONNECT_WITH_US, MAIN_SELECTING_ACTION, MARKET_SELECTING_ACTION, SELECTING_MARKET, \
    PLANS_SELECTING_ACTION, ADD_MARKETS_TO_PLAN, ADD_PERIOD_TO_PLAN = map(chr, range(10))

    SAVE_PLAN_BUTTON_TEXT = 'ذخیره برنامه'
    PLANS_MENU_BUTTON_TEXT = "📌استراتژي‌ها"
    ADD_PLAN_BUTTON_TEXT = '⏰ اضافه کردن برنامه جدید'
    MARKET_MENU_BUTTON_TEXT = "💵 بازار"
    MARKETS_OVER_VIEW_BUTTON_TEXT = "📃 مشاهده همه بازار‌ها"
    MARKET_ONLINE_PRICE_BUTTON_TEXT = "🔎 مشاهده قیمت لحظه ای بازار‌ها"

    @classmethod
    def start(cls, update, context):
        message = 'لطفا از منوی زیر یکی از گزینه ها رو انتخاب کنید'
        obj, created = message_handler_models.Subscriber.objects.get_or_create(chat_id=update.message.chat_id)

        buttons = [
            [
                KeyboardButton(text=cls.MARKET_MENU_BUTTON_TEXT),
                KeyboardButton(text=cls.PLANS_MENU_BUTTON_TEXT),
            ],
            [KeyboardButton(text="⚙️ تنظیمات"),
             KeyboardButton(text="☎️ ارتباط‌با‌ما")
             ]
        ]
        keyboard = ReplyKeyboardMarkup(buttons)
        if created:
            message = 'به ربات قیمت لحظه ای خوش آمدید, لطفا از منوی زیر یکی از گزینه ها رو انتخاب کنید'
        update.message.reply_text(text=message, reply_markup=keyboard)
        return cls.MAIN_SELECTING_ACTION

    @classmethod
    def market_menu(cls, update, context):
        message = "منوی بازار"
        buttons = [
            [
                KeyboardButton(text=cls.MARKETS_OVER_VIEW_BUTTON_TEXT),
                KeyboardButton(text=cls.MARKET_ONLINE_PRICE_BUTTON_TEXT),
            ],
        ]
        keyboard = ReplyKeyboardMarkup(buttons)
        update.message.reply_text(text=message, reply_markup=keyboard)
        return cls.MARKET_SELECTING_ACTION

    @classmethod
    def show_market_list(cls, update, context):
        message = price_collector_models.Market.get_all_markets_from_db_and_create_message()
        update.message.reply_text(message)
        return cls.MARKET_SELECTING_ACTION

    @classmethod
    def market_online_price_entry_point(cls, update, context):
        message = "لطفا بازار مورد نظر خود را وارد کنید.\n"
        message += "مثال های مورد قبول : BTC_IRT, btc_irt, BTC_irt"
        update.message.reply_text(text=message, reply_markup=ReplyKeyboardRemove())
        return cls.SELECTING_MARKET

    @classmethod
    def show_a_market_price(cls, update, context):
        message = 'ارز وارد شده یافت نشد لطفا دوباره تلاش کنید'
        market = update.message.text.upper().replace("_", "")
        sell_price = TREDIS.redis_instance.get(f'{market}_ask')
        buy_price = TREDIS.redis_instance.get(f'{market}_bid')
        if buy_price and sell_price:
            message = f"🟢  {update.message.text.upper()} \n\n"
            message += f'SELL : {sell_price}\n'
            message += f'BUY : {buy_price}'
        update.message.reply_text(text=message)
        return cls.SELECTING_MARKET

    @classmethod
    def plans_menu(cls, update, context):
        message = "منوی استراتژی‌ها"
        buttons = [
            [
                KeyboardButton(text=cls.ADD_PLAN_BUTTON_TEXT),
            ],
        ]
        keyboard = ReplyKeyboardMarkup(buttons)
        update.message.reply_text(text=message, reply_markup=keyboard)
        return cls.PLANS_SELECTING_ACTION

    @classmethod
    def add_plan_entry_point(cls, update, context):
        message = "لطفا بازه زمانی را برای این برنامه به ثانیه مشخص کنید.(حداقل مقدار 300 ثانیه و‌ حداکثر 604800 ثانیه است.)"
        update.message.reply_text(text=message, reply_markup=ReplyKeyboardRemove())
        return cls.ADD_PERIOD_TO_PLAN

    @classmethod
    def add_plan_period(cls, update, context):
        try:
            buttons = [
                [
                    KeyboardButton(text=cls.SAVE_PLAN_BUTTON_TEXT),
                ],
            ]
            keyboard = ReplyKeyboardMarkup(buttons)
            period = int(update.message.text)
            if 300 <= period <= 604800:
                subscriber = message_handler_models.Subscriber.objects.get(chat_id=update.message.chat_id)
                plan = message_handler_models.SubscribePlan.objects.create(period_in_second=period, active=False,
                                                                           subscriber=subscriber)
                context.user_data['plan_id'] = plan.pk
                message = "لطفا مازکت های مورد نظر‌خود را وارد کنید سپس دکمه ذخیره را لمس کنید"
                update.message.reply_text(text=message, reply_markup=keyboard)
                return cls.ADD_MARKETS_TO_PLAN
            else:
                raise Exception()
        except Exception as ve:
            update.message.reply_text("لطفا عدد را بدرستی وارد کنید و دوباره امتحان کنید")
            return cls.ADD_PERIOD_TO_PLAN

    @classmethod
    def add_markets_to_plan(cls, update, context):
        try:
            first_currency, second_currency = update.message.text.upper().split("_")
            market = price_collector_models.Market.objects.get(first_currency_symbol=first_currency,
                                                               second_currency_symbol=second_currency)
            plan_id = context.user_data['plan_id']
            message_handler_models.SubscribePlan.objects.get(id=plan_id).markets.add(market)
            update.message.reply_text(text="ارز مورد نظر ذخیره شد.")
            return cls.ADD_MARKETS_TO_PLAN
        except Exception as ve:
            print(ve)
            update.message.reply_text("لطفا بازار را بدرسنی وارد کنید")
            return cls.ADD_MARKETS_TO_PLAN

    @classmethod
    def save_plan(cls, update, context):
        plan_id = context.user_data['plan_id']
        message_handler_models.SubscribePlan.objects.filter(id=plan_id).update(active=True)
        update.message.reply_text('با موفقیت ذخیره شد')

    @classmethod
    def stop(cls, update, context):
        update.message.reply_text("Okay, bye.")


class Bot:

    def __init__(self, bot_token):
        self.bot = Updater(bot_token, use_context=True)
        self.dispatcher = self.bot.dispatcher

    def start_polling(self):
        markets_online_price_conv_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.text(TelegramMessageHandler.MARKET_ONLINE_PRICE_BUTTON_TEXT),
                                         TelegramMessageHandler.market_online_price_entry_point)], states={
                TelegramMessageHandler.SELECTING_MARKET: [
                    MessageHandler(Filters.text, TelegramMessageHandler.show_a_market_price)]
            }, fallbacks=[CommandHandler('stop', TelegramMessageHandler.stop)])

        markets_handlers = [
            markets_online_price_conv_handler,
            MessageHandler(Filters.text(TelegramMessageHandler.MARKETS_OVER_VIEW_BUTTON_TEXT),
                           TelegramMessageHandler.show_market_list),
        ]

        market_conv_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.text(TelegramMessageHandler.MARKET_MENU_BUTTON_TEXT),
                                         TelegramMessageHandler.market_menu)],
            fallbacks=[CommandHandler('stop', TelegramMessageHandler.stop)], states={
                TelegramMessageHandler.MARKET_SELECTING_ACTION: markets_handlers
            })

        add_plan_conv_handler = ConversationHandler(entry_points=[
            MessageHandler(Filters.text(TelegramMessageHandler.ADD_PLAN_BUTTON_TEXT),
                           TelegramMessageHandler.add_plan_entry_point)], states={
            TelegramMessageHandler.ADD_PERIOD_TO_PLAN: [
                MessageHandler(Filters.text, TelegramMessageHandler.add_plan_period)],
            TelegramMessageHandler.ADD_MARKETS_TO_PLAN: [
                MessageHandler(Filters.text(TelegramMessageHandler.SAVE_PLAN_BUTTON_TEXT),
                               TelegramMessageHandler.save_plan),
                MessageHandler(Filters.text, TelegramMessageHandler.add_markets_to_plan)]
        }, fallbacks=[CommandHandler('stop', TelegramMessageHandler.stop)])

        plan_handlers = [
            add_plan_conv_handler
        ]

        plan_conv_handler = ConversationHandler(
            entry_points=[MessageHandler(
                Filters.text(TelegramMessageHandler.PLANS_MENU_BUTTON_TEXT), TelegramMessageHandler.plans_menu)],
            states={
                TelegramMessageHandler.PLANS_SELECTING_ACTION: plan_handlers
            }
            , fallbacks=[CommandHandler('stop', TelegramMessageHandler.stop)]
        )

        main_handlers = [
            market_conv_handler,
            plan_conv_handler
        ]
        start_handler = ConversationHandler(entry_points=[CommandHandler('start', TelegramMessageHandler.start)],
                                            states={
                                                TelegramMessageHandler.MAIN_SELECTING_ACTION: main_handlers
                                            }, fallbacks=[CommandHandler('stop', TelegramMessageHandler.stop)],
                                            allow_reentry=True)

        self.dispatcher.add_handler(start_handler)
        self.bot.start_polling()
        self.bot.idle()


price_bot_informer = Bot(bot_token=settings.BOT_TOKEN)
