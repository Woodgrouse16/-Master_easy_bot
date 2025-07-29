import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from dotenv import load_dotenv

# Загружаем токены из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MASTERS_CHAT_ID = int(os.getenv("MASTERS_CHAT_ID"))

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определяем состояния
class Form(StatesGroup):
    service = State()
    date = State()
    time = State()
    name_phone = State()

# Старт
@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer(
        "Здравствуйте! Я — помощник мастера. Помогу вам записаться на удобное время ✨\n"
        "Сейчас уточню пару моментов — и мы всё оформим!"
    )

    # Кнопки с выбором услуг
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Массаж спины"))
    keyboard.add(KeyboardButton("Массаж лица"))
    keyboard.add(KeyboardButton("Общий массаж"))
    keyboard.add(KeyboardButton("Свой вариант"))

    await message.answer("Какую услугу вы бы хотели записать?", reply_markup=keyboard)
    await Form.service.set()

# Услуга
@dp.message_handler(state=Form.service)
async def get_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)

    await message.answer(
        "На какой день вы хотите записаться?\n"
        'Можете указать конкретную дату (например, "1 августа") или просто день недели ("в пятницу").',
        reply_markup=ReplyKeyboardRemove()
    )
    await Form.date.set()

# Дата
@dp.message_handler(state=Form.date)
async def get_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Утро (до 12:00)"))
    keyboard.add(KeyboardButton("День (12:00–17:00)"))
    keyboard.add(KeyboardButton("Вечер (после 17:00)"))

    await message.answer("А в какое время дня вам удобнее?", reply_markup=keyboard)
    await Form.time.set()

# Время
@dp.message_handler(state=Form.time)
async def get_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)

    await message.answer("Как к вам можно обращаться?\nИ, пожалуйста, оставьте номер телефона для связи.")
    await Form.name_phone.set()

# Имя и телефон
@dp.message_handler(state=Form.name_phone)
async def get_name_phone(message: types.Message, state: FSMContext):
    await state.update_data(name_phone=message.text)

    data = await state.get_data()
    text = (
        "📥 Новая заявка:\n"
        f"🛎 Услуга: {data['service']}\n"
        f"📅 Дата: {data['date']}\n"
        f"⏰ Время: {data['time']}\n"
        f"👤 Клиент: {data['name_phone']}"
    )

    # Отправляем мастеру
    await bot.send_message(MASTERS_CHAT_ID, text)

    await message.answer(
        "Спасибо! Я передам данные мастеру — и с вами свяжутся в ближайшее время.\nХорошего дня 🌿",
        reply_markup=ReplyKeyboardRemove()
    )

    await state.finish()

# Запуск
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
