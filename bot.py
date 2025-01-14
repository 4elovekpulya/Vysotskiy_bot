from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# Замените "YOUR_BOT_TOKEN" на токен вашего бота
API_TOKEN = '7698586191:AAEs6BoAz9-KGAVvX85ysPVWZEVz6cydxFk'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния FSM
class QuizStates(StatesGroup):
    ANSWERING = State()

# Структура данных для вопросов и ответов
QUESTIONS = {
    1: {
        'text': "Что для вас самое важное в жизни?",
        'options': {
            'a': "Свобода и риск",
            'b': "Честь и верность",
            'c': "Бунт против несправедливости",
            'd': "Творчество и поиск себя"
        }
    },
    2: {
        'text': "Если бы вы оказались в сложной ситуации, как бы поступили?",
        'options': {
            'a': "Рискнули всем ради свободы",
            'b': "Сплотили вокруг себя людей",
            'c': "Столкнулись с врагом лицом к лицу",
            'd': "Нашли выход, используя смекалку"
        }
    },
    3: {
        'text': "Какое место больше всего напоминает вашу стихию?",
        'options': {
            'a': "Горы, полные риска и свободы",
            'b': "Поле боя, где решается судьба",
            'c': "Тюремная камера, где обостряется характер",
            'd': "Театр или съемочная площадка"
        }
    },
    4: {
        'text': "Как вы общаетесь с окружающими?",
        'options': {
            'a': "Прямо и честно, даже если это рискованно",
            'b': "Сильно и вдохновляюще, поднимая их дух",
            'c': "Немного отстраненно, но ваши действия говорят громче слов",
            'd': "Умеете подстраиваться под ситуацию, оставаясь собой"
        }
    },
    5: {
        'text': "Что могло бы стать вашим девизом?",
        'options': {
            'a': "«Лучше умереть стоя, чем жить на коленях!»",
            'b': "«Сила — в единстве!»",
            'c': "«Вы можете меня сломить, но не сломать!»",
            'd': "«Жизнь — это сцена, и я играю главную роль»"
        }
    }
}

RESULTS = {
    'a': "Вы — Георгий Клочков (фильм «Вертикаль»). Как альпинист Клочков, вы готовы рисковать всем ради свободы и высоты. Ваш дух приключений вдохновляет окружающих, даже если путь к цели полон опасностей. По промокоду GEROY мы дарим выгоду 10% на покупку билетов. Билеты: https://clck.ru/3Fhknq. Количество использований промокода ограничено.",
    'b': "Вы — Глеб Жеглов (фильм «Место встречи изменить нельзя»). Вы лидер и борец за справедливость, который знает, что «вор должен сидеть в тюрьме». У вас сильный характер, а ваш авторитет невозможно оспорить. По промокоду GEROY мы дарим выгоду 10% на покупку билетов. Билеты: https://clck.ru/3Fhknq. Количество использований промокода ограничено.",
    'c': "Вы — Дон Гуан (фильм «Маленькие трагедии»). Как бунтарь и философ, вы не боитесь бросить вызов обществу, но ваши действия всегда имеют глубокий смысл. Ваш внутренний мир — это тайна, которая манит других. По промокоду GEROY мы дарим выгоду 10% на покупку билетов. Билеты: https://clck.ru/3Fhknq. Количество использований промокода ограничено.",
    'd': "Вы — Хлопуша (спектакль «Пугачёв»). Вы творческий и свободолюбивый человек, который не терпит ограничений. Ваша сила в том, чтобы находить нестандартные решения и вдохновлять других своим примером. По промокоду GEROY мы дарим выгоду 10% на покупку билетов. Билеты: https://clck.ru/3Fhknq. Количество использований промокода ограничено."
}

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Начало теста"""
    await state.set_data({"question": 1, "answers": {}})
    await send_question(message, 1)
    await state.set_state(QuizStates.ANSWERING)

async def send_question(message: types.Message, question_num: int):
    """Отправка вопроса пользователю"""
    kb = []
    question = QUESTIONS[question_num]
    
    for key, value in question['options'].items():
        kb.append([types.InlineKeyboardButton(
            text=value,
            callback_data=f"{question_num}_{key}"
        )])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(
        f"Вопрос {question_num}/5:\n{question['text']}", 
        reply_markup=keyboard
    )

@dp.callback_query(QuizStates.ANSWERING)
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработка ответов пользователя"""
    question_num, answer = callback.data.split('_')
    question_num = int(question_num)
    
    data = await state.get_data()
    answers = data.get("answers", {})
    answers[question_num] = answer
    await state.update_data(answers=answers)
    
    if question_num < 5:
        await send_question(callback.message, question_num + 1)
    else:
        await show_result(callback.message, answers)
        await state.clear()
    
    await callback.answer()

def calculate_result(answers: dict) -> str:
    """Подсчет результатов теста"""
    answer_counts = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
    for answer in answers.values():
        answer_counts[answer] += 1
    
    max_answer = max(answer_counts.items(), key=lambda x: x[1])[0]
    return RESULTS[max_answer]

async def show_result(message: types.Message, answers: dict):
    """Показ результата теста"""
    result = calculate_result(answers)
    await message.answer(
        f"Ваш результат:\n\n{result}\n\nЧтобы пройти тест заново, нажмите /start"
    )

async def main():
    """Запуск бота"""
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())