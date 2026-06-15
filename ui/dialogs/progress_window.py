"""
Clixpert S Pro Ultimate - Progress Window Dialog
Отдельное окно с прогресс-баром для отслеживания выполнения
"""

import tkinter as tk
from tkinter import ttk


class ProgressWindow:
    """
    Отдельное окно с прогресс-баром.
    Можно перемещать по экрану.
    """

    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        self.x = 0
        self.y = 0
        self.create_window()

    def create_window(self):
        """Создание окна прогресса"""
        if self.window is not None:
            return

        self.window = tk.Toplevel(self.app.root)
        self.window.title("Progress")
        self.window.geometry("300x120")
        self.window.overrideredirect(True)  # Без рамки
        self.window.attributes('-topmost', True)
        self.window.configure(bg='#1e1e2f')
        self.window.attributes('-alpha', 0.92)

        # Для перемещения окна
        self.window.bind('<Button-1>', self.start_move)
        self.window.bind('<B1-Motion>', self.on_move)

        # Основной фрейм
        frame = tk.Frame(self.window, bg='#1e1e2f', padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Метка прогресса
        self.label = tk.Label(
            frame,
            text="Progress: 0.00 / 0.00 (0%)",
            fg='white',
            bg='#1e1e2f',
            font=('Segoe UI', 10, 'bold')
        )
        self.label.pack(pady=(0, 5))

        # Прогресс-бар
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "TProgressbar",
            thickness=20,
            troughcolor='#2a2a3c',
            background='#5a9cff'
        )
        self.progress = ttk.Progressbar(
            frame,
            orient=tk.HORIZONTAL,
            length=280,
            mode='determinate'
        )
        self.progress.pack(pady=5)

        # Метка ETA
        self.eta_label = tk.Label(
            frame,
            text="Estimated time left: —",
            fg='#cccccc',
            bg='#1e1e2f',
            font=('Segoe UI', 9)
        )
        self.eta_label.pack(pady=(2, 0))

        # Кнопка скрытия
        btn_frame = tk.Frame(frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Button(
            btn_frame,
            text="Hide",
            command=self.hide,
            bg='#3a3a5c',
            fg='white',
            bd=0,
            padx=10
        ).pack(side=tk.RIGHT)

    def start_move(self, event):
        """Начало перемещения окна"""
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        """Перемещение окна"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")

    def update(self, current: float, total: float, percent: float, eta_text: str):
        """
        Обновление данных прогресса.

        Args:
            current: Текущее значение
            total: Максимальное значение
            percent: Процент выполнения
            eta_text: Текст ETA
        """
        if self.window is None or not self.window.winfo_exists():
            return

        lang = self.app.lang if hasattr(self.app, 'lang') else 'ru'
        from languages import get_text

        self.label.config(
            text=get_text('progress_label', lang).format(current, total, percent)
        )
        self.progress['value'] = percent
        self.eta_label.config(text=get_text('eta_label', lang).format(eta_text))

    def show(self):
        """Показать окно"""
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.deiconify()

    def hide(self):
        """Скрыть окно"""
        if self.window is not None:
            self.window.withdraw()

    def destroy(self):
        """Уничтожить окно"""
        if self.window is not None:
            self.window.destroy()
            self.window = None