from telegram import Bot

# Сіздің боттың токені (жоғарыда берген)
TOKEN = "8331691424:AAEJMLGpVfvX6UR0ni7R6AHAR0K-UQb6R18"

# Бұл чат ID — сіз опросты қай чатқа жібергіңіз келеді, соны жазу керек
# Мысалы, жеке адам болса — 123456789
# Топ немесе канал болса — минуспен басталады: -1001234567890
CHAT_ID = -8331691424 # 👈 Мұны нақты ID-мен алмастырыңыз

# Telegram Bot объектісін құрамыз
bot = Bot(token=TOKEN)

# Сауалнама сұрағы мен жауап нұсқалары
question = "Python-ды қай деңгейде меңгердіңіз?"
options = ["Жаңадан үйреніп жүрмін", "Орташа", "Кәсіби", "Білмеймін"]

# Опрос жіберу
bot.send_poll(
    chat_id=CHAT_ID,
    question=question,
    options=options,
    is_anonymous=True,
    allows_multiple_answers=False
)

print("✅ Опрос Telegram-ға сәтті жіберілді.")
