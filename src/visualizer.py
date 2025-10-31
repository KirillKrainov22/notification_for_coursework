import matplotlib.pyplot as plt
# import pandas as pd
# import os


class Visualizer:
    def __init__(self):
        plt.style.use('default')
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']

    def create_simple_analysis_plot(self, hourly_activity, peak_hours, save_path=None):
        # Создание графика активности по дням недели

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Создаем сетку графиков
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()

        for i, day in enumerate(days):
            # Данные для текущего дня
            day_data = hourly_activity[hourly_activity['day_name'] == day].sort_values('hour')
            ax = axes[i]

            # Линия активности
            ax.plot(day_data['hour'], day_data['screen_time'],
                    marker='o', linewidth=3, markersize=8, color='blue',
                    label='Активность')

            # Отмечаем выбранное время для уведомлений
            notification_times = peak_hours[day.lower()]
            for hour in notification_times:
                hour_activity = day_data[day_data['hour'] == hour]['screen_time']
                if len(hour_activity) > 0:
                    # Красные точки - время уведомлений
                    if hour == notification_times[0]:
                        label_text = 'Время уведомлений'
                    else:
                        label_text = ""
                    ax.plot(hour, hour_activity.values[0], 'ro', markersize=12, label=label_text)

            ax.set_title(f'{day}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Час дня')
            ax.set_ylabel('Активность (минуты)')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(6, 23)
            ax.legend()

        # Скрываем последний пустой график
        axes[-1].set_visible(False)

        plt.tight_layout()
        plt.suptitle('Анализ активности и выбор времени уведомлений',
                     fontsize=16, fontweight='bold')
        plt.subplots_adjust(top=0.93)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"График сохранен: {save_path}")
        else:
            plt.show()