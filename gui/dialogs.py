import flet as ft
from core.task_manager import TaskManager
from core.models import Task
from datetime import date, time

_current_dialog = None


def show_add_task_dialog(page: ft.Page, tm: TaskManager, on_saved=None):
    global _current_dialog

    title_field = ft.TextField(label="Название задачи", width=300)

    categories = tm.get_categories()
    category_dropdown = ft.Dropdown(
        label="Категория",
        options=[ft.dropdown.Option(cat.name) for cat in categories],
        value=categories[0].name if categories else None,
        width=300,
    )

    date_field = ft.TextField(label="Дата", value=date.today().isoformat(), width=150)
    start_time_field = ft.TextField(label="Начало", value="10:00", width=100)
    end_time_field = ft.TextField(label="Конец", value="11:00", width=100)

    priority_dropdown = ft.Dropdown(
        label="Приоритет",
        options=[
            ft.dropdown.Option("Низкий"),
            ft.dropdown.Option("Средний"),
            ft.dropdown.Option("Высокий"),
        ],
        value="Средний",
        width=300,
    )

    repeat_dropdown = ft.Dropdown(
        label="Повторять",
        options=[
            ft.dropdown.Option("Нет"),
            ft.dropdown.Option("Ежедневно"),
            ft.dropdown.Option("Еженедельно"),
            ft.dropdown.Option("Ежемесячно"),
        ],
        value="Нет",
        width=300,
    )

    desc_field = ft.TextField(label="Описание", multiline=True, min_lines=2, width=300)

    def close_current_dialog():
        global _current_dialog
        if _current_dialog:
            _current_dialog.open = False
            _current_dialog = None
            page.update()

    def save_task(_):
        if not title_field.value:
            title_field.error_text = "Введите название"
            page.update()
            return

        cat_name = category_dropdown.value
        cat_id = 1
        for c in categories:
            if c.name == cat_name:
                cat_id = c.id
                break

        priority_map = {"Низкий": 1, "Средний": 2, "Высокий": 3}
        repeat_map = {"Нет": None, "Ежедневно": "daily", "Еженедельно": "weekly", "Ежемесячно": "monthly"}

        task_date_val = date.fromisoformat(date_field.value)

        start_str = start_time_field.value.strip()
        end_str = end_time_field.value.strip()

        if len(start_str.split(':')[0]) == 1:
            start_str = f"0{start_str}"
        if len(end_str.split(':')[0]) == 1:
            end_str = f"0{end_str}"

        if len(start_str) == 5:
            start_str = f"{start_str}:00"
        if len(end_str) == 5:
            end_str = f"{end_str}:00"

        start_val = time.fromisoformat(start_str)
        end_val = time.fromisoformat(end_str)

        def save_task_continue():
            task = Task(
                title=title_field.value,
                category_id=cat_id,
                task_date=task_date_val,
                start_time=start_val,
                end_time=end_val,
                priority=priority_map[priority_dropdown.value],
                description=desc_field.value,
                status=0,
                repeat_type=repeat_map[repeat_dropdown.value]
            )

            tm.add_task(task)

            if _current_dialog:
                _current_dialog.open = False
            page.update()

            if on_saved:
                on_saved(task.task_date)

        has_conflict, conflict_task = tm.check_time_conflict(task_date_val, start_val, end_val)

        if has_conflict:
            def confirm_save(_):
                confirm_dialog.open = False
                page.update()
                save_task_continue()

            def cancel_save(_):
                confirm_dialog.open = False
                page.update()

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Конфликт времени"),
                content=ft.Text(f"Задача пересекается с «{conflict_task}». Всё равно сохранить?"),
                actions=[
                    ft.TextButton("Отмена", on_click=cancel_save),
                    ft.TextButton("Сохранить", on_click=confirm_save, style=ft.ButtonStyle(color=ft.Colors.BLUE)),
                ],
            )
            page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            page.update()
            return

        save_task_continue()

    def cancel_dialog(_):
        close_current_dialog()

    _current_dialog = ft.AlertDialog(
        title=ft.Text("Новая задача"),
        content=ft.Column([
            title_field,
            category_dropdown,
            ft.Row([date_field, start_time_field, end_time_field], wrap=True),
            priority_dropdown,
            repeat_dropdown,
            desc_field,
        ], scroll=ft.ScrollMode.AUTO, height=450),
        actions=[
            ft.TextButton("Отмена", on_click=cancel_dialog),
            ft.TextButton("Сохранить", on_click=save_task),
        ],
    )

    page.overlay.append(_current_dialog)
    _current_dialog.open = True
    page.update()


