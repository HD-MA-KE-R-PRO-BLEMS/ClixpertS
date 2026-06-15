"""
Clixpert S Pro Ultimate - Action Editor Dialog
Редактирование действий (клик, клавиша, задержка)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import keyboard


class ActionEditorDialog:
    """
    Диалог редактирования действия.
    Поддерживает редактирование кликов, клавиш и задержек.
    """

    def __init__(self, parent, action, callback, app=None):
        self.parent = parent
        self.action = action.copy() if action else {}
        self.callback = callback
        self.app = app
        self.dialog = None
        self.waiting_for_key = False
        self.temp_hook = None

        # Переменные для виджетов
        self.delay_var = None
        self.variation_var = None
        self.contrib_var = None
        self.click_vars = {}
        self.key_vars = {}
        self.cond_vars = {}
        self.loop_vars = {}

    def show(self):
        """Показать диалог"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Edit Action")
        self.dialog.geometry("550x650")
        self.dialog.configure(bg='#1e1e2f')
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        main_frame = tk.Frame(self.dialog, bg='#1e1e2f', padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Тип действия (только для просмотра)
        type_frame = tk.LabelFrame(
            main_frame, text="Action Type", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        type_frame.pack(fill=tk.X, pady=5)

        action_type = self.action.get('type', 'click')
        type_label = tk.Label(
            type_frame, text=action_type.upper(), bg='#1e1e2f', fg='#5a9cff',
            font=('Segoe UI', 12, 'bold')
        )
        type_label.pack()

        # Задержка
        delay_frame = tk.LabelFrame(
            main_frame, text="Delay (ms)", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        delay_frame.pack(fill=tk.X, pady=5)

        # Используем глобальную задержку из настроек, если действие новое
        default_delay = self.action.get('delay_ms')
        if default_delay is None and self.app:
            default_delay = self.app.settings.get('global_delay_ms', 1000)
        self.delay_var = tk.IntVar(value=default_delay or 1000)
        tk.Entry(delay_frame, textvariable=self.delay_var, width=10, bg='#2a2a3c', fg='white').pack()

        # Вариация задержки
        variation_frame = tk.LabelFrame(
            main_frame, text="Delay Variation (±ms)", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        variation_frame.pack(fill=tk.X, pady=5)

        self.variation_var = tk.IntVar(value=self.action.get('variation_ms', 0))
        tk.Entry(variation_frame, textvariable=self.variation_var, width=10, bg='#2a2a3c', fg='white').pack()

        # Параметры в зависимости от типа
        if action_type == 'click':
            self._create_click_ui(main_frame)
        elif action_type == 'key':
            self._create_key_ui(main_frame)
        elif action_type == 'delay':
            pass

        # Условие
        self._create_condition_ui(main_frame)

        # Вклад в прогресс
        contrib_frame = tk.LabelFrame(
            main_frame, text="Progress Contribution", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        contrib_frame.pack(fill=tk.X, pady=5)

        self.contrib_var = tk.StringVar(value=str(self.action.get('progress_contrib', '')))
        tk.Entry(contrib_frame, textvariable=self.contrib_var, width=10, bg='#2a2a3c', fg='white').pack()
        tk.Label(
            contrib_frame, text="Leave empty for default",
            bg='#1e1e2f', fg='#888888', font=('Segoe UI', 8)
        ).pack()

        # Кнопки
        btn_frame = tk.Frame(main_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(
            btn_frame, text="💾 Save", command=self._save,
            bg='#2a8c4a', fg='white', bd=0, padx=20, pady=5
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="❌ Cancel", command=self.dialog.destroy,
            bg='#8c2a2a', fg='white', bd=0, padx=20, pady=5
        ).pack(side=tk.LEFT, padx=5)

    def _create_click_ui(self, parent):
        """Создание UI для клика"""
        # Координаты
        coord_frame = tk.LabelFrame(
            parent, text="Coordinates", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        coord_frame.pack(fill=tk.X, pady=5)

        xy_frame = tk.Frame(coord_frame, bg='#1e1e2f')
        xy_frame.pack()

        tk.Label(xy_frame, text="X:", bg='#1e1e2f', fg='white').pack(side=tk.LEFT)
        x_var = tk.IntVar(value=self.action.get('x', 0))
        tk.Entry(xy_frame, textvariable=x_var, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        tk.Label(xy_frame, text="Y:", bg='#1e1e2f', fg='white').pack(side=tk.LEFT)
        y_var = tk.IntVar(value=self.action.get('y', 0))
        tk.Entry(xy_frame, textvariable=y_var, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        tk.Button(
            xy_frame, text="🎯 Get",
            command=lambda: (x_var.set(pyautogui.position()[0]), y_var.set(pyautogui.position()[1])),
            bg='#3a3a5c', fg='white', bd=0
        ).pack(side=tk.LEFT, padx=10)

        # Удержание
        hold_frame = tk.LabelFrame(
            parent, text="Hold Time (ms)", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        hold_frame.pack(fill=tk.X, pady=5)

        hold_var = tk.IntVar(value=self.action.get('hold_ms', 0))
        tk.Entry(hold_frame, textvariable=hold_var, width=10, bg='#2a2a3c', fg='white').pack()

        # Случайное смещение (используем глобальное значение по умолчанию)
        default_offset = self.action.get('random_offset')
        if default_offset == 0 and self.app and self.action.get('type') == 'click':
            default_offset = self.app.settings.get('random_click_offset', 5)
        offset_var = tk.IntVar(value=default_offset)
        offset_frame = tk.LabelFrame(
            parent, text="Random Offset (px)", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        offset_frame.pack(fill=tk.X, pady=5)
        tk.Entry(offset_frame, textvariable=offset_var, width=10, bg='#2a2a3c', fg='white').pack()

        # Humanize (используем глобальное значение по умолчанию)
        default_humanize = self.action.get('humanize')
        if self.app and self.action.get('type') == 'click':
            default_humanize = self.app.settings.get('humanize_mouse', False)
        humanize_var = tk.BooleanVar(value=default_humanize or False)
        tk.Checkbutton(
            parent, text="Humanize mouse movement", variable=humanize_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).pack(anchor=tk.W, pady=5)

        # Сохраняем переменные
        self.click_vars = {
            'x': x_var, 'y': y_var, 'hold_ms': hold_var,
            'random_offset': offset_var, 'humanize': humanize_var
        }

    def _create_key_ui(self, parent):
        """Создание UI для клавиши"""
        key_frame = tk.LabelFrame(
            parent, text="Key", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        key_frame.pack(fill=tk.X, pady=5)

        key_var = tk.StringVar(value=self.action.get('key', ''))
        key_entry = tk.Entry(key_frame, textvariable=key_var, width=15, bg='#2a2a3c', fg='white')
        key_entry.pack()

        tk.Button(
            key_frame, text="⌨ Record",
            command=lambda: self._record_key(key_var),
            bg='#3a3a5c', fg='white', bd=0
        ).pack(pady=5)

        # Удержание клавиши
        hold_var = tk.BooleanVar(value=self.action.get('key_hold', False))
        tk.Checkbutton(
            parent, text="Hold key", variable=hold_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).pack(anchor=tk.W, pady=5)

        hold_ms_frame = tk.Frame(parent, bg='#1e1e2f')
        hold_ms_frame.pack(fill=tk.X, pady=5)
        tk.Label(hold_ms_frame, text="Hold duration (ms):", bg='#1e1e2f', fg='white').pack(side=tk.LEFT)
        hold_ms_var = tk.IntVar(value=self.action.get('key_hold_ms', 100))
        tk.Entry(hold_ms_frame, textvariable=hold_ms_var, width=8, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        self.key_vars = {
            'key': key_var, 'key_hold': hold_var, 'key_hold_ms': hold_ms_var
        }

    def _record_key(self, key_var):
        """Запись клавиши"""
        self.waiting_for_key = True
        status_label = tk.Label(
            self.dialog, text="Press any key...", bg='#1e1e2f', fg='#88ff88'
        )
        status_label.pack(pady=5)

        def on_key(e):
            if self.waiting_for_key:
                self.waiting_for_key = False
                keyboard.unhook(self.temp_hook)
                key_var.set(e.name)
                status_label.config(text=f"Key '{e.name}' recorded", fg='#88ff88')
                self.dialog.after(2000, status_label.destroy)

        self.temp_hook = keyboard.on_press(on_key)
        self.dialog.after(10000, lambda: self._cancel_recording(status_label))

    def _cancel_recording(self, status_label):
        """Отмена записи клавиши"""
        if self.waiting_for_key:
            self.waiting_for_key = False
            keyboard.unhook(self.temp_hook)
            status_label.config(text="Recording cancelled", fg='#ff8888')
            self.dialog.after(2000, status_label.destroy)

    def _create_condition_ui(self, parent):
        """Создание UI для условия"""
        cond_frame = tk.LabelFrame(
            parent, text="Condition", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        cond_frame.pack(fill=tk.X, pady=5)

        cond_type_var = tk.StringVar(value='none')
        cond_types = ['none', 'pixel', 'image', 'sound']
        cond_combo = ttk.Combobox(
            cond_frame, textvariable=cond_type_var, values=cond_types, state='readonly'
        )
        cond_combo.pack(fill=tk.X)

        # Контейнер для ID условия
        cond_id_frame = tk.Frame(cond_frame, bg='#1e1e2f')
        cond_id_frame.pack(fill=tk.X, pady=5)

        # Загружаем существующее условие
        existing_cond = self.action.get('condition')
        if existing_cond:
            cond_type = existing_cond.get('type', 'pixel')
            if cond_type in cond_types:
                cond_type_var.set(cond_type)

        def update_cond_id(*args):
            for w in cond_id_frame.winfo_children():
                w.destroy()

            cond_type = cond_type_var.get()
            if cond_type == 'none' or not self.app:
                return

            cond_ids = []
            if cond_type == 'pixel' and hasattr(self.app, 'condition_manager'):
                cond_ids = [c.id for c in self.app.condition_manager.pixel_conditions]
            elif cond_type == 'image' and hasattr(self.app, 'condition_manager'):
                cond_ids = [c.id for c in self.app.condition_manager.image_conditions]
            elif cond_type == 'sound' and hasattr(self.app, 'condition_manager'):
                cond_ids = [c.id for c in self.app.condition_manager.sound_conditions]

            if cond_ids:
                tk.Label(cond_id_frame, text="Condition ID:", bg='#1e1e2f', fg='white').pack()
                cond_id_var = tk.StringVar(
                    value=existing_cond.get('id', '') if existing_cond else ''
                )
                id_combo = ttk.Combobox(
                    cond_id_frame, textvariable=cond_id_var, values=cond_ids
                )
                id_combo.pack(fill=tk.X)
                cond_id_frame.cond_var = cond_id_var

        cond_type_var.trace('w', update_cond_id)
        update_cond_id()

        # Действие при совпадении
        action_frame = tk.LabelFrame(
            parent, text="Action on Match", bg='#1e1e2f', fg='white', padx=10, pady=5
        )
        action_frame.pack(fill=tk.X, pady=5)

        action_var = tk.StringVar(value=self.action.get('action_on_match', 'click_center'))
        action_combo = ttk.Combobox(
            action_frame, textvariable=action_var,
            values=['click_center', 'click_at_coords', 'hover', 'save_screenshot']
        )
        action_combo.pack(fill=tk.X)

        self.cond_vars = {
            'type': cond_type_var,
            'action': action_var,
            'id_frame': cond_id_frame
        }

        # Loop until found
        loop_var = tk.BooleanVar(value=self.action.get('loop_until_found', False))
        tk.Checkbutton(
            parent, text="Loop until condition met", variable=loop_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).pack(anchor=tk.W, pady=5)

        max_attempts_frame = tk.Frame(parent, bg='#1e1e2f')
        max_attempts_frame.pack(fill=tk.X, pady=5)
        tk.Label(max_attempts_frame, text="Max attempts:", bg='#1e1e2f', fg='white').pack(side=tk.LEFT)
        max_attempts_var = tk.IntVar(value=self.action.get('max_attempts', 10))
        tk.Entry(max_attempts_frame, textvariable=max_attempts_var, width=8, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        self.loop_vars = {
            'loop': loop_var,
            'max_attempts': max_attempts_var
        }

    def _save(self):
        """Сохранение действия"""
        # Базовые параметры
        self.action['delay_ms'] = self.delay_var.get()
        self.action['variation_ms'] = self.variation_var.get()

        contrib_value = self.contrib_var.get().strip()
        self.action['progress_contrib'] = float(contrib_value) if contrib_value else None

        # Параметры в зависимости от типа
        action_type = self.action.get('type', 'click')

        if action_type == 'click' and self.click_vars:
            self.action['x'] = self.click_vars['x'].get()
            self.action['y'] = self.click_vars['y'].get()
            self.action['hold_ms'] = self.click_vars['hold_ms'].get()
            self.action['random_offset'] = self.click_vars['random_offset'].get()
            self.action['humanize'] = self.click_vars['humanize'].get()

        elif action_type == 'key' and self.key_vars:
            self.action['key'] = self.key_vars['key'].get()
            self.action['key_hold'] = self.key_vars['key_hold'].get()
            self.action['key_hold_ms'] = self.key_vars['key_hold_ms'].get()

        # Условие
        cond_type = self.cond_vars['type'].get()
        if cond_type != 'none' and hasattr(self.cond_vars['id_frame'], 'cond_var'):
            cond_id = self.cond_vars['id_frame'].cond_var.get()
            if cond_id:
                self.action['condition'] = {
                    'type': cond_type,
                    'id': cond_id
                }
            else:
                self.action['condition'] = None
        else:
            self.action['condition'] = None
        self.action['action_on_match'] = self.cond_vars['action'].get()

        # Loop
        self.action['loop_until_found'] = self.loop_vars['loop'].get()
        self.action['max_attempts'] = self.loop_vars['max_attempts'].get()

        if self.callback:
            self.callback(self.action)

        self.dialog.destroy()