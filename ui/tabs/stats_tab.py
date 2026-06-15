"""
Clixpert S Pro Ultimate - Statistics Tab
Вкладка статистики и аналитики: производительность, тепловая карта кликов
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np


class StatsTab:
    """
    Вкладка статистики.
    Содержит:
    - Показатели производительности (среднее время, процент успеха)
    - Тепловая карта кликов
    - Кнопки управления статистикой
    """

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg='#1a1a2e')
        self.heatmap_image = None
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов вкладки"""
        # Показатели производительности
        perf_frame = tk.LabelFrame(
            self.frame, text="Performance", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        perf_frame.pack(fill=tk.X, pady=5, padx=10)

        self.avg_response_label = tk.Label(
            perf_frame, text="Avg response: 0 ms",
            bg='#1e1e2f', fg='#88ff88', font=('Segoe UI', 11)
        )
        self.avg_response_label.pack(anchor=tk.W, pady=2)

        self.success_rate_label = tk.Label(
            perf_frame, text="Success rate: 0%",
            bg='#1e1e2f', fg='#88ff88', font=('Segoe UI', 11)
        )
        self.success_rate_label.pack(anchor=tk.W, pady=2)

        self.total_actions_label = tk.Label(
            perf_frame, text="Total actions: 0",
            bg='#1e1e2f', fg='#88ff88', font=('Segoe UI', 11)
        )
        self.total_actions_label.pack(anchor=tk.W, pady=2)

        self.total_time_label = tk.Label(
            perf_frame, text="Total time: 0 sec",
            bg='#1e1e2f', fg='#88ff88', font=('Segoe UI', 11)
        )
        self.total_time_label.pack(anchor=tk.W, pady=2)

        # Тепловая карта
        heatmap_frame = tk.LabelFrame(
            self.frame, text="Click Heatmap", bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        heatmap_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)

        self.heatmap_canvas = tk.Canvas(
            heatmap_frame, width=600, height=400, bg='#2a2a3c'
        )
        self.heatmap_canvas.pack(fill=tk.BOTH, expand=True)

        # Кнопки управления
        btn_frame = tk.Frame(heatmap_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame, text="🔥 Show Heatmap", command=self._on_show_heatmap,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="🗑 Reset Stats", command=self._on_reset_stats,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=5)

        # Запускаем обновление статистики
        self._update_stats()

    def _update_stats(self):
        """Обновление статистики"""
        if hasattr(self.app, 'stats'):
            stats = self.app.stats.get_summary() if hasattr(self.app.stats, 'get_summary') else {}

            self.avg_response_label.config(
                text=f"Avg response: {stats.get('avg_response_ms', 0):.0f} ms"
            )
            self.success_rate_label.config(
                text=f"Success rate: {stats.get('success_rate', 0):.1f}%"
            )
            self.total_actions_label.config(
                text=f"Total actions: {stats.get('total_actions', 0)}"
            )
            self.total_time_label.config(
                text=f"Total time: {stats.get('total_time_sec', 0):.0f} sec"
            )

        # Обновляем каждую секунду
        self.frame.after(1000, self._update_stats)

    def _on_show_heatmap(self):
        """Показать тепловую карту кликов"""
        if not hasattr(self.app, 'stats') or not self.app.stats.click_positions:
            messagebox.showinfo("Info", "No click data available. Run some actions first.")
            return

        try:
            # Генерируем тепловую карту
            heatmap = self.app.stats.get_heatmap_image(800, 600)

            # Масштабируем для отображения
            h, w = heatmap.shape[:2]
            scale = min(580 / w, 380 / h)
            new_w, new_h = int(w * scale), int(h * scale)
            heatmap_resized = cv2.resize(heatmap, (new_w, new_h))

            # Конвертируем в PhotoImage
            heatmap_rgb = cv2.cvtColor(heatmap_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(heatmap_rgb)
            self.heatmap_image = ImageTk.PhotoImage(img)

            # Отображаем
            self.heatmap_canvas.delete("all")
            self.heatmap_canvas.create_image(
                new_w // 2, new_h // 2, image=self.heatmap_image
            )
            self.app.update_status("🔥 Heatmap generated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate heatmap: {e}")

    def _on_reset_stats(self):
        """Сброс статистики"""
        if messagebox.askyesno("Confirm", "Reset all statistics?"):
            if hasattr(self.app, 'stats'):
                self.app.stats.reset()
            self.heatmap_canvas.delete("all")
            self.app.update_status("📊 Statistics reset")

    def update_stats(self, stats_data):
        """Обновление статистики извне"""
        self.avg_response_label.config(text=f"Avg response: {stats_data.get('avg_response_ms', 0):.0f} ms")
        self.success_rate_label.config(text=f"Success rate: {stats_data.get('success_rate', 0):.1f}%")
        self.total_actions_label.config(text=f"Total actions: {stats_data.get('total_actions', 0)}")
        self.total_time_label.config(text=f"Total time: {stats_data.get('total_time_sec', 0):.0f} sec")

    def get_frame(self):
        """Получить фрейм вкладки"""
        return self.frame

    def refresh_texts(self):
        """Обновление текстов интерфейса"""
        # Обновляем заголовки фреймов
        for child in self.frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                text = child.cget("text")
                if text == "Performance":
                    child.config(text=self.app.get_text('performance'))
                elif text == "Click Heatmap":
                    child.config(text=self.app.get_text('heatmap'))

        # Обновляем метки внутри Performance
        for child in self.frame.winfo_children():
            if isinstance(child, tk.LabelFrame) and child.cget("text") == self.app.get_text('performance'):
                for label in child.winfo_children():
                    if isinstance(label, tk.Label):
                        current_text = label.cget("text")
                        if current_text.startswith("Avg response:"):
                            label.config(text=self.app.get_text('avg_response') + " 0 ms")
                        elif current_text.startswith("Success rate:"):
                            label.config(text=self.app.get_text('success_rate') + " 0%")
                        elif current_text.startswith("Total actions:"):
                            label.config(text=self.app.get_text('total_actions') + " 0")
                        elif current_text.startswith("Total time:"):
                            label.config(text=self.app.get_text('total_time') + " 0 sec")

        # Обновляем кнопки
        for child in self.frame.winfo_children():
            if isinstance(child, tk.LabelFrame):
                for frame in child.winfo_children():
                    if isinstance(frame, tk.Frame):
                        for btn in frame.winfo_children():
                            if isinstance(btn, tk.Button):
                                text = btn.cget("text")
                                if text == "🔥 Show Heatmap":
                                    btn.config(text="🔥 " + self.app.get_text('show_heatmap'))
                                elif text == "🗑 Reset Stats":
                                    btn.config(text="🗑 " + self.app.get_text('reset_stats'))