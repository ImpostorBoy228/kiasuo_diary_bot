import requests
import logging
from datetime import datetime
from config import USER_ID
from auth import load_token
from llm import llm_transform

logger = logging.getLogger(__name__)

def fetch_homeworks():
    BEARER_TOKEN = load_token()
    if not BEARER_TOKEN:
        logger.warning("🔒 Токен отсутствует, мой Владыка...")
        return "❌ Токен утрачен в бездне..."

    url_schedule = 'https://diaryapi.kiasuo.ru/diary/api/schedule'

    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Accept': 'application/json'
    }

    today = datetime.now()
    week_number = today.isocalendar()[1]
    year = today.year
    params_schedule = {'id': USER_ID, 'week': str(week_number), 'year': str(year)}

    try:
        logger.info("📅 Запрашиваю расписание с домашками...")
        resp = requests.get(url_schedule, headers=headers, params=params_schedule, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        schedule = data.get('schedule', [])
        homeworks_data = data.get('homeworks', [])

        logger.info("🗓 Получено %s уроков и %s домашних заданий.", len(schedule), len(homeworks_data))

        # Мапим домашки по id для быстрого поиска
        homeworks_map = {hw['id']: hw for hw in homeworks_data}

        # Собираем финальный список домашних заданий с датами и предметами
        homeworks_list = []

        for lesson in schedule:
            lesson_date = lesson.get('lesson_date')
            subject = lesson.get('subject', 'Предмет')
            hw_ids = lesson.get('homework_to_check_ids', [])
            for hw_id in hw_ids:
                hw = homeworks_map.get(hw_id)
                if hw:
                    text = hw.get('text', 'Без задания').strip()
                    if text and text.lower() not in ('без задания', 'нет задания', 'нет дз', ''):
                        homeworks_list.append({
                            'lesson_date': lesson_date,
                            'subject': subject,
                            'task': text
                        })

        if not homeworks_list:
            return "❌ ДЗ не найдено, мой Владыка."

        # Форматируем текст
        report = llm_transform(homeworks_list)
        return report

    except Exception as e:
        logger.error("💣 Ошибка при запросе или обработке данных: %s", e, exc_info=True)
        return "⚠️ Демоны парсинга восстали! Ошибка."