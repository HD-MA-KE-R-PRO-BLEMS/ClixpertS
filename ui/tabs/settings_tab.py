"""
Clixpert S Pro Ultimate - Settings Tab
Вкладка настроек: горячие клавиши, поиск изображений, Telegram и т.д.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SettingsTab:
    """
    Вкладка настроек.
    Содержит:
    - Основные настройки (задержки, допуски)
    - Настройки горячих клавиш
    - Настройки поиска изображений
    - Настройки Telegram
    """

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg='#1a1a2e')
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов вкладки"""
        # Canvas с прокруткой
        canvas = tk.Canvas(self.frame, bg='#1a1a2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a2e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Основные настройки
        self._create_basic_settings(scrollable_frame)

        # Настройки горячих клавиш
        self._create_hotkey_settings(scrollable_frame)

        # Настройки поиска изображений
        self._create_image_settings(scrollable_frame)

        # Настройки Telegram
        self._create_telegram_settings(scrollable_frame)

        # Кнопка применения
        tk.Button(
            scrollable_frame, text="✅ Apply Settings", command=self._on_apply_settings,
            bg='#5a9cff', fg='white', bd=0, padx=30, pady=10,
            font=('Segoe UI', 11, 'bold')
        ).pack(pady=20)

    def _create_basic_settings(self, parent):
        """Создание основных настроек"""
        frame = tk.LabelFrame(
            parent, text="Basic Settings", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        frame.pack(fill=tk.X, pady=10, padx=10)

        # Global delay
        row = 0
        tk.Label(frame, text="Global delay (ms):", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W,
                                                                                  pady=5)
        self.global_delay_var = tk.IntVar(value=self.app.settings.get('global_delay_ms', 1000))
        tk.Entry(frame, textvariable=self.global_delay_var, width=10, bg='#2a2a3c', fg='white').grid(row=row, column=1,
                                                                                                     padx=10)
        row += 1

        # Color tolerance
        tk.Label(frame, text="Color tolerance (0-50):", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W,
                                                                                       pady=5)
        self.color_tolerance_var = tk.IntVar(value=self.app.settings.get('color_tolerance', 10))
        tk.Scale(
            frame, from_=0, to=50, variable=self.color_tolerance_var,
            orient=tk.HORIZONTAL, length=150, bg='#1e1e2f', fg='white', troughcolor='#2a2a3c'
        ).grid(row=row, column=1, padx=10)
        row += 1

        # Always on top
        self.always_on_top_var = tk.BooleanVar(value=self.app.settings.get('always_on_top', False))
        tk.Checkbutton(
            frame, text="Always on top", variable=self.always_on_top_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1

        # Use conditions
        self.use_conditions_var = tk.BooleanVar(value=self.app.settings.get('use_conditions', True))
        tk.Checkbutton(
            frame, text="Apply conditions (if set)", variable=self.use_conditions_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1

        # Humanize mouse
        self.humanize_mouse_var = tk.BooleanVar(value=self.app.settings.get('humanize_mouse', True))
        tk.Checkbutton(
            frame, text="Humanize mouse movement", variable=self.humanize_mouse_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1

    def _create_hotkey_settings(self, parent):
        """Создание настроек горячих клавиш"""
        frame = tk.LabelFrame(
            parent, text="Hotkeys", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        frame.pack(fill=tk.X, pady=10, padx=10)

        row = 0
        tk.Label(frame, text="Record click:", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.hotkey_click_var = tk.StringVar(value=self.app.settings.get('hotkey_record_click', 'f2'))
        tk.Entry(frame, textvariable=self.hotkey_click_var, width=10, bg='#2a2a3c', fg='white').grid(row=row, column=1,
                                                                                                     padx=10)
        row += 1

        tk.Label(frame, text="Record key:", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.hotkey_key_var = tk.StringVar(value=self.app.settings.get('hotkey_record_key', 'f3'))
        tk.Entry(frame, textvariable=self.hotkey_key_var, width=10, bg='#2a2a3c', fg='white').grid(row=row, column=1,
                                                                                                   padx=10)
        row += 1

        tk.Label(frame, text="Start/Stop:", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.hotkey_toggle_var = tk.StringVar(value=self.app.settings.get('hotkey_toggle', 'f1'))
        tk.Entry(frame, textvariable=self.hotkey_toggle_var, width=10, bg='#2a2a3c', fg='white').grid(row=row, column=1,
                                                                                                      padx=10)
        row += 1

        tk.Label(frame, text="Record start:", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.hotkey_record_start_var = tk.StringVar(value=self.app.settings.get('hotkey_record_start', 'f8'))
        tk.Entry(frame, textvariable=self.hotkey_record_start_var, width=10, bg='#2a2a3c', fg='white').grid(row=row,
                                                                                                            column=1,
                                                                                                            padx=10)
        row += 1

        tk.Label(frame, text="Record stop:", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.hotkey_record_stop_var = tk.StringVar(value=self.app.settings.get('hotkey_record_stop', 'f9'))
        tk.Entry(frame, textvariable=self.hotkey_record_stop_var, width=10, bg='#2a2a3c', fg='white').grid(row=row,
                                                                                                           column=1,
                                                                                                           padx=10)
        row += 1

    def _create_image_settings(self, parent):
        """Создание настроек поиска изображений"""
        frame = tk.LabelFrame(
            parent, text="Image Search Settings", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        frame.pack(fill=tk.X, pady=10, padx=10)

        row = 0
        tk.Label(frame, text="Image tolerance (0-100%):", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W,
                                                                                         pady=5)
        self.image_tolerance_var = tk.IntVar(value=self.app.settings.get('image_tolerance', 80))
        tk.Scale(
            frame, from_=0, to=100, variable=self.image_tolerance_var,
            orient=tk.HORIZONTAL, length=150, bg='#1e1e2f', fg='white', troughcolor='#2a2a3c'
        ).grid(row=row, column=1, padx=10)
        row += 1

        self.multi_scale_var = tk.BooleanVar(value=self.app.settings.get('multi_scale_search', False))
        tk.Checkbutton(
            frame, text="Multi-scale search (for transparent)", variable=self.multi_scale_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1

        tk.Label(frame, text="Rotation tolerance (degrees):", bg='#1e1e2f', fg='white').grid(row=row, column=0,
                                                                                             sticky=tk.W, pady=5)
        self.rotation_tolerance_var = tk.IntVar(value=self.app.settings.get('rotation_tolerance', 0))
        tk.Scale(
            frame, from_=0, to=180, variable=self.rotation_tolerance_var,
            orient=tk.HORIZONTAL, length=150, bg='#1e1e2f', fg='white', troughcolor='#2a2a3c'
        ).grid(row=row, column=1, padx=10)
        row += 1

        tk.Label(frame, text="Search method:", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.search_method_var = tk.StringVar(value=self.app.settings.get('search_method', 'template_matching'))
        method_combo = ttk.Combobox(
            frame, textvariable=self.search_method_var,
            values=['template_matching', 'feature_matching', 'canny_edge']
        )
        method_combo.grid(row=row, column=1, padx=10)
        row += 1

    def _create_telegram_settings(self, parent):
        """Создание настроек Telegram"""
        frame = tk.LabelFrame(
            parent, text="Telegram Bot", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        frame.pack(fill=tk.X, pady=10, padx=10)

        row = 0
        tk.Label(frame, text="Bot token:", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.telegram_token_var = tk.StringVar(value=self.app.settings.get('telegram_token', ''))
        tk.Entry(frame, textvariable=self.telegram_token_var, width=35, bg='#2a2a3c', fg='white').grid(row=row,
                                                                                                       column=1,
                                                                                                       padx=10)
        row += 1

        tk.Label(frame, text="Chat ID:", bg='#1e1e2f', fg='white').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.telegram_chat_id_var = tk.StringVar(value=self.app.settings.get('telegram_chat_id', ''))
        tk.Entry(frame, textvariable=self.telegram_chat_id_var, width=35, bg='#2a2a3c', fg='white').grid(row=row,
                                                                                                         column=1,
                                                                                                         padx=10)
        row += 1

        self.telegram_notify_var = tk.BooleanVar(value=self.app.settings.get('telegram_notify', False))
        tk.Checkbutton(
            frame, text="Notify on errors", variable=self.telegram_notify_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1

        tk.Button(
            frame, text="Send Test", command=self._on_test_telegram,
            bg='#3a3a5c', fg='white', bd=0, padx=15
        ).grid(row=row, column=0, columnspan=2, pady=10)

    def _on_apply_settings(self):
        """Применение настроек"""
        # Сохраняем настройки
        self.app.settings['global_delay_ms'] = self.global_delay_var.get()
        self.app.settings['color_tolerance'] = self.color_tolerance_var.get()
        self.app.settings['always_on_top'] = self.always_on_top_var.get()
        self.app.settings['use_conditions'] = self.use_conditions_var.get()
        self.app.settings['humanize_mouse'] = self.humanize_mouse_var.get()

        self.app.settings['hotkey_record_click'] = self.hotkey_click_var.get()
        self.app.settings['hotkey_record_key'] = self.hotkey_key_var.get()
        self.app.settings['hotkey_toggle'] = self.hotkey_toggle_var.get()
        self.app.settings['hotkey_record_start'] = self.hotkey_record_start_var.get()
        self.app.settings['hotkey_record_stop'] = self.hotkey_record_stop_var.get()

        self.app.settings['image_tolerance'] = self.image_tolerance_var.get()
        self.app.settings['multi_scale_search'] = self.multi_scale_var.get()
        self.app.settings['rotation_tolerance'] = self.rotation_tolerance_var.get()
        self.app.settings['search_method'] = self.search_method_var.get()

        self.app.settings['telegram_token'] = self.telegram_token_var.get()
        self.app.settings['telegram_chat_id'] = self.telegram_chat_id_var.get()
        self.app.settings['telegram_notify'] = self.telegram_notify_var.get()

        # Применяем
        self.app.save_settings()
        self.app.update_always_on_top()
        self.app.hotkey_manager.register_all()

        # Настройка Telegram
        if self.telegram_token_var.get() and self.telegram_chat_id_var.get():
            self.app.telegram.set_config(
                self.telegram_token_var.get(),
                self.telegram_chat_id_var.get()
            )

        self.app.update_status("✅ Settings applied")

    def _on_test_telegram(self):
        """Тестирование Telegram бота"""
        token = self.telegram_token_var.get().strip()
        chat_id = self.telegram_chat_id_var.get().strip()

        if not token or not chat_id:
            messagebox.showerror("Error", "Please enter Bot Token and Chat ID")
            return

        self.app.telegram.set_config(token, chat_id)
        if self.app.telegram.send_message("🧪 Test message from Clixpert S Pro Ultimate"):
            messagebox.showinfo("Success", "Message sent successfully!")
            self.app.update_status("✅ Telegram test message sent")
        else:
            messagebox.showerror("Error", "Failed to send message. Check token and chat ID")

    def get_frame(self):
        """Получить фрейм вкладки"""
        return self.frame

    def refresh_texts(self):
        """Обновление текстов интерфейса"""
        # Обновляем заголовки фреймов
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Canvas):
                for frame in child.winfo_children():
                    if isinstance(frame, tk.Frame):
                        for label_frame in frame.winfo_children():
                            if isinstance(label_frame, tk.LabelFrame):
                                text = label_frame.cget("text")
                                if text == "Basic Settings":
                                    label_frame.config(text=self.app.get_text('basic_settings'))
                                elif text == "Hotkeys":
                                    label_frame.config(text=self.app.get_text('hotkeys'))
                                elif text == "Image Search Settings":
                                    label_frame.config(text=self.app.get_text('image_search_settings'))
                                elif text == "Telegram Bot":
                                    label_frame.config(text=self.app.get_text('telegram_bot'))

        # Обновляем метки внутри Basic Settings
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Canvas):
                for frame in child.winfo_children():
                    if isinstance(frame, tk.Frame):
                        for label_frame in frame.winfo_children():
                            if isinstance(label_frame, tk.LabelFrame) and label_frame.cget("text") == self.app.get_text(
                                    'basic_settings'):
                                for label in label_frame.winfo_children():
                                    if isinstance(label, tk.Label):
                                        text = label.cget("text")
                                        if text == "Global delay (ms):":
                                            label.config(text=self.app.get_text('global_delay'))
                                        elif text == "Color tolerance (0-50):":
                                            label.config(text=self.app.get_text('color_tolerance'))
                                        elif text == "Always on top":
                                            label.config(text=self.app.get_text('always_on_top'))
                                        elif text == "Apply conditions (if set)":
                                            label.config(text=self.app.get_text('use_conditions'))
                                        elif text == "Humanize mouse movement":
                                            label.config(text=self.app.get_text('humanize_mouse'))

        # Обновляем метки внутри Hotkeys
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Canvas):
                for frame in child.winfo_children():
                    if isinstance(frame, tk.Frame):
                        for label_frame in frame.winfo_children():
                            if isinstance(label_frame, tk.LabelFrame) and label_frame.cget("text") == self.app.get_text(
                                    'hotkeys'):
                                for label in label_frame.winfo_children():
                                    if isinstance(label, tk.Label):
                                        text = label.cget("text")
                                        if text == "Record click:":
                                            label.config(text=self.app.get_text('record_click'))
                                        elif text == "Record key:":
                                            label.config(text=self.app.get_text('record_key'))
                                        elif text == "Start/Stop:":
                                            label.config(text=self.app.get_text('toggle'))
                                        elif text == "Record start:":
                                            label.config(text=self.app.get_text('record_start'))
                                        elif text == "Record stop:":
                                            label.config(text=self.app.get_text('record_stop'))

        # Обновляем метки внутри Image Search Settings
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Canvas):
                for frame in child.winfo_children():
                    if isinstance(frame, tk.Frame):
                        for label_frame in frame.winfo_children():
                            if isinstance(label_frame, tk.LabelFrame) and label_frame.cget("text") == self.app.get_text(
                                    'image_search_settings'):
                                for label in label_frame.winfo_children():
                                    if isinstance(label, tk.Label):
                                        text = label.cget("text")
                                        if text == "Image tolerance (0-100%):":
                                            label.config(text=self.app.get_text('image_tolerance'))
                                        elif text == "Multi-scale search (for transparent)":
                                            label.config(text=self.app.get_text('multi_scale_search'))
                                        elif text == "Rotation tolerance (degrees):":
                                            label.config(text=self.app.get_text('rotation_tolerance'))
                                        elif text == "Search method:":
                                            label.config(text=self.app.get_text('search_method'))

        # Обновляем метки внутри Telegram Bot
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Canvas):
                for frame in child.winfo_children():
                    if isinstance(frame, tk.Frame):
                        for label_frame in frame.winfo_children():
                            if isinstance(label_frame, tk.LabelFrame) and label_frame.cget("text") == self.app.get_text(
                                    'telegram_bot'):
                                for label in label_frame.winfo_children():
                                    if isinstance(label, tk.Label):
                                        text = label.cget("text")
                                        if text == "Bot token:":
                                            label.config(text=self.app.get_text('bot_token'))
                                        elif text == "Chat ID:":
                                            label.config(text=self.app.get_text('chat_id'))
                                        elif text == "Notify on errors":
                                            label.config(text=self.app.get_text('notify_on_error'))

        # Обновляем кнопку применения
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Canvas):
                for frame in child.winfo_children():
                    if isinstance(frame, tk.Frame):
                        for btn in frame.winfo_children():
                            if isinstance(btn, tk.Button) and btn.cget("text") == "✅ Apply Settings":
                                btn.config(text="✅ " + self.app.get_text('apply_settings'))
                            elif isinstance(btn, tk.Button) and btn.cget("text") == "Send Test":
                                btn.config(text=self.app.get_text('send_test'))