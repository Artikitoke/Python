import asyncio
from datetime import datetime
import pytz
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Вставте сюди ваш токен бота від @BotFather
BOT_TOKEN = "8446665709:AAFN_10mZbfPtiWOCK_Xm8vajfjHkBRvzqQ"

# Часові пояси
TIMEZONES = {
    "ua": {"tz": pytz.timezone("Europe/Kyiv"), "name_ua": "Україна 🇺🇦", "name_en": "Ukraine 🇺🇦", "name_ru": "Украина 🇺🇦"},
    "ru": {"tz": pytz.timezone("Europe/Moscow"), "name_ua": "Москва 🇷🇺", "name_en": "Moscow 🇷🇺", "name_ru": "Москва 🇷🇺"},
    "gb": {"tz": pytz.timezone("Europe/London"), "name_ua": "Лондон 🇬🇧", "name_en": "London 🇬🇧", "name_ru": "Лондон 🇬🇧"}
}

# Тексти для різних мов
TEXTS = {
    "ua": {
        "welcome": "🎄 Вітаю! Я допоможу тобі відрахувати час до Нового Року! 🎆\n\nОбери мову та часовий пояс:",
        "choose_timezone": "🌍 Обери часовий пояс:",
        "choose_language": "🌐 Обери мову:\n\nLanguage | Мова | Язык",
        "countdown": "🎄✨ <b>ВІДЛІК ДО НОВОГО 2026 РОКУ</b> ✨🎄",
        "time_left": "⏰ <b>Залишилось:</b>",
        "days": "днів",
        "hours": "годин",
        "minutes": "хвилин",
        "seconds": "секунд",
        "timezone": "🌍 <b>Часовий пояс:</b>",
        "happy_new_year": "🎉🎊 <b>З НОВИМ 2026 РОКОМ!</b> 🎊🎉\n\n✨ Нехай цей рік принесе радість, здоров'я та успіх! ✨",
        "change_settings": "⚙️ Змінити налаштування"
    },
    "en": {
        "welcome": "🎄 Welcome! I'll help you count down to the New Year! 🎆\n\nChoose your language and timezone:",
        "choose_timezone": "🌍 Choose timezone:",
        "choose_language": "🌐 Choose language:\n\nLanguage | Мова | Язык",
        "countdown": "🎄✨ <b>COUNTDOWN TO 2026</b> ✨🎄",
        "time_left": "⏰ <b>Time left:</b>",
        "days": "days",
        "hours": "hours",
        "minutes": "minutes",
        "seconds": "seconds",
        "timezone": "🌍 <b>Timezone:</b>",
        "happy_new_year": "🎉🎊 <b>HAPPY NEW YEAR 2026!</b> 🎊🎉\n\n✨ May this year bring you joy, health and success! ✨",
        "change_settings": "⚙️ Change settings"
    },
    "ru": {
        "welcome": "🎄 Привет! Я помогу тебе отсчитать время до Нового Года! 🎆\n\nВыбери язык и часовой пояс:",
        "choose_timezone": "🌍 Выбери часовой пояс:",
        "choose_language": "🌐 Выбери язык:\n\nLanguage | Мова | Язык",
        "countdown": "🎄✨ <b>ОТСЧЁТ ДО НОВОГО 2026 ГОДА</b> ✨🎄",
        "time_left": "⏰ <b>Осталось:</b>",
        "days": "дней",
        "hours": "часов",
        "minutes": "минут",
        "seconds": "секунд",
        "timezone": "🌍 <b>Часовой пояс:</b>",
        "happy_new_year": "🎉🎊 <b>С НОВЫМ 2026 ГОДОМ!</b> 🎊🎉\n\n✨ Пусть этот год принесёт радость, здоровье и успех! ✨",
        "change_settings": "⚙️ Изменить настройки"
    }
}

# Зберігання даних користувачів
user_data = {}

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обробка команди /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_ua")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])
    
    await message.answer(
        "🌐 Choose language | Оберіть мову | Выберите язык:",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("lang_"))
