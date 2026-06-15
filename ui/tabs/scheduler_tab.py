"""
Clixpert S Pro Ultimate - Scheduler Tab
Вкладка планировщика задач
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re


class SchedulerTab:
    """
    Вкладка планировщика задач.
    Позволяет добавлять, удалять и просматривать запланированные задачи.
    """

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg='#1a1a2e')
        self.task_days_vars = {}
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов вкладки"""
        # Список задач
        tasks_frame = tk.LabelFrame(
            self.frame, text="📋 Scheduled Tasks",
            bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        tasks_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)

        self.tasks_listbox = tk.Listbox(
            tasks_frame, height=8, bg='#2a2a3c', fg='white',
            font=('Segoe UI', 10), selectmode=tk.SINGLE
        )
        self.tasks_listbox.pack(fill=tk.BOTH, expand=True)
        self.tasks_listbox.bind('<Double-1>', self._edit_task)

        # Кнопки управления списком
        list_btn_frame = tk.Frame(tasks_frame, bg='#1e1e2f')
        list_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            list_btn_frame, text="🗑 Delete Task", command=self._delete_task,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            list_btn_frame, text="🔄 Refresh", command=self.refresh,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=5)

        # Добавление задачи
        add_frame = tk.LabelFrame(
            self.frame, text="➕ Schedule New Task",
            bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        add_frame.pack(fill=tk.X, pady=5, padx=10)

        # Имя задачи
        name_frame = tk.Frame(add_frame, bg='#1e1e2f')
        name_frame.pack(fill=tk.X, pady=2)
        tk.Label(name_frame, text="Task name:", bg='#1e1e2f', fg='white', width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.task_name_var = tk.StringVar()
        tk.Entry(name_frame, textvariable=self.task_name_var, width=25, bg='#2a2a3c', fg='white').pack(side=tk.LEFT,
                                                                                                       padx=5)

        # Время
        time_frame = tk.Frame(add_frame, bg='#1e1e2f')
        time_frame.pack(fill=tk.X, pady=2)
        tk.Label(time_frame, text="Time (HH:MM):", bg='#1e1e2f', fg='white', width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.task_time_var = tk.StringVar(value="12:00")
        tk.Entry(time_frame, textvariable=self.task_time_var, width=10, bg='#2a2a3c', fg='white').pack(side=tk.LEFT,
                                                                                                       padx=5)

        # Дни недели
        days_frame = tk.Frame(add_frame, bg='#1e1e2f')
        days_frame.pack(fill=tk.X, pady=2)
        tk.Label(days_frame, text="Days:", bg='#1e1e2f', fg='white', width=12, anchor=tk.W).pack(side=tk.LEFT)

        days_inner = tk.Frame(days_frame, bg='#1e1e2f')
        days_inner.pack(side=tk.LEFT, padx=5)

        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(day_names):
            var = tk.BooleanVar(value=True)
            self.task_days_vars[day] = var
            tk.Checkbutton(
                days_inner, text=day, variable=var,
                bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
            ).grid(row=i // 4, column=i % 4, padx=2)

        # Кнопка добавления
        tk.Button(
            add_frame, text="➕ Add Task", command=self._add_task,
            bg='#2a8c4a', fg='white', bd=0, padx=20, pady=5
        ).pack(pady=10)

        # Обновляем список
        self.refresh()

    def refresh(self):
        """Обновление списка задач"""
        self.tasks_listbox.delete(0, tk.END)

        if hasattr(self.app, 'scheduler'):
            for task in self.app.scheduler.get_all_tasks():
                status = "✅" if task['enabled'] else "⏸"
                days_str = ','.join(task['days']) if task['days'] else 'Every day'
                self.tasks_listbox.insert(
                    tk.END,
                    f"{status} {task['name']} - {task['task_time']} ({days_str}) [runs: {task['run_count']}]"
                )

    def _add_task(self):
        """Добавление задачи"""
        name = self.task_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter task name")
            return

        time_str = self.task_time_var.get().strip()
        if not re.match(r'^\d{2}:\d{2}$', time_str):
            messagebox.showerror("Error", "Invalid time format. Use HH:MM")
            return

        days = [day for day, var in self.task_days_vars.items() if var.get()]
        if not days:
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        script = self.app.main_window.get_expert_script() if self.app.main_window else ""

        if hasattr(self.app, 'scheduler'):
            task_id = self.app.scheduler.add_task(name, script, time_str, days)
            if task_id:
                self.refresh()
                self.app.update_status(f"✅ Task '{name}' scheduled at {time_str}")
                self.task_name_var.set("")
            else:
                messagebox.showerror("Error", "Failed to add task")

    def _delete_task(self):
        """Удаление задачи"""
        selected = self.tasks_listbox.curselection()
        if not selected:
            messagebox.showinfo("Info", "Select a task to delete")
            return

        task_str = self.tasks_listbox.get(selected[0])
        # Извлекаем имя задачи из строки
        import re
        match = re.search(r'[✅⏸]\s+(.+?)\s+-', task_str)
        if match:
            task_name = match.group(1)
            if messagebox.askyesno("Confirm", f"Delete task '{task_name}'?"):
                if hasattr(self.app, 'scheduler'):
                    # Находим ID задачи по имени
                    for task in self.app.scheduler.get_all_tasks():
                        if task['name'] == task_name:
                            self.app.scheduler.delete_task(task['id'])
                            break
                    self.refresh()
                    self.app.update_status(f"🗑 Task '{task_name}' deleted")

    def _edit_task(self, event=None):
        """Редактирование задачи (двойной клик)"""
        selected = self.tasks_listbox.curselection()
        if selected:
            messagebox.showinfo("Info", "Edit task feature coming soon!")

    def get_frame(self):
        """Получить фрейм вкладки"""
        return self.frame

    def refresh_texts(self):
        """Обновление текстов интерфейса"""
        # Обновляем заголовки фреймов
        for child in self.frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                text = child.cget("text")
                if text == "📋 Scheduled Tasks":
                    child.config(text="📋 " + self.app.get_text('scheduled_tasks'))
                elif text == "➕ Schedule New Task":
                    child.config(text="➕ " + self.app.get_text('schedule_task'))

        # Обновляем метки
        for child in self.frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                for frame in child.winfo_children():
                    if isinstance(frame, tk.Frame):
                        for label in frame.winfo_children():
                            if isinstance(label, tk.Label):
                                text = label.cget("text")
                                if text == "Task name:":
                                    label.config(text=self.app.get_text('task_name'))
                                elif text == "Time (HH:MM):":
                                    label.config(text=self.app.get_text('task_time'))
                                elif text == "Days:":
                                    label.config(text=self.app.get_text('task_days'))

        # Обновляем кнопки
        for child in self.frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                for frame in child.winfo_children():
                    if isinstance(frame, tk.Frame):
                        for btn in frame.winfo_children():
                            if isinstance(btn, tk.Button):
                                text = btn.cget("text")
                                if text == "🗑 Delete Task":
                                    btn.config(text="🗑 " + self.app.get_text('delete_task'))
                                elif text == "🔄 Refresh":
                                    btn.config(text="🔄 " + self.app.get_text('refresh'))
                                elif text == "➕ Add Task":
                                    btn.config(text="➕ " + self.app.get_text('add_task'))