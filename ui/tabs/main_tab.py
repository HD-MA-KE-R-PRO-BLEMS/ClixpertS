"""
Clixpert S Pro Ultimate - Main Tab
Основная вкладка: режимы, прогресс, список действий, кнопки управления
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui


class MainTab:
    """
    Основная вкладка приложения.
    Содержит:
    - Переключение режимов (бесконечный/ограниченный)
    - Настройки лимитов
    - Отображение прогресса
    - Список действий
    - Кнопки добавления действий
    - Кнопки управления циклом
    """

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg='#1a1a2e')
        self.actions_tree = None
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов вкладки"""
        # Панель с двумя колонками
        paned = tk.PanedWindow(self.frame, bg='#1a1a2e', sashwidth=5, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - список действий
        left_frame = tk.Frame(paned, bg='#1a1a2e')
        paned.add(left_frame, width=700)

        # Правая панель - настройки и управление
        right_frame = tk.Frame(paned, bg='#1a1a2e')
        paned.add(right_frame, width=350)

        self._create_left_panel(left_frame)
        self._create_right_panel(right_frame)

    def _create_left_panel(self, parent):
        """Создание левой панели (список действий)"""
        # Режим работы
        mode_frame = tk.LabelFrame(
            parent, text="Mode", bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        mode_frame.pack(fill=tk.X, pady=5)

        mode_inner = tk.Frame(mode_frame, bg='#1e1e2f')
        mode_inner.pack(fill=tk.X)

        self.mode_var = tk.IntVar(value=self.app.settings.get('mode', 0))

        tk.Radiobutton(
            mode_inner, text="Infinite loop", variable=self.mode_var, value=0,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            mode_inner, text="Limited", variable=self.mode_var, value=1,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).pack(side=tk.LEFT, padx=10)

        # Параметры ограничения
        limit_frame = tk.LabelFrame(
            parent, text="Limit Parameters", bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        limit_frame.pack(fill=tk.X, pady=5)

        # Initial count
        tk.Label(limit_frame, text="Initial count:", bg='#1e1e2f', fg='white').grid(row=0, column=0, sticky=tk.W)
        self.initial_count_var = tk.DoubleVar(value=self.app.settings.get('initial_count', 100))
        tk.Entry(limit_frame, textvariable=self.initial_count_var, width=10, bg='#2a2a3c', fg='white').grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=5)

        # Default deduction
        tk.Label(limit_frame, text="Default deduction:", bg='#1e1e2f', fg='white').grid(row=1, column=0, sticky=tk.W)
        self.deduction_var = tk.DoubleVar(value=self.app.settings.get('deduction', 10))
        tk.Entry(limit_frame, textvariable=self.deduction_var, width=10, bg='#2a2a3c', fg='white').grid(row=1, column=1,
                                                                                                        padx=5)

        # Deduction multiplier
        tk.Label(limit_frame, text="Deduction multiplier (0-1):", bg='#1e1e2f', fg='white').grid(row=2, column=0,
                                                                                                 sticky=tk.W)
        self.deduction_mult_var = tk.DoubleVar(value=self.app.settings.get('deduction_mult', 0.33))
        tk.Entry(limit_frame, textvariable=self.deduction_mult_var, width=10, bg='#2a2a3c', fg='white').grid(row=2,
                                                                                                             column=1,
                                                                                                             padx=5)

        # Прогресс
        progress_frame = tk.LabelFrame(
            parent, text="Progress", bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        progress_frame.pack(fill=tk.X, pady=5)

        self.count_label = tk.Label(
            progress_frame, text="Progress: 0/0 (0%)",
            bg='#1e1e2f', fg='white'
        )
        self.count_label.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.eta_label = tk.Label(
            progress_frame, text="ETA: --",
            bg='#1e1e2f', fg='#aaaaaa'
        )
        self.eta_label.pack(anchor=tk.W)

        # Список действий
        actions_frame = tk.LabelFrame(
            parent, text="Action Sequence", bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        actions_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Таблица действий
        columns = ('type', 'params', 'delay', 'cond', 'action')
        self.actions_tree = ttk.Treeview(actions_frame, columns=columns, show='headings', height=12)
        self.actions_tree.heading('type', text='Type')
        self.actions_tree.heading('params', text='Parameters')
        self.actions_tree.heading('delay', text='Delay (ms)')
        self.actions_tree.heading('cond', text='Condition')
        self.actions_tree.heading('action', text='Action')

        self.actions_tree.column('type', width=80)
        self.actions_tree.column('params', width=200)
        self.actions_tree.column('delay', width=80)
        self.actions_tree.column('cond', width=120)
        self.actions_tree.column('action', width=120)

        self.actions_tree.pack(fill=tk.BOTH, expand=True)

        # Скроллбар
        scrollbar = ttk.Scrollbar(actions_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        self.actions_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки управления действиями
        action_btns = tk.Frame(actions_frame, bg='#1e1e2f')
        action_btns.pack(fill=tk.X, pady=5)

        tk.Button(
            action_btns, text="+ Delay", command=self._on_add_delay,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            action_btns, text="Edit", command=self._on_edit_action,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            action_btns, text="Delete", command=self._on_delete_action,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            action_btns, text="Clear", command=self._on_clear_actions,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            action_btns, text="Save Profile", command=self._on_save_profile,
            bg='#2a8c4a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            action_btns, text="Load Profile", command=self._on_load_profile,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            action_btns, text="Conditions", command=self._on_show_conditions,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

    def _create_right_panel(self, parent):
        """Создание правой панели (добавление действий и управление)"""
        # Добавление действий
        add_frame = tk.LabelFrame(
            parent, text="Add Action", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        add_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            add_frame, text="🖱 Click (F2)", command=self._on_record_click,
            bg='#5a9cff', fg='white', bd=0, padx=20, pady=8,
            font=('Segoe UI', 10)
        ).pack(pady=5, fill=tk.X)

        tk.Button(
            add_frame, text="⌨ Key (F3)", command=self._on_record_key,
            bg='#5a9cff', fg='white', bd=0, padx=20, pady=8,
            font=('Segoe UI', 10)
        ).pack(pady=5, fill=tk.X)

        hotkeys_text = "F2: click | F3: key | F1: start/stop"
        tk.Label(
            add_frame, text=hotkeys_text,
            bg='#1e1e2f', fg='#aaaaaa', font=('Segoe UI', 9)
        ).pack(pady=10)

        # Настройки действия по умолчанию
        default_frame = tk.LabelFrame(
            parent, text="Default Action Settings", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        default_frame.pack(fill=tk.X, pady=5)

        # Global delay
        delay_frame = tk.Frame(default_frame, bg='#1e1e2f')
        delay_frame.pack(fill=tk.X, pady=2)
        tk.Label(delay_frame, text="Global delay (ms):", bg='#1e1e2f', fg='white').pack(side=tk.LEFT)
        self.global_delay_var = tk.IntVar(value=self.app.settings.get('global_delay_ms', 1000))
        tk.Entry(delay_frame, textvariable=self.global_delay_var, width=8, bg='#2a2a3c', fg='white').pack(side=tk.LEFT,
                                                                                                          padx=5)

        # Random offset
        offset_frame = tk.Frame(default_frame, bg='#1e1e2f')
        offset_frame.pack(fill=tk.X, pady=2)
        tk.Label(offset_frame, text="Random offset (px):", bg='#1e1e2f', fg='white').pack(side=tk.LEFT)
        self.random_offset_var = tk.IntVar(value=self.app.settings.get('random_click_offset', 5))
        tk.Entry(offset_frame, textvariable=self.random_offset_var, width=8, bg='#2a2a3c', fg='white').pack(
            side=tk.LEFT, padx=5)

        # Humanize mouse
        self.humanize_var = tk.BooleanVar(value=self.app.settings.get('humanize_mouse', True))
        tk.Checkbutton(
            default_frame, text="Humanize mouse movement", variable=self.humanize_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).pack(anchor=tk.W, pady=2)

        # Управление циклом
        control_frame = tk.Frame(parent, bg='#1a1a2e')
        control_frame.pack(fill=tk.X, pady=10)

        self.start_stop_btn = tk.Button(
            control_frame, text="Start (F1)", command=self._on_toggle_cycle,
            bg='#2a8c4a', fg='white', bd=0, padx=30, pady=10,
            font=('Segoe UI', 12, 'bold')
        )
        self.start_stop_btn.pack(fill=tk.X, pady=5)

        tk.Button(
            control_frame, text="Minimize to tray", command=self._on_minimize,
            bg='#3a3a5c', fg='white', bd=0, padx=20, pady=5
        ).pack(fill=tk.X, pady=2)

        tk.Button(
            control_frame, text="Exit", command=self._on_exit,
            bg='#8c2a2a', fg='white', bd=0, padx=20, pady=5
        ).pack(fill=tk.X, pady=2)

        # Статус
        self.status_var = tk.StringVar(value="Waiting")
        status_label = tk.Label(
            parent, textvariable=self.status_var,
            bg='#1a1a2e', fg='#88ff88', font=('Segoe UI', 10, 'bold')
        )
        status_label.pack(pady=10)

    def _on_record_click(self):
        """Запись клика"""
        x, y = pyautogui.position()
        self.app.action_manager.add_action(
            self.app.action_manager.create_click_action(
                x, y,
                delay_ms=self.global_delay_var.get(),
                random_offset=self.random_offset_var.get(),
                humanize=self.humanize_var.get()
            )
        )
        self.update_actions_tree()
        self.status_var.set(f"Click added: ({x}, {y})")

    def _on_record_key(self):
        """Запись клавиши - открывает диалог для выбора/записи клавиши"""
        from ui.dialogs.action_editor import ActionEditorDialog

        # Создаём пустое действие для клавиши
        empty_action = {
            'type': 'key',
            'key': '',
            'delay_ms': self.global_delay_var.get(),
            'key_hold': False,
            'key_hold_ms': 100
        }

        def on_action_saved(new_action_data):
            """Обработчик сохранения действия"""
            from core.actions import Action
            new_action = Action.from_dict(new_action_data)
            self.app.action_manager.add_action(new_action)
            self.update_actions_tree()
            self.status_var.set(f"Key added: {new_action.key}")

        dialog = ActionEditorDialog(
            self.frame, empty_action, on_action_saved, self.app
        )
        dialog.show()

    def _on_add_delay(self):
        """Добавление задержки"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Add Delay")
        dialog.geometry("300x150")
        dialog.configure(bg='#1e1e2f')
        dialog.transient(self.frame)
        dialog.grab_set()

        tk.Label(dialog, text="Delay (ms):", bg='#1e1e2f', fg='white').pack(pady=10)
        delay_var = tk.IntVar(value=1000)
        tk.Entry(dialog, textvariable=delay_var, bg='#2a2a3c', fg='white').pack()

        def save():
            self.app.action_manager.add_action(
                self.app.action_manager.create_delay_action(delay_var.get())
            )
            self.update_actions_tree()
            dialog.destroy()
            self.status_var.set(f"Delay added: {delay_var.get()}ms")

        tk.Button(dialog, text="Add", command=save, bg='#2a8c4a', fg='white', bd=0, padx=20).pack(pady=10)

    def _on_edit_action(self):
        """Редактирование выбранного действия"""
        selected = self.actions_tree.selection()
        if not selected:
            self.status_var.set("Select an action to edit")
            return

        item_iid = selected[0]
        action = self.app.action_manager.get_action_by_iid(item_iid)
        if action:
            from ui.dialogs.action_editor import ActionEditorDialog

            def on_action_saved(new_action_data):
                from core.actions import Action
                new_action = Action.from_dict(new_action_data)
                # Сохраняем старый IID
                new_action.tree_iid = item_iid
                self.app.action_manager.update_action_by_iid(item_iid, new_action)
                self.update_actions_tree()
                self.status_var.set("Action updated")

            dialog = ActionEditorDialog(
                self.frame, action.to_dict(), on_action_saved, self.app
            )
            dialog.show()

    def _on_action_updated(self, item_id, new_action_data):
        """Обработчик обновления действия"""
        from core.actions import Action
        new_action = Action.from_dict(new_action_data)
        new_action.tree_iid = item_id
        self.app.action_manager.update_action_by_iid(item_id, new_action)
        self.update_actions_tree()
        self.status_var.set("Action updated")

    def _on_delete_action(self):
        """Удаление выбранного действия"""
        selected = self.actions_tree.selection()
        if not selected:
            return
        for item in selected:
            self.app.action_manager.remove_action_by_iid(item)
        self.update_actions_tree()
        self.status_var.set(f"Deleted {len(selected)} action(s)")

    def _on_clear_actions(self):
        """Очистка всех действий"""
        if messagebox.askyesno("Confirm", "Clear all actions?"):
            self.app.action_manager.clear_actions()
            self.update_actions_tree()
            self.status_var.set("All actions cleared")

    def _on_save_profile(self):
        """Сохранение профиля"""
        if self.app.action_manager.is_empty():
            messagebox.showwarning("Error", "Add at least one action")
            return
        self.app.profile_manager.save_current_profile()

    def _on_load_profile(self):
        """Загрузка профиля"""
        self.app.profile_manager.load_profile_dialog()
        self.update_actions_tree()

    def _on_show_conditions(self):
        """Показать диалог условий"""
        if hasattr(self.app, 'pixel_conditions_dialog') and self.app.pixel_conditions_dialog:
            self.app.pixel_conditions_dialog.show()
        else:
            messagebox.showinfo("Info", "Conditions dialog not available")

    def _on_toggle_cycle(self):
        """Запуск/остановка цикла"""
        if self.app.running:
            self.app.stop_cycle()
            self.start_stop_btn.config(text="Start (F1)", bg='#2a8c4a')
        else:
            # Сохраняем настройки
            self.app.settings['mode'] = self.mode_var.get()
            self.app.settings['initial_count'] = self.initial_count_var.get()
            self.app.settings['deduction'] = self.deduction_var.get()
            self.app.settings['deduction_mult'] = self.deduction_mult_var.get()
            self.app.settings['global_delay_ms'] = self.global_delay_var.get()
            self.app.settings['random_click_offset'] = self.random_offset_var.get()
            self.app.settings['humanize_mouse'] = self.humanize_var.get()

            self.app.start_cycle()
            self.start_stop_btn.config(text="Stop (F1)", bg='#8c2a2a')

    def _on_minimize(self):
        """Свернуть в трей"""
        if self.app:
            self.app.hide_window()

    def _on_exit(self):
        """Выход из программы"""
        if self.app:
            self.app.quit_app()

    def update_actions_tree(self):
        """Обновление дерева действий"""
        # Очищаем все элементы
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)

        # Вставляем действия заново
        for action in self.app.action_manager.actions:
            # Убеждаемся, что у действия есть уникальный IID
            if not action.tree_iid:
                import uuid
                action.tree_iid = str(uuid.uuid4())

            # Формируем параметры для отображения
            if action.type.value == 'click':
                params = f"X={action.x}, Y={action.y}"
                if action.hold_ms > 0:
                    params += f", hold={action.hold_ms}ms"
                if action.random_offset > 0:
                    params += f", ±{action.random_offset}px"
            elif action.type.value == 'key':
                params = f"Key: {action.key}"
                if action.key_hold:
                    params += f" (hold {action.key_hold_ms}ms)"
            else:
                params = f"Pause {action.delay_ms}ms"
                if action.variation_ms > 0:
                    params += f" ±{action.variation_ms}ms"

            cond = action.condition.get('id', '—') if action.condition else '—'

            # Вставляем с проверкой на существование
            try:
                self.actions_tree.insert('', tk.END, iid=action.tree_iid, values=(
                    action.type.value.capitalize(),
                    params,
                    action.delay_ms,
                    cond,
                    action.action_on_match
                ))
            except tk.TclError:
                # Если IID уже существует, вставляем без указания iid
                self.actions_tree.insert('', tk.END, values=(
                    action.type.value.capitalize(),
                    params,
                    action.delay_ms,
                    cond,
                    action.action_on_match
                ))

    def update_progress(self, current, total, percent, eta_text):
        """Обновление прогресса"""
        self.count_label.config(text=f"Progress: {current:.1f} / {total:.1f} ({percent:.1f}%)")
        self.progress_bar['value'] = percent
        self.eta_label.config(text=f"ETA: {eta_text}")

    def update_status(self, message):
        """Обновление статуса"""
        self.status_var.set(message)

    def update_start_stop_button(self, is_running):
        """Обновление кнопки старт/стоп"""
        if is_running:
            self.start_stop_btn.config(text="Stop (F1)", bg='#8c2a2a')
        else:
            self.start_stop_btn.config(text="Start (F1)", bg='#2a8c4a')

    def get_frame(self):
        """Получить фрейм вкладки"""
        return self.frame

    def refresh_texts(self):
        """Обновление текстов интерфейса"""
        # Обновляем заголовки фреймов
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for side_frame in child.panes():
                    for subchild in side_frame.winfo_children():
                        if isinstance(subchild, tk.LabelFrame):
                            text = subchild.cget("text")
                            if text == "Mode":
                                subchild.config(text=self.app.get_text('mode'))
                            elif text == "Limit Parameters":
                                subchild.config(text=self.app.get_text('limit_params'))
                            elif text == "Progress":
                                subchild.config(text=self.app.get_text('progress'))
                            elif text == "Action Sequence":
                                subchild.config(text=self.app.get_text('actions'))
                            elif text == "Add Action":
                                subchild.config(text=self.app.get_text('add_action'))
                            elif text == "Default Action Settings":
                                subchild.config(text=self.app.get_text('default_settings'))

        # Обновляем радиокнопки
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for side_frame in child.panes():
                    for subchild in side_frame.winfo_children():
                        if isinstance(subchild, tk.LabelFrame):
                            for rb in subchild.winfo_children():
                                if isinstance(rb, tk.Radiobutton):
                                    if rb.cget("text") == "Infinite loop":
                                        rb.config(text=self.app.get_text('infinite'))
                                    elif rb.cget("text") == "Limited":
                                        rb.config(text=self.app.get_text('limited'))

        # Обновляем метки в Limit Parameters
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for side_frame in child.panes():
                    for subchild in side_frame.winfo_children():
                        if isinstance(subchild, tk.LabelFrame) and subchild.cget("text") == self.app.get_text(
                                'limit_params'):
                            for label in subchild.winfo_children():
                                if isinstance(label, tk.Label):
                                    text = label.cget("text")
                                    if text == "Initial count:":
                                        label.config(text=self.app.get_text('initial_count'))
                                    elif text == "Default deduction:":
                                        label.config(text=self.app.get_text('default_deduction'))
                                    elif text == "Deduction multiplier (0-1):":
                                        label.config(text=self.app.get_text('deduction_mult'))

        # Обновляем кнопки
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for side_frame in child.panes():
                    for subchild in side_frame.winfo_children():
                        if isinstance(subchild, tk.LabelFrame):
                            for btn_frame in subchild.winfo_children():
                                if isinstance(btn_frame, tk.Frame):
                                    for btn in btn_frame.winfo_children():
                                        if isinstance(btn, tk.Button):
                                            text = btn.cget("text")
                                            if text == "+ Delay":
                                                btn.config(text="+ " + self.app.get_text('delay'))
                                            elif text == "Edit":
                                                btn.config(text=self.app.get_text('edit'))
                                            elif text == "Delete":
                                                btn.config(text=self.app.get_text('delete'))
                                            elif text == "Clear":
                                                btn.config(text=self.app.get_text('clear'))
                                            elif text == "Save Profile":
                                                btn.config(text=self.app.get_text('save_profile'))
                                            elif text == "Load Profile":
                                                btn.config(text=self.app.get_text('load_profile'))
                                            elif text == "Conditions":
                                                btn.config(text=self.app.get_text('conditions'))
                                            elif text == "Minimize to tray":
                                                btn.config(text=self.app.get_text('tray'))
                                            elif text == "Exit":
                                                btn.config(text=self.app.get_text('exit'))

        # Обновляем метки настроек
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for side_frame in child.panes():
                    for subchild in side_frame.winfo_children():
                        if isinstance(subchild, tk.LabelFrame) and subchild.cget("text") == self.app.get_text(
                                'default_settings'):
                            for frame in subchild.winfo_children():
                                if isinstance(frame, tk.Frame):
                                    for label in frame.winfo_children():
                                        if isinstance(label, tk.Label):
                                            text = label.cget("text")
                                            if text == "Global delay (ms):":
                                                label.config(text=self.app.get_text('global_delay'))
                                            elif text == "Random offset (px):":
                                                label.config(text=self.app.get_text('random_click_offset'))
                                            elif text == "Humanize mouse movement":
                                                label.config(text=self.app.get_text('humanize_mouse'))