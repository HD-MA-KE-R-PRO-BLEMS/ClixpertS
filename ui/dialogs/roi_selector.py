"""
Clixpert S Pro Ultimate - ROI Selector Dialog
Выбор области на экране (Region of Interest)
"""

import tkinter as tk


class ROISelector:
    """
    Выбор области на экране с помощью мыши.
    Позволяет выделить прямоугольную область.
    """

    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.window = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.rect = None
        self.result = None

    def select(self) -> tuple:
        """
        Запустить выбор области.

        Returns:
            Кортеж (x1, y1, x2, y2) или None
        """
        self.result = None
        self._create_overlay()
        return self.result

    def _create_overlay(self):
        """Создание полупрозрачного оверлея"""
        self.window = tk.Toplevel(self.parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-alpha', 0.3)
        self.window.configure(bg='black')
        self.window.attributes('-topmost', True)

        # Привязываем события мыши
        self.window.bind('<Button-1>', self._on_mouse_down)
        self.window.bind('<B1-Motion>', self._on_mouse_move)
        self.window.bind('<ButtonRelease-1>', self._on_mouse_up)
        self.window.bind('<Escape>', self._on_cancel)

        # Создаём canvas для рисования
        self.canvas = tk.Canvas(self.window, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _on_mouse_down(self, event):
        """Нажатие кнопки мыши - начало выделения"""
        self.start_x = event.x_root
        self.start_y = event.y_root

    def _on_mouse_move(self, event):
        """Движение мыши - рисование прямоугольника"""
        if self.start_x == 0 and self.start_y == 0:
            return

        # Удаляем старый прямоугольник
        if self.rect:
            self.canvas.delete(self.rect)

        # Рисуем новый
        self.end_x = event.x_root
        self.end_y = event.y_root
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.end_x, self.end_y,
            outline='red', width=3, fill=''
        )

    def _on_mouse_up(self, event):
        """Отпускание кнопки - завершение выделения"""
        self.end_x = event.x_root
        self.end_y = event.y_root

        # Определяем корректные координаты (min/max)
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)

        # Проверяем, что область не нулевая
        if x2 - x1 > 5 and y2 - y1 > 5:
            self.result = (x1, y1, x2, y2)
        else:
            self.result = None

        self._close()

    def _on_cancel(self, event=None):
        """Отмена выбора"""
        self.result = None
        self._close()

    def _close(self):
        """Закрытие оверлея"""
        if self.window:
            self.window.destroy()
            self.window = None
        if self.callback and self.result:
            self.callback(self.result)