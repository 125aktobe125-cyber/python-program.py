from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import openpyxl
from openpyxl import Workbook
from collections import defaultdict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# ---------------- Токен ----------------
TOKEN = "8331691424:AAFUSp-4BjaUmVn92tFgCLfJZUJx75AnC_k"

# ---------------- Сауалнама сұрақтары ----------------
questions = {
    "parent": [
        "1. Менің балам мектепке қуана барады",
        "2. Сыныпта қолайлы атмосфера бар",
        "3. Мектеп сапалы білім береді",
        "4. Оқу пәндері менің балама оңай беріледі",
        "5. Мұғалімдер біздің баланың оқудағы жетістіктерін әділ бағалайды",
        "6. Біздің баламыз оқу сабақтары мен үй тапсырмаларына шамадан тыс жүктелмейді",
        "7. Мектепте қолданылатын оқытудың жаңа тәсілдері біздің баламыздың қабілеттерінің көрінісі мен дамуына жағдай жасайды",
        "8. Мен баланың оқу жетістіктері мен мінез-құлқы туралы ақпараттандыру сапасына қанағаттанамын",
        "9. Мен мектептегі сабақтан тыс жұмыс бағдарламасына ризамын",
        "10. Мен баламның сынып жетекшісінің жұмысына қанағаттанамын",
        "11. Мектепте біздің баламыз үшін пайдалы және қызықты іс-шаралар өткізіледі",
        "12. Мен мектеп асханасы/буфет жұмысымен қанағаттанамын",
        "13. Педагогтар педагогикалық этика нормаларын сақтайды",
        "14. Менің балам мектепте қауіпсіз",
        "15. Мектепте олар біздің баламыздың денсаулығына қамқорлық жасайды",
        "16. Мен мектеп әкімшілігінің жұмысына қанағаттанамын",
        "17. Мектеп өміріне қатысуға ниет бар",
    ],
    "student": [
        "1. Мен өз мектебімде оқуға қызығамын",
        "2. Менің сүйікті пәндерім бар (егер солай болса, қайсысы?)",
        "3. Менің сүйікті мұғалімдерім бар",
        "4. Біздің мектеп мұғалімдеріне қиын жағдайда кеңес пен көмек сұрауға болады",
        "5. Сабақта мен әрқашан өз пікірімді еркін айта аламын",
        "6. Сабақта мұғалім менің мінез-құлқымды емес, менің білімімді бағалайды",
        "7. Мен мектепте жиі шаршаймын",
        "8. Менің мектебімде дербес және жиынтық жұмыстардың саны бір күнде екіден көп",
        "9. Мен мектепте өзімді қауіпсіз сезінемін, психологиялық тұрғыдан ыңғайлы",
        "10. Мен тамақтану сапасына қанағаттанамын",
        "11. Мен өз құқығымды білемін",
        "12. Мен келесі үйірмелерге, секцияларға, ансамбльдерге барамын",
        "13. Менде мектеп істеріне қатысуға деген ұмтылыс пен қажеттілік бар",
        "14. Менің мектебімде ол үшін пайдалы және маңызды нәрсе жасаған кезде менің жетістіктерім байқалады",
        "15. Мен өз мектебімді жақсы көремін және онда оқығанымды мақтан тұтамын",
    ],
    "teacher": [
        "1. Мен осы мектепте жұмыс істегенімді мақтан тұтамын",
        "2. Мен тиімді әдістемелік көмек аламын",
        "3. Мен еңбек жағдайына қанағаттанамын",
        "4. Мен мектеп әкімшілігінің жұмыс стиліне қанағаттанамын",
        "5. Мектеп оқушылар арасындағы жанжалдарды тоқтатады және тиімді шешеді",
        "6. Мен мектептің оқу-материалдық базасына қанағаттанамын",
        "7. Ұжымда қолайлы моральдық-психологиялық ахуал бар",
        "8. Мен мектептегі тамақтану сапасына қанағаттанамын",
        "9. Әріптестер маған көмектесуге әрқашан дайын",
        "10. Оқу сабақтарын сәтті өткізу үшін мектеп барлық қажетті оқу-әдістемелік және техникалық құралдарды ұсынды",
        "11. Мектепте менің кәсіби және шығармашылық өсуім үшін жағдай жасалған",
        "12. Мектепте педагогтарды көтермелеу әдістері белгіленген",
        "13. Мен жұмыс істейтін балалар білімге ұмтылады",
        "14. Мен оқушылармен қарым-қатынасыма қанағаттанамын",
        "15. Мен сынып жетекшісі ретіндегі жұмысыма қанағаттанамын",
    ]
}

