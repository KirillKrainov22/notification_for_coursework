import os
from data_processor import DataProcessor
from activity_analyzer import ActivityAnalyzer
from schedule_generator import ScheduleGenerator
from visualizer import Visualizer


# Основной метод запуска всего анализа
class NotificationScheduler:

    def __init__(self):
        self.data_processor = DataProcessor()
        self.df = None

    def run_full_analysis(self):
        # Загрузка данных
        data_file = "../data/processed_screen_time_data.csv"
        if not self.data_processor.load_data(data_file):
            print("Ошибка загрузки данных")
            return

        self.df = self.data_processor.preprocess_data()
        print(f"Данные загружены: {len(self.df)} строк")

        # Анализ активности
        analyzer = ActivityAnalyzer(self.df)
        activity_data = analyzer.analyze_hourly_activity()
        best_times = analyzer.find_peak_hours_per_day(activity_data)

        # Расчет эффективности выбранного времени
        coverage = analyzer.calculate_coverage(activity_data, best_times)

        print(f"ЭФФЕКТИВНОСТЬ АЛГОРИТМА:")
        print(f"   Общее покрытие активности: {coverage['overall_coverage']:.1f}%")
        print(f"   Всего активности: {coverage['total_activity']:.0f} мин")
        print(f"   Покрыто уведомлениями: {coverage['covered_activity']:.0f} мин")

        print(f"Покрытие по дням:")
        for day, coverage_percent in coverage['daily_coverage'].items():
            print(f"   {day}: {coverage_percent:.1f}%")

        # Сравнение с другими алгоритмами
        comparison = analyzer.compare_with_other_algorithms(activity_data, best_times)

        print(f"СРАВНЕНИЕ АЛГОРИТМОВ:")
        print(f"   Наш алгоритм (с интервалами): {comparison['our_algorithm']['coverage']:.1f}%")
        print(f"   CV алгоритм (стабильность): {comparison['cv_algorithm']['coverage']:.1f}%")
        print(f"   Случайный алгоритм: {comparison['random_algorithm']:.1f}%")
        print(f"   Улучшение над CV: +{comparison['improvement_over_cv']:.1f}%")
        print(f"   Улучшение над случайным: +{comparison['improvement_over_random']:.1f}%")

        # Генерация расписания
        generator = ScheduleGenerator()
        final_schedule = generator.generate_schedule(best_times, self.df)

        # Сохранение результатов
        output_file = "../output/notification_schedule.json"
        os.makedirs("../output", exist_ok=True)
        generator.save_schedule(final_schedule, output_file)
        print(f"Расписание сохранено: {output_file}")

        # Создание графиков
        visualizer = Visualizer()
        os.makedirs("../reports", exist_ok=True)
        plot_file = "../reports/main_analysis.png"
        visualizer.create_simple_analysis_plot(activity_data, best_times, plot_file)

        print("Анализ завершен!")

        # Показываем итоговое расписание
        print("Итоговое расписание уведомлений:")
        for day, times in best_times.items():
            print(f"   {day}: {times} (количество: {len(times)})")