import logging
import re
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
            # Escape periods in dates for MarkdownV2
            formatted_date = date.strftime('%d.%m').replace('.', r'\.')
            # Use escaped hyphen in header
            lines.append(f"*{day_ru} \- {formatted_date}*")
            for subj, text in hw_by_date[date]:
                task_text = text if text.strip() and text.lower() not in ['без задания', 'нет задания', 'нет дз'] else "❌ ДЗ нет"
                # Escape special characters in task_text
                task_text = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', task_text)
                # Escape periods in URLs and dates within task_text
                task_text = re.sub(r'(\d{1,2})\.(\d{1,2})', r'\1\.\2', task_text)
                task_text = re.sub(r'(\w+)\.(\w+)', r'\1\.\2', task_text)
                lines.append(f"• _{subj}_: {task_text}")
            lines.append("")  # Add blank line between days

        # Join lines and remove trailing blank line
        result = "\n".join(lines).rstrip()
        return result

    except Exception as e:
        logger.error("🤯 Ошибка форматирования текста: %s", e, exc_info=True)
        return "⚠️ Ошибка при обработке ДЗ\\. Проверь логи\\."