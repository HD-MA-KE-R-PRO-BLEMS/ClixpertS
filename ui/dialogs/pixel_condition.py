"""
Clixpert S Pro Ultimate - Pixel Condition Dialog
Управление пиксельными условиями (добавление, редактирование, тестирование)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import keyboard


class PixelConditionDialog:
    """
    Диалог управления пиксельными условиями.
    Позволяет добавлять, редактировать, удалять и тестировать условия.
    """

    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        self.conditions = []
        self.create_window()

    def create_window(self):
        """Создание главного окна диалога"""
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Pixel Conditions Manager")
        self.window.geometry("750x550")
        self.window.configure(bg='#1e1e2f')
        self.window.attributes('-alpha', 0.96)
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

        try:
            import pywinstyles
            pywinstyles.apply_style(self.window, "dark")
        except:
            pass

        main_frame = tk.Frame(self.window, bg='#1e1e2f', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Список условий
        list_frame = tk.LabelFrame(
            main_frame,
            text="Pixel Conditions",
            bg='#1e1e2f',
            fg='white',
            padx=5,
            pady=5
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Таблица условий
        columns = ('id', 'x', 'y', 'r', 'g', 'b', 'tolerance')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.tree.heading('id', text='ID')
        self.tree.heading('x', text='X')
        self.tree.heading('y', text='Y')
        self.tree.heading('r', text='R')
        self.tree.heading('g', text='G')
        self.tree.heading('b', text='B')
        self.tree.heading('tolerance', text='Tolerance')

        self.tree.column('id', width=100)
        self.tree.column('x', width=60)
        self.tree.column('y', width=60)
        self.tree.column('r', width=50)
        self.tree.column('g', width=50)
        self.tree.column('b', width=50)
        self.tree.column('tolerance', width=80)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', self.edit_selected)

        # Кнопки управления
        btn_frame = tk.Frame(list_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame, text="➕ Add", command=self.add_condition,
            bg='#2a8c4a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="✏ Edit", command=self.edit_selected,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="🗑 Delete", command=self.delete_selected,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="📋 Test", command=self.test_condition,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="🗑 Clear All", command=self.clear_all,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        # Информация
        info_frame = tk.Frame(main_frame, bg='#1e1e2f')
        info_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            info_frame,
            text="💡 Tip: Double-click to edit, or use buttons above",
            bg='#1e1e2f',
            fg='#888888'
        ).pack()

        self.refresh_list()

    def add_condition(self, edit_item=None, existing_id=None):
        """Добавление или редактирование условия"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Pixel Condition" if not edit_item else "Edit Pixel Condition")
        dialog.geometry("500x550")
        dialog.configure(bg='#1e1e2f')
        dialog.transient(self.window)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg='#1e1e2f', padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ID
        tk.Label(
            main_frame, text="Condition ID:", bg='#1e1e2f', fg='white',
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor=tk.W)
        id_var = tk.StringVar(value=existing_id if existing_id else "")
        tk.Entry(
            main_frame, textvariable=id_var, bg='#2a2a3c', fg='white',
            font=('Segoe UI', 10), width=30
        ).pack(fill=tk.X, pady=5)

        # Координаты
        coord_frame = tk.LabelFrame(
            main_frame, text="Coordinates", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        coord_frame.pack(fill=tk.X, pady=10)

        # X
        x_frame = tk.Frame(coord_frame, bg='#1e1e2f')
        x_frame.pack(fill=tk.X, pady=2)
        tk.Label(x_frame, text="X:", bg='#1e1e2f', fg='white', width=5, anchor=tk.W).pack(side=tk.LEFT)
        x_var = tk.IntVar(value=0)
        tk.Entry(x_frame, textvariable=x_var, width=8, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        # Y
        y_frame = tk.Frame(coord_frame, bg='#1e1e2f')
        y_frame.pack(fill=tk.X, pady=2)
        tk.Label(y_frame, text="Y:", bg='#1e1e2f', fg='white', width=5, anchor=tk.W).pack(side=tk.LEFT)
        y_var = tk.IntVar(value=0)
        tk.Entry(y_frame, textvariable=y_var, width=8, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        # Кнопка получения позиции
        tk.Button(
            coord_frame, text="🎯 Get Current Mouse Position",
            command=lambda: self._get_mouse_position(x_var, y_var),
            bg='#3a3a5c', fg='white', bd=0, padx=10, pady=3
        ).pack(pady=10)

        # Цвет
        color_frame = tk.LabelFrame(
            main_frame, text="Target Color", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        color_frame.pack(fill=tk.X, pady=10)

        rgb_frame = tk.Frame(color_frame, bg='#1e1e2f')
        rgb_frame.pack()

        tk.Label(rgb_frame, text="R:", bg='#1e1e2f', fg='white').grid(row=0, column=0, padx=5)
        r_var = tk.IntVar(value=0)
        tk.Entry(rgb_frame, textvariable=r_var, width=5, bg='#2a2a3c', fg='white').grid(row=0, column=1, padx=5)

        tk.Label(rgb_frame, text="G:", bg='#1e1e2f', fg='white').grid(row=0, column=2, padx=5)
        g_var = tk.IntVar(value=0)
        tk.Entry(rgb_frame, textvariable=g_var, width=5, bg='#2a2a3c', fg='white').grid(row=0, column=3, padx=5)

        tk.Label(rgb_frame, text="B:", bg='#1e1e2f', fg='white').grid(row=0, column=4, padx=5)
        b_var = tk.IntVar(value=0)
        tk.Entry(rgb_frame, textvariable=b_var, width=5, bg='#2a2a3c', fg='white').grid(row=0, column=5, padx=5)

        # Предпросмотр цвета
        color_preview = tk.Label(color_frame, width=30, height=2, bg='gray', relief=tk.RAISED)
        color_preview.pack(pady=10)

        def update_preview(*args):
            try:
                hex_color = '#{:02x}{:02x}{:02x}'.format(r_var.get(), g_var.get(), b_var.get())
                color_preview.config(bg=hex_color)
            except:
                pass

        r_var.trace('w', update_preview)
        g_var.trace('w', update_preview)
        b_var.trace('w', update_preview)

        # Кнопка выбора цвета
        tk.Button(
            color_frame, text="🎨 Pick Color from Screen",
            command=lambda: self._pick_color(x_var.get(), y_var.get(), r_var, g_var, b_var),
            bg='#3a3a5c', fg='white', bd=0, padx=10, pady=3
        ).pack(pady=5)

        # Допуск
        tol_frame = tk.LabelFrame(
            main_frame, text="Tolerance", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        tol_frame.pack(fill=tk.X, pady=10)

        tol_var = tk.IntVar(value=self.app.settings.get("color_tolerance", 10))
        tol_scale = tk.Scale(
            tol_frame, from_=0, to=50, orient=tk.HORIZONTAL, variable=tol_var,
            bg='#1e1e2f', fg='white', troughcolor='#2a2a3c', length=200
        )
        tol_scale.pack()
        tk.Label(tol_frame, textvariable=tol_var, bg='#1e1e2f', fg='#88ff88').pack()

        # Загрузка данных при редактировании
        if edit_item:
            cond = self._get_condition_by_item(edit_item)
            if cond:
                x_var.set(cond['x'])
                y_var.set(cond['y'])
                r_var.set(cond['color'][0])
                g_var.set(cond['color'][1])
                b_var.set(cond['color'][2])
                if 'tolerance' in cond:
                    tol_var.set(cond['tolerance'])
                update_preview()

        # Кнопки сохранения/отмены
        btn_frame = tk.Frame(main_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=10)

        def save():
            cond_id = id_var.get().strip()
            if not cond_id:
                messagebox.showerror("Error", "Please enter a condition ID")
                return
            if not edit_item and any(c['id'] == cond_id for c in self.conditions):
                messagebox.showerror("Error", f"Condition ID '{cond_id}' already exists")
                return

            new_cond = {
                'id': cond_id,
                'x': x_var.get(),
                'y': y_var.get(),
                'color': (r_var.get(), g_var.get(), b_var.get()),
                'tolerance': tol_var.get()
            }

            if edit_item:
                for i, c in enumerate(self.conditions):
                    if c['id'] == existing_id:
                        self.conditions[i] = new_cond
                        break
            else:
                self.conditions.append(new_cond)

            self.refresh_list()
            dialog.destroy()
            self.app.update_status(f"Condition '{cond_id}' saved")

        tk.Button(
            btn_frame, text="💾 Save", command=save,
            bg='#2a8c4a', fg='white', bd=0, padx=20, pady=5
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="❌ Cancel", command=dialog.destroy,
            bg='#8c2a2a', fg='white', bd=0, padx=20, pady=5
        ).pack(side=tk.LEFT, padx=5)

    def _get_mouse_position(self, x_var, y_var):
        """Получить позицию курсора"""
        x, y = pyautogui.position()
        x_var.set(x)
        y_var.set(y)
        self.app.update_status(f"Mouse position: ({x}, {y})")

    def _pick_color(self, x, y, r_var, g_var, b_var):
        """Взять цвет с экрана"""
        if x == 0 and y == 0:
            x, y = pyautogui.position()
        try:
            color = pyautogui.pixel(x, y)
            r_var.set(color[0])
            g_var.set(color[1])
            b_var.set(color[2])
            self.app.update_status(f"Color picked: RGB({color[0]}, {color[1]}, {color[2]})")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to pick color: {e}")

    def _get_condition_by_item(self, item):
        """Получить условие по элементу дерева"""
        values = self.tree.item(item)['values']
        if not values:
            return None
        cond_id = values[0]
        for c in self.conditions:
            if c['id'] == cond_id:
                return c
        return None

    def edit_selected(self, event=None):
        """Редактирование выбранного условия"""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            cond = self._get_condition_by_item(item)
            if cond:
                self.add_condition(edit_item=item, existing_id=cond['id'])

    def delete_selected(self):
        """Удаление выбранных условий"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to delete")
            return
        if messagebox.askyesno("Confirm", f"Delete {len(selected)} condition(s)?"):
            for item in selected:
                cond_id = self.tree.item(item)['values'][0]
                self.conditions = [c for c in self.conditions if c['id'] != cond_id]
            self.refresh_list()
            self.app.update_status(f"Deleted {len(selected)} condition(s)")

    def test_condition(self):
        """Тестирование выбранного условия"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to test")
            return

        cond = self._get_condition_by_item(selected[0])
        if not cond:
            return

        try:
            pixel = pyautogui.pixel(cond['x'], cond['y'])
            tolerance = cond.get('tolerance', self.app.settings.get("color_tolerance", 10))
            match = all(abs(pixel[i] - cond['color'][i]) <= tolerance for i in range(3))

            result_text = f"""📊 Condition Test Result

Condition ID: {cond['id']}
Position: ({cond['x']}, {cond['y']})
Target Color: RGB{cond['color']}
Current Color: RGB{pixel}
Tolerance: {tolerance}

Result: {'✅ PASSED' if match else '❌ FAILED'}"""

            if match:
                messagebox.showinfo("Test Result - PASSED", result_text)
                self.app.update_status(f"Condition '{cond['id']}' PASSED")
            else:
                messagebox.showwarning("Test Result - FAILED", result_text)
                self.app.update_status(f"Condition '{cond['id']}' FAILED")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test condition: {e}")

    def clear_all(self):
        """Очистка всех условий"""
        if not self.conditions:
            return
        if messagebox.askyesno("Confirm", "Delete ALL pixel conditions?"):
            self.conditions.clear()
            self.refresh_list()
            self.app.update_status("All pixel conditions cleared")

    def refresh_list(self):
        """Обновление списка условий"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for cond in self.conditions:
            self.tree.insert('', tk.END, values=(
                cond['id'],
                cond['x'],
                cond['y'],
                cond['color'][0],
                cond['color'][1],
                cond['color'][2],
                cond.get('tolerance', self.app.settings.get("color_tolerance", 10))
            ))

    def get_condition_by_id(self, cond_id):
        """Получить условие по ID"""
        for c in self.conditions:
            if c['id'] == cond_id:
                return c
        return None

    def show(self):
        """Показать окно"""
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.deiconify()
            self.window.lift()

    def hide(self):
        """Скрыть окно"""
        if self.window:
            self.window.withdraw()