import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import base64
import json
import os
import cv2
import numpy as np
import pyautogui
import keyboard
from PIL import Image, ImageDraw
import pystray

# ---------- Языковые ресурсы ----------
LANGUAGES = {
    'ru': {
        'title': 'Clixpert S',
        'mode': 'Режим',
        'infinite': 'Бесконечный цикл',
        'limited': 'С ограничением',
        'limit_params': 'Параметры ограничения',
        'initial_count': 'Начальное кол-во:',
        'default_deduction': 'Вычет по умолчанию:',
        'deduction_mult': 'Множитель вычета (0..1):',
        'deduction_hint': '(вычитается: Вычет × (1 - Множитель))',
        'show_progress_window': 'Показывать отдельное окно прогресса',
        'progress': 'Прогресс',
        'progress_label': 'Прогресс: {:.2f} / {:.2f} ({:.1f}%)',
        'eta_label': 'Осталось примерно: {}',
        'actions': 'Последовательность действий',
        'clear': 'Очистить',
        'delete': 'Удалить',
        'edit': 'Редактировать',
        'add_delay': '+ Задержка',
        'save_profile': 'Сохранить профиль',
        'load_profile': 'Загрузить профиль',
        'conditions': 'Условия',
        'settings': 'Настройки',
        'global_delay': 'Глоб. задержка (мс):',
        'record_click': 'Клавиша записи клика:',
        'record_key': 'Клавиша записи клавиши:',
        'toggle': 'Клавиша запуска/остановки:',
        'always_on_top': 'Окно всегда сверху',
        'color_tolerance': 'Допуск цвета (0-50):',
        'use_conditions': 'Применять условия (если заданы)',
        'apply_settings': 'Применить настройки',
        'start': 'Запустить',
        'stop': 'Остановить',
        'tray': 'Свернуть в трей',
        'exit': 'Выход',
        'waiting': 'Ожидание',
        'cycle_running': 'Цикл запущен...',
        'cycle_stopped': 'Цикл остановлен',
        'cycle_finished': 'Цикл завершён',
        'completion_title': 'Цикл успешно завершен',
        'completion_message': 'УСПЕШНОЕ ЗАВЕРШЕНИЕ',
        'no_actions': 'Добавьте хотя бы одно действие.',
        'error': 'Ошибка',
        'invalid_delay': 'Глобальная задержка должна быть неотрицательным целым числом (мс)',
        'cannot_edit_running': 'Нельзя редактировать во время работы цикла!',
        'select_image': 'Выберите изображение',
        'confidence': 'Порог совпадения (0.5-1.0):',
        'click': 'Клик',
        'key': 'Клавиша',
        'delay': 'Пауза',
        'params': 'Параметры',
        'delay_ms': 'Задержка (мс)',
        'hold_ms': 'Удержание (мс)',
        'condition': 'Условие',
        'contrib': 'Вклад',
        'edit_action': 'Редактировать действие',
        'save': 'Сохранить',
        'cancel': 'Отмена',
        'language': 'Язык',
        'hotkeys_hint': '{}: клик | {}: клавиша | {}: старт/стоп',
        'condition_type': 'Тип условия',
        'none': 'Нет',
        'pixel': 'Пиксель',
        'color_area': 'Цвет в области',
        'image_search': 'Поиск изображения',
        'search_area': 'Область поиска',
        'x1': 'X1:', 'y1': 'Y1:', 'x2': 'X2:', 'y2': 'Y2:',
        'target_color': 'Целевой цвет (RGB)',
        'pick_color': 'Взять цвет',
        'select_image_file': 'Выбрать файл',
        'skip_on_true': 'Пропустить остальные, если условие выполнено',
        'skip_on_false': 'Пропустить остальные, если условие НЕ выполнено',
        'progress_contrib': 'Вклад в прогресс (пусто = стандартный)',
        'wait_condition': 'Ждать выполнения условия (иначе пропустить действие)',
    },
    'en': {
        'title': 'Clixpert S',
        'mode': 'Mode',
        'infinite': 'Infinite loop',
        'limited': 'Limited',
        'limit_params': 'Limit parameters',
        'initial_count': 'Initial count:',
        'default_deduction': 'Default deduction:',
        'deduction_mult': 'Deduction multiplier (0..1):',
        'deduction_hint': '(subtracted: Deduction × (1 - Multiplier))',
        'show_progress_window': 'Show separate progress window',
        'progress': 'Progress',
        'progress_label': 'Progress: {:.2f} / {:.2f} ({:.1f}%)',
        'eta_label': 'Estimated time left: {}',
        'actions': 'Action sequence',
        'clear': 'Clear',
        'delete': 'Delete',
        'edit': 'Edit',
        'add_delay': '+ Delay',
        'save_profile': 'Save profile',
        'load_profile': 'Load profile',
        'conditions': 'Conditions',
        'settings': 'Settings',
        'global_delay': 'Global delay (ms):',
        'record_click': 'Record click hotkey:',
        'record_key': 'Record key hotkey:',
        'toggle': 'Start/stop hotkey:',
        'always_on_top': 'Always on top',
        'color_tolerance': 'Color tolerance (0-50):',
        'use_conditions': 'Apply conditions (if set)',
        'apply_settings': 'Apply settings',
        'start': 'Start',
        'stop': 'Stop',
        'tray': 'Minimize to tray',
        'exit': 'Exit',
        'waiting': 'Waiting',
        'cycle_running': 'Cycle running...',
        'cycle_stopped': 'Cycle stopped',
        'cycle_finished': 'Cycle finished',
        'completion_title': 'Cycle completed',
        'completion_message': 'SUCCESSFUL COMPLETION',
        'no_actions': 'Add at least one action.',
        'error': 'Error',
        'invalid_delay': 'Global delay must be a non-negative integer (ms)',
        'cannot_edit_running': 'Cannot edit while cycle is running!',
        'select_image': 'Select image',
        'confidence': 'Confidence threshold (0.5-1.0):',
        'click': 'Click',
        'key': 'Key',
        'delay': 'Delay',
        'params': 'Parameters',
        'delay_ms': 'Delay (ms)',
        'hold_ms': 'Hold (ms)',
        'condition': 'Condition',
        'contrib': 'Contrib',
        'edit_action': 'Edit action',
        'save': 'Save',
        'cancel': 'Cancel',
        'language': 'Language',
        'hotkeys_hint': '{}: click | {}: key | {}: start/stop',
        'condition_type': 'Condition type',
        'none': 'None',
        'pixel': 'Pixel',
        'color_area': 'Color in area',
        'image_search': 'Image search',
        'search_area': 'Search area',
        'x1': 'X1:', 'y1': 'Y1:', 'x2': 'X2:', 'y2': 'Y2:',
        'target_color': 'Target color (RGB)',
        'pick_color': 'Pick color',
        'select_image_file': 'Select file',
        'skip_on_true': 'Skip rest if condition met',
        'skip_on_false': 'Skip rest if condition NOT met',
        'progress_contrib': 'Contrib (empty=default)',
        'wait_condition': 'Wait for condition (otherwise skip action)',
    }
}


