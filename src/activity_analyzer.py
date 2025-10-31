import random


class ActivityAnalyzer:
    def __init__(self, df):
        self.df = df

    def analyze_hourly_activity(self):
        # Анализ активности пользователей по часам (только дневное время 6-23)
        filtered_data = self.df[self.df['hour'].between(6, 23)]

        # Группируем данные по дням недели и часам, суммируем экранное время
        activity_by_hour = filtered_data.groupby(['day_name', 'hour'])['screen_time'].sum().reset_index()
        return activity_by_hour

    def find_peak_hours_per_day(self, hourly_activity, num_peaks=3):
        # Поиск лучшего времени для уведомлений по дням недели
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        best_times = {}

        for day in days_of_week:
            # Берем данные для текущего дня
            day_data = hourly_activity[hourly_activity['day_name'] == day].copy()

            # Если данных нет - используем время по умолчанию
            if len(day_data) == 0:
                best_times[day.lower()] = [9, 14, 19]
                continue

            # Находим самые активные часы
            top_hours = day_data.nlargest(6, 'screen_time')
            selected_hours = []
            top_hours = top_hours.sort_values('screen_time', ascending=False)

            # Отбираем часы с интервалом не менее 3 часов
            for _, row in top_hours.iterrows():
                current_hour = row['hour']

                # Проверяем что текущий час не слишком близко к уже выбранным
                is_good_interval = True
                for chosen_hour in selected_hours:
                    time_difference = abs(current_hour - chosen_hour)
                    if time_difference < 3:
                        is_good_interval = False
                        break

                # Если интервал подходит - добавляем час в расписание
                if is_good_interval:
                    selected_hours.append(current_hour)

                    # Если набрали нужное количество часов - выходим из цикла
                    if len(selected_hours) >= num_peaks:
                        break

            # Если не набрали нужное количество - добавляем из оставшихся
            if len(selected_hours) < num_peaks:
                remaining = top_hours[~top_hours['hour'].isin(selected_hours)]
                for _, row in remaining.iterrows():
                    if len(selected_hours) < num_peaks:
                        selected_hours.append(row['hour'])

            # Если все еще не хватает - добавляем время по умолчанию
            while len(selected_hours) < num_peaks:
                default_times = [9, 14, 19]
                for default_hour in default_times:
                    if default_hour not in selected_hours and len(selected_hours) < num_peaks:
                        selected_hours.append(default_hour)
                        break

            best_times[day.lower()] = sorted(selected_hours[:num_peaks])

            # Выводим информацию о выборе времени для каждого дня
            print(f"{day}:")
            print(f"   Самые активные часы: {top_hours['hour'].tolist()}")
            print(f"   После фильтрации интервалов: {best_times[day.lower()]}")

        return best_times

    def calculate_coverage(self, hourly_activity, peak_hours):
        # Расчет процента активности который покрывают выбранные часы
        total_covered = 0
        coverage_by_day = {}

        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for day in days_of_week:
            day_data = hourly_activity[hourly_activity['day_name'] == day]
            total_day_activity = day_data['screen_time'].sum()

            # Считаем активность в выбранные часы
            chosen_hours = peak_hours[day.lower()]
            covered_activity = day_data[day_data['hour'].isin(chosen_hours)]['screen_time'].sum()

            # Расчет процента покрытия
            if total_day_activity > 0:
                day_coverage_percent = (covered_activity / total_day_activity) * 100
            else:
                day_coverage_percent = 0

            coverage_by_day[day] = day_coverage_percent
            total_covered += covered_activity

        # Общий процент покрытия по всем дням
        total_activity = hourly_activity['screen_time'].sum()
        if total_activity > 0:
            overall_coverage = (total_covered / total_activity) * 100
        else:
            overall_coverage = 0

        return {
            'overall_coverage': overall_coverage,
            'daily_coverage': coverage_by_day,
            'total_activity': total_activity,
            'covered_activity': total_covered
        }

    def compare_with_other_algorithms(self, hourly_activity, our_peak_hours):
        # Сравнение нашего алгоритма с CV алгоритмом и случайным выбором

        # Наш алгоритм
        our_coverage = self.calculate_coverage(hourly_activity, our_peak_hours)

        # CV алгоритм (стабильность)
        cv_peak_hours = self._cv_algorithm(hourly_activity)
        cv_coverage = self.calculate_coverage(hourly_activity, cv_peak_hours)

        # Случайный алгоритм
        random_coverage = self._random_algorithm(hourly_activity)

        return {
            'our_algorithm': {
                'coverage': our_coverage['overall_coverage'],
                'daily_coverage': our_coverage['daily_coverage']
            },
            'cv_algorithm': {
                'coverage': cv_coverage['overall_coverage'],
                'daily_coverage': cv_coverage['daily_coverage']
            },
            'random_algorithm': random_coverage,
            'improvement_over_cv': our_coverage['overall_coverage'] - cv_coverage['overall_coverage'],
            'improvement_over_random': our_coverage['overall_coverage'] - random_coverage
        }

    def _cv_algorithm(self, hourly_activity, num_peaks=3):
        # CV алгоритм - выбирает часы на основе стабильности активности
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        peak_hours = {}

        # Рассчитываем стабильность активности
        stability_scores = self._calculate_activity_stability(hourly_activity)

        for day in days_of_week:
            day_data = hourly_activity[hourly_activity['day_name'] == day].copy()

            if len(day_data) == 0:
                peak_hours[day.lower()] = [9, 14, 19]
                continue

            # Добавляем стабильность к данным
            day_data['stability'] = day_data['hour'].apply(
                lambda h: stability_scores.get((day, h), 0.5)
            )

            # Комбинированный балл: активность × стабильность
            day_data['score'] = day_data['screen_time'] * day_data['stability']

            # Берем топ часов по комбинированному баллу
            top_hours = day_data.nlargest(num_peaks * 2, 'score')

            # Фильтруем интервалы
            filtered_hours = []
            top_hours = top_hours.sort_values('score', ascending=False)

            # Отбираем часы с интервалом не менее 3 часов
            for _, row in top_hours.iterrows():
                hour = row['hour']

                # Проверяем что текущий час не слишком близко к уже выбранным
                is_good_interval = True
                for existing_hour in filtered_hours:
                    time_difference = abs(hour - existing_hour)
                    if time_difference < 3:
                        is_good_interval = False
                        break

                # Если интервал подходит - добавляем час в расписание
                if is_good_interval:
                    filtered_hours.append(hour)

                    # Если набрали нужное количество часов - выходим из цикла
                    if len(filtered_hours) >= num_peaks:
                        break

            peak_hours[day.lower()] = sorted(filtered_hours[:num_peaks])

            # Выводим отладочную информацию для CV алгоритма
            print(f"{day} (CV алгоритм):")
            print(f"   Лучшие по стабильности: {day_data.nlargest(3, 'stability')['hour'].tolist()}")
            print(f"   Лучшие по комбинированному баллу: {top_hours['hour'].tolist()}")
            print(f"   Итоговый выбор: {peak_hours[day.lower()]}")

        return peak_hours

    def _calculate_activity_stability(self, hourly_activity):
        # Расчет стабильности активности (коэффициент вариации)
        stability_scores = {}

        # Группируем по неделям для расчета стабильности
        self.df['week'] = self.df['date'].dt.isocalendar().week
        self.df['year'] = self.df['date'].dt.isocalendar().year

        for day in hourly_activity['day_name'].unique():
            for hour in range(6, 24):
                hour_data = self.df[
                    (self.df['day_name'] == day) &
                    (self.df['hour'] == hour)
                    ]

                if len(hour_data) > 0:
                    # Группируем по неделям чтобы увидеть стабильность
                    weekly_activity = hour_data.groupby(['year', 'week'])['screen_time'].sum()

                    if len(weekly_activity) > 1 and weekly_activity.mean() > 0:
                        # Коэффициент вариации = std / mean
                        cv = weekly_activity.std() / weekly_activity.mean()
                        # Преобразуем в стабильность (чем меньше CV -> тем больше стабильность)
                        stability = max(0, 1 - min(cv, 1.0))
                    else:
                        stability = 0.5  # средняя стабильность при недостатке данных
                else:
                    stability = 0.0  # нет данных

                stability_scores[(day, hour)] = stability

        return stability_scores

    def _random_algorithm(self, hourly_activity):
        # Случайный алгоритм - генерирует случайное расписание
        random_schedule = {}

        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            random_hours = random.sample(range(6, 24), 3)
            random_schedule[day] = random_hours

        coverage = self.calculate_coverage(hourly_activity, random_schedule)

        # Выводим random расписание
        print(f"RANDOM РАСПИСАНИЕ:")
        print(f"   Покрытие: {coverage['overall_coverage']:.1f}%")
        for day, hours in random_schedule.items():
            print(f"      {day}: {hours}")

        return coverage['overall_coverage']