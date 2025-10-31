from models import NotificationSchedule


class ScheduleGenerator:
    def __init__(self):
        pass

    def generate_schedule(self, peak_hours, df):
        # Создание финального расписания на основе анализа
        schedule = NotificationSchedule.create_from_analysis(peak_hours, df)
        return schedule

    def save_schedule(self, schedule: NotificationSchedule, output_path: str):
        # Сохранение расписания в файл
        schedule.save_to_json(output_path)