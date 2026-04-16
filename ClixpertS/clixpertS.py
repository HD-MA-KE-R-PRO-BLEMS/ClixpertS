import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import threading
import time
import win32con
import win32gui
import pygetwindow as gw
import pyautogui
import keyboard
from PIL import Image, ImageDraw
import pystray
import json
import os

class ProgressWindow:
    """Отдельное окно с прогресс-баром опыта."""
    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        self.create_window()

    def create_window(self):
        if self.window is not None:
            return
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Прогресс прокачки")
        self.window.geometry("300x120")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.configure(bg='#2d2d2d')

        self.window.bind('<Button-1>', self.start_move)
        self.window.bind('<B1-Motion>', self.on_move)

        frame = tk.Frame(self.window, bg='#2d2d2d', padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.label = tk.Label(frame, text="Опыт: 0.00 / 0.00 (0%)",
                              fg='white', bg='#2d2d2d', font=('Arial', 10, 'bold'))
        self.label.pack(pady=(0, 5))

        self.progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=280, mode='determinate')
        self.progress.pack(pady=5)

        self.eta_label = tk.Label(frame, text="Осталось примерно: —",
                                  fg='white', bg='#2d2d2d', font=('Arial', 9))
        self.eta_label.pack(pady=(2, 0))

        btn_frame = tk.Frame(frame, bg='#2d2d2d')
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Button(btn_frame, text="Скрыть", command=self.hide, bg='#555', fg='white',
                  bd=0, padx=10).pack(side=tk.RIGHT)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")

    def update(self, current, total, percent, eta_text):
        if self.window is None or not self.window.winfo_exists():
            return
        self.label.config(text=f"Опыт: {current:.2f} / {total:.2f} ({percent:.1f}%)")
        self.progress['value'] = percent
        self.eta_label.config(text=f"Осталось примерно: {eta_text}")

    def show(self):
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.deiconify()

    def hide(self):
        if self.window is not None:
            self.window.withdraw()

    def destroy(self):
        if self.window is not None:
            self.window.destroy()
            self.window = None


class PixelConditionDialog:
    """Окно управления пиксельными условиями."""
    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        self.conditions = []  # список словарей: {'id': str, 'x': int, 'y': int, 'color': (r,g,b)}
        self.create_window()

    def create_window(self):
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Пиксельные условия")
        self.window.geometry("600x450")
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

        frame = ttk.Frame(self.window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Таблица условий
        columns = ('id', 'pos', 'color')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)
        self.tree.heading('id', text='ID')
        self.tree.heading('pos', text='Координаты')
        self.tree.heading('color', text='Цвет (RGB)')
        self.tree.column('id', width=120)
        self.tree.column('pos', width=150)
        self.tree.column('color', width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Добавить из текущей позиции", command=self.add_from_current).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить все", command=self.clear_all).pack(side=tk.LEFT, padx=5)

        ttk.Label(frame, text="Допуск по цвету (0-50):").pack(anchor=tk.W, pady=(10,0))
        self.tolerance_var = tk.IntVar(value=self.app.color_tolerance_var.get())
        ttk.Scale(frame, from_=0, to=50, variable=self.tolerance_var, orient=tk.HORIZONTAL,
                  command=lambda v: self.app.color_tolerance_var.set(int(float(v)))).pack(fill=tk.X)
        ttk.Label(frame, textvariable=self.tolerance_var).pack()

        ttk.Button(frame, text="Закрыть", command=self.hide).pack(pady=10)

        self.refresh_list()

    def add_from_current(self):
        x, y = pyautogui.position()
        try:
            color = pyautogui.pixel(x, y)
        except:
            messagebox.showerror("Ошибка", "Не удалось получить цвет пикселя.")
            return
        cond_id = simpledialog.askstring("Идентификатор", "Введите уникальный идентификатор условия:")
        if not cond_id:
            return
        if any(c['id'] == cond_id for c in self.conditions):
            messagebox.showerror("Ошибка", "Условие с таким ID уже существует.")
            return
        self.conditions.append({
            'id': cond_id,
            'x': x, 'y': y,
            'color': color
        })
        self.refresh_list()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        for item in selected:
            cond_id = self.tree.item(item)['values'][0]
            self.conditions = [c for c in self.conditions if c['id'] != cond_id]
        self.refresh_list()

    def clear_all(self):
        self.conditions.clear()
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cond in self.conditions:
            self.tree.insert('', tk.END, values=(
                cond['id'],
                f"({cond['x']}, {cond['y']})",
                f"{cond['color'][0]}, {cond['color'][1]}, {cond['color'][2]}"
            ))

    def get_condition_by_id(self, cond_id):
        for c in self.conditions:
            if c['id'] == cond_id:
                return c
        return None

    def show(self):
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.deiconify()

    def hide(self):
        if self.window:
            self.window.withdraw()


class ClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clixpert S")
        self.root.geometry("720x800")
        self.root.resizable(False, False)

        self.running = False
        self.thread = None
        # actions: {'type': 'click'/'key', 'x':x, 'y':y, 'key':key, 'delay_ms':int, 'hold_ms':int (только для клика), 'condition_id': str/None}
        self.actions = []
        self.target_hwnd = None
        self.target_title = ""

        # Переменные параметров
        self.powerlevel_var = tk.IntVar(value=0)
        self.exp_initial_var = tk.DoubleVar(value=100.0)
        self.exp_deduction_var = tk.DoubleVar(value=10.0)
        self.deduction_mult_var = tk.DoubleVar(value=0.33)
        self.global_delay_ms_var = tk.IntVar(value=1000)

        self.hotkey_record_click_var = tk.StringVar(value='f2')
        self.hotkey_record_key_var = tk.StringVar(value='f3')
        self.hotkey_toggle_var = tk.StringVar(value='f1')
        self.hotkey_pick_color_var = tk.StringVar(value='f4')

        self.always_on_top_var = tk.BooleanVar(value=False)
        self.show_progress_window_var = tk.BooleanVar(value=False)

        # Пиксельные условия
        self.color_tolerance_var = tk.IntVar(value=10)
        self.use_conditions_var = tk.BooleanVar(value=True)
        self.pixel_conditions_dialog = PixelConditionDialog(self)

        # Флаг ожидания клавиши для записи
        self.waiting_for_key = False

        self.current_exp = self.exp_initial_var.get()
        self.progress_window = None
        self.tray_icon = None

        self.create_tray_icon()
        self.create_widgets()
        self.root.after(100, self.init_progress_window)

        self.update_exp_display()
        self.register_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.update_always_on_top()
        self.refresh_window_list()

    def init_progress_window(self):
        self.progress_window = ProgressWindow(self)
        if self.show_progress_window_var.get():
            self.progress_window.show()
        else:
            self.progress_window.hide()

    def toggle_progress_window(self):
        if self.show_progress_window_var.get():
            if self.progress_window:
                self.progress_window.show()
        else:
            if self.progress_window:
                self.progress_window.hide()

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color='gray')
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill='blue')
        draw.text((20, 20), "CS", fill='white')
        menu = pystray.Menu(
            pystray.MenuItem("Показать", self.show_window, default=True),
            pystray.MenuItem("Выход", self.quit_app)
        )
        self.tray_icon = pystray.Icon("clixpert", image, "Clixpert S", menu)

    def show_window(self, *_):
        self.root.after(0, self.root.deiconify)

    def hide_window(self, *_):
        self.root.withdraw()
        if self.tray_icon:
            self.tray_icon.notify("Clixpert S свёрнут в трей.\nГорячие клавиши активны.", "Clixpert S")

    def quit_app(self, *_):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        keyboard.unhook_all()
        if self.progress_window:
            self.progress_window.destroy()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()

    def update_always_on_top(self):
        self.root.attributes('-topmost', self.always_on_top_var.get())

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Выбор окна ---
        window_frame = ttk.LabelFrame(main_frame, text="Целевое окно", padding="5")
        window_frame.pack(fill=tk.X, pady=5)

        top_win_frame = ttk.Frame(window_frame)
        top_win_frame.pack(fill=tk.X)
        ttk.Label(top_win_frame, text="Выберите окно:").pack(side=tk.LEFT)
        self.window_combobox = ttk.Combobox(top_win_frame, state="readonly", width=40)
        self.window_combobox.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(top_win_frame, text="Обновить", command=self.refresh_window_list).pack(side=tk.LEFT, padx=5)

        self.selected_window_label = ttk.Label(window_frame, text="Окно не выбрано")
        self.selected_window_label.pack(anchor=tk.W, pady=2)
        self.window_combobox.bind('<<ComboboxSelected>>', self.on_window_select)

        # --- Режим работы ---
        mode_frame = ttk.LabelFrame(main_frame, text="Режим", padding="5")
        mode_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(mode_frame, text="Обычный (бесконечный цикл)", variable=self.powerlevel_var, value=0).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Прокачка (с опытом)", variable=self.powerlevel_var, value=1).pack(anchor=tk.W)

        # --- Параметры опыта ---
        exp_frame = ttk.LabelFrame(main_frame, text="Параметры опыта (для режима прокачки)", padding="5")
        exp_frame.pack(fill=tk.X, pady=5)

        ttk.Label(exp_frame, text="Начальный опыт:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(exp_frame, textvariable=self.exp_initial_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(exp_frame, text="Вычет (EXP_DEDUCTION):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(exp_frame, textvariable=self.exp_deduction_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)

        ttk.Label(exp_frame, text="Множитель вычета (0..1):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(exp_frame, textvariable=self.deduction_mult_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Label(exp_frame, text="(вычитается: Вычет × (1 - Множитель))").grid(row=2, column=2, sticky=tk.W, padx=5)

        ttk.Checkbutton(exp_frame, text="Показывать отдельное окно прогресса",
                        variable=self.show_progress_window_var,
                        command=self.toggle_progress_window).grid(row=3, column=0, columnspan=3, pady=5, sticky=tk.W)

        # --- Последовательность действий ---
        actions_frame = ttk.LabelFrame(main_frame, text="Последовательность действий", padding="5")
        actions_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Treeview для отображения действий
        columns = ('type', 'params', 'delay', 'hold', 'cond')
        self.actions_tree = ttk.Treeview(actions_frame, columns=columns, show='headings', height=6)
        self.actions_tree.heading('type', text='Тип')
        self.actions_tree.heading('params', text='Параметры')
        self.actions_tree.heading('delay', text='Задержка (мс)')
        self.actions_tree.heading('hold', text='Удержание (мс)')
        self.actions_tree.heading('cond', text='Условие')
        self.actions_tree.column('type', width=70, anchor='center')
        self.actions_tree.column('params', width=180)
        self.actions_tree.column('delay', width=90, anchor='center')
        self.actions_tree.column('hold', width=90, anchor='center')
        self.actions_tree.column('cond', width=90, anchor='center')
        self.actions_tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(actions_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        self.actions_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.actions_tree.bind('<Double-1>', self.edit_action_double_click)

        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Очистить список", command=self.clear_actions).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить выбранное", command=self.remove_selected_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit_selected_action).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сохранить профиль", command=self.save_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Загрузить профиль", command=self.load_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Пиксельные условия", command=self.pixel_conditions_dialog.show).pack(side=tk.LEFT, padx=5)

        hotkeys_info = (
            f"F2: запись клика | F3: запись клавиши | F4: цвет пикселя | F1: пуск/стоп"
        )
        ttk.Label(actions_frame, text=hotkeys_info).pack(pady=2)

        # --- Настройки ---
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding="5")
        settings_frame.pack(fill=tk.X, pady=5)

        ttk.Label(settings_frame, text="Глоб. задержка (мс):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.global_delay_ms_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(settings_frame, text="Клавиша записи клика:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.hotkey_record_click_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)

        ttk.Label(settings_frame, text="Клавиша записи клавиши:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.hotkey_record_key_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5)

        ttk.Label(settings_frame, text="Клавиша запуска/остановки:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.hotkey_toggle_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5)

        ttk.Label(settings_frame, text="Клавиша цвета пикселя:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.hotkey_pick_color_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=5)

        ttk.Checkbutton(settings_frame, text="Окно всегда сверху", variable=self.always_on_top_var,
                        command=self.update_always_on_top).grid(row=5, column=0, columnspan=2, pady=5)

        ttk.Label(settings_frame, text="Допуск цвета (0-50):").grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.color_tolerance_var, width=10).grid(row=6, column=1, sticky=tk.W, padx=5)

        ttk.Checkbutton(settings_frame, text="Применять пиксельные условия (если заданы)",
                        variable=self.use_conditions_var).grid(row=7, column=0, columnspan=2, pady=5)

        ttk.Button(settings_frame, text="Применить настройки", command=self.apply_settings).grid(row=8, column=0, columnspan=2, pady=10)

        # --- Прогресс опыт ---
        status_frame = ttk.LabelFrame(main_frame, text="Опыт", padding="5")
        status_frame.pack(fill=tk.X, pady=5)

        self.exp_label = ttk.Label(status_frame, text="Опыт: 0.00 / 0.00 (0%)")
        self.exp_label.pack(anchor=tk.W)

        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        self.eta_label = ttk.Label(status_frame, text="Осталось примерно: —")
        self.eta_label.pack(anchor=tk.W, pady=(2, 0))

        # --- Управление ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.start_stop_btn = ttk.Button(control_frame, text="Запустить цикл (F1)", command=self.toggle_cycle)
        self.start_stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Свернуть в трей", command=self.hide_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Выход", command=self.quit_app).pack(side=tk.RIGHT, padx=5)

        self.status_var = tk.StringVar(value="Ожидание")
        ttk.Label(main_frame, textvariable=self.status_var).pack(fill=tk.X, pady=5)

    def refresh_window_list(self):
        """Обновляет список окон в выпадающем списке."""
        windows = gw.getAllWindows()
        titles = [w.title for w in windows if w.title.strip() != ""]
        self.window_combobox['values'] = titles
        if titles:
            self.window_combobox.current(0)
            self.on_window_select()

    def on_window_select(self, event=None):
        """Обработчик выбора окна."""
        title = self.window_combobox.get()
        if title:
            try:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    win = windows[0]
                    self.target_hwnd = win._hWnd
                    self.target_title = title
                    self.selected_window_label.config(text=f"Выбрано: {title} (HWND: {self.target_hwnd})")
                else:
                    self.target_hwnd = None
                    self.target_title = ""
                    self.selected_window_label.config(text="Окно не найдено")
            except Exception as e:
                self.target_hwnd = None
                self.target_title = ""
                self.selected_window_label.config(text=f"Ошибка: {e}")

    def register_hotkeys(self):
        keyboard.unhook_all()
        click_key = self.hotkey_record_click_var.get().strip()
        key_key = self.hotkey_record_key_var.get().strip()
        toggle_key = self.hotkey_toggle_var.get().strip()
        color_key = self.hotkey_pick_color_var.get().strip()
        if click_key:
            keyboard.add_hotkey(click_key, self.record_click_action)
        if key_key:
            keyboard.add_hotkey(key_key, self.start_key_recording)
        if toggle_key:
            keyboard.add_hotkey(toggle_key, self.toggle_cycle)
        if color_key:
            keyboard.add_hotkey(color_key, self.pick_color_action)
        # Дополнительный хук для захвата клавиши при ожидании
        keyboard.on_press(self._on_key_press_for_recording)

    def _on_key_press_for_recording(self, event):
        if self.waiting_for_key:
            # Игнорируем служебные клавиши-модификаторы
            if event.name in ('shift', 'ctrl', 'alt', 'windows', 'right shift', 'right ctrl', 'right alt'):
                return
            self.waiting_for_key = False
            self.root.after(0, lambda: self._add_key_action(event.name))

    def start_key_recording(self):
        if self.running:
            self.status_var.set("Нельзя добавлять действия во время работы цикла!")
            return
        self.status_var.set("Ожидание нажатия клавиши... Нажмите нужную клавишу.")
        self.waiting_for_key = True

    def _add_key_action(self, key_name):
        action = {
            'type': 'key',
            'key': key_name,
            'delay_ms': self.global_delay_ms_var.get(),
            'hold_ms': 0,
            'condition_id': None
        }
        self.actions.append(action)
        self._add_action_to_tree(action)
        self.status_var.set(f"Добавлена клавиша: {key_name}")

    def apply_settings(self):
        try:
            delay = self.global_delay_ms_var.get()
            if delay < 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Глобальная задержка должна быть неотрицательным целым числом (мс)")
            return

        self.register_hotkeys()
        toggle_key = self.hotkey_toggle_var.get().strip()
        self.start_stop_btn.config(text=f"Запустить цикл ({toggle_key.upper()})")
        self.status_var.set("Настройки применены")

    def record_click_action(self):
        """Запись клика мышью."""
        if self.running:
            self.status_var.set("Нельзя добавлять действия во время работы цикла!")
            return
        x, y = pyautogui.position()
        action = {
            'type': 'click',
            'x': x, 'y': y,
            'delay_ms': self.global_delay_ms_var.get(),
            'hold_ms': 0,
            'condition_id': None
        }
        self.actions.append(action)
        self._add_action_to_tree(action)
        self.status_var.set(f"Добавлен клик: ({x}, {y})")

    def pick_color_action(self):
        """Получить цвет пикселя под курсором и показать."""
        x, y = pyautogui.position()
        try:
            color = pyautogui.pixel(x, y)
            hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
            self.status_var.set(f"Цвет пикселя ({x},{y}): RGB{color} HEX {hex_color}")
        except Exception as e:
            self.status_var.set(f"Ошибка получения цвета: {e}")

    def _add_action_to_tree(self, action):
        """Добавляет действие в Treeview."""
        if action['type'] == 'click':
            params = f"X={action['x']}, Y={action['y']}"
            hold = f"{action.get('hold_ms', 0)}"
        else:
            params = f"Key: {action['key']}"
            hold = "—"
        delay = action.get('delay_ms', self.global_delay_ms_var.get())
        cond = action.get('condition_id', '') or '—'
        item = self.actions_tree.insert('', tk.END,
                                        values=(action['type'].capitalize(), params, delay, hold, cond))
        action['tree_iid'] = item

    def clear_actions(self):
        if self.running:
            self.status_var.set("Нельзя очищать список во время работы цикла!")
            return
        self.actions.clear()
        for item in self.actions_tree.get_children():
            self.actions_tree.delete(item)
        self.status_var.set("Список действий очищен")

    def remove_selected_action(self):
        if self.running:
            self.status_var.set("Нельзя изменять список во время работы цикла!")
            return
        selected = self.actions_tree.selection()
        if selected:
            for item in selected:
                for i, act in enumerate(self.actions):
                    if act.get('tree_iid') == item:
                        del self.actions[i]
                        break
                self.actions_tree.delete(item)
            self.status_var.set("Действие удалено")

    def edit_selected_action(self):
        selected = self.actions_tree.selection()
        if selected:
            self.edit_action_double_click(None, item=selected[0])

    def edit_action_double_click(self, event, item=None):
        """Двойной клик для редактирования задержки, удержания, координат, условия и клавиши."""
        if self.running:
            self.status_var.set("Нельзя редактировать во время работы цикла!")
            return
        if item is None:
            selected = self.actions_tree.selection()
            if not selected:
                return
            item = selected[0]
        action = None
        for act in self.actions:
            if act.get('tree_iid') == item:
                action = act
                break
        if not action:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать действие")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Общие поля
        ttk.Label(dialog, text="Задержка перед выполнением (мс):").pack(pady=5)
        delay_var = tk.IntVar(value=action.get('delay_ms', self.global_delay_ms_var.get()))
        ttk.Entry(dialog, textvariable=delay_var, width=15).pack()

        if action['type'] == 'click':
            # Координаты
            coord_frame = ttk.Frame(dialog)
            coord_frame.pack(pady=5)
            ttk.Label(coord_frame, text="X:").pack(side=tk.LEFT)
            x_var = tk.IntVar(value=action['x'])
            ttk.Entry(coord_frame, textvariable=x_var, width=6).pack(side=tk.LEFT, padx=5)
            ttk.Label(coord_frame, text="Y:").pack(side=tk.LEFT)
            y_var = tk.IntVar(value=action['y'])
            ttk.Entry(coord_frame, textvariable=y_var, width=6).pack(side=tk.LEFT, padx=5)
            ttk.Button(coord_frame, text="Взять текущие",
                       command=lambda: self._update_coords_from_mouse(x_var, y_var)).pack(side=tk.LEFT, padx=5)

            # Удержание
            ttk.Label(dialog, text="Время удержания кнопки (мс, 0 = клик):").pack(pady=5)
            hold_var = tk.IntVar(value=action.get('hold_ms', 0))
            ttk.Entry(dialog, textvariable=hold_var, width=15).pack()

            # Условие
            cond_frame = ttk.LabelFrame(dialog, text="Условие по цвету", padding=5)
            cond_frame.pack(fill=tk.X, pady=10, padx=10)

            cond_var = tk.StringVar(value=action.get('condition_id', ''))
            cond_ids = [''] + [c['id'] for c in self.pixel_conditions_dialog.conditions]
            cond_combo = ttk.Combobox(cond_frame, textvariable=cond_var, values=cond_ids, state='readonly', width=25)
            cond_combo.pack(side=tk.LEFT, padx=5)

            ttk.Button(cond_frame, text="Создать условие из текущей позиции",
                       command=lambda: self._create_condition_from_current(cond_var, cond_combo)).pack(side=tk.LEFT)

            ttk.Checkbutton(cond_frame, text="Использовать условие",
                            variable=tk.BooleanVar(value=bool(action.get('condition_id'))),
                            command=lambda: cond_var.set('') if not cond_var.get() else None).pack()
        else:
            # Клавиша
            key_frame = ttk.Frame(dialog)
            key_frame.pack(pady=5)
            ttk.Label(key_frame, text="Клавиша:").pack(side=tk.LEFT)
            key_var = tk.StringVar(value=action['key'])
            key_combo = ttk.Combobox(key_frame, textvariable=key_var, values=self._get_key_list(), width=15)
            key_combo.pack(side=tk.LEFT, padx=5)
            ttk.Button(key_frame, text="Записать нажатие",
                       command=lambda: self._record_key_for_dialog(key_var, dialog)).pack(side=tk.LEFT, padx=5)

        def save_changes():
            action['delay_ms'] = delay_var.get()
            if action['type'] == 'click':
                action['x'] = x_var.get()
                action['y'] = y_var.get()
                action['hold_ms'] = hold_var.get()
                action['condition_id'] = cond_var.get() if cond_var.get() else None
                params = f"X={action['x']}, Y={action['y']}"
                hold = str(action['hold_ms'])
                cond = action['condition_id'] or '—'
            else:
                action['key'] = key_var.get()
                params = f"Key: {action['key']}"
                hold = "—"
                cond = "—"
            # Обновить отображение
            self.actions_tree.item(item, values=(
                action['type'].capitalize(),
                params,
                action['delay_ms'],
                hold,
                cond
            ))
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save_changes).pack(pady=15)
        dialog.wait_window()

    def _update_coords_from_mouse(self, x_var, y_var):
        x, y = pyautogui.position()
        x_var.set(x)
        y_var.set(y)

    def _create_condition_from_current(self, cond_var, cond_combo):
        x, y = pyautogui.position()
        try:
            color = pyautogui.pixel(x, y)
        except:
            messagebox.showerror("Ошибка", "Не удалось получить цвет пикселя.")
            return
        cond_id = simpledialog.askstring("Идентификатор", "Введите уникальный идентификатор условия:")
        if not cond_id:
            return
        if any(c['id'] == cond_id for c in self.pixel_conditions_dialog.conditions):
            messagebox.showerror("Ошибка", "Условие с таким ID уже существует.")
            return
        self.pixel_conditions_dialog.conditions.append({
            'id': cond_id,
            'x': x, 'y': y,
            'color': color
        })
        self.pixel_conditions_dialog.refresh_list()
        # Обновить список в комбобоксе
        cond_ids = [''] + [c['id'] for c in self.pixel_conditions_dialog.conditions]
        cond_combo['values'] = cond_ids
        cond_var.set(cond_id)

    def _get_key_list(self):
        """Возвращает список часто используемых клавиш для выпадающего списка."""
        return ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                '0','1','2','3','4','5','6','7','8','9',
                'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12',
                'enter','space','tab','escape','backspace','shift','ctrl','alt']

    def _record_key_for_dialog(self, key_var, dialog):
        dialog.grab_release()
        self.status_var.set("Нажмите клавишу для записи...")
        self.waiting_for_key = True
        # Временно перехватываем нажатие
        def temp_handler(e):
            if self.waiting_for_key and e.name not in ('shift', 'ctrl', 'alt', 'windows'):
                self.waiting_for_key = False
                key_var.set(e.name)
                self.status_var.set(f"Клавиша '{e.name}' записана.")
                dialog.grab_set()
                keyboard.unhook(hook_id)
        hook_id = keyboard.on_press(temp_handler)
        # Установим таймаут, чтобы вернуть фокус через 10 секунд, если ничего не нажато
        def timeout():
            if self.waiting_for_key:
                self.waiting_for_key = False
                self.status_var.set("Запись клавиши отменена по таймауту.")
                dialog.grab_set()
                keyboard.unhook(hook_id)
        self.root.after(10000, timeout)

    def toggle_cycle(self):
        if self.running:
            self.stop_cycle()
        else:
            self.start_cycle()

    def start_cycle(self):
        if self.running:
            return
        if not self.actions:
            messagebox.showwarning("Нет действий", "Добавьте хотя бы одно действие.")
            return
        if self.target_hwnd is None:
            messagebox.showwarning("Не выбрано окно", "Выберите целевое окно.")
            return
        if not win32gui.IsWindow(self.target_hwnd):
            messagebox.showerror("Ошибка", "Выбранное окно больше не существует. Обновите список.")
            return

        powerlevel = self.powerlevel_var.get()
        if powerlevel == 1:
            try:
                init_exp = self.exp_initial_var.get()
                if init_exp <= 0:
                    messagebox.showerror("Ошибка", "Начальный опыт должен быть > 0")
                    return
                self.current_exp = init_exp
                self.update_exp_display()
            except tk.TclError:
                messagebox.showerror("Ошибка", "Некорректное значение опыта")
                return

        self.running = True
        toggle_key = self.hotkey_toggle_var.get().strip()
        self.start_stop_btn.config(text=f"Остановить цикл ({toggle_key.upper()})")
        self.status_var.set("Цикл запущен...")

        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop_cycle(self):
        self.running = False
        toggle_key = self.hotkey_toggle_var.get().strip()
        self.start_stop_btn.config(text=f"Запустить цикл ({toggle_key.upper()})")
        self.status_var.set("Цикл остановлен")
        self.eta_label.config(text="Осталось примерно: —")
        if self.progress_window:
            self.progress_window.eta_label.config(text="Осталось примерно: —")

    def _check_pixel_condition(self, condition_id):
        """Проверяет, совпадает ли текущий цвет пикселя с заданным условием."""
        if not condition_id:
            return True
        cond = self.pixel_conditions_dialog.get_condition_by_id(condition_id)
        if not cond:
            return True
        try:
            current_color = pyautogui.pixel(cond['x'], cond['y'])
        except:
            return False
        target = cond['color']
        tol = self.color_tolerance_var.get()
        return all(abs(current_color[i] - target[i]) <= tol for i in range(3))

    def _screen_to_client(self, hwnd, x, y):
        """Преобразует экранные координаты в клиентские для указанного окна."""
        pt = win32gui.Point(x, y)
        win32gui.ScreenToClient(hwnd, pt)
        return pt.x, pt.y

    def _send_click(self, x, y, hold_ms=0):
        """Отправляет клик/зажатие в фоновое окно с преобразованием координат."""
        if not win32gui.IsWindow(self.target_hwnd):
            return False
        client_x, client_y = self._screen_to_client(self.target_hwnd, x, y)
        lParam = (client_y << 16) | (client_x & 0xFFFF)
        try:
            win32gui.PostMessage(self.target_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            if hold_ms > 0:
                time.sleep(hold_ms / 1000.0)
            else:
                time.sleep(0.05)
            win32gui.PostMessage(self.target_hwnd, win32con.WM_LBUTTONUP, 0, lParam)
            return True
        except Exception as e:
            if "Отказано в доступе" in str(e) or "Access is denied" in str(e):
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка доступа",
                    "Не удалось отправить сообщение в целевое окно.\n"
                    "Попробуйте запустить программу от имени администратора."
                ))
                self.running = False
                return False
            else:
                raise

    def _send_key(self, key):
        """Отправляет нажатие клавиши в фоновое окно."""
        if not win32gui.IsWindow(self.target_hwnd):
            return False
        vk_code = self._key_to_vk(key)
        if vk_code is None:
            return False
        try:
            win32gui.PostMessage(self.target_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
            time.sleep(0.05)
            win32gui.PostMessage(self.target_hwnd, win32con.WM_KEYUP, vk_code, 0)
            return True
        except Exception as e:
            if "Отказано в доступе" in str(e) or "Access is denied" in str(e):
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка доступа",
                    "Не удалось отправить сообщение в целевое окно.\n"
                    "Попробуйте запустить программу от имени администратора."
                ))
                self.running = False
                return False
            else:
                raise

    def _key_to_vk(self, key):
        """Преобразует строковое представление клавиши в виртуальный код."""
        try:
            return ord(key.upper())
        except:
            pass
        special_keys = {
            'enter': win32con.VK_RETURN,
            'space': win32con.VK_SPACE,
            'tab': win32con.VK_TAB,
            'escape': win32con.VK_ESCAPE,
            'backspace': win32con.VK_BACK,
            'shift': win32con.VK_SHIFT,
            'ctrl': win32con.VK_CONTROL,
            'alt': win32con.VK_MENU,
            'f1': win32con.VK_F1, 'f2': win32con.VK_F2, 'f3': win32con.VK_F3, 'f4': win32con.VK_F4,
            'f5': win32con.VK_F5, 'f6': win32con.VK_F6, 'f7': win32con.VK_F7, 'f8': win32con.VK_F8,
            'f9': win32con.VK_F9, 'f10': win32con.VK_F10, 'f11': win32con.VK_F11, 'f12': win32con.VK_F12,
        }
        return special_keys.get(key.lower(), None)

    def _run_loop(self):
        powerlevel = self.powerlevel_var.get()
        actions = list(self.actions)

        while self.running:
            for action in actions:
                if not self.running:
                    break

                if not win32gui.IsWindow(self.target_hwnd):
                    self.root.after(0, lambda: self.status_var.set("Ошибка: целевое окно закрыто!"))
                    self.running = False
                    break

                # Индивидуальная задержка перед действием
                delay_ms = action.get('delay_ms', self.global_delay_ms_var.get())
                if delay_ms > 0:
                    waited = 0.0
                    while waited < delay_ms / 1000.0 and self.running:
                        time.sleep(0.01)
                        waited += 0.01
                    if not self.running:
                        break

                # Проверка условия для клика
                if action['type'] == 'click' and self.use_conditions_var.get():
                    cond_id = action.get('condition_id')
                    if cond_id and not self._check_pixel_condition(cond_id):
                        continue  # пропускаем действие, условие не выполнено

                if action['type'] == 'click':
                    hold_ms = action.get('hold_ms', 0)
                    success = self._send_click(action['x'], action['y'], hold_ms)
                    desc = f"Клик: ({action['x']}, {action['y']})" + (f" (удержание {hold_ms} мс)" if hold_ms else "")
                else:
                    success = self._send_key(action['key'])
                    desc = f"Клавиша: {action['key']}"

                if not self.running:
                    break

                if success:
                    self.root.after(0, lambda d=desc: self.status_var.set(d))
                else:
                    self.root.after(0, lambda: self.status_var.set("Ошибка отправки действия"))
                    if not self.running:
                        break

                if powerlevel == 1:
                    try:
                        deduction = self.exp_deduction_var.get()
                        multiplier = self.deduction_mult_var.get()
                        if multiplier < 0:
                            multiplier = 0
                        elif multiplier > 1:
                            multiplier = 1
                        actual_deduction = deduction * (1.0 - multiplier)
                    except tk.TclError:
                        actual_deduction = 0

                    self.current_exp -= actual_deduction
                    self.root.after(0, self.update_exp_display)

                    if self.current_exp <= 0:
                        self.running = False
                        self.root.after(0, self._show_completion_message)
                        break

        self.root.after(0, lambda: self.start_stop_btn.config(
            text=f"Запустить цикл ({self.hotkey_toggle_var.get().strip().upper()})"))
        self.root.after(0, lambda: self.status_var.set("Цикл завершён"))
        self.running = False

    def _show_completion_message(self):
        self.status_var.set("ПРОКАЧКА ЗАВЕРШЕНА. СМЕНИТЕ ИНСТРУМЕНТ")
        messagebox.showinfo("Прокачка завершена", "ПРОКАЧКА ЗАВЕРШЕНА. СМЕНИТЕ ИНСТРУМЕНТ")

    def _calculate_eta(self):
        if self.powerlevel_var.get() == 0 or not self.running:
            return "—"
        try:
            deduction = self.exp_deduction_var.get()
            multiplier = self.deduction_mult_var.get()
            if multiplier < 0:
                multiplier = 0
            elif multiplier > 1:
                multiplier = 1
            actual_deduction = deduction * (1.0 - multiplier)
            if actual_deduction <= 0:
                return "∞"
            actions_count = len(self.actions)
            if actions_count == 0:
                return "—"

            total_delay_ms = sum(act.get('delay_ms', self.global_delay_ms_var.get()) for act in self.actions)
            cycle_time_sec = total_delay_ms / 1000.0
            remaining_clicks = self.current_exp / actual_deduction
            total_seconds = remaining_clicks * cycle_time_sec

            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            if minutes > 0:
                return f"{minutes} мин {seconds} сек"
            else:
                return f"{seconds} сек"
        except:
            return "—"

    def update_exp_display(self):
        try:
            init = self.exp_initial_var.get()
        except tk.TclError:
            init = 0
        current = self.current_exp
        percent = (current / init * 100) if init > 0 else 0
        self.exp_label.config(text=f"Опыт: {current:.2f} / {init:.2f} ({percent:.1f}%)")
        self.progress['value'] = percent

        eta_text = self._calculate_eta()
        self.eta_label.config(text=f"Осталось примерно: {eta_text}")

        if self.progress_window and self.show_progress_window_var.get():
            self.progress_window.update(current, init, percent, eta_text)

    def save_profile(self):
        """Сохранение текущего профиля в JSON."""
        if not self.actions:
            messagebox.showwarning("Нет действий", "Нечего сохранять.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить профиль"
        )
        if not filename:
            return

        actions_serializable = []
        for act in self.actions:
            act_copy = act.copy()
            act_copy.pop('tree_iid', None)
            actions_serializable.append(act_copy)

        profile = {
            'target_title': self.target_title,
            'global_delay_ms': self.global_delay_ms_var.get(),
            'actions': actions_serializable,
            'hotkeys': {
                'record_click': self.hotkey_record_click_var.get(),
                'record_key': self.hotkey_record_key_var.get(),
                'toggle': self.hotkey_toggle_var.get(),
                'pick_color': self.hotkey_pick_color_var.get(),
            },
            'pixel_conditions': self.pixel_conditions_dialog.conditions,
            'color_tolerance': self.color_tolerance_var.get(),
            'use_conditions': self.use_conditions_var.get(),
        }
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            self.status_var.set(f"Профиль сохранён: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def load_profile(self):
        """Загрузка профиля из JSON."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить профиль"
        )
        if not filename:
            return
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                profile = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
            return

        self.target_title = profile.get('target_title', '')
        if self.target_title:
            windows = gw.getWindowsWithTitle(self.target_title)
            if windows:
                self.target_hwnd = windows[0]._hWnd
                self.selected_window_label.config(text=f"Выбрано: {self.target_title} (HWND: {self.target_hwnd})")
                if self.target_title in self.window_combobox['values']:
                    self.window_combobox.set(self.target_title)
                else:
                    self.window_combobox.set('')
            else:
                self.target_hwnd = None
                self.selected_window_label.config(text=f"Окно '{self.target_title}' не найдено")
                self.window_combobox.set('')
        else:
            self.target_hwnd = None
            self.selected_window_label.config(text="Окно не выбрано")

        self.global_delay_ms_var.set(profile.get('global_delay_ms', 1000))

        hk = profile.get('hotkeys', {})
        self.hotkey_record_click_var.set(hk.get('record_click', 'f2'))
        self.hotkey_record_key_var.set(hk.get('record_key', 'f3'))
        self.hotkey_toggle_var.set(hk.get('toggle', 'f1'))
        self.hotkey_pick_color_var.set(hk.get('pick_color', 'f4'))
        self.apply_settings()

        self.pixel_conditions_dialog.conditions = profile.get('pixel_conditions', [])
        self.pixel_conditions_dialog.refresh_list()
        self.color_tolerance_var.set(profile.get('color_tolerance', 10))
        self.use_conditions_var.set(profile.get('use_conditions', True))

        self.clear_actions()
        for act in profile.get('actions', []):
            if 'delay_ms' not in act:
                act['delay_ms'] = self.global_delay_ms_var.get()
            if act['type'] == 'click' and 'hold_ms' not in act:
                act['hold_ms'] = 0
            if 'condition_id' not in act:
                act['condition_id'] = None
            self.actions.append(act)
            self._add_action_to_tree(act)

        self.status_var.set(f"Профиль загружен: {os.path.basename(filename)}")

    def run_tray(self):
        self.tray_icon.run()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClickerApp(root)
    threading.Thread(target=app.run_tray, daemon=True).start()
    root.mainloop()