answers = ["Толық келісемін", "Келісемін", "Келіспеймін", "Толық келіспеймін", "Басқа"]

all_results = defaultdict(list)

# ---------------- Excel-ге жазу ----------------
def save_to_excel(filename="survey_results.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Survey Results"

    ws.append(["User ID", "Рөл", "Сұрақ", "Жауап"])
    for user_id, records in all_results.items():
        for role, q, a in records:
            ws.append([user_id, role, q, a])

    ws_stats = wb.create_sheet("Statistics")

    header = ["Рөл", "Сұрақ"]
    for ans in answers:
        header.append(f"{ans} (саны)")
        header.append(f"{ans} (%)")
    ws_stats.append(header)

    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    total_counts = defaultdict(lambda: defaultdict(int))

    for user_id, records in all_results.items():
        for role, q, a in records:
            stats[role][q][a] += 1
            total_counts[role][q] += 1

    for role, qs in stats.items():
        for q, answers_dict in qs.items():
            total = total_counts[role][q]
            row = [role, q]

            for ans in answers:
                count = answers_dict.get(ans, 0)
                percent = (count / total) * 100 if total > 0 else 0
                row.append(count)
                row.append(f"{percent:.2f}%")

            ws_stats.append(row)

    wb.save(filename)
    return filename

# ---------------- Email жіберу ----------------
def send_email_with_attachment(receiver_email, subject, body, filename):
    sender_email = "125aktobe125@gmail.com"
    sender_password = "rvrkygnxnglgwiix"  # Gmail App Password!

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

# ---------------- Telegram логикасы ----------------
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Оқушы", callback_data="role_student")],
        [InlineKeyboardButton("Ата-ана", callback_data="role_parent")],
        [InlineKeyboardButton("Оқытушы", callback_data="role_teacher")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("125 AKTOBE мектебінің сауалнамасына қош келдіңіз! Өз рөліңізді таңдаңыз:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data.startswith("role_"):
        role = query.data.split("_")[1]
        context.user_data["role"] = role
        context.user_data["q_index"] = 0
        context.user_data["answers"] = []
        send_question(query, context)

    elif query.data.startswith("ans_"):
        _, choice = query.data.split("_", 1)
        role = context.user_data["role"]
        q_index = context.user_data["q_index"]

        if choice == "Басқа":
            context.user_data["awaiting_custom_answer"] = True
            query.message.reply_text("Өз жауабыңызды жазыңыз:")
        else:
            q = questions[role][q_index]
            context.user_data["answers"].append((role, q, choice))
            next_question(query, context)

def custom_answer(update: Update, context: CallbackContext):
    if context.user_data.get("awaiting_custom_answer"):
        role = context.user_data["role"]
        q_index = context.user_data["q_index"]
        answer_text = update.message.text

        q = questions[role][q_index]
        context.user_data["answers"].append((role, q, answer_text))
        context.user_data["awaiting_custom_answer"] = False

        next_question(update, context, from_message=True)

def next_question(source, context, from_message=False):
    role = context.user_data["role"]
    context.user_data["q_index"] += 1
    q_index = context.user_data["q_index"]

    if q_index < len(questions[role]):
        question = questions[role][q_index]
        keyboard = [[InlineKeyboardButton(a, callback_data=f"ans_{a}")] for a in answers]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if from_message:
            source.message.reply_text(question, reply_markup=reply_markup)
        else:
            source.message.reply_text(question, reply_markup=reply_markup)
    else:
        user_id = source.from_user.id if not from_message else source.message.from_user.id
        for role, q, a in context.user_data["answers"]:
            all_results[user_id].append((role, q, a))

        file = save_to_excel()
        send_email_with_attachment("125aktobe125@gmail.com", "Сауалнама нәтижелері", "Сауалнама жауаптары Excel файлында.", file)

        source.message.reply_text("✅ Сауалнама аяқталды! ")

def send_question(query, context):
    role = context.user_data["role"]
    q_index = context.user_data["q_index"]
    question = questions[role][q_index]

    keyboard = [[InlineKeyboardButton(a, callback_data=f"ans_{a}")] for a in answers]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_text(question, reply_markup=reply_markup)

# ---------------- Запуск ----------------
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, custom_answer))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
