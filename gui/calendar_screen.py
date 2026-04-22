import flet as ft
from core.task_manager import TaskManager
from datetime import date, timedelta


def build_calendar_screen(page: ft.Page, tm: TaskManager):
    page.clean()
    page.bgcolor = ft.Colors.GREY_100
    page.padding = 0

    content = ft.ListView(spacing=0, padding=0, expand=True)

    selected_date = date.today()
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    current_week_start = monday

    def refresh_calendar():
        while len(content.controls) > 2:
            content.controls.pop()

        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        week_dates = [current_week_start + timedelta(days=i) for i in range(7)]

        weekdays_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(day, size=13, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_600),
                    width=45,
                    alignment=ft.Alignment(0, 0),
                )
                for day in days
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )
        content.controls.append(ft.Container(content=weekdays_row, padding=ft.padding.symmetric(horizontal=20)))

        date_controls = []
        for d in week_dates:
            is_selected = d == selected_date
            is_today = d == today

            date_container = ft.Container(
                content=ft.Text(str(d.day), size=16, weight=ft.FontWeight.W_500),
                width=45,
                height=45,
                alignment=ft.Alignment(0, 0),
                border_radius=23,
                bgcolor=ft.Colors.BLUE if is_selected else (ft.Colors.BLUE_100 if is_today else ft.Colors.TRANSPARENT),
                border=ft.border.all(1, ft.Colors.GREY_300) if not is_selected and not is_today else None,
                on_click=lambda e, date=d: select_date(date),
            )
            date_controls.append(date_container)

        dates_row = ft.Row(
            controls=date_controls,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )
        content.controls.append(ft.Container(content=dates_row, padding=ft.padding.symmetric(horizontal=20)))

        content.controls.append(ft.Divider(height=1, color=ft.Colors.GREY_300))

        months = ["января", "февраля", "марта", "апреля", "мая", "июня",
                  "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        date_str = f"Задачи на {selected_date.day} {months[selected_date.month - 1]}"

        content.controls.append(ft.Container(
            content=ft.Text(date_str, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
            padding=ft.padding.only(left=20, top=20, bottom=10),
        ))

        tasks = tm.get_tasks_for_date(selected_date)

        if not tasks:
            content.controls.append(ft.Container(
                content=ft.Text("Нет задач на этот день", size=14, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                padding=ft.padding.all(40),
            ))
        else:
            for task in tasks:
                task_id, title, cat_id, task_date, start_time, end_time, priority, desc, status, cat_name, cat_color, repeat_type = task

                task_item = ft.Container(
                    content=ft.Row([
                        ft.Container(width=4, height=24, border_radius=2, bgcolor=cat_color),
                        ft.Column([
                            ft.Text(
                                title,
                                size=15,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.GREY_500 if status == 1 else ft.Colors.BLUE_GREY_800,
                            ),
                            ft.Text(f"{start_time[:5]} - {end_time[:5]}", size=13, color=ft.Colors.GREY_600),
                        ], expand=True),
                        ft.Text(cat_name, size=12, color=ft.Colors.GREY_600),
                    ], spacing=12),
                    padding=ft.padding.symmetric(horizontal=20, vertical=8),
                )
                content.controls.append(task_item)

        page.update()

    def select_date(new_date: date):
        nonlocal selected_date
        selected_date = new_date
        refresh_calendar()

    def previous_week(e):
        nonlocal current_week_start, selected_date
        current_week_start = current_week_start - timedelta(days=7)
        selected_date = current_week_start
        refresh_calendar()

    def next_week(e):
        nonlocal current_week_start, selected_date
        current_week_start = current_week_start + timedelta(days=7)
        selected_date = current_week_start
        refresh_calendar()

    header = ft.Container(
        content=ft.Text("Календарь", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
        padding=ft.padding.only(left=20, top=20, right=20, bottom=5),
    )
    content.controls.append(header)

    nav_row = ft.Row([
        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=previous_week),
        ft.Text("Неделя", size=14, weight=ft.FontWeight.W_500),
        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=next_week),
    ], alignment=ft.MainAxisAlignment.CENTER)
    content.controls.append(ft.Container(content=nav_row, padding=ft.padding.only(left=20, right=20, bottom=10)))

    page.add(content)
    refresh_calendar()