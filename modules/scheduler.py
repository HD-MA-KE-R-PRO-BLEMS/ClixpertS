"""
Clixpert S Pro Ultimate - Task Scheduler Module
Планировщик задач для автоматического запуска скриптов по расписанию
"""

import sqlite3
import threading
import time
from datetime import datetime, time as dt_time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class TaskScheduler:
    """
    Планировщик задач для автоматического выполнения скриптов.
    Поддерживает:
    - Запуск по времени (HH:MM)
    - Выбор дней недели
    - Включение/отключение задач
    - Статистику выполнения
    """

    def __init__(self, app, db_path: Optional[str] = None):
        self.app = app
        self.running = True
        self.db_path = db_path or "clixpert_tasks.db"
        self._scheduler_thread: Optional[threading.Thread] = None
        self._init_db()

    def _init_db(self) -> None:
        """Инициализация базы данных задач"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Проверяем существующие колонки
        c.execute("PRAGMA table_info(tasks)")
        existing_columns = [col[1] for col in c.fetchall()]

        if not existing_columns:
            # Создаём новую таблицу
            c.execute('''
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    script TEXT NOT NULL,
                    task_time TEXT NOT NULL,
                    days TEXT,
                    enabled INTEGER DEFAULT 1,
                    last_run TEXT,
                    run_count INTEGER DEFAULT 0,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
        else:
            # Добавляем недостающие колонки
            if 'run_count' not in existing_columns:
                c.execute("ALTER TABLE tasks ADD COLUMN run_count INTEGER DEFAULT 0")
            if 'last_run' not in existing_columns:
                c.execute("ALTER TABLE tasks ADD COLUMN last_run TEXT")
            if 'enabled' not in existing_columns:
                c.execute("ALTER TABLE tasks ADD COLUMN enabled INTEGER DEFAULT 1")
            if 'created_at' not in existing_columns:
                c.execute("ALTER TABLE tasks ADD COLUMN created_at TEXT")
            if 'updated_at' not in existing_columns:
                c.execute("ALTER TABLE tasks ADD COLUMN updated_at TEXT")

        conn.commit()
        conn.close()

    def add_task(self, name: str, script: str, task_time: str, days: List[str]) -> int:
        """
        Добавить задачу.

        Args:
            name: Название задачи
            script: Текст скрипта
            task_time: Время выполнения (HH:MM)
            days: Список дней недели

        Returns:
            ID созданной задачи
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().isoformat()

        c.execute('''
            INSERT INTO tasks (name, script, task_time, days, enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, ?, ?)
        ''', (name, script, task_time, ','.join(days), now, now))

        task_id = c.lastrowid
        conn.commit()
        conn.close()

        return task_id

    def update_task(self, task_id: int, **kwargs) -> bool:
        """
        Обновить задачу.

        Args:
            task_id: ID задачи
            **kwargs: Поля для обновления

        Returns:
            True если обновление успешно
        """
        allowed_fields = ['name', 'script', 'task_time', 'days', 'enabled']
        updates = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                if field == 'days' and isinstance(value, list):
                    values.append(','.join(value))
                else:
                    values.append(value)

        if not updates:
            return False

        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(task_id)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
        conn.close()

        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Удалить задачу.

        Args:
            task_id: ID задачи

        Returns:
            True если удаление успешно
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return True

    def toggle_task(self, task_id: int, enabled: bool) -> bool:
        """
        Включить/отключить задачу.

        Args:
            task_id: ID задачи
            enabled: True - включить, False - отключить

        Returns:
            True если операция успешна
        """
        return self.update_task(task_id, enabled=1 if enabled else 0)

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить задачу по ID.

        Args:
            task_id: ID задачи

        Returns:
            Словарь с данными задачи или None
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT id, name, script, task_time, days, enabled, last_run, run_count, created_at, updated_at FROM tasks WHERE id = ?",
            (task_id,))
        row = c.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "script": row[2],
                "task_time": row[3],
                "days": row[4].split(',') if row[4] else [],
                "enabled": bool(row[5]),
                "last_run": row[6],
                "run_count": row[7],
                "created_at": row[8],
                "updated_at": row[9],
            }
        return None

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Получить все задачи.

        Returns:
            Список словарей с задачами
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, name, task_time, days, enabled, run_count, last_run FROM tasks ORDER BY task_time")
        rows = c.fetchall()
        conn.close()

        tasks = []
        for row in rows:
            tasks.append({
                "id": row[0],
                "name": row[1],
                "task_time": row[2],
                "days": row[3].split(',') if row[3] else [],
                "enabled": bool(row[4]),
                "run_count": row[5],
                "last_run": row[6],
            })
        return tasks

    def get_tasks_for_time(self, current_time: dt_time) -> List[Dict[str, Any]]:
        """
        Получить задачи для указанного времени.

        Args:
            current_time: Время для проверки

        Returns:
            Список задач, которые должны выполниться
        """
        tasks = self.get_all_tasks()
        result = []
        current_day = datetime.now().strftime("%a")

        for task in tasks:
            if not task["enabled"]:
                continue

            try:
                task_time = datetime.strptime(task["task_time"], "%H:%M").time()
            except ValueError:
                continue

            # Проверка времени (с учётом секунд: 0 или 30)
            if (task_time.hour == current_time.hour and
                    task_time.minute == current_time.minute and
                    current_time.second in [0, 30]):

                # Проверка дня недели
                days = task["days"]
                if not days or current_day in days:
                    result.append(task)

        return result

    def _run_task(self, task: Dict[str, Any]) -> None:
        """
        Выполнить задачу.

        Args:
            task: Данные задачи
        """
        if not self.app:
            return

        # Обновляем статистику
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("UPDATE tasks SET last_run = ?, run_count = run_count + 1 WHERE id = ?", (now, task["id"]))
        conn.commit()
        conn.close()

        # Запускаем скрипт в главном потоке
        if hasattr(self.app, 'run_script'):
            self.app.root.after(0, lambda: self.app.run_script(task["script"]))

        if self.app and hasattr(self.app, 'update_status'):
            self.app.update_status(f"⏰ Running scheduled task: {task['name']}")

    def _scheduler_loop(self) -> None:
        """Основной цикл планировщика"""
        last_minute = -1

        while self.running:
            try:
                now = datetime.now()
                current_time = now.time()

                # Проверяем каждую минуту
                if current_time.minute != last_minute:
                    last_minute = current_time.minute
                    tasks = self.get_tasks_for_time(current_time)

                    for task in tasks:
                        self._run_task(task)

            except Exception as e:
                print(f"Scheduler error: {e}")

            time.sleep(0.5)  # Проверяем каждые 0.5 секунды

    def start(self) -> None:
        """Запустить планировщик"""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return

        self.running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()

    def stop(self) -> None:
        """Остановить планировщик"""
        self.running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=2.0)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику планировщика.

        Returns:
            Словарь со статистикой
        """
        tasks = self.get_all_tasks()
        enabled_count = sum(1 for t in tasks if t["enabled"])
        total_runs = sum(t["run_count"] for t in tasks)

        return {
            "total_tasks": len(tasks),
            "enabled_tasks": enabled_count,
            "disabled_tasks": len(tasks) - enabled_count,
            "total_runs": total_runs,
        }

    def clear_completed(self) -> int:
        """
        Очистить завершённые задачи (с run_count > 0).

        Returns:
            Количество удалённых задач
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE run_count > 0")
        deleted = c.rowcount
        conn.commit()
        conn.close()
        return deleted


if __name__ == "__main__":
    # Тестирование модуля планировщика
    print("=" * 50)
    print("Testing TaskScheduler Module")
    print("=" * 50)


    # Создаём мок-приложение
    class MockApp:
        def __init__(self):
            self.root = type('obj', (object,), {'after': lambda self, t, f: f()})()

        def run_script(self, script):
            print(f"   Running script: {script[:50]}...")

        def update_status(self, msg):
            print(f"   Status: {msg}")


    app = MockApp()
    scheduler = TaskScheduler(app, ":memory:")  # Используем временную БД

    # Добавляем тестовую задачу
    task_id = scheduler.add_task(
        name="Test Task",
        script='print("Hello from scheduled task!")',
        task_time="12:00",
        days=["Mon", "Tue", "Wed"]
    )
    print(f"\n📋 Added task with ID: {task_id}")

    # Получаем все задачи
    tasks = scheduler.get_all_tasks()
    print(f"\n📊 All tasks: {len(tasks)}")
    for task in tasks:
        print(f"   {task['name']} - {task['task_time']} - {'enabled' if task['enabled'] else 'disabled'}")

    # Статистика
    stats = scheduler.get_statistics()
    print(f"\n📈 Statistics: {stats}")

    print("\n✅ Module ready!")