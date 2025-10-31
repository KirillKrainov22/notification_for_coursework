import pandas as pd


class DataProcessor:
    def __init__(self):
        self.df = None

    def load_data(self, file_path):
        # Загрузка данных из CSV файла
        try:
            self.df = pd.read_csv(file_path, delimiter=';')
            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False

    def preprocess_data(self):
        # Подготовка данных для анализа

        # Преобразуем экранное время в числа
        self.df['screen_time'] = self.df['screen_time'].str.replace(',', '.').astype(float)

        # Преобразуем даты в правильный формат
        self.df['date'] = pd.to_datetime(self.df['date'])

        # Извлекаем час из даты
        self.df['hour'] = self.df['date'].dt.hour

        # Помечаем выходные дни
        self.df['is_weekend'] = self.df['day_of_week'].isin([6, 7])

        return self.df

    def get_clean_data(self):
        # Возвращает обработанные данные
        return self.df