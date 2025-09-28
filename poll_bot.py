poll_bot.py
python
from aiogram import Bot, Dispatcher, types, executor

API_TOKEN = '8331691424:AAEJMLGpVfvX6UR0ni7R6AHAR0K-UQb6R18'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    await message.answer("Сәлем! Сауалнамаға қатысу үшін төмендегіні көріңіз 👇")

    await bot.send_poll(
        chat_id=message.chat.id,
        question="Оқушылар сабаққа қандай құрылғымен қатысады?",
        options=["Компьютер", "Интерактивті тақта", "Телефон", "Қағаз/дәптер"],
        is_anonymous=False
    )

if _name_ == '_main_':
    executor.start_polling(dp)
