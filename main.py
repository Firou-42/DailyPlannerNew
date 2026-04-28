import flet as ft
from gui.main_screen import build_main_screen
from gui.calendar_screen import build_calendar_screen
from gui.analytics_screen import build_analytics_screen
from gui.export_screen import build_export_screen
from gui.settings_screen import build_settings_screen
from gui.dialogs import show_add_task_dialog, show_about_dialog
from core.task_manager import TaskManager
from datetime import date
import threading
import time as t


def main(page: ft.Page):
    page.title = "Планировщик"
    page.padding = 0

    tm = TaskManager()
    current_date = date.today()
    current_tab_index = 0

    saved_theme = tm.get_setting("theme", "light")
    page.theme_mode = ft.ThemeMode.DARK if saved_theme == "dark" else ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_900 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_100

    tm.generate_recurring_tasks()

    def check_notifications():
        notified_tasks = set()

        while True:
            try:
                reminder_time = int(tm.get_setting("reminder_time", "15"))
                upcoming = tm.get_upcoming_tasks(reminder_time)

                for task, minutes_left in upcoming:
                    task_id = task[0]

                    if task_id in notified_tasks:
                        continue

                    title = task[1]
                    from plyer import notification
                    notification.notify(
                        title="Планировщик",
                        message=f"Задача «{title}» начнётся через {minutes_left} мин.",
                        app_name="DailyPlanner",
                        timeout=10
                    )
                    notified_tasks.add(task_id)

                current_time = t.localtime()

                if current_time.tm_hour == 20 and current_time.tm_min == 0:
                    stats = tm.get_statistics()
                    total = stats["total"]
                    completed = stats["completed"]

                    if total > 0 and completed / total < 0.5:
                        from plyer import notification
                        notification.notify(
                            title="Планировщик",
                            message=f"За эту неделю выполнено только {completed} из {total} задач. Не забывайте про дела!",
                            app_name="DailyPlanner",
                            timeout=10
                        )

                if current_time.tm_min == 0:
                    notified_tasks.clear()

                t.sleep(30)
            except Exception: # nosec B110
                pass

    notifications_enabled = tm.get_setting("notifications", "on") == "on"
    if notifications_enabled:
        thread = threading.Thread(target=check_notifications, daemon=True)
        thread.start()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Главная"),
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_TODAY, label="Календарь"),
            ft.NavigationBarDestination(icon=ft.Icons.ANALYTICS, label="Аналитика"),
            ft.NavigationBarDestination(icon=ft.Icons.DOWNLOAD, label="Экспорт"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Настройки"),
        ],
        selected_index=0,
    )
    page.navigation_bar = nav_bar

    page.appbar = ft.AppBar(
        title=ft.Text("Планировщик"),
        center_title=False,
        bgcolor=ft.Colors.BLUE_GREY,
        actions=[
            ft.IconButton(ft.Icons.INFO, on_click=lambda e: show_about_dialog(page)),
        ],
    )

    def apply_global_theme():
        page.theme_mode = ft.ThemeMode.DARK if tm.get_setting("theme", "light") == "dark" else ft.ThemeMode.LIGHT
        page.bgcolor = ft.Colors.GREY_900 if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.GREY_100

    def rebuild_current_tab():
        nonlocal current_tab_index
        page.clean()
        if current_tab_index == 0:
            build_main_screen(page, tm, current_date, switch_to_main)
        elif current_tab_index == 1:
            build_calendar_screen(page, tm)
        elif current_tab_index == 2:
            build_analytics_screen(page, tm)
        elif current_tab_index == 3:
            build_export_screen(page, tm)
        elif current_tab_index == 4:
            build_settings_screen(page, tm, rebuild_current_tab)
        page.update()

    def change_tab(e):
        nonlocal current_tab_index
        current_tab_index = e.control.selected_index
        rebuild_current_tab()

    def switch_to_main(new_date: date = None):
        nonlocal current_date, current_tab_index
        if new_date:
            current_date = new_date
        current_tab_index = 0
        nav_bar.selected_index = 0
        rebuild_current_tab()

    nav_bar.on_change = change_tab

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        on_click=lambda e: show_add_task_dialog(page, tm, switch_to_main),
        bgcolor=ft.Colors.BLUE,
    )

    rebuild_current_tab()


ft.run(main)