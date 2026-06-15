"""
Clixpert S Pro Ultimate - Main Window
Главное окно приложения с вкладками
"""

import tkinter as tk
from tkinter import ttk
import threading

from ui.tabs.main_tab import MainTab
from ui.tabs.expert_tab import ExpertTab
from ui.tabs.conditions_tab import ConditionsTab
from ui.tabs.scheduler_tab import SchedulerTab
from ui.tabs.stats_tab import StatsTab
from ui.tabs.settings_tab import SettingsTab
from ui.dialogs.progress_window import ProgressWindow
from config import APP_NAME, VERSION, get_theme


class MainWindow:
    """
    Главное окно приложения.
    Управляет вкладками и связывает их с приложением.
    """

    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.notebook = None
        self.tabs = {}
        self.progress_window = None
        self.tray_icon = None
        self._pixel_dialog = None  # Ленивая инициализация

        self._create_ui()
        self._setup_tray()

    def _create_ui(self):
        """Создание интерфейса"""
        # Верхняя панель
        top_bar = tk.Frame(self.root, bg='#1a1a2e')
        top_bar.pack(fill=tk.X, pady=(0, 10), padx=10)

        # Заголовок
        tk.Label(
            top_bar, text=f"{APP_NAME} v{VERSION}",
            bg='#1a1a2e', fg='#5a9cff', font=('Segoe UI', 14, 'bold')
        ).pack(side=tk.LEFT)

        # Кнопка переключения языка
        self.lang_btn = tk.Button(
            top_bar, text="EN", command=self._toggle_language,
            bg='#3a3a5c', fg='white', bd=0, width=4
        )
        self.lang_btn.pack(side=tk.RIGHT, padx=5)

        # Создание вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Вкладка Main
        self.tabs['main'] = MainTab(self.notebook, self.app)
        self.notebook.add(self.tabs['main'].get_frame(), text="⚡ Main")

        # Вкладка Expert Mode
        self.tabs['expert'] = ExpertTab(self.notebook, self.app)
        self.notebook.add(self.tabs['expert'].get_frame(), text="🎯 Expert Mode")

        # Вкладка Conditions
        self.tabs['conditions'] = ConditionsTab(self.notebook, self.app)
        self.notebook.add(self.tabs['conditions'].get_frame(), text="🎨 Conditions")

        # Вкладка Scheduler
        self.tabs['scheduler'] = SchedulerTab(self.notebook, self.app)
        self.notebook.add(self.tabs['scheduler'].get_frame(), text="⏰ Scheduler")

        # Вкладка Stats
        self.tabs['stats'] = StatsTab(self.notebook, self.app)
        self.notebook.add(self.tabs['stats'].get_frame(), text="📊 Stats")

        # Вкладка Settings
        self.tabs['settings'] = SettingsTab(self.notebook, self.app)
        self.notebook.add(self.tabs['settings'].get_frame(), text="⚙ Settings")

        # Создаём окно прогресса (но не показываем)
        self.progress_window = ProgressWindow(self.app)
        self.progress_window.hide()

    def get_pixel_dialog(self):
        """Ленивое создание диалога пиксельных условий (только при необходимости)"""
        if self._pixel_dialog is None:
            from ui.dialogs.pixel_condition import PixelConditionDialog
            self._pixel_dialog = PixelConditionDialog(self.app)
            self._pixel_dialog.hide()  # Скрываем, не показываем при создании
        return self._pixel_dialog

    def _setup_tray(self):
        """Настройка иконки в трее"""
        try:
            from PIL import Image, ImageDraw
            import pystray

            image = Image.new('RGB', (64, 64), color='#1a1a2e')
            draw = ImageDraw.Draw(image)
            draw.rectangle((16, 16, 48, 48), fill='#5a9cff')
            draw.text((22, 22), "CS", fill='white')

            menu = pystray.Menu(
                pystray.MenuItem("Show", self._show_window),
                pystray.MenuItem("Start/Stop", self._toggle_cycle),
                pystray.MenuItem("Exit", self._quit_app)
            )

            self.tray_icon = pystray.Icon("clixpert", image, APP_NAME, menu)

            def run_tray():
                self.tray_icon.run()

            threading.Thread(target=run_tray, daemon=True).start()
        except ImportError:
            self.tray_icon = None

    def _toggle_language(self):
        """Переключение языка"""
        self.app.switch_language()
        self.lang_btn.config(text="RU" if self.app.lang == 'en' else "EN")
        self.refresh_texts()

    def _show_window(self):
        """Показать окно"""
        self.root.deiconify()
        self.root.lift()

    def _toggle_cycle(self):
        """Запуск/остановка цикла"""
        if self.app.running:
            self.app.stop_cycle()
        else:
            self.app.start_cycle()

    def _quit_app(self):
        """Выход из приложения"""
        self.app.quit_app()

    def refresh_texts(self):
        """Обновление текстов интерфейса"""
        self.root.title(self.app.get_text('title'))

        self.notebook.tab(0, text=self.app.get_text('tab_main'))
        self.notebook.tab(1, text=self.app.get_text('tab_expert'))
        self.notebook.tab(2, text=self.app.get_text('tab_conditions'))
        self.notebook.tab(3, text=self.app.get_text('tab_scheduler'))
        self.notebook.tab(4, text=self.app.get_text('tab_stats'))
        self.notebook.tab(5, text=self.app.get_text('tab_settings'))

        if 'main' in self.tabs:
            self.tabs['main'].refresh_texts()
        if 'expert' in self.tabs:
            self.tabs['expert'].refresh_texts()
        if 'conditions' in self.tabs:
            self.tabs['conditions'].refresh_texts()
        if 'scheduler' in self.tabs:
            self.tabs['scheduler'].refresh_texts()
        if 'stats' in self.tabs:
            self.tabs['stats'].refresh_texts()
        if 'settings' in self.tabs:
            self.tabs['settings'].refresh_texts()

    def update_actions_tree(self):
        if 'main' in self.tabs:
            self.tabs['main'].update_actions_tree()

    def update_progress(self, current, total, percent, eta_text):
        if 'main' in self.tabs:
            self.tabs['main'].update_progress(current, total, percent, eta_text)
        if self.progress_window and self.app.settings.get('show_progress_window', False):
            self.progress_window.update(current, total, percent, eta_text)

    def update_status(self, message):
        if 'main' in self.tabs:
            self.tabs['main'].update_status(message)

    def update_start_stop_button(self, is_running):
        if 'main' in self.tabs:
            self.tabs['main'].update_start_stop_button(is_running)

    def update_script_logs(self, log_entry):
        if 'expert' in self.tabs:
            self.tabs['expert'].update_logs(log_entry)

    def update_variables(self, variables):
        if 'expert' in self.tabs:
            self.tabs['expert'].update_variables(variables)

    def get_expert_script(self):
        if 'expert' in self.tabs:
            return self.tabs['expert'].get_script()
        return ""

    def set_expert_script(self, script):
        if 'expert' in self.tabs:
            self.tabs['expert'].set_script(script)

    def show_progress_window(self, show):
        if show:
            self.progress_window.show()
        else:
            self.progress_window.hide()

    def refresh_conditions(self):
        if 'conditions' in self.tabs:
            self.tabs['conditions'].refresh()

    def refresh_scheduler(self):
        if 'scheduler' in self.tabs:
            self.tabs['scheduler'].refresh()

    def update_stats(self, stats_data):
        if 'stats' in self.tabs:
            self.tabs['stats'].update_stats(stats_data)