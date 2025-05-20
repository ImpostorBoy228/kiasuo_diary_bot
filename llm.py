import requests
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

WEEKDAYS_RU = {
    "Monday": "Понедельник", "Tuesday": "Вторник", "Wednesday": "Среда",
    "Thursday": "Четверг", "Friday": "Пятница", "Saturday": "Суббота", "Sunday": "Воскресенье"
}

def llm_transform(homeworks: list) -> str:
    try:
        # Группируем домашки по дате и предмету
        hw_by_date = {}
        for hw in homeworks:
            date_str = hw.get('lesson_date')
            subject = hw.get('subject') or "Предмет без названия"
            text = hw.get('task') or "Без задания"
            if not date_str:
                continue
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            hw_by_date.setdefault(date_obj, []).append((subject, text))

        lines = []
        for date in sorted(hw_by_date):
            day_ru = WEEKDAYS_RU[date.strftime('%A')]
            lines.append(f"*{day_ru} - {date.strftime('%d.%m')}*")
            for subj, text in hw_by_date[date]:
                task_text = text if text.strip() and text.lower() not in ['без задания', 'нет задания', 'нет дз'] else "❌ ДЗ нет"
                lines.append(f"• _{subj}_: {task_text}")
            lines.append("")

        # Очищаем текст от лишних пробелов и переносов
        lines = [line.strip() for line in lines if line.strip()]
        prompt = (
            "Ты — ассистент, превращающий школьные домашние задания в понятный и приятный отчёт.\n"
            "Вот список домашних заданий, разбитый по дням и предметам:\n\n"
            + "\n".join(lines) +
            "\nСоставь подробный и структурированный текст на русском языке в формате MarkdownV2. "
            "Используй *жирный текст* для заголовков дней и _курсив_ для названий предметов. "
            "Экранируй точки в датах и URL (например, 17.05 → 17\\.05, edsso.ru → edsso\\.ru)."
        )

        logger.info("🧾 RAW PROMPT TO LLM:\n%s", prompt)

        start_time = time.time()

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": "gemma:2b",
                "prompt": prompt,
                "stream": False,
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json().get("response", "🧠 Демон впал в ступор. Нет ответа.")

        # Дополнительная очистка результата
        result = re.sub(r'\s+', ' ', result).strip()  # Удаляем лишние пробелы
        result = re.sub(r'\n\n+', '\n', result)  # Удаляем лишние переносы строк

        logger.info("✅ LLM ответ получен за %.2f сек:\n%s", time.time() - start_time, result)
        return result

    except Exception as e:
        logger.error("🤯 Ошибка общения с LLM: %s", e, exc_info=True)
        return "⚠️ LLM демон захлебнулся в своих видениях."