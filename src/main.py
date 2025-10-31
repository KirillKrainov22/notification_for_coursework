from notification_scheduler import NotificationScheduler

def main():
    # Запуск анализа для определения лучшего времени уведомлений
    scheduler = NotificationScheduler()
    scheduler.run_full_analysis()

if __name__ == "__main__":
    main()