def show_edit_task_dialog(page: ft.Page, tm: TaskManager, task_data: tuple, on_saved=None):
    global _current_dialog

    task_id = task_data[0]
    title = task_data[1]
    cat_id = task_data[2]
    task_date_str = task_data[3]
    start_time_str = task_data[4]
    end_time_str = task_data[5]
    priority = task_data[6]
    desc = task_data[7]
    status = task_data[8]
    cat_name = task_data[9]
    repeat_type = task_data[11] if len(task_data) > 11 else None

    title_field = ft.TextField(label="Название задачи", value=title, width=300)

    categories = tm.get_categories()
    category_dropdown = ft.Dropdown(
        label="Категория",
        options=[ft.dropdown.Option(c.name) for c in categories],
        value=cat_name,
        width=300,
    )

    date_field = ft.TextField(label="Дата", value=task_date_str, width=150)
    start_field = ft.TextField(label="Начало", value=start_time_str[:5], width=100)
    end_field = ft.TextField(label="Конец", value=end_time_str[:5], width=100)

    priority_map = {1: "Низкий", 2: "Средний", 3: "Высокий"}
    priority_dropdown = ft.Dropdown(
        label="Приоритет",
        options=[
            ft.dropdown.Option("Низкий"),
            ft.dropdown.Option("Средний"),
            ft.dropdown.Option("Высокий"),
        ],
        value=priority_map.get(priority, "Средний"),
        width=300,
    )

    repeat_map = {None: "Нет", "daily": "Ежедневно", "weekly": "Еженедельно", "monthly": "Ежемесячно"}
    repeat_dropdown = ft.Dropdown(
        label="Повторять",
        options=[
            ft.dropdown.Option("Нет"),
            ft.dropdown.Option("Ежедневно"),
            ft.dropdown.Option("Еженедельно"),
            ft.dropdown.Option("Ежемесячно"),
        ],
        value=repeat_map.get(repeat_type, "Нет"),
        width=300,
    )

    desc_field = ft.TextField(label="Описание", value=desc or "", multiline=True, min_lines=2, width=300)

    def show_snack(message: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED if is_error else ft.Colors.GREEN,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def split_task(_):
        try:
            start_str = start_field.value.strip()
            end_str = end_field.value.strip()

            if len(start_str.split(':')[0]) == 1:
                start_str = f"0{start_str}"
            if len(end_str.split(':')[0]) == 1:
                end_str = f"0{end_str}"

            if len(start_str) == 5:
                start_str = f"{start_str}:00"
            if len(end_str) == 5:
                end_str = f"{end_str}:00"

            start_val = time.fromisoformat(start_str)
            end_val = time.fromisoformat(end_str)

            duration = (end_val.hour * 60 + end_val.minute) - (start_val.hour * 60 + start_val.minute)

            if duration <= 120:
                show_snack("Задача короче 2 часов, разбивать не нужно")
                return

            parts = duration // 60
            if duration % 60 > 0:
                parts += 1

            part_duration = duration // parts

            current_start = start_val
            cat_name_val = category_dropdown.value
            cat_id_val = 1
            for c in categories:
                if c.name == cat_name_val:
                    cat_id_val = c.id
                    break

            priority_rev = {"Низкий": 1, "Средний": 2, "Высокий": 3}
            repeat_rev = {"Нет": None, "Ежедневно": "daily", "Еженедельно": "weekly", "Ежемесячно": "monthly"}

            for i in range(parts):
                current_end_hour = current_start.hour + (current_start.minute + part_duration) // 60
                current_end_minute = (current_start.minute + part_duration) % 60
                current_end = time(current_end_hour, current_end_minute)

                new_task = Task(
                    title=f"{title_field.value} (часть {i+1}/{parts})",
                    category_id=cat_id_val,
                    task_date=date.fromisoformat(date_field.value),
                    start_time=current_start,
                    end_time=current_end,
                    priority=priority_rev[priority_dropdown.value],
                    description=desc_field.value,
                    status=0,
                    repeat_type=repeat_rev[repeat_dropdown.value]
                )
                tm.add_task(new_task)
                current_start = current_end

            show_snack(f"Задача разбита на {parts} частей")

            if _current_dialog:
                _current_dialog.open = False
            page.update()

            if on_saved:
                on_saved(date.fromisoformat(date_field.value))
        except Exception as ex:
            show_snack(f"Ошибка при разбиении: {str(ex)}", is_error=True)

    def close_current_dialog():
        global _current_dialog
        if _current_dialog:
            _current_dialog.open = False
            _current_dialog = None
            page.update()

    def save_task(_):
        if not title_field.value:
            title_field.error_text = "Введите название"
            page.update()
            return

        cat_name_val = category_dropdown.value
        cat_id_val = 1
        for c in categories:
            if c.name == cat_name_val:
                cat_id_val = c.id
                break

        priority_rev = {"Низкий": 1, "Средний": 2, "Высокий": 3}
        repeat_rev = {"Нет": None, "Ежедневно": "daily", "Еженедельно": "weekly", "Ежемесячно": "monthly"}

        task_date_val = date.fromisoformat(date_field.value)

        start_str = start_field.value.strip()
        end_str = end_field.value.strip()

        if len(start_str.split(':')[0]) == 1:
            start_str = f"0{start_str}"
        if len(end_str.split(':')[0]) == 1:
            end_str = f"0{end_str}"

        if len(start_str) == 5:
            start_str = f"{start_str}:00"
        if len(end_str) == 5:
            end_str = f"{end_str}:00"

        start_val = time.fromisoformat(start_str)
        end_val = time.fromisoformat(end_str)

        def save_task_continue():
            task = Task(
                id=task_id,
                title=title_field.value,
                category_id=cat_id_val,
                task_date=task_date_val,
                start_time=start_val,
                end_time=end_val,
                priority=priority_rev[priority_dropdown.value],
                description=desc_field.value,
                status=status,
                repeat_type=repeat_rev[repeat_dropdown.value]
            )

            tm.update_task(task)

            if _current_dialog:
                _current_dialog.open = False
            page.update()

            if on_saved:
                on_saved(task.task_date)

        has_conflict, conflict_task = tm.check_time_conflict(task_date_val, start_val, end_val, exclude_task_id=task_id)

        if has_conflict:
            def confirm_save(_):
                confirm_dialog.open = False
                page.update()
                save_task_continue()

            def cancel_save(_):
                confirm_dialog.open = False
                page.update()

            confirm_dialog = ft.AlertDialog(
                title=ft.Text("Конфликт времени"),
                content=ft.Text(f"Задача пересекается с «{conflict_task}». Всё равно сохранить?"),
                actions=[
                    ft.TextButton("Отмена", on_click=cancel_save),
                    ft.TextButton("Сохранить", on_click=confirm_save, style=ft.ButtonStyle(color=ft.Colors.BLUE)),
                ],
            )
            page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            page.update()
            return

        save_task_continue()

    def cancel_dialog(_):
        close_current_dialog()

    _current_dialog = ft.AlertDialog(
        title=ft.Text("Редактирование задачи"),
        content=ft.Column([
            title_field,
            category_dropdown,
            ft.Row([date_field, start_field, end_field], wrap=True),
            priority_dropdown,
            repeat_dropdown,
            desc_field,
        ], scroll=ft.ScrollMode.AUTO, height=450),
        actions=[
            ft.TextButton("Отмена", on_click=cancel_dialog),
            ft.TextButton("Разбить", on_click=split_task),
            ft.TextButton("Сохранить", on_click=save_task),
        ],
    )

    page.overlay.append(_current_dialog)
    _current_dialog.open = True
    page.update()


def show_about_dialog(page: ft.Page):
    global _current_dialog

    def close_current_dialog():
        global _current_dialog
        if _current_dialog:
            _current_dialog.open = False
            _current_dialog = None
            page.update()

    _current_dialog = ft.AlertDialog(
        title=ft.Text("О программе"),
        content=ft.Column([
            ft.Text("Планировщик рабочего дня", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("Версия 1.0", size=14),
            ft.Divider(height=20),
            ft.Text("Приложение для индивидуального планирования рабочего дня фрилансера.", size=14),
            ft.Text("Разработчик: Синякин Д.Р., группа ИС-23", size=12, color=ft.Colors.GREY),
            ft.Text("ГПОУ «Мариинский политехнический техникум»", size=12, color=ft.Colors.GREY),
            ft.Text("2026", size=12, color=ft.Colors.GREY),
        ]),
        actions=[
            ft.TextButton("Закрыть", on_click=lambda _: close_current_dialog()),
        ],
    )

    page.overlay.append(_current_dialog)
    _current_dialog.open = True
    page.update()