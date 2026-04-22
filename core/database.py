import sqlite3
import os
from datetime import date, time, datetime
from typing import List, Optional
from core.models import Task, Category


class Database:
    def __init__(self, db_path: str = "data/planner.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._create_tables()
        self._init_categories()
        self._add_repeat_column()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    color TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    task_date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    priority INTEGER DEFAULT 2,
                    description TEXT DEFAULT '',
                    status INTEGER DEFAULT 0,
                    repeat_type TEXT DEFAULT NULL,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

    def _add_repeat_column(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'repeat_type' not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN repeat_type TEXT DEFAULT NULL")

    def _init_categories(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                categories = [
                    ("Работа", "#0078D4"),
                    ("Личное", "#107C10"),
                    ("Здоровье", "#D83B01"),
                ]
                cursor.executemany(
                    "INSERT INTO categories (name, color) VALUES (?, ?)",
                    categories
                )

    def get_categories(self) -> List[Category]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, color FROM categories ORDER BY id")
            rows = cursor.fetchall()
            return [Category(id=row[0], name=row[1], color=row[2]) for row in rows]

    def add_task(self, task: Task) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (title, category_id, task_date, start_time, end_time, priority, description, status, repeat_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.title,
                task.category_id,
                task.task_date.isoformat() if task.task_date else None,
                task.start_time.isoformat() if task.start_time else None,
                task.end_time.isoformat() if task.end_time else None,
                task.priority,
                task.description,
                task.status,
                task.repeat_type
            ))
            return cursor.lastrowid

    def get_tasks_by_date(self, target_date: date) -> List[tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.title, t.category_id, t.task_date, t.start_time, t.end_time,
                       t.priority, t.description, t.status, c.name, c.color, t.repeat_type
                FROM tasks t
                JOIN categories c ON t.category_id = c.id
                WHERE t.task_date = ?
                ORDER BY t.start_time
            """, (target_date.isoformat(),))
            return cursor.fetchall()

    def update_task_status(self, task_id: int, status: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))

    def delete_task(self, task_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def get_all_tasks(self) -> List[tuple]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.title, t.category_id, t.task_date, t.start_time, t.end_time,
                       t.priority, t.description, t.status, c.name, c.color, t.repeat_type
                FROM tasks t
                JOIN categories c ON t.category_id = c.id
                ORDER BY t.task_date DESC, t.start_time
            """)
            return cursor.fetchall()

    def update_task(self, task: Task):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks 
                SET title = ?, category_id = ?, task_date = ?, start_time = ?, end_time = ?,
                    priority = ?, description = ?, status = ?, repeat_type = ?
                WHERE id = ?
            """, (
                task.title,
                task.category_id,
                task.task_date.isoformat() if task.task_date else None,
                task.start_time.isoformat() if task.start_time else None,
                task.end_time.isoformat() if task.end_time else None,
                task.priority,
                task.description,
                task.status,
                task.repeat_type,
                task.id
            ))

    def get_setting(self, key: str, default: str = None) -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?
            """, (key, value, value))