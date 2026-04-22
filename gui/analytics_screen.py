import flet as ft
from core.task_manager import TaskManager
from datetime import date, timedelta


def build_analytics_screen(page: ft.Page, tm: TaskManager):
    page.clean()
    page.bgcolor = ft.Colors.GREY_100
    page.padding = 0

    content = ft.ListView(spacing=0, padding=0, expand=True)

    header = ft.Container(
        content=ft.Text("Аналитика", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
        padding=ft.padding.only(left=20, top=20, right=20, bottom=10),
    )
    content.controls.append(header)

    stats = tm.get_statistics()
    weekly_stats = tm.get_weekly_stats()

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    max_completed = 0
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = day.isoformat()
        completed = weekly_stats.get(day_str, {}).get("completed", 0)
        if completed > max_completed:
            max_completed = completed

    chart_bars = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = day.isoformat()
        completed = weekly_stats.get(day_str, {}).get("completed", 0)

        height = 40
        if max_completed > 0:
            height = 40 + int((completed / max_completed) * 160) if completed > 0 else 40

        color = ft.Colors.BLUE if day == today else ft.Colors.BLUE_300

        chart_bars.append(
            ft.Container(
                content=ft.Column([
                    ft.Container(width=30, height=height, bgcolor=color, border_radius=8),
                    ft.Text(days[i], size=12, color=ft.Colors.GREY_600),
                    ft.Text(str(completed), size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            )
        )

    chart_card = ft.Container(
        content=ft.Column([
            ft.Text("📊 Продуктивность за неделю", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
            ft.Container(height=10),
            ft.Row(chart_bars, alignment=ft.MainAxisAlignment.SPACE_AROUND),
        ]),
        padding=ft.padding.all(20),
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        margin=ft.margin.symmetric(horizontal=20, vertical=10),
        shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_300, offset=ft.Offset(0, 2)),
    )
    content.controls.append(chart_card)

    stats_card = ft.Container(
        content=ft.Column([
            ft.Text("Статистика", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Row([
                ft.Column([
                    ft.Text(str(stats["total"]), size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                    ft.Text("Всего задач", size=13, color=ft.Colors.GREY_600),
                ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([
                    ft.Text(str(stats["completed"]), size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                    ft.Text("Выполнено", size=13, color=ft.Colors.GREY_600),
                ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Column([
                    ft.Text(str(stats["overdue"]), size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                    ft.Text("Просрочено", size=13, color=ft.Colors.GREY_600),
                ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ]),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Text(f"Процент выполнения: {stats['completion_rate']}%", size=14, color=ft.Colors.GREY_600),
        ]),
        padding=ft.padding.all(20),
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        margin=ft.margin.symmetric(horizontal=20, vertical=10),
        shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_300, offset=ft.Offset(0, 2)),
    )
    content.controls.append(stats_card)

    by_category_card = ft.Container(
        content=ft.Column([
            ft.Text("По категориям", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ]),
        padding=ft.padding.all(20),
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        margin=ft.margin.symmetric(horizontal=20, vertical=10),
        shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_300, offset=ft.Offset(0, 2)),
    )

    for cat_name, count in stats["by_category"].items():
        categories = tm.get_categories()
        cat_color = "#0078D4"
        for cat in categories:
            if cat.name == cat_name:
                cat_color = cat.color
                break

        by_category_card.content.controls.append(
            ft.Row([
                ft.Container(width=12, height=12, border_radius=6, bgcolor=cat_color),
                ft.Text(cat_name, size=14, color=ft.Colors.BLUE_GREY_800),
                ft.Text(str(count), size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

    content.controls.append(by_category_card)

    page.add(content)
    page.update()