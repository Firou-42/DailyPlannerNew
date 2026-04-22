import flet as ft
from core.task_manager import TaskManager


def build_settings_screen(page: ft.Page, tm: TaskManager = None, rebuild_callback=None):
    page.clean()
    page.padding = 0

    content = ft.ListView(spacing=0, padding=0, expand=True)

    theme_switch = ft.Switch(label="Тёмная тема", value=page.theme_mode == ft.ThemeMode.DARK)

    first_day_dropdown = ft.Dropdown(
        label="Первый день недели",
        options=[
            ft.dropdown.Option("Понедельник"),
            ft.dropdown.Option("Воскресенье"),
        ],
        value="Понедельник",
        width=200,
    )

    notifications_switch = ft.Switch(label="Включить уведомления", value=True)

    reminder_slider_text = ft.Text("Напоминать за 15 минут до начала", size=12, color=ft.Colors.GREY_600)

    reminder_slider = ft.Slider(
        min=5,
        max=60,
        divisions=11,
        value=15,
        label="{value} мин",
    )

    def load_settings():
        if tm:
            theme = tm.get_setting("theme", "light")
            theme_switch.value = (theme == "dark")

            first_day = tm.get_setting("first_day", "monday")
            first_day_dropdown.value = "Понедельник" if first_day == "monday" else "Воскресенье"

            notifications = tm.get_setting("notifications", "on")
            notifications_switch.value = (notifications == "on")

            reminder = tm.get_setting("reminder_time", "15")
            reminder_slider.value = int(reminder)
            reminder_slider_text.value = f"Напоминать за {reminder} минут до начала"

    def save_settings(e):
        if tm:
            tm.set_setting("theme", "dark" if theme_switch.value else "light")
            tm.set_setting("first_day", "monday" if first_day_dropdown.value == "Понедельник" else "sunday")
            tm.set_setting("notifications", "on" if notifications_switch.value else "off")
            tm.set_setting("reminder_time", str(int(reminder_slider.value)))

            show_snack("Настройки сохранены")

            if rebuild_callback:
                rebuild_callback()

    def clear_all_data(e):
        def confirm_clear(e):
            if tm:
                all_tasks = tm.get_all_tasks()
                for task in all_tasks:
                    tm.delete_task(task[0])
            dialog.open = False
            page.update()
            show_snack("Все данные удалены")
            if rebuild_callback:
                rebuild_callback()

        def cancel_clear(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Подтверждение"),
            content=ft.Text("Удалить все задачи? Это действие нельзя отменить."),
            actions=[
                ft.TextButton("Отмена", on_click=cancel_clear),
                ft.TextButton("Удалить", on_click=confirm_clear, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def show_snack(message: str):
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    is_dark = page.theme_mode == ft.ThemeMode.DARK

    header = ft.Container(
        content=ft.Text("Настройки", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_300 if is_dark else ft.Colors.BLUE_GREY_800),
        padding=ft.padding.only(left=20, top=20, right=20, bottom=15),
    )
    content.controls.append(header)

    content.controls.append(ft.Container(
        content=ft.Text("Внешний вид", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_300 if is_dark else ft.Colors.BLUE_GREY_800),
        padding=ft.padding.only(left=20, right=20, bottom=5),
    ))
    content.controls.append(ft.Container(content=theme_switch, padding=ft.padding.only(left=20, right=20, bottom=15)))

    content.controls.append(ft.Divider(height=1, color=ft.Colors.GREY_700 if is_dark else ft.Colors.GREY_300))

    content.controls.append(ft.Container(
        content=ft.Text("Календарь", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_300 if is_dark else ft.Colors.BLUE_GREY_800),
        padding=ft.padding.only(left=20, top=15, bottom=5),
    ))
    content.controls.append(ft.Container(content=first_day_dropdown, padding=ft.padding.only(left=20, right=20, bottom=15)))

    content.controls.append(ft.Divider(height=1, color=ft.Colors.GREY_700 if is_dark else ft.Colors.GREY_300))

    content.controls.append(ft.Container(
        content=ft.Text("Уведомления", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_300 if is_dark else ft.Colors.BLUE_GREY_800),
        padding=ft.padding.only(left=20, top=15, bottom=5),
    ))
    content.controls.append(ft.Container(content=notifications_switch, padding=ft.padding.only(left=20, right=20)))
    content.controls.append(ft.Container(content=reminder_slider_text, padding=ft.padding.only(left=20, right=20, top=5)))
    content.controls.append(ft.Container(content=reminder_slider, padding=ft.padding.only(left=20, right=20, bottom=15)))

    content.controls.append(ft.Divider(height=1, color=ft.Colors.GREY_700 if is_dark else ft.Colors.GREY_300))

    content.controls.append(ft.Container(
        content=ft.ElevatedButton(
            "Сохранить настройки",
            icon=ft.Icons.SAVE,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
            on_click=save_settings,
        ),
        padding=ft.padding.only(left=20, right=20, top=20),
    ))

    content.controls.append(ft.Container(
        content=ft.ElevatedButton(
            "Очистить все данные",
            icon=ft.Icons.DELETE_FOREVER,
            style=ft.ButtonStyle(color=ft.Colors.RED),
            on_click=clear_all_data,
        ),
        padding=ft.padding.only(left=20, right=20, top=10),
    ))

    page.add(content)
    load_settings()
    page.update()