async def callback_language(callback: types.CallbackQuery):
    """Обробка вибору мови"""
    await callback.answer()
    
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    
    if user_id not in user_data:
        user_data[user_id] = {"language": "ua", "timezone": "ua", "message_id": None, "task": None}
    
    user_data[user_id]["language"] = lang
    
    # Показати вибір часового поясу
    texts = TEXTS[lang]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TIMEZONES["ua"][f"name_{lang}"], callback_data="tz_ua")],
        [InlineKeyboardButton(text=TIMEZONES["ru"][f"name_{lang}"], callback_data="tz_ru")],
        [InlineKeyboardButton(text=TIMEZONES["gb"][f"name_{lang}"], callback_data="tz_gb")]
    ])
    
    await callback.message.edit_text(
        texts["choose_timezone"],
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("tz_"))
async def callback_timezone(callback: types.CallbackQuery):
    """Обробка вибору часового поясу"""
    await callback.answer()
    
    user_id = callback.from_user.id
    tz = callback.data.split("_")[1]
    
    user_data[user_id]["timezone"] = tz
    
    # Зупинити попередню задачу, якщо вона є
    if user_data[user_id]["task"]:
        user_data[user_id]["task"].cancel()
    
    # Створити нове повідомлення з відліком
    message = await callback.message.answer("⏳ Запускаю відлік...")
    user_data[user_id]["message_id"] = message.message_id
    
    # Видалити старе повідомлення
    await callback.message.delete()
    
    # Запустити відлік
    task = asyncio.create_task(countdown_loop(user_id, callback.message.chat.id))
    user_data[user_id]["task"] = task

@dp.callback_query(F.data == "change_settings")
async def callback_change_settings(callback: types.CallbackQuery):
    """Обробка зміни налаштувань"""
    await callback.answer()
    
    user_id = callback.from_user.id
    lang = user_data[user_id]["language"]
    texts = TEXTS[lang]
    
    # Зупинити відлік
    if user_data[user_id]["task"]:
        user_data[user_id]["task"].cancel()
    
    # Показати вибір мови
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_ua")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ])
    
    await callback.message.edit_text(
        texts["choose_language"],
        reply_markup=keyboard
    )

async def countdown_loop(user_id: int, chat_id: int):
    """Цикл оновлення відліку"""
    try:
        while True:
            if user_id not in user_data:
                break
            
            lang = user_data[user_id]["language"]
            tz_key = user_data[user_id]["timezone"]
            message_id = user_data[user_id]["message_id"]
            
            texts = TEXTS[lang]
            tz = TIMEZONES[tz_key]["tz"]
            
            # Поточний час у вибраному поясі
            now = datetime.now(tz)
            
            # Новий рік у вибраному поясі
            new_year = tz.localize(datetime(2026, 1, 1, 0, 0, 0))
            
            # Різниця часу
            delta = new_year - now
            
            if delta.total_seconds() <= 0:
                # Новий рік настав!
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=texts["change_settings"], callback_data="change_settings")]
                ])
                
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f"{texts['happy_new_year']}\n\n🌟💫🎆🎊🎉",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                break
            
            # Розрахунок днів, годин, хвилин, секунд
            days = delta.days
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            seconds = delta.seconds % 60
            
            # Формування тексту
            text = f"{texts['countdown']}\n\n"
            text += f"🎊 {texts['time_left']} 🎊\n\n"
            text += f"📅 <b>{days}</b> {texts['days']}\n"
            text += f"🕐 <b>{hours:02d}</b> {texts['hours']}\n"
            text += f"⏱ <b>{minutes:02d}</b> {texts['minutes']}\n"
            text += f"⏲ <b>{seconds:02d}</b> {texts['seconds']}\n\n"
            text += f"{texts['timezone']} {TIMEZONES[tz_key][f'name_{lang}']}\n\n"
            text += "🎄 🎁 ❄️ ⭐ 🎅 🔔 ✨"
            
            # Кнопка налаштувань
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=texts["change_settings"], callback_data="change_settings")]
            ])
            
            # Оновлення повідомлення
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except Exception:
                pass  # Ігнорувати помилки, якщо текст не змінився
            
            await asyncio.sleep(1)
    
    except asyncio.CancelledError:
        pass

async def main():
    """Запуск бота"""
    print("🤖 Бот запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())