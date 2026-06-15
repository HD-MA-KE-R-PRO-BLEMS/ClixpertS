"""
Clixpert S Pro Ultimate - Expert Mode Tab
Вкладка Expert Mode: редактор скриптов, отладка, переменные, логи
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class ExpertTab:
    """
    Вкладка Expert Mode.
    Содержит:
    - Редактор скриптов с подсветкой
    - Панель отладки (step mode, slow motion)
    - Панель переменных
    - Панель логов
    """

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg='#1a1a2e')
        self.script_text = None
        self.logs_text = None
        self.vars_listbox = None
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов вкладки"""
        # Панель с двумя колонками
        paned = tk.PanedWindow(self.frame, bg='#1a1a2e', orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - редактор
        left_frame = tk.Frame(paned, bg='#1a1a2e')
        paned.add(left_frame, width=700)

        # Правая панель - отладка, переменные, логи
        right_frame = tk.Frame(paned, bg='#1a1a2e')
        paned.add(right_frame, width=350)

        self._create_editor_panel(left_frame)
        self._create_right_panel(right_frame)

    def _create_editor_panel(self, parent):
        """Создание панели редактора"""
        editor_frame = tk.LabelFrame(
            parent, text="Script Editor", bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        editor_frame.pack(fill=tk.BOTH, expand=True)

        # Текстовый редактор
        self.script_text = tk.Text(
            editor_frame, height=20, bg='#2a2a3c', fg='#aaccff',
            insertbackground='white', font=('Consolas', 10), wrap=tk.NONE
        )
        self.script_text.pack(fill=tk.BOTH, expand=True)

        # Скроллбары
        scroll_y = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.script_text.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.script_text.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.script_text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Кнопки управления
        btn_frame = tk.Frame(editor_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame, text="▶ Run Script", command=self._on_run_script,
            bg='#2a8c4a', fg='white', bd=0, padx=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="⏹ Stop", command=self._on_stop_script,
            bg='#8c2a2a', fg='white', bd=0, padx=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="❓ Syntax Help", command=self._on_syntax_help,
            bg='#3a3a5c', fg='white', bd=0, padx=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="📁 Load", command=self._on_load_script,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="💾 Save", command=self._on_save_script,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=5)

        # Пример скрипта
        self._load_example_script()

    def _create_right_panel(self, parent):
        """Создание правой панели"""
        # Отладка
        debug_frame = tk.LabelFrame(
            parent, text="Debug Mode", bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        debug_frame.pack(fill=tk.X, pady=5)

        debug_inner = tk.Frame(debug_frame, bg='#1e1e2f')
        debug_inner.pack(fill=tk.X)

        self.step_mode_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            debug_inner, text="Step Mode", variable=self.step_mode_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).pack(side=tk.LEFT, padx=5)

        tk.Label(debug_inner, text="Slow Motion (ms):", bg='#1e1e2f', fg='white').pack(side=tk.LEFT, padx=5)
        self.slow_mode_var = tk.IntVar(value=0)
        tk.Entry(debug_inner, textvariable=self.slow_mode_var, width=5, bg='#2a2a3c', fg='white').pack(side=tk.LEFT)

        tk.Button(
            debug_inner, text="Apply", command=self._on_apply_debug,
            bg='#3a3a5c', fg='white', bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            debug_inner, text="Continue", command=self._on_debug_continue,
            bg='#3a3a5c', fg='white', bd=0
        ).pack(side=tk.LEFT, padx=5)

        # Переменные
        vars_frame = tk.LabelFrame(
            parent, text="Variables", bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        vars_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.vars_listbox = tk.Listbox(
            vars_frame, height=8, bg='#2a2a3c', fg='#aaccff', font=('Consolas', 9)
        )
        self.vars_listbox.pack(fill=tk.BOTH, expand=True)

        # Логи
        logs_frame = tk.LabelFrame(
            parent, text="Logs", bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        logs_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.logs_text = tk.Text(
            logs_frame, height=10, bg='#1a1a2a', fg='#88ff88',
            font=('Consolas', 9), wrap=tk.WORD
        )
        self.logs_text.pack(fill=tk.BOTH, expand=True)

        logs_scroll = ttk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=self.logs_text.yview)
        logs_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.logs_text.configure(yscrollcommand=logs_scroll.set)

        logs_btn = tk.Frame(logs_frame, bg='#1e1e2f')
        logs_btn.pack(fill=tk.X, pady=5)

        tk.Button(
            logs_btn, text="Clear Logs", command=self._on_clear_logs,
            bg='#3a3a5c', fg='white', bd=0
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            logs_btn, text="Export Logs", command=self._on_export_logs,
            bg='#3a3a5c', fg='white', bd=0
        ).pack(side=tk.LEFT, padx=5)

    def _load_example_script(self):
        """Загрузка примера скрипта"""
        example = '''# ⚡ Clixpert S Pro Ultimate Script Example

# Variables
counter = 0
found = False

# Search for image with advanced features
if find_image_advanced("button.png", confidence=0.8):
    counter = counter + 1
    print(f"✅ Image found! Counter: {counter}")
    click_at_match_center()
else:
    print("❌ Image not found")

# Loop with human-like behavior
for i in range(3):
    print(f"🔄 Iteration {i+1}")

    # Human click
    click_human(500, 500, 50, 200)

    # Wait with random variation
    wait(500)

    # Key press
    key("enter")

print("🎉 Script execution completed!")
'''
        self.script_text.insert('1.0', example)

    def _on_run_script(self):
        """Запуск скрипта"""
        script = self.script_text.get('1.0', tk.END)
        if not script.strip():
            messagebox.showwarning("Error", "No script to execute")
            return

        # Применяем настройки отладки
        if hasattr(self.app, 'script_executor') and self.app.script_executor:
            self.app.script_executor.debug_executor.set_step_mode(self.step_mode_var.get())
            self.app.script_executor.debug_executor.set_slow_mode(self.slow_mode_var.get())

        self.app.run_script(script)
        self.app.update_status("Running script...")

    def _on_stop_script(self):
        """Остановка скрипта"""
        self.app.stop_script()
        self.app.update_status("Script stopped")

    def _on_syntax_help(self):
        """Показать справку по синтаксису"""
        help_window = tk.Toplevel(self.frame)
        help_window.title("Syntax Help")
        help_window.geometry("700x600")
        help_window.configure(bg='#1e1e2f')

        text = tk.Text(help_window, bg='#2a2a3c', fg='#aaccff', font=('Consolas', 10), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        help_text = """
=== CLIXPERT S PRO ULTIMATE - SYNTAX HELP ===

VARIABLES:
    x = 10
    name = "Hello"
    result = x * 2 + 5

LOOPS:
    for i in range(5):         # 0,1,2,3,4
    for i in range(1, 10, 2):  # 1,3,5,7,9
    for item in [1, "text", 3.14]:
        click(100, 100)
        wait(100)

CONDITIONS:
    if x > 5:
        print("x is greater than 5")
    elif x == 5:
        print("x equals 5")
    else:
        print("x is less than 5")

CLICK COMMANDS:
    click(x, y)              # Simple click
    click(x, y, 500)         # Click with 500ms hold
    click_random(x, y, 10)   # Click with random offset
    click_at_match_center()  # Click at last found image center
    click_human(x, y, 50, 200) # Human-like click

KEY COMMANDS:
    key("enter")             # Press and release
    key_down("ctrl")         # Hold key down
    key_up("ctrl")           # Release key
    key_human("space", 50, 150) # Human-like key press

MOUSE COMMANDS:
    move(x, y)               # Move mouse
    move_human(x, y, "normal") # Human-like movement
    scroll(100)              # Scroll up
    scroll_human(100)        # Human-like scroll
    mouse_down(x, y, "left") # Hold mouse button
    mouse_up(x, y, "left")   # Release mouse button
    drag_human(x1, y1, x2, y2) # Drag and drop
    type("text")             # Type text
    type_human("text")       # Human-like typing

TIMING:
    wait(1000)               # Pause 1000ms

CONDITION CHECKS:
    if exists_image("C:/image.png"):
        click(100, 100)

    if find_image_advanced("button.png", confidence=0.8):
        click_at_match_center()

    if color_match(500, 300, 255, 0, 0, 10):
        print("Red pixel found")

    if find_text("OK", 85):
        print("Text found!")

    if sound_detected(500, 0.5):
        print("Sound detected!")
"""
        text.insert('1.0', help_text)
        text.config(state=tk.DISABLED)

        tk.Button(help_window, text="Close", command=help_window.destroy, bg='#3a3a5c', fg='white', bd=0).pack(pady=10)

    def _on_load_script(self):
        """Загрузка скрипта из файла"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Script files", "*.txt *.clix"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.script_text.delete('1.0', tk.END)
                self.script_text.insert('1.0', content)
                self.app.update_status(f"Loaded script: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load script: {e}")

    def _on_save_script(self):
        """Сохранение скрипта в файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".clix",
            filetypes=[("Clixpert scripts", "*.clix"), ("Text files", "*.txt")]
        )
        if filepath:
            try:
                content = self.script_text.get('1.0', tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.app.update_status(f"Saved script: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save script: {e}")

    def _on_apply_debug(self):
        """Применение настроек отладки"""
        if hasattr(self.app, 'script_executor') and self.app.script_executor:
            self.app.script_executor.debug_executor.set_step_mode(self.step_mode_var.get())
            self.app.script_executor.debug_executor.set_slow_mode(self.slow_mode_var.get())
            self.app.update_status("Debug settings applied")

    def _on_debug_continue(self):
        """Продолжить выполнение после паузы"""
        if hasattr(self.app, 'script_executor') and self.app.script_executor:
            self.app.script_executor.debug_executor.continue_execution()

    def _on_clear_logs(self):
        """Очистка логов"""
        self.logs_text.delete('1.0', tk.END)
        if hasattr(self.app, 'script_executor') and self.app.script_executor:
            self.app.script_executor.logs = []
        self.app.update_status("Logs cleared")

    def _on_export_logs(self):
        """Экспорт логов в файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if filepath:
            try:
                logs = self.logs_text.get('1.0', tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(logs)
                self.app.update_status(f"Logs exported to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {e}")

    def update_logs(self, log_entry):
        """Обновление панели логов"""
        self.logs_text.insert(tk.END, log_entry + "\n")
        self.logs_text.see(tk.END)

    def update_variables(self, variables):
        """Обновление панели переменных"""
        self.vars_listbox.delete(0, tk.END)
        for var_name, var_value in variables.items():
            self.vars_listbox.insert(tk.END, f"{var_name} = {var_value}")

    def get_script(self):
        """Получить текст скрипта"""
        return self.script_text.get('1.0', tk.END)

    def set_script(self, script):
        """Установить текст скрипта"""
        self.script_text.delete('1.0', tk.END)
        self.script_text.insert('1.0', script)

    def get_frame(self):
        """Получить фрейм вкладки"""
        return self.frame

    def refresh_texts(self):
        """Обновление текстов интерфейса"""
        # Обновляем заголовок редактора
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for frame in child.panes():
                    for subchild in frame.winfo_children():
                        if isinstance(subchild, tk.LabelFrame):
                            if subchild.cget("text") == "Script Editor":
                                subchild.config(text=self.app.get_text('script_editor'))
                            elif subchild.cget("text") == "Debug Mode":
                                subchild.config(text=self.app.get_text('debug_mode'))
                            elif subchild.cget("text") == "Variables":
                                subchild.config(text=self.app.get_text('variables'))
                            elif subchild.cget("text") == "Logs":
                                subchild.config(text=self.app.get_text('logs'))

        # Обновляем текст кнопок в редакторе
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for frame in child.panes():
                    for subchild in frame.winfo_children():
                        if isinstance(subchild, tk.LabelFrame):
                            for btn in subchild.winfo_children():
                                if isinstance(btn, tk.Frame):
                                    for b in btn.winfo_children():
                                        if isinstance(b, tk.Button):
                                            text = b.cget("text")
                                            if text == "▶ Run Script":
                                                b.config(text="▶ " + self.app.get_text('run_script'))
                                            elif text == "⏹ Stop":
                                                b.config(text="⏹ " + self.app.get_text('stop'))
                                            elif text == "❓ Syntax Help":
                                                b.config(text="❓ " + self.app.get_text('syntax_help'))
                                            elif text == "📁 Load":
                                                b.config(text="📁 " + self.app.get_text('load'))
                                            elif text == "💾 Save":
                                                b.config(text="💾 " + self.app.get_text('save'))
                                            elif text == "Clear Logs":
                                                b.config(text=self.app.get_text('clear_logs'))
                                            elif text == "Export Logs":
                                                b.config(text=self.app.get_text('export_logs'))
                                            elif text == "Apply":
                                                b.config(text=self.app.get_text('apply'))
                                            elif text == "Continue":
                                                b.config(text=self.app.get_text('continue'))

        # Обновляем текст чекбоксов
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for frame in child.panes():
                    for subchild in frame.winfo_children():
                        if isinstance(subchild, tk.LabelFrame):
                            for cb in subchild.winfo_children():
                                if isinstance(cb, tk.Checkbutton) and cb.cget("text") == "Step Mode":
                                    cb.config(text=self.app.get_text('step_mode'))
                                elif isinstance(cb, tk.Checkbutton) and cb.cget("text") == "Step Mode":
                                    cb.config(text=self.app.get_text('step_mode'))