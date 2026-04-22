from datetime import date, time, datetime
from typing import List, Tuple, Optional
from core.database import Database
from core.models import Task, Category
from datetime import date, time, datetime, timedelta

class TaskManager:
    def __init__(self):
        self.db = Database()
        self.current_date = date.today()

    def get_categories(self) -> List[Category]:
        return self.db.get_categories()

    def get_tasks_for_date(self, target_date: date = None) -> List[tuple]:
        if target_date is None:
            target_date = self.current_date
        return self.db.get_tasks_by_date(target_date)

    def add_task(self, task: Task) -> int:
        return self.db.add_task(task)

    def update_task(self, task: Task):
        self.db.update_task(task)

    def toggle_task_status(self, task_id: int, current_status: int):
        new_status = 1 if current_status == 0 else 0
        self.db.update_task_status(task_id, new_status)

    def delete_task(self, task_id: int):
        self.db.delete_task(task_id)

    def check_time_conflict(self, task_date: date, start_time: time, end_time: time, exclude_task_id: int = None) -> Tuple[bool, Optional[str]]:
        tasks = self.db.get_tasks_by_date(task_date)
        for task in tasks:
            task_id = task[0]
            if exclude_task_id and task_id == exclude_task_id:
                continue

            task_start = time.fromisoformat(task[4])
            task_end = time.fromisoformat(task[5])

            if max(start_time, task_start) < min(end_time, task_end):
                return True, task[1]
        return False, None

    def get_all_tasks(self) -> List[tuple]:
        return self.db.get_all_tasks()

    def get_statistics(self) -> dict:
        tasks = self.db.get_all_tasks()
        total = len(tasks)
        completed = sum(1 for t in tasks if t[8] == 1)
        overdue = sum(1 for t in tasks if t[8] == 0 and datetime.fromisoformat(t[3]).date() < date.today())

        by_category = {}
        for t in tasks:
            cat_name = t[9]
            by_category[cat_name] = by_category.get(cat_name, 0) + 1

        return {
            "total": total,
            "completed": completed,
            "overdue": overdue,
            "completion_rate": round(completed / total * 100) if total > 0 else 0,
            "by_category": by_category
        }

    def get_setting(self, key: str, default: str = None) -> str:
        return self.db.get_setting(key, default)

    def set_setting(self, key: str, value: str):
        self.db.set_setting(key, value)

    def get_upcoming_tasks(self, minutes_before: int = 15) -> List[tuple]:
        now = datetime.now()
        current_time = now.time()
        current_date = now.date()

        upcoming = []
        tasks = self.db.get_tasks_by_date(current_date)

        for task in tasks:
            if task[8] == 1:
                continue

            task_start = time.fromisoformat(task[4])
            diff_minutes = (task_start.hour * 60 + task_start.minute) - (current_time.hour * 60 + current_time.minute)

            if 0 < diff_minutes <= minutes_before:
                upcoming.append((task, diff_minutes))

        return upcoming

    def generate_recurring_tasks(self):
        today = date.today()
        all_tasks = self.db.get_all_tasks()

        for task in all_tasks:
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

            if status == 1:
                continue

            if not repeat_type:
                continue

            task_date_obj = date.fromisoformat(task_date_str)

            if task_date_obj >= today:
                continue

            new_date = task_date_obj
            if repeat_type == "daily":
                new_date = today
            elif repeat_type == "weekly":
                days_diff = (today - task_date_obj).days
                if days_diff % 7 == 0:
                    new_date = today
                else:
                    continue
            elif repeat_type == "monthly":
                if today.day == task_date_obj.day:
                    new_date = today
                else:
                    continue

            if new_date != task_date_obj:
                existing = self.db.get_tasks_by_date(new_date)
                exists = any(t[1] == title and t[4] == start_time for t in existing)
                if not exists:
                    new_task = Task(
                        title=title,
                        category_id=cat_id,
                        task_date=new_date,
                        start_time=time.fromisoformat(start_time),
                        end_time=time.fromisoformat(end_time),
                        priority=priority,
                        description=desc,
                        status=0,
                        repeat_type=repeat_type
                    )
                    self.db.add_task(new_task)

    def get_weekly_stats(self) -> dict:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        stats = {}
        for i in range(7):
            day = week_start + timedelta(days=i)
            tasks = self.db.get_tasks_by_date(day)
            completed = sum(1 for t in tasks if t[8] == 1)
            total = len(tasks)
            stats[day.isoformat()] = {"completed": completed, "total": total}

        return stats