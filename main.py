import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

PROFESSIONS_DATA = {
    "Медицина": {
        "p1": ("IT-медик", "img/11.png"),
        "p2": ("Архитектор медоборудования", "img/12.png"),
        "p3": ("Биоэтик", "img/13.png"),
        "p4": ("Генетический консультант", "img/14.png")
    },
    "Строительство": {
        "p5": ("Специалист по модернизации строительных технологий", "img/15.png"),
        "p6": ("Проектировщик умного дома", "img/16.png"),
        "p7": ("Прораб-вотчер", "img/17.png"),
        "p8": ("BIM-менеджер", "img/18.png")
    },
    "Авиация": {
        "p9": ("Инженер малой авиации", "img/19.png"),
        "p10": ("Аналитик эксплуатационных данных", "img/20.png"),
        "p11": ("Проектировщик дирижаблей", "img/21.png"),
        "p12": ("Проектировщик интерфейса беспилотников", "img/22.png")
    },
    "Безопасность": {
        "p13": ("Аудитор промышленной безопасности", "img/23.png"),
        "p14": ("Дистанционный координатор безопасности", "img/24.png"),
        "p15": ("Экологический системный специалист", "img/25.png"),
        "p16": ("Проектировщик личной безопасности", "img/26.png")
    }
}

IMG_MAP = {
    "Медицина": "img/7.png",
    "Строительство": "img/8.png",
    "Безопасность": "img/9.png",
    "Авиация": "img/10.png"
}

PROF_ID_TO_NAME = {}
PROF_NAME_TO_ID = {}

for industry, professions in PROFESSIONS_DATA.items():
    for pid, (name, _) in professions.items():
        PROF_ID_TO_NAME[pid] = (name, industry)
        PROF_NAME_TO_ID[name] = pid


def load_descriptions(file_path="descriptions.txt"):
    descriptions = {}
    current_profession = None
    current_lines = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                if current_profession and current_lines:
                    descriptions[current_profession] = current_lines
                current_profession = line[1:].strip()
                current_lines = []
            elif line == "":
                continue
            else:
                current_lines.append(line)

        if current_profession and current_lines:
            descriptions[current_profession] = current_lines

    return descriptions


QUIZ_QUESTIONS = [
    {
        "question": "1. Кто создает программное обеспечение для лечебного и диагностического оборудования?",
        "options": ["IT-медик", "Биоэтик"],
        "correct": "IT-медик"
    },
    {
        "question": "2. Кто является специалистом в области инженерной и компьютерной графики?",
        "options": [
            "Специалист по модернизации строительных технологий",
            "Архитектор медоборудования"
        ],
        "correct": "Архитектор медоборудования"
    },
    {
        "question": "3. Специалист, занимающийся проектированием, установкой и настройкой интеллектуальной системы управления домашним хозяйством — это...",
        "options": [
            "Прораб-вотчер",
            "Проектировщик инфраструктуры 'умного дома'",
            "Хоз - IT специалист"
        ],
        "correct": "Проектировщик инфраструктуры 'умного дома'"
    },
    {
        "question": "4. Проектировщик личной безопасности – это специалист, оценивающий жизнь человека с точки зрения всех возможных рисков и...",
        "options": [
            "передает данные о вашем местоположении третьим лицам",
            "не подпускает к вам на порог незванных гостей",
            "их предотвращения"
        ],
        "correct": "их предотвращения"
    },
    {
        "question": "5. Специалист, оценивающий состояние безопасности на уже имеющемся объекте — это...",
        "options": [
            "Аудитор комплексной безопасности в промышленности",
            "Специалист по преодолению системных экологических катастроф",
            "Дистанционный координатор безопасности"
        ],
        "correct": "Аудитор комплексной безопасности в промышленности"
    },
    {
        "question": "6. Этот специалист занимается проектированием и моделированием дешевых летательных аппаратов малой авиации:",
        "options": [
            "Аналитик эксплуатационных данных",
            "Инженер производства малой авиации",
            "Глобальный инженер военных БПЛА"
        ],
        "correct": "Инженер производства малой авиации"
    },
    {
        "question": "7. Специалист, работающий над полным жизненным циклом объекта — это...",
        "options": [
            "Специалист по модернизации строительных технологий",
            "Прораб-вотчер",
            "BIM-менеджер-проектировщик"
        ],
        "correct": "BIM-менеджер-проектировщик"
    },
    {
        "question": "8. Какая отрасль является одним из лидеров по числу рабочих мест в стране?",
        "options": [
            "Медицина",
            "Строительство",
            "Безопасность",
            "Авиация"
        ],
        "correct": "Строительство"
    }
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Хорошо, я готов", callback_data="start")],
        [InlineKeyboardButton("Пройти викторину", callback_data="quiz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_photo(open("img/1.png", "rb"))
        await update.message.reply_text(
            "Добро пожаловать!🖐️ Перед вами бот, который поможет разобраться в популярных цифровых профессиях."
            "Вам откроется квиз в 'Начале', который вы сможете пройти после просмотра нескольких профессий",
            reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_photo(open("img/1.png", "rb"))
        await update.callback_query.message.reply_text(
            "Добро пожаловать!🖐️ Перед вами бот, который поможет разобраться в популярных цифровых профессиях."
            "Вам откроется квиз в 'Начале', который вы сможете пройти после просмотра нескольких профессий",
            reply_markup=reply_markup)


async def start_callback(message, context):
    keyboard = [
        [InlineKeyboardButton("Хорошо, я готов", callback_data="start")],
        [InlineKeyboardButton("Пройти викторину", callback_data="quiz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_photo(open("img/1.png", "rb"))
    await message.reply_text(
        "Добро пожаловать!🖐️ Перед вами бот, который поможет разобраться в популярных цифровых профессиях."
        "Вам откроется квиз в 'Начале', который вы сможете пройти после просмотра нескольких профессий",
        reply_markup=reply_markup)


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["quiz_step"] = 0
    context.user_data["score"] = 0
    await send_quiz_question(update.callback_query.message, context)


async def send_quiz_question(message, context):
    step = context.user_data.get("quiz_step", 0)
    if step < len(QUIZ_QUESTIONS):
        question_data = QUIZ_QUESTIONS[step]
        keyboard = [
            [InlineKeyboardButton(option, callback_data=f"q_{int(option == question_data['correct'])}")]
            for option in question_data["options"]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(question_data["question"], reply_markup=reply_markup)
    else:
        score = context.user_data.get("score", 0)
        await message.reply_text(f"Вы прошли викторину! Ваш результат: {score} из {len(QUIZ_QUESTIONS)}")
        keyboard = [[InlineKeyboardButton("⬅️ Вернуться в начало", callback_data="to_main")]]
        await message.reply_text("Хотите пройти еще раз или вернуться назад?",
                                 reply_markup=InlineKeyboardMarkup(keyboard))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "start":
        await query.message.reply_photo(open("img/2.png", "rb"))
        keyboard = [
            [InlineKeyboardButton(industry, callback_data=f"i_{industry}")]
            for industry in PROFESSIONS_DATA
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="to_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите интересующую вас отрасль:", reply_markup=reply_markup)
        return

    if data == "to_main":
        await start_callback(query.message, context)
        return

    if data == "quiz":
        await start_quiz(update, context)
        return

    if data.startswith("q_"):
        is_correct = bool(int(data[2:]))
        if is_correct:
            context.user_data["score"] = context.user_data.get("score", 0) + 1
            await query.message.reply_text("✅ Верно!")
        else:
            await query.message.reply_text("❌ Неверно.")
        context.user_data["quiz_step"] = context.user_data.get("quiz_step", 0) + 1
        await send_quiz_question(query.message, context)
        return

    if data.startswith("i_"):
        industry = data[2:]
        context.user_data["industry"] = industry
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"p_{pid}")]
            for pid, (name, _) in PROFESSIONS_DATA[industry].items()
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="start")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_photo(
            photo=open(IMG_MAP[industry], "rb"),
            caption="Выберите интересующую вас профессию:",
            reply_markup=reply_markup
        )
        return

    if data.startswith("p_"):
        pid = data[2:]
        if pid not in PROF_ID_TO_NAME:
            await query.message.reply_text("Ошибка: профессия не найдена.")
            return
        name, industry = PROF_ID_TO_NAME[pid]
        img_path = PROFESSIONS_DATA[industry][pid][1]
        await query.message.reply_photo(open(img_path, "rb"))
        await query.message.reply_text(f"Вы выбрали профессию: {name}")
        await asyncio.sleep(1)
        for part in DESCRIPTIONS.get(name, ["Описание временно недоступно."]):
            await query.message.reply_text(part)
            await asyncio.sleep(2)
        keyboard = [[InlineKeyboardButton("⬅️ Вернуться назад", callback_data=f"i_{industry}")]]
        await query.message.reply_text("Вы можете вернуться назад:", reply_markup=InlineKeyboardMarkup(keyboard))
        return


def main():
    global DESCRIPTIONS
    DESCRIPTIONS = load_descriptions("descriptions.txt")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