class ProgressWindow:
    """Отдельное окно с прогресс-баром."""
    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        self.create_window()

    def create_window(self):
        if self.window is not None:
            return
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Progress")
        self.window.geometry("300x120")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.configure(bg='#1e1e2f')
        self.window.attributes('-alpha', 0.92)

        self.window.bind('<Button-1>', self.start_move)
        self.window.bind('<B1-Motion>', self.on_move)

        frame = tk.Frame(self.window, bg='#1e1e2f', padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.label = tk.Label(frame, text="Progress: 0.00 / 0.00 (0%)",
                              fg='white', bg='#1e1e2f', font=('Segoe UI', 10, 'bold'))
        self.label.pack(pady=(0, 5))

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=20, troughcolor='#2a2a3c', background='#5a9cff')
        self.progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=280, mode='determinate')
        self.progress.pack(pady=5)

        self.eta_label = tk.Label(frame, text="Estimated time left: —",
                                  fg='#cccccc', bg='#1e1e2f', font=('Segoe UI', 9))
        self.eta_label.pack(pady=(2, 0))

        btn_frame = tk.Frame(frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Button(btn_frame, text="Hide", command=self.hide, bg='#3a3a5c', fg='white',
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
        lang = self.app.lang
        self.label.config(text=LANGUAGES[lang]['progress_label'].format(current, total, percent))
        self.progress['value'] = percent
        self.eta_label.config(text=LANGUAGES[lang]['eta_label'].format(eta_text))

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
    """Окно управления пиксельными условиями (для типа 'pixel')."""
    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        self.conditions = []  # список {'id': str, 'x': int, 'y': int, 'color': (r,g,b)}
        self.create_window()

    def create_window(self):
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Pixel conditions")
        self.window.geometry("650x450")
        self.window.configure(bg='#1e1e2f')
        self.window.attributes('-alpha', 0.96)
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

        frame = tk.Frame(self.window, bg='#1e1e2f', padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'pos', 'color')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)
        self.tree.heading('id', text='ID')
        self.tree.heading('pos', text='Coordinates')
        self.tree.heading('color', text='Color (RGB)')
        self.tree.column('id', width=120)
        self.tree.column('pos', width=150)
        self.tree.column('color', width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tree.bind('<Double-1>', self.edit_selected)

        btn_frame = tk.Frame(frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="Add", command=self.add_condition, bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_selected, bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear all", command=self.clear_all, bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=5)

        tk.Label(frame, text="Color tolerance (0-50):", fg='white', bg='#1e1e2f').pack(anchor=tk.W, pady=(10,0))
        self.tolerance_var = tk.IntVar(value=self.app.color_tolerance_var.get())
        tk.Scale(frame, from_=0, to=50, variable=self.tolerance_var, orient=tk.HORIZONTAL,
                 bg='#1e1e2f', fg='white', troughcolor='#2a2a3c', highlightbackground='#1e1e2f',
                 command=lambda v: self.app.color_tolerance_var.set(int(float(v)))).pack(fill=tk.X)
        tk.Label(frame, textvariable=self.tolerance_var, fg='white', bg='#1e1e2f').pack()

        tk.Button(frame, text="Close", command=self.hide, bg='#3a3a5c', fg='white', bd=0).pack(pady=10)

        self.refresh_list()

    def add_condition(self, edit_item=None, existing_id=None):
        dialog = tk.Toplevel(self.window)
        dialog.title("Edit condition" if edit_item else "New condition")
        dialog.geometry("350x350")
        dialog.configure(bg='#1e1e2f')
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(dialog, text="ID:", fg='white', bg='#1e1e2f').pack(pady=5)
        id_var = tk.StringVar(value=existing_id if existing_id else "")
        tk.Entry(dialog, textvariable=id_var, bg='#2a2a3c', fg='white', insertbackground='white').pack()

        coord_frame = tk.Frame(dialog, bg='#1e1e2f')
        coord_frame.pack(pady=5)
        tk.Label(coord_frame, text="X:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
        x_var = tk.IntVar(value=0)
        tk.Entry(coord_frame, textvariable=x_var, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Label(coord_frame, text="Y:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
        y_var = tk.IntVar(value=0)
        tk.Entry(coord_frame, textvariable=y_var, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        tk.Button(dialog, text="Pick coords", command=lambda: self._pick_coords(x_var, y_var), bg='#3a3a5c', fg='white').pack(pady=5)

        color_frame = tk.Frame(dialog, width=50, height=50, bg='gray')
        color_frame.pack(pady=5)
        color_frame.pack_propagate(False)

        color_label = tk.Label(dialog, text="Color: ???", fg='white', bg='#1e1e2f')
        color_label.pack(pady=5)

        rgb_frame = tk.Frame(dialog, bg='#1e1e2f')
        rgb_frame.pack(pady=5)
        tk.Label(rgb_frame, text="R:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
        r_var = tk.IntVar(value=0)
        tk.Entry(rgb_frame, textvariable=r_var, width=4, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Label(rgb_frame, text="G:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
        g_var = tk.IntVar(value=0)
        tk.Entry(rgb_frame, textvariable=g_var, width=4, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Label(rgb_frame, text="B:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
        b_var = tk.IntVar(value=0)
        tk.Entry(rgb_frame, textvariable=b_var, width=4, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=2)

        def update_display():
            r, g, b = r_var.get(), g_var.get(), b_var.get()
            hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            color_frame.config(bg=hex_color)
            color_label.config(text=f"Color: ({r}, {g}, {b})")

        tk.Button(dialog, text="Apply RGB", command=update_display, bg='#3a3a5c', fg='white').pack(pady=5)
        tk.Button(dialog, text="Pick color", command=lambda: self._pick_color(x_var.get(), y_var.get(), r_var, g_var, b_var, color_frame, color_label), bg='#3a3a5c', fg='white').pack(pady=5)

        if edit_item:
            cond = self._get_condition_by_item(edit_item)
            if cond:
                x_var.set(cond['x'])
                y_var.set(cond['y'])
                r_var.set(cond['color'][0])
                g_var.set(cond['color'][1])
                b_var.set(cond['color'][2])
                update_display()

        def save():
            cond_id = id_var.get().strip()
            if not cond_id:
                messagebox.showerror("Error", "Enter ID")
                return
            if not edit_item and any(c['id'] == cond_id for c in self.conditions):
                messagebox.showerror("Error", "ID already exists")
                return
            color = (r_var.get(), g_var.get(), b_var.get())
            new_cond = {'id': cond_id, 'x': x_var.get(), 'y': y_var.get(), 'color': color}
            if edit_item:
                for i, c in enumerate(self.conditions):
                    if c['id'] == existing_id:
                        self.conditions[i] = new_cond
                        break
            else:
                self.conditions.append(new_cond)
            self.refresh_list()
            dialog.destroy()

        tk.Button(dialog, text="Save", command=save, bg='#3a3a5c', fg='white').pack(pady=10)

    def _pick_coords(self, x_var, y_var):
        top = tk.Toplevel(self.window)
        top.title("Pick coords")
        top.geometry("250x100")
        tk.Label(top, text="Move mouse and press SPACE").pack(pady=10)
        top.focus_set()
        def on_space(e):
            if e.name == 'space':
                x, y = pyautogui.position()
                x_var.set(x)
                y_var.set(y)
                top.destroy()
                keyboard.unhook(hook)
        hook = keyboard.on_press(on_space)
        top.protocol("WM_DELETE_WINDOW", lambda: (keyboard.unhook(hook), top.destroy()))

    def _pick_color(self, x, y, r_var, g_var, b_var, color_frame, color_label):
        try:
            color = pyautogui.pixel(x, y)
            r_var.set(color[0])
            g_var.set(color[1])
            b_var.set(color[2])
            hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
            color_frame.config(bg=hex_color)
            color_label.config(text=f"Color: ({color[0]}, {color[1]}, {color[2]})")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get color: {e}")

    def _get_condition_by_item(self, item):
        values = self.tree.item(item)['values']
        if not values:
            return None
        cond_id = values[0]
        for c in self.conditions:
            if c['id'] == cond_id:
                return c
        return None

    def edit_selected(self, event):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            cond = self._get_condition_by_item(item)
            if cond:
                self.add_condition(edit_item=item, existing_id=cond['id'])

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
        self.lang = 'ru'
        self.root.title(LANGUAGES[self.lang]['title'])
        self.root.geometry("920x880")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a2e')
        self.root.attributes('-alpha', 0.96)

        self.running = False
        self.thread = None
        self.actions = []          # список действий
        self.image_cache = {}      # base64 -> np.array для поиска изображений

        # Переменные режима
        self.mode_var = tk.IntVar(value=0)
        self.initial_count_var = tk.DoubleVar(value=100.0)
        self.deduction_var = tk.DoubleVar(value=10.0)
        self.deduction_mult_var = tk.DoubleVar(value=0.33)
        self.current_count = self.initial_count_var.get()

        self.global_delay_ms_var = tk.IntVar(value=1000)

        self.hotkey_record_click_var = tk.StringVar(value='f2')
        self.hotkey_record_key_var = tk.StringVar(value='f3')
        self.hotkey_toggle_var = tk.StringVar(value='f1')

        self.always_on_top_var = tk.BooleanVar(value=False)
        self.show_progress_window_var = tk.BooleanVar(value=False)
        self.color_tolerance_var = tk.IntVar(value=10)
        self.use_conditions_var = tk.BooleanVar(value=True)

        self.pixel_conditions_dialog = PixelConditionDialog(self)
        self.waiting_for_key = False
        self.temp_key_hook = None
        self.progress_window = None
        self.tray_icon = None

        self.create_tray_icon()
        self.create_widgets()
        self.root.after(100, self.init_progress_window)

        self.update_count_display()
        self.register_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.update_always_on_top()

    # ---------- UI Creation ----------
    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg='#1a1a2e', padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Верхняя панель с языком
        top_bar = tk.Frame(self.main_frame, bg='#1a1a2e')
        top_bar.pack(fill=tk.X, pady=(0,5))
        self.lang_btn = tk.Button(top_bar, text="EN", command=self.toggle_language,
                                  bg='#3a3a5c', fg='white', bd=0, width=3)
        self.lang_btn.pack(side=tk.RIGHT)

        # Режим
        self.mode_frame = tk.LabelFrame(self.main_frame, text=LANGUAGES[self.lang]['mode'],
                                        bg='#1e1e2f', fg='white', padx=5, pady=5)
        self.mode_frame.pack(fill=tk.X, pady=5)
        tk.Radiobutton(self.mode_frame, text=LANGUAGES[self.lang]['infinite'],
                       variable=self.mode_var, value=0, bg='#1e1e2f', fg='white',
                       selectcolor='#1e1e2f', activebackground='#1e1e2f').pack(anchor=tk.W)
        tk.Radiobutton(self.mode_frame, text=LANGUAGES[self.lang]['limited'],
                       variable=self.mode_var, value=1, bg='#1e1e2f', fg='white',
                       selectcolor='#1e1e2f', activebackground='#1e1e2f').pack(anchor=tk.W)

        # Параметры ограничения
        self.limit_frame = tk.LabelFrame(self.main_frame, text=LANGUAGES[self.lang]['limit_params'],
                                         bg='#1e1e2f', fg='white', padx=5, pady=5)
        self.limit_frame.pack(fill=tk.X, pady=5)

        tk.Label(self.limit_frame, text=LANGUAGES[self.lang]['initial_count'],
                 bg='#1e1e2f', fg='white').grid(row=0, column=0, sticky=tk.W, pady=2)
        tk.Entry(self.limit_frame, textvariable=self.initial_count_var, width=10,
                 bg='#2a2a3c', fg='white', insertbackground='white').grid(row=0, column=1, sticky=tk.W, padx=5)

        tk.Label(self.limit_frame, text=LANGUAGES[self.lang]['default_deduction'],
                 bg='#1e1e2f', fg='white').grid(row=1, column=0, sticky=tk.W, pady=2)
        tk.Entry(self.limit_frame, textvariable=self.deduction_var, width=10,
                 bg='#2a2a3c', fg='white', insertbackground='white').grid(row=1, column=1, sticky=tk.W, padx=5)

        tk.Label(self.limit_frame, text=LANGUAGES[self.lang]['deduction_mult'],
                 bg='#1e1e2f', fg='white').grid(row=2, column=0, sticky=tk.W, pady=2)
        tk.Entry(self.limit_frame, textvariable=self.deduction_mult_var, width=10,
                 bg='#2a2a3c', fg='white', insertbackground='white').grid(row=2, column=1, sticky=tk.W, padx=5)
        tk.Label(self.limit_frame, text=LANGUAGES[self.lang]['deduction_hint'],
                 bg='#1e1e2f', fg='#aaaaaa').grid(row=2, column=2, sticky=tk.W, padx=5)

        tk.Checkbutton(self.limit_frame, text=LANGUAGES[self.lang]['show_progress_window'],
                       variable=self.show_progress_window_var, command=self.toggle_progress_window,
                       bg='#1e1e2f', fg='white', selectcolor='#1e1e2f', activebackground='#1e1e2f'
                       ).grid(row=3, column=0, columnspan=3, pady=5, sticky=tk.W)

        # Прогресс
        self.progress_frame = tk.LabelFrame(self.main_frame, text=LANGUAGES[self.lang]['progress'],
                                            bg='#1e1e2f', fg='white', padx=5, pady=5)
        self.progress_frame.pack(fill=tk.X, pady=5)

        self.count_label = tk.Label(self.progress_frame,
                                    text=LANGUAGES[self.lang]['progress_label'].format(0.0, 0.0, 0.0),
                                    bg='#1e1e2f', fg='white')
        self.count_label.pack(anchor=tk.W)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=20, troughcolor='#2a2a3c', background='#5a9cff')
        self.progress = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        self.eta_label = tk.Label(self.progress_frame,
                                  text=LANGUAGES[self.lang]['eta_label'].format('—'),
                                  bg='#1e1e2f', fg='#cccccc')
        self.eta_label.pack(anchor=tk.W, pady=(2,0))

        # Последовательность действий
        self.actions_frame = tk.LabelFrame(self.main_frame, text=LANGUAGES[self.lang]['actions'],
                                           bg='#1e1e2f', fg='white', padx=5, pady=5)
        self.actions_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ('type', 'params', 'delay', 'hold', 'cond', 'contrib')
        self.actions_tree = ttk.Treeview(self.actions_frame, columns=columns, show='headings', height=6)
        self.actions_tree.heading('type', text='Type')
        self.actions_tree.heading('params', text='Params')
        self.actions_tree.heading('delay', text='Delay (ms)')
        self.actions_tree.heading('hold', text='Hold (ms)')
        self.actions_tree.heading('cond', text='Cond')
        self.actions_tree.heading('contrib', text='Contrib')
        self.actions_tree.column('type', width=70, anchor='center')
        self.actions_tree.column('params', width=180)
        self.actions_tree.column('delay', width=80, anchor='center')
        self.actions_tree.column('hold', width=80, anchor='center')
        self.actions_tree.column('cond', width=80, anchor='center')
        self.actions_tree.column('contrib', width=60, anchor='center')
        self.actions_tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.actions_frame, orient=tk.VERTICAL, command=self.actions_tree.yview)
        self.actions_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.actions_tree.bind('<Double-1>', self.edit_action_double_click)

        btn_frame = tk.Frame(self.actions_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text=LANGUAGES[self.lang]['clear'], command=self.clear_actions,
                  bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text=LANGUAGES[self.lang]['delete'], command=self.remove_selected_action,
                  bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text=LANGUAGES[self.lang]['edit'], command=self.edit_selected_action,
                  bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text=LANGUAGES[self.lang]['add_delay'], command=self.add_delay_action,
                  bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text=LANGUAGES[self.lang]['save_profile'], command=self.save_profile,
                  bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text=LANGUAGES[self.lang]['load_profile'], command=self.load_profile,
                  bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text=LANGUAGES[self.lang]['conditions'], command=self.pixel_conditions_dialog.show,
                  bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=2)

        hotkeys_text = LANGUAGES[self.lang]['hotkeys_hint'].format(
            self.hotkey_record_click_var.get().upper(),
            self.hotkey_record_key_var.get().upper(),
            self.hotkey_toggle_var.get().upper()
        )
        tk.Label(self.actions_frame, text=hotkeys_text, bg='#1e1e2f', fg='#aaaaaa').pack(pady=2)

        # Настройки
        self.settings_frame = tk.LabelFrame(self.main_frame, text=LANGUAGES[self.lang]['settings'],
                                            bg='#1e1e2f', fg='white', padx=5, pady=5)
        self.settings_frame.pack(fill=tk.X, pady=5)

        tk.Label(self.settings_frame, text=LANGUAGES[self.lang]['global_delay'],
                 bg='#1e1e2f', fg='white').grid(row=0, column=0, sticky=tk.W, pady=2)
        tk.Entry(self.settings_frame, textvariable=self.global_delay_ms_var, width=10,
                 bg='#2a2a3c', fg='white', insertbackground='white').grid(row=0, column=1, sticky=tk.W, padx=5)

        tk.Label(self.settings_frame, text=LANGUAGES[self.lang]['record_click'],
                 bg='#1e1e2f', fg='white').grid(row=1, column=0, sticky=tk.W, pady=2)
        tk.Entry(self.settings_frame, textvariable=self.hotkey_record_click_var, width=10,
                 bg='#2a2a3c', fg='white', insertbackground='white').grid(row=1, column=1, sticky=tk.W, padx=5)

        tk.Label(self.settings_frame, text=LANGUAGES[self.lang]['record_key'],
                 bg='#1e1e2f', fg='white').grid(row=2, column=0, sticky=tk.W, pady=2)
        tk.Entry(self.settings_frame, textvariable=self.hotkey_record_key_var, width=10,
                 bg='#2a2a3c', fg='white', insertbackground='white').grid(row=2, column=1, sticky=tk.W, padx=5)

        tk.Label(self.settings_frame, text=LANGUAGES[self.lang]['toggle'],
                 bg='#1e1e2f', fg='white').grid(row=3, column=0, sticky=tk.W, pady=2)
        tk.Entry(self.settings_frame, textvariable=self.hotkey_toggle_var, width=10,
                 bg='#2a2a3c', fg='white', insertbackground='white').grid(row=3, column=1, sticky=tk.W, padx=5)

        tk.Checkbutton(self.settings_frame, text=LANGUAGES[self.lang]['always_on_top'],
                       variable=self.always_on_top_var, command=self.update_always_on_top,
                       bg='#1e1e2f', fg='white', selectcolor='#1e1e2f', activebackground='#1e1e2f'
                       ).grid(row=4, column=0, columnspan=2, pady=5)

        tk.Label(self.settings_frame, text=LANGUAGES[self.lang]['color_tolerance'],
                 bg='#1e1e2f', fg='white').grid(row=5, column=0, sticky=tk.W, pady=2)
        tk.Entry(self.settings_frame, textvariable=self.color_tolerance_var, width=10,
                 bg='#2a2a3c', fg='white', insertbackground='white').grid(row=5, column=1, sticky=tk.W, padx=5)

        tk.Checkbutton(self.settings_frame, text=LANGUAGES[self.lang]['use_conditions'],
                       variable=self.use_conditions_var,
                       bg='#1e1e2f', fg='white', selectcolor='#1e1e2f', activebackground='#1e1e2f'
                       ).grid(row=6, column=0, columnspan=2, pady=5)

        tk.Button(self.settings_frame, text=LANGUAGES[self.lang]['apply_settings'],
                  command=self.apply_settings, bg='#3a3a5c', fg='white', bd=0
                  ).grid(row=7, column=0, columnspan=2, pady=10)

        # Управление
        control_frame = tk.Frame(self.main_frame, bg='#1a1a2e')
        control_frame.pack(fill=tk.X, pady=10)

        self.start_stop_btn = tk.Button(control_frame,
                                        text=LANGUAGES[self.lang]['start'] + " (F1)",
                                        command=self.toggle_cycle,
                                        bg='#5a9cff', fg='white', bd=0, padx=10)
        self.start_stop_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text=LANGUAGES[self.lang]['tray'], command=self.hide_window,
                  bg='#3a3a5c', fg='white', bd=0).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text=LANGUAGES[self.lang]['exit'], command=self.quit_app,
                  bg='#3a3a5c', fg='white', bd=0).pack(side=tk.RIGHT, padx=5)

        self.status_var = tk.StringVar(value=LANGUAGES[self.lang]['waiting'])
        tk.Label(self.main_frame, textvariable=self.status_var, bg='#1a1a2e', fg='#aaaaaa').pack(fill=tk.X, pady=5)

    def toggle_language(self):
        self.lang = 'en' if self.lang == 'ru' else 'ru'
        self.lang_btn.config(text="RU" if self.lang == 'en' else "EN")
        self._refresh_ui_texts()

    def _refresh_ui_texts(self):
        self.root.title(LANGUAGES[self.lang]['title'])
        self.mode_frame.config(text=LANGUAGES[self.lang]['mode'])
        for child in self.mode_frame.winfo_children():
            if isinstance(child, tk.Radiobutton):
                child.config(text=LANGUAGES[self.lang]['infinite'] if child['value']==0 else LANGUAGES[self.lang]['limited'])
        self.limit_frame.config(text=LANGUAGES[self.lang]['limit_params'])
        self.progress_frame.config(text=LANGUAGES[self.lang]['progress'])
        self.actions_frame.config(text=LANGUAGES[self.lang]['actions'])
        self.settings_frame.config(text=LANGUAGES[self.lang]['settings'])
        self.start_stop_btn.config(text=(LANGUAGES[self.lang]['stop'] if self.running else LANGUAGES[self.lang]['start']) + f" ({self.hotkey_toggle_var.get().upper()})")
        self.status_var.set(LANGUAGES[self.lang]['cycle_running'] if self.running else LANGUAGES[self.lang]['waiting'])
        self.update_count_display()

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
        image = Image.new('RGB', (64,64), color='gray')
        draw = ImageDraw.Draw(image)
        draw.rectangle((16,16,48,48), fill='blue')
        draw.text((20,20), "CS", fill='white')
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window, default=True),
            pystray.MenuItem("Exit", self.quit_app)
        )
        self.tray_icon = pystray.Icon("clixpert", image, "Clixpert S", menu)

    def show_window(self, *_):
        self.root.after(0, self.root.deiconify)

    def hide_window(self, *_):
        self.root.withdraw()
        if self.tray_icon:
            self.tray_icon.notify("Clixpert S minimized to tray.\nHotkeys active.", "Clixpert S")

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

    # ---------- Hotkeys & Recording ----------
    def register_hotkeys(self):
        keyboard.unhook_all()
        if self.hotkey_record_click_var.get():
            keyboard.add_hotkey(self.hotkey_record_click_var.get().strip(), self.record_click_action)
        if self.hotkey_record_key_var.get():
            keyboard.add_hotkey(self.hotkey_record_key_var.get().strip(), self.start_key_recording)
        if self.hotkey_toggle_var.get():
            keyboard.add_hotkey(self.hotkey_toggle_var.get().strip(), self.toggle_cycle)

    def apply_settings(self):
        try:
            if self.global_delay_ms_var.get() < 0:
                raise ValueError
        except:
            messagebox.showerror(LANGUAGES[self.lang]['error'], LANGUAGES[self.lang]['invalid_delay'])
            return
        self.register_hotkeys()
        self.start_stop_btn.config(text=(LANGUAGES[self.lang]['stop'] if self.running else LANGUAGES[self.lang]['start']) + f" ({self.hotkey_toggle_var.get().upper()})")
        self.status_var.set(LANGUAGES[self.lang]['waiting'])

    def record_click_action(self):
        if self.running:
            self.status_var.set(LANGUAGES[self.lang]['cannot_edit_running'])
            return
        x, y = pyautogui.position()
        action = {
            'type': 'click',
            'x': x, 'y': y,
            'delay_ms': self.global_delay_ms_var.get(),
            'hold_ms': 0,
            'condition': None,
            'wait_condition': False,
            'skip_on_true': False,
            'skip_on_false': False,
            'progress_contrib': None
        }
        self.actions.append(action)
        self._add_action_to_tree(action)
        self.status_var.set(f"Click added: ({x}, {y})")

    def start_key_recording(self):
        if self.running:
            self.status_var.set(LANGUAGES[self.lang]['cannot_edit_running'])
            return
        self.status_var.set("Press a key...")
        self.waiting_for_key = True
        def handler(e):
            if self.waiting_for_key and e.name not in ('shift','ctrl','alt','windows','right shift','right ctrl','right alt'):
                self.waiting_for_key = False
                keyboard.unhook(self.temp_key_hook)
                self.root.after(0, lambda: self._add_key_action(e.name))
        self.temp_key_hook = keyboard.on_press(handler)
        self.root.after(10000, self._cancel_key_recording)

    def _cancel_key_recording(self):
        if self.waiting_for_key:
            self.waiting_for_key = False
            keyboard.unhook(self.temp_key_hook)
            self.status_var.set("Key recording cancelled")

    def _add_key_action(self, key_name):
        action = {
            'type': 'key',
            'key': key_name,
            'delay_ms': self.global_delay_ms_var.get(),
            'hold_ms': 0,
            'condition': None,
            'wait_condition': False,
            'skip_on_true': False,
            'skip_on_false': False,
            'progress_contrib': None
        }
        self.actions.append(action)
        self._add_action_to_tree(action)
        self.status_var.set(f"Key added: {key_name}")

    def add_delay_action(self):
        if self.running:
            self.status_var.set(LANGUAGES[self.lang]['cannot_edit_running'])
            return
        d = tk.Toplevel(self.root)
        d.title("Add delay")
        d.geometry("250x120")
        d.configure(bg='#1e1e2f')
        d.transient(self.root)
        d.grab_set()
        tk.Label(d, text="Delay (ms):", fg='white', bg='#1e1e2f').pack(pady=10)
        v = tk.IntVar(value=1000)
        tk.Entry(d, textvariable=v, width=15, bg='#2a2a3c', fg='white').pack()
        def save():
            action = {'type': 'delay', 'delay_ms': v.get(), 'progress_contrib': None}
            self.actions.append(action)
            self._add_action_to_tree(action)
            d.destroy()
        tk.Button(d, text="Add", command=save, bg='#3a3a5c', fg='white').pack(pady=10)

    def _add_action_to_tree(self, action):
        if action['type'] == 'click':
            params = f"X={action['x']}, Y={action['y']}"
            hold = str(action.get('hold_ms', 0))
            cond = action['condition']['type'] if action.get('condition') else '—'
        elif action['type'] == 'key':
            params = f"Key: {action['key']}"
            hold = '—'
            cond = action['condition']['type'] if action.get('condition') else '—'
        else:  # delay
            params = "Pause"
            hold = '—'
            cond = '—'
        delay = action.get('delay_ms', self.global_delay_ms_var.get())
        contrib = action.get('progress_contrib')
        item = self.actions_tree.insert('', tk.END, values=(
            action['type'].capitalize(), params, delay, hold, cond,
            f"{contrib:.2f}" if contrib is not None else "—"
        ))
        action['tree_iid'] = item

    def clear_actions(self):
        if self.running:
            self.status_var.set(LANGUAGES[self.lang]['cannot_edit_running'])
            return
        self.actions.clear()
        self.actions_tree.delete(*self.actions_tree.get_children())
        self.status_var.set("Actions cleared")

    def remove_selected_action(self):
        if self.running:
            self.status_var.set(LANGUAGES[self.lang]['cannot_edit_running'])
            return
        for item in self.actions_tree.selection():
            for i, act in enumerate(self.actions):
                if act.get('tree_iid') == item:
                    del self.actions[i]
                    break
            self.actions_tree.delete(item)

    def edit_selected_action(self):
        sel = self.actions_tree.selection()
        if sel:
            self.edit_action_double_click(None, item=sel[0])

    def edit_action_double_click(self, event, item=None):
        if self.running:
            self.status_var.set(LANGUAGES[self.lang]['cannot_edit_running'])
            return
        if item is None:
            sel = self.actions_tree.selection()
            if not sel:
                return
            item = sel[0]
        action = next((a for a in self.actions if a.get('tree_iid') == item), None)
        if not action:
            return

        d = tk.Toplevel(self.root)
        d.title(LANGUAGES[self.lang]['edit_action'])
        d.geometry("550x700")
        d.configure(bg='#1e1e2f')
        d.transient(self.root)
        d.grab_set()

        # Задержка
        tk.Label(d, text=LANGUAGES[self.lang]['delay_ms'], fg='white', bg='#1e1e2f').pack(pady=5)
        delay_var = tk.IntVar(value=action.get('delay_ms', self.global_delay_ms_var.get()))
        tk.Entry(d, textvariable=delay_var, width=15, bg='#2a2a3c', fg='white').pack()

        # Параметры в зависимости от типа
        if action['type'] == 'click':
            f = tk.Frame(d, bg='#1e1e2f')
            f.pack(pady=5)
            tk.Label(f, text="X:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
            xv = tk.IntVar(value=action['x'])
            tk.Entry(f, textvariable=xv, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)
            tk.Label(f, text="Y:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
            yv = tk.IntVar(value=action['y'])
            tk.Entry(f, textvariable=yv, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)
            tk.Button(f, text="Get current", command=lambda: (xv.set(pyautogui.position()[0]), yv.set(pyautogui.position()[1])),
                      bg='#3a3a5c', fg='white').pack(side=tk.LEFT, padx=5)

            tk.Label(d, text=LANGUAGES[self.lang]['hold_ms'], fg='white', bg='#1e1e2f').pack(pady=5)
            hold_var = tk.IntVar(value=action.get('hold_ms', 0))
            tk.Entry(d, textvariable=hold_var, width=15, bg='#2a2a3c', fg='white').pack()

        elif action['type'] == 'key':
            f = tk.Frame(d, bg='#1e1e2f')
            f.pack(pady=5)
            tk.Label(f, text="Key:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
            key_var = tk.StringVar(value=action['key'])
            cb = ttk.Combobox(f, textvariable=key_var, values=self._get_key_list(), width=15)
            cb.pack(side=tk.LEFT, padx=5)
            tk.Button(f, text="Record", command=lambda: self._record_key_for_dialog(key_var, d),
                      bg='#3a3a5c', fg='white').pack(side=tk.LEFT)

        # Блок условия
        cond_frame = tk.LabelFrame(d, text=LANGUAGES[self.lang]['condition'], bg='#1e1e2f', fg='white', padx=5, pady=5)
        cond_frame.pack(fill=tk.X, pady=10, padx=10)

        cond_type_var = tk.StringVar(value=action.get('condition', {}).get('type', 'none') if action.get('condition') else 'none')
        types = ['none', 'pixel', 'color_area', 'image_search']
        cb_type = ttk.Combobox(cond_frame, textvariable=cond_type_var, values=types, state='readonly', width=20)
        cb_type.pack(pady=5)

        # Контейнер для динамических параметров условия
        cond_params_frame = tk.Frame(cond_frame, bg='#1e1e2f')
        cond_params_frame.pack(fill=tk.X, pady=5)

        # Флажки
        wait_var = tk.BooleanVar(value=action.get('wait_condition', False))
        tk.Checkbutton(d, text=LANGUAGES[self.lang]['wait_condition'], variable=wait_var,
                       bg='#1e1e2f', fg='white', selectcolor='#1e1e2f', activebackground='#1e1e2f').pack(anchor=tk.W, pady=5)

        skip_true_var = tk.BooleanVar(value=action.get('skip_on_true', False))
        tk.Checkbutton(d, text=LANGUAGES[self.lang]['skip_on_true'], variable=skip_true_var,
                       bg='#1e1e2f', fg='white', selectcolor='#1e1e2f', activebackground='#1e1e2f').pack(anchor=tk.W)
        skip_false_var = tk.BooleanVar(value=action.get('skip_on_false', False))
        tk.Checkbutton(d, text=LANGUAGES[self.lang]['skip_on_false'], variable=skip_false_var,
                       bg='#1e1e2f', fg='white', selectcolor='#1e1e2f', activebackground='#1e1e2f').pack(anchor=tk.W)

        # Вклад в прогресс
        tk.Label(d, text=LANGUAGES[self.lang]['progress_contrib'], fg='white', bg='#1e1e2f').pack(pady=5)
        contrib_var = tk.StringVar(value=str(action.get('progress_contrib', '')))
        tk.Entry(d, textvariable=contrib_var, width=15, bg='#2a2a3c', fg='white').pack()

        # Функция обновления панели параметров условия
        def update_cond_params(*args):
            for w in cond_params_frame.winfo_children():
                w.destroy()
            t = cond_type_var.get()
            if t == 'pixel':
                tk.Label(cond_params_frame, text="Pixel ID:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
                ids = [''] + [c['id'] for c in self.pixel_conditions_dialog.conditions]
                pixel_id_var = tk.StringVar(value=action.get('condition', {}).get('id', '') if action.get('condition') else '')
                cb = ttk.Combobox(cond_params_frame, textvariable=pixel_id_var, values=ids, state='readonly', width=15)
                cb.pack(side=tk.LEFT, padx=5)
                cond_params_frame.pixel_id_var = pixel_id_var
            elif t == 'color_area':
                # Область
                tk.Label(cond_params_frame, text="X1:", fg='white', bg='#1e1e2f').grid(row=0, column=0)
                x1v = tk.IntVar(value=action.get('condition', {}).get('area', [0,0,100,100])[0] if action.get('condition') else 0)
                tk.Entry(cond_params_frame, textvariable=x1v, width=5, bg='#2a2a3c', fg='white').grid(row=0, column=1)
                tk.Label(cond_params_frame, text="Y1:", fg='white', bg='#1e1e2f').grid(row=0, column=2)
                y1v = tk.IntVar(value=action.get('condition', {}).get('area', [0,0,100,100])[1] if action.get('condition') else 0)
                tk.Entry(cond_params_frame, textvariable=y1v, width=5, bg='#2a2a3c', fg='white').grid(row=0, column=3)
                tk.Label(cond_params_frame, text="X2:", fg='white', bg='#1e1e2f').grid(row=1, column=0)
                x2v = tk.IntVar(value=action.get('condition', {}).get('area', [0,0,100,100])[2] if action.get('condition') else 100)
                tk.Entry(cond_params_frame, textvariable=x2v, width=5, bg='#2a2a3c', fg='white').grid(row=1, column=1)
                tk.Label(cond_params_frame, text="Y2:", fg='white', bg='#1e1e2f').grid(row=1, column=2)
                y2v = tk.IntVar(value=action.get('condition', {}).get('area', [0,0,100,100])[3] if action.get('condition') else 100)
                tk.Entry(cond_params_frame, textvariable=y2v, width=5, bg='#2a2a3c', fg='white').grid(row=1, column=3)
                # Цвет
                tk.Label(cond_params_frame, text="R:", fg='white', bg='#1e1e2f').grid(row=2, column=0)
                rv = tk.IntVar(value=action.get('condition', {}).get('color', [0,0,0])[0] if action.get('condition') else 0)
                tk.Entry(cond_params_frame, textvariable=rv, width=4, bg='#2a2a3c', fg='white').grid(row=2, column=1)
                tk.Label(cond_params_frame, text="G:", fg='white', bg='#1e1e2f').grid(row=2, column=2)
                gv = tk.IntVar(value=action.get('condition', {}).get('color', [0,0,0])[1] if action.get('condition') else 0)
                tk.Entry(cond_params_frame, textvariable=gv, width=4, bg='#2a2a3c', fg='white').grid(row=2, column=3)
                tk.Label(cond_params_frame, text="B:", fg='white', bg='#1e1e2f').grid(row=2, column=4)
                bv = tk.IntVar(value=action.get('condition', {}).get('color', [0,0,0])[2] if action.get('condition') else 0)
                tk.Entry(cond_params_frame, textvariable=bv, width=4, bg='#2a2a3c', fg='white').grid(row=2, column=5)
                cond_params_frame.vars = (x1v, y1v, x2v, y2v, rv, gv, bv)
            elif t == 'image_search':
                tk.Label(cond_params_frame, text="Image file:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
                img_path_var = tk.StringVar()
                tk.Entry(cond_params_frame, textvariable=img_path_var, width=25, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)
                tk.Button(cond_params_frame, text="Browse", command=lambda: self._browse_image(img_path_var),
                          bg='#3a3a5c', fg='white').pack(side=tk.LEFT)
                # Область поиска
                area_frame = tk.Frame(cond_params_frame, bg='#1e1e2f')
                area_frame.pack(pady=5)
                tk.Label(area_frame, text="X1:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
                x1v = tk.IntVar(value=action.get('condition', {}).get('area', [0,0,1920,1080])[0] if action.get('condition') else 0)
                tk.Entry(area_frame, textvariable=x1v, width=5, bg='#2a2a3c', fg='white').pack(side=tk.LEFT)
                tk.Label(area_frame, text="Y1:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
                y1v = tk.IntVar(value=action.get('condition', {}).get('area', [0,0,1920,1080])[1] if action.get('condition') else 0)
                tk.Entry(area_frame, textvariable=y1v, width=5, bg='#2a2a3c', fg='white').pack(side=tk.LEFT)
                tk.Label(area_frame, text="X2:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
                x2v = tk.IntVar(value=action.get('condition', {}).get('area', [0,0,1920,1080])[2] if action.get('condition') else 1920)
                tk.Entry(area_frame, textvariable=x2v, width=5, bg='#2a2a3c', fg='white').pack(side=tk.LEFT)
                tk.Label(area_frame, text="Y2:", fg='white', bg='#1e1e2f').pack(side=tk.LEFT)
                y2v = tk.IntVar(value=action.get('condition', {}).get('area', [0,0,1920,1080])[3] if action.get('condition') else 1080)
                tk.Entry(area_frame, textvariable=y2v, width=5, bg='#2a2a3c', fg='white').pack(side=tk.LEFT)
                # Confidence
                tk.Label(cond_params_frame, text="Confidence (0.5-1.0):", fg='white', bg='#1e1e2f').pack()
                conf_var = tk.DoubleVar(value=action.get('condition', {}).get('confidence', 0.8) if action.get('condition') else 0.8)
                tk.Scale(cond_params_frame, from_=0.5, to=1.0, resolution=0.01, variable=conf_var, orient=tk.HORIZONTAL,
                         bg='#1e1e2f', fg='white', troughcolor='#2a2a3c').pack(fill=tk.X)
                cond_params_frame.vars = (img_path_var, x1v, y1v, x2v, y2v, conf_var)
                # Сохраняем текущее изображение, если есть
                if action.get('condition') and action['condition'].get('image'):
                    cond_params_frame.cached_image = action['condition']['image']

        cond_type_var.trace('w', update_cond_params)
        update_cond_params()

        def save():
            action['delay_ms'] = delay_var.get()
            if action['type'] == 'click':
                action['x'] = xv.get()
                action['y'] = yv.get()
                action['hold_ms'] = hold_var.get()
            elif action['type'] == 'key':
                action['key'] = key_var.get()

            # Сохраняем условие
            t = cond_type_var.get()
            if t == 'none':
                action['condition'] = None
            else:
                cond = {'type': t}
                if t == 'pixel':
                    cond['id'] = cond_params_frame.pixel_id_var.get()
                elif t == 'color_area':
                    x1, y1, x2, y2, r, g, b = cond_params_frame.vars
                    cond['area'] = [x1.get(), y1.get(), x2.get(), y2.get()]
                    cond['color'] = [r.get(), g.get(), b.get()]
                elif t == 'image_search':
                    img_path, x1, y1, x2, y2, conf = cond_params_frame.vars
                    # Загружаем и кодируем изображение
                    if hasattr(cond_params_frame, 'cached_image'):
                        cond['image'] = cond_params_frame.cached_image
                    elif img_path.get():
                        with open(img_path.get(), 'rb') as f:
                            cond['image'] = base64.b64encode(f.read()).decode('utf-8')
                    cond['area'] = [x1.get(), y1.get(), x2.get(), y2.get()]
                    cond['confidence'] = conf.get()
                action['condition'] = cond

            action['wait_condition'] = wait_var.get()
            action['skip_on_true'] = skip_true_var.get()
            action['skip_on_false'] = skip_false_var.get()
            cs = contrib_var.get().strip()
            action['progress_contrib'] = float(cs) if cs else None

            # Обновляем отображение в дереве
            self.actions_tree.item(item, values=(
                action['type'].capitalize(),
                f"X={action['x']}, Y={action['y']}" if action['type']=='click' else f"Key: {action['key']}" if action['type']=='key' else "Pause",
                action['delay_ms'],
                str(action.get('hold_ms',0)) if action['type']=='click' else '—',
                action['condition']['type'] if action.get('condition') else '—',
                f"{action['progress_contrib']:.2f}" if action['progress_contrib'] is not None else "—"
            ))
            d.destroy()

        tk.Button(d, text=LANGUAGES[self.lang]['save'], command=save, bg='#3a3a5c', fg='white').pack(pady=15)

    def _browse_image(self, var):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if path:
            var.set(path)

    def _get_key_list(self):
        return ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                '0','1','2','3','4','5','6','7','8','9',
                'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12',
                'enter','space','tab','escape','backspace','shift','ctrl','alt']

    def _record_key_for_dialog(self, key_var, dialog):
        dialog.grab_release()
        self.status_var.set("Press a key...")
        self.waiting_for_key = True
        def handler(e):
            if self.waiting_for_key and e.name not in ('shift','ctrl','alt','windows','right shift','right ctrl','right alt'):
                self.waiting_for_key = False
                keyboard.unhook(hook)
                key_var.set(e.name)
                self.status_var.set(f"Key '{e.name}' recorded.")
                dialog.grab_set()
        hook = keyboard.on_press(handler)
        self.root.after(10000, lambda: self._cancel_key_dialog(dialog, hook))

    def _cancel_key_dialog(self, dialog, hook):
        if self.waiting_for_key:
            self.waiting_for_key = False
            keyboard.unhook(hook)
            self.status_var.set("Recording cancelled")
            dialog.grab_set()

    # ---------- Cycle control ----------
    def toggle_cycle(self):
        if self.running:
            self.stop_cycle()
        else:
            self.start_cycle()

    def start_cycle(self):
        if self.running:
            return
        if not self.actions:
            messagebox.showwarning(LANGUAGES[self.lang]['error'], LANGUAGES[self.lang]['no_actions'])
            return
        if self.mode_var.get() == 1:
            try:
                if self.initial_count_var.get() <= 0:
                    raise ValueError
                self.current_count = self.initial_count_var.get()
            except:
                messagebox.showerror(LANGUAGES[self.lang]['error'], "Invalid initial count")
                return
        self.running = True
        self.start_stop_btn.config(text=LANGUAGES[self.lang]['stop'] + f" ({self.hotkey_toggle_var.get().upper()})")
        self.status_var.set(LANGUAGES[self.lang]['cycle_running'])
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop_cycle(self):
        self.running = False
        self.start_stop_btn.config(text=LANGUAGES[self.lang]['start'] + f" ({self.hotkey_toggle_var.get().upper()})")
        self.status_var.set(LANGUAGES[self.lang]['cycle_stopped'])
        self.eta_label.config(text=LANGUAGES[self.lang]['eta_label'].format('—'))
        if self.progress_window:
            self.progress_window.eta_label.config(text='—')

    def _check_condition(self, cond):
        """Возвращает True, если условие выполнено."""
        if not cond or not self.use_conditions_var.get():
            return True
        tol = self.color_tolerance_var.get()
        t = cond['type']
        if t == 'pixel':
            c = self.pixel_conditions_dialog.get_condition_by_id(cond.get('id'))
            if not c:
                return True
            try:
                cur = pyautogui.pixel(c['x'], c['y'])
                return all(abs(cur[i] - c['color'][i]) <= tol for i in range(3))
            except:
                return False
        elif t == 'color_area':
            x1, y1, x2, y2 = cond['area']
            target = cond['color']
            # Проверяем с шагом 5 для производительности
            for y in range(y1, y2, 5):
                for x in range(x1, x2, 5):
                    try:
                        cur = pyautogui.pixel(x, y)
                        if all(abs(cur[i] - target[i]) <= tol for i in range(3)):
                            return True
                    except:
                        pass
            return False
        elif t == 'image_search':
            area = cond.get('area', [0, 0, pyautogui.size().width, pyautogui.size().height])
            conf = cond.get('confidence', 0.8)
            img_b64 = cond.get('image')
            if not img_b64:
                return False
            if img_b64 in self.image_cache:
                template = self.image_cache[img_b64]
            else:
                nparr = np.frombuffer(base64.b64decode(img_b64), np.uint8)
                template = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                self.image_cache[img_b64] = template
            x1, y1, x2, y2 = area
            # Проверка границ
            if x2 <= x1 or y2 <= y1:
                return False
            screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            return max_val >= conf
        return True

    def _run_loop(self):
        mode = self.mode_var.get()
        actions = list(self.actions)

        while self.running:
            skip_rest = False
            for act in actions:
                if not self.running or skip_rest:
                    break

                # Задержка перед действием
                delay = act.get('delay_ms', self.global_delay_ms_var.get())
                if delay > 0:
                    time.sleep(delay / 1000.0)
                if not self.running:
                    break

                # Если задано условие и включена проверка
                cond_met = True
                if act.get('condition') and self.use_conditions_var.get():
                    # Если нужно ждать условие
                    if act.get('wait_condition', False):
                        self.root.after(0, lambda: self.status_var.set(f"Waiting for condition: {act['condition'].get('type')}"))
                        while self.running and not self._check_condition(act['condition']):
                            time.sleep(0.1)
                        if not self.running:
                            break
                        cond_met = True
                    else:
                        cond_met = self._check_condition(act['condition'])

                # Обработка пропуска остальных действий
                if act.get('condition'):
                    if cond_met and act.get('skip_on_true'):
                        skip_rest = True
                    if not cond_met and act.get('skip_on_false'):
                        skip_rest = True

                if not cond_met:
                    continue

                # Выполнение действия
                if act['type'] == 'click':
                    hold = act.get('hold_ms', 0)
                    pyautogui.moveTo(act['x'], act['y'])
                    if hold > 0:
                        pyautogui.mouseDown()
                        time.sleep(hold / 1000.0)
                        pyautogui.mouseUp()
                    else:
                        pyautogui.click()
                elif act['type'] == 'key':
                    keyboard.press_and_release(act['key'])
                # тип 'delay' уже учтён в начальной задержке

                # Учёт прогресса
                if mode == 1:
                    contrib = act.get('progress_contrib')
                    if contrib is not None:
                        self.current_count -= contrib
                    elif act['type'] != 'delay':
                        deduct = self.deduction_var.get()
                        mult = self.deduction_mult_var.get()
                        if mult < 0:
                            mult = 0
                        elif mult > 1:
                            mult = 1
                        self.current_count -= deduct * (1.0 - mult)
                    self.root.after(0, self.update_count_display)
                    if self.current_count <= 0:
                        self.running = False
                        self.root.after(0, self._show_completion_message)
                        break

            self.root.after(0, self.update_count_display)

        self.root.after(0, lambda: self.start_stop_btn.config(
            text=LANGUAGES[self.lang]['start'] + f" ({self.hotkey_toggle_var.get().upper()})"))
        self.root.after(0, lambda: self.status_var.set(LANGUAGES[self.lang]['cycle_finished']))
        self.running = False

    def _show_completion_message(self):
        self.status_var.set(LANGUAGES[self.lang]['completion_title'])
        messagebox.showinfo(LANGUAGES[self.lang]['completion_title'], LANGUAGES[self.lang]['completion_message'])

    def _calculate_eta(self):
        if self.mode_var.get() == 0 or not self.running:
            return '—'
        try:
            total_delay = sum(a.get('delay_ms', self.global_delay_ms_var.get()) for a in self.actions)
            cycle_time = total_delay / 1000.0
            contrib = 0.0
            for a in self.actions:
                if a.get('progress_contrib') is not None:
                    contrib += a['progress_contrib']
                elif a['type'] != 'delay':
                    d = self.deduction_var.get()
                    m = self.deduction_mult_var.get()
                    if m < 0: m = 0
                    elif m > 1: m = 1
                    contrib += d * (1.0 - m)
            if contrib <= 0:
                return '∞'
            cycles = self.current_count / contrib
            secs = cycles * cycle_time
            m, s = divmod(int(secs), 60)
            return f"{m} min {s} sec" if m > 0 else f"{s} sec"
        except:
            return '—'

    def update_count_display(self):
        try:
            init = self.initial_count_var.get()
        except:
            init = 0
        cur = self.current_count
        pct = (cur / init * 100) if init > 0 else 0
        self.count_label.config(text=LANGUAGES[self.lang]['progress_label'].format(cur, init, pct))
        self.progress['value'] = pct
        eta = self._calculate_eta()
        self.eta_label.config(text=LANGUAGES[self.lang]['eta_label'].format(eta))
        if self.progress_window and self.show_progress_window_var.get():
            self.progress_window.update(cur, init, pct, eta)

    def save_profile(self):
        if not self.actions:
            messagebox.showwarning(LANGUAGES[self.lang]['error'], LANGUAGES[self.lang]['no_actions'])
            return
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not f:
            return
        acts = []
        for a in self.actions:
            ac = a.copy()
            ac.pop('tree_iid', None)
            acts.append(ac)
        prof = {
            'mode': self.mode_var.get(),
            'initial_count': self.initial_count_var.get(),
            'deduction': self.deduction_var.get(),
            'deduction_mult': self.deduction_mult_var.get(),
            'global_delay_ms': self.global_delay_ms_var.get(),
            'actions': acts,
            'hotkeys': {
                'click': self.hotkey_record_click_var.get(),
                'key': self.hotkey_record_key_var.get(),
                'toggle': self.hotkey_toggle_var.get()
            },
            'pixel_conditions': self.pixel_conditions_dialog.conditions,
            'color_tolerance': self.color_tolerance_var.get(),
            'use_conditions': self.use_conditions_var.get(),
        }
        with open(f, 'w', encoding='utf-8') as fp:
            json.dump(prof, fp, indent=2, ensure_ascii=False)
        self.status_var.set(f"Profile saved: {os.path.basename(f)}")

    def load_profile(self):
        f = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not f:
            return
        with open(f, 'r', encoding='utf-8') as fp:
            prof = json.load(fp)
        self.mode_var.set(prof.get('mode', 0))
        self.initial_count_var.set(prof.get('initial_count', 100))
        self.deduction_var.set(prof.get('deduction', 10))
        self.deduction_mult_var.set(prof.get('deduction_mult', 0.33))
        self.global_delay_ms_var.set(prof.get('global_delay_ms', 1000))
        hk = prof.get('hotkeys', {})
        self.hotkey_record_click_var.set(hk.get('click', 'f2'))
        self.hotkey_record_key_var.set(hk.get('key', 'f3'))
        self.hotkey_toggle_var.set(hk.get('toggle', 'f1'))
        self.pixel_conditions_dialog.conditions = prof.get('pixel_conditions', [])
        self.pixel_conditions_dialog.refresh_list()
        self.color_tolerance_var.set(prof.get('color_tolerance', 10))
        self.use_conditions_var.set(prof.get('use_conditions', True))
        self.clear_actions()
        for a in prof.get('actions', []):
            if 'delay_ms' not in a:
                a['delay_ms'] = self.global_delay_ms_var.get()
            if 'condition' not in a:
                a['condition'] = None
            if 'wait_condition' not in a:
                a['wait_condition'] = False
            if 'skip_on_true' not in a:
                a['skip_on_true'] = False
            if 'skip_on_false' not in a:
                a['skip_on_false'] = False
            if 'progress_contrib' not in a:
                a['progress_contrib'] = None
            self.actions.append(a)
            self._add_action_to_tree(a)
        self.apply_settings()
        self.status_var.set(f"Profile loaded: {os.path.basename(f)}")

    def run_tray(self):
        self.tray_icon.run()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClickerApp(root)
    threading.Thread(target=app.run_tray, daemon=True).start()
    root.mainloop()