from pydantic import BaseModel, Field, validator
from typing import List, Dict
from datetime import datetime


class NotificationTime(BaseModel):
    # Хранит информацию о времени уведомлений для одного дня
    times: List[int] = Field(..., description="Список часов для уведомлений")
    count: int = Field(..., description="Количество уведомлений в день")

    @validator('times', each_item=True)
    def validate_hours(cls, hour_value):
        # Проверка что время уведомлений находится в допустимом диапазоне (6-23)
        if hour_value < 6 or hour_value > 23:
            raise ValueError(f'Время уведомлений должно быть между 6 и 23, получено {hour_value}')
        return hour_value

    @validator('count')
    def validate_count(cls, count_value):
        # Проверка что количество уведомлений не превышает лимит
        if count_value < 1 or count_value > 4:
            raise ValueError(f'Количество уведомлений должно быть от 1 до 4, получено {count_value}')
        return count_value


class GlobalSchedule(BaseModel):
    # Расписание уведомлений на всю неделю
    monday: NotificationTime
    tuesday: NotificationTime
    wednesday: NotificationTime
    thursday: NotificationTime
    friday: NotificationTime
    saturday: NotificationTime
    sunday: NotificationTime


class AnalysisMetadata(BaseModel):
    # Информация о проведенном анализе данных
    total_users_analyzed: int = Field(..., ge=0)
    data_period_days: int = Field(..., ge=1)
    total_activity_records: int = Field(..., ge=0)
    analysis_date: str


class NotificationSchedule(BaseModel):
    # Основная модель содержащая все расписание и метаданные
    global_schedule: GlobalSchedule
    analysis_metadata: AnalysisMetadata

    def save_to_json(self, file_path: str):
        # Сохранение готового расписания в JSON файл
        with open(file_path, 'w', encoding='utf-8') as file:
            json_data = self.model_dump_json(indent=2, ensure_ascii=False)
            file.write(json_data)

    @classmethod
    def create_from_analysis(cls, peak_hours: Dict, df):
        # Создание расписания на основе результатов анализа

        # Формируем расписание для каждого дня недели
        schedule_for_week = {}
        for day_name, hours_list in peak_hours.items():
            schedule_for_week[day_name] = NotificationTime(
                times=hours_list,
                count=len(hours_list)
            )

        # Собираем информацию об анализе
        analysis_info = AnalysisMetadata(
            total_users_analyzed=df['user_id'].nunique(),
            data_period_days=(df['date'].max() - df['date'].min()).days,
            total_activity_records=len(df),
            analysis_date=datetime.now().strftime("%Y-%m-%d")
        )

        return cls(
            global_schedule=GlobalSchedule(**schedule_for_week),
            analysis_metadata=analysis_info
        )