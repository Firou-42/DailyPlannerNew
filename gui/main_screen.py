import flet as ft
from core.task_manager import TaskManager
from datetime import date, timedelta
from gui.dialogs import show_edit_task_dialog


def build_main_screen(page: ft.Page, tm: TaskManager, target_date: date = None, switch_callback=None):
    if target_date is None:
        target_date = date.today()

    page.clean()
    page.bgcolor = ft.Colors.GREY_100
    page.padding = 0

    search_field = ft.TextField(
        hint_text="Поиск задач...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=30,
        height=50,
        on_change=lambda e: apply_filters(),
    )

    header = ft.Container(
        content=ft.Column([
            ft.Text("Планировщик", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
            search_field,
        ]),
        padding=ft.padding.only(left=20, top=20, right=20, bottom=10),
    )
    page.add(header)

    categories = tm.get_categories()
    selected_category = None

    def filter_by_category(cat_name):
        nonlocal selected_category
        if selected_category == cat_name:
            selected_category = None
        else:
            selected_category = cat_name
        rebuild_category_chips()
        apply_filters()

    def rebuild_category_chips():
        category_chips.controls.clear()
        for cat in categories:
            is_selected = (selected_category == cat.name)
            category_chips.controls.append(
                ft.Chip(
                    label=ft.Text(cat.name, size=13),
                    leading=ft.Container(width=10, height=10, border_radius=5, bgcolor=cat.color),
                    bgcolor=ft.Colors.BLUE_100 if is_selected else ft.Colors.WHITE,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    on_click=lambda e, c=cat.name: filter_by_category(c),
                )
            )
        page.update()

    category_chips = ft.Row(scroll=ft.ScrollMode.AUTO)
    rebuild_category_chips()
    page.add(ft.Container(content=category_chips, padding=ft.padding.only(left=20, right=20, bottom=15)))

    months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]

    if target_date == date.today():
        date_str = f"Сегодня, {target_date.day} {months[target_date.month - 1]}"
    elif target_date == date.today() - timedelta(days=1):
        date_str = f"Вчера, {target_date.day} {months[target_date.month - 1]}"
    elif target_date == date.today() + timedelta(days=1):
        date_str = f"Завтра, {target_date.day} {months[target_date.month - 1]}"
    else:
        date_str = f"{target_date.day} {months[target_date.month - 1]}"

    date_row = ft.Row([
        ft.Text(date_str, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
        ft.Row([
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                icon_size=20,
                icon_color=ft.Colors.GREY_600,
                on_click=lambda e: change_date(-1)
            ),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                icon_size=20,
                icon_color=ft.Colors.GREY_600,
                on_click=lambda e: change_date(1)
            ),
        ]),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    page.add(ft.Container(content=date_row, padding=ft.padding.only(left=20, right=20, bottom=10)))

    def change_date(delta: int):
        new_date = target_date + timedelta(days=delta)
        build_main_screen(page, tm, new_date, switch_callback)

    all_tasks = tm.get_tasks_for_date(target_date)
    filtered_tasks = all_tasks.copy()

    def apply_filters():
        nonlocal filtered_tasks
        query = search_field.value if search_field else ""
        filtered_tasks = all_tasks.copy()

        if query:
            query = query.lower()
            filtered_tasks = [
                t for t in filtered_tasks
                if query in t[1].lower() or (t[7] and query in t[7].lower())
            ]

        if selected_category:
            filtered_tasks = [
                t for t in filtered_tasks
                if t[9] == selected_category
            ]

        rebuild_task_list()

    def rebuild_task_list():
        tasks_column.controls.clear()

        if not filtered_tasks:
            tasks_column.controls.append(
                ft.Container(
                    content=ft.Text("Нет задач", size=14, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    padding=ft.padding.all(40),
                )
            )
        else:
            for task in filtered_tasks:
                task_id = task[0]
                title = task[1]
                cat_id = task[2]
                task_date_str = task[3]
                start_time = task[4]
                end_time = task[5]
                priority = task[6]
                desc = task[7]
                status = task[8]
                cat_name = task[9]
                cat_color = task[10]
                repeat_type = task[11] if len(task) > 11 else None

                task_date_obj = date.fromisoformat(task_date_str)
                is_overdue = (task_date_obj < date.today() and status == 0)

                card = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(start_time[:5], size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                            width=55,
                        ),
                        ft.Container(width=4, height=40, border_radius=2, bgcolor=cat_color),
                        ft.Column([
                            ft.Text(
                                title,
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.GREY_500 if status == 1 else ft.Colors.BLUE_GREY_800,
                            ),
                            ft.Row([
                                ft.Text(cat_name, size=12, color=ft.Colors.GREY_600),
                                ft.Text(" 🔄", size=12, color=ft.Colors.BLUE) if repeat_type else ft.Text(""),
                            ]),
                        ], expand=True),
                        ft.Checkbox(
                            value=status == 1,
                            fill_color=ft.Colors.BLUE,
                            check_color=ft.Colors.WHITE,
                            on_change=lambda e, tid=task_id, st=status: toggle_task_status(tm, tid, st, page, target_date, switch_callback),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_size=20,
                            icon_color=ft.Colors.GREY_500,
                            on_click=lambda e, t=task: show_edit_task_dialog(page, tm, t, switch_callback),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=20,
                            icon_color=ft.Colors.GREY_500,
                            on_click=lambda e, tid=task_id, ttl=title: delete_task(tm, tid, ttl, page, target_date, switch_callback),
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(16),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=16,
                    border=ft.border.all(2, ft.Colors.RED) if is_overdue else None,
                    shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.GREY_300, offset=ft.Offset(0, 2)),
                )
                tasks_column.controls.append(card)

        page.update()

    tasks_column = ft.ListView(spacing=12, padding=ft.padding.symmetric(horizontal=20), expand=True)
    page.add(tasks_column)

    apply_filters()


def toggle_task_status(tm: TaskManager, task_id: int, current_status: int, page: ft.Page, target_date: date, switch_callback=None):
    tm.toggle_task_status(task_id, current_status)
    build_main_screen(page, tm, target_date, switch_callback)


def delete_task(tm: TaskManager, task_id: int, task_title: str, page: ft.Page, target_date: date, switch_callback=None):
    def confirm_delete(e):
        tm.delete_task(task_id)
        dialog.open = False
        page.update()
        build_main_screen(page, tm, target_date, switch_callback)

    def cancel_delete(e):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        title=ft.Text("Подтверждение"),
        content=ft.Text(f"Удалить задачу «{task_title}»?"),
        actions=[
            ft.TextButton("Отмена", on_click=cancel_delete),
            ft.TextButton("Удалить", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
        ],
    )
    page.overlay.append(dialog)
    dialog.open = True
    page.update()