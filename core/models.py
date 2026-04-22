from dataclasses import dataclass
from datetime import date, time


@dataclass
class Category:
    id: int
    name: str
    color: str


@dataclass
class Task:
    id: int = None
    title: str = ""
    category_id: int = 1
    task_date: date = None
    start_time: time = None
    end_time: time = None
    priority: int = 2
    description: str = ""
    status: int = 0
    repeat_type: str = None