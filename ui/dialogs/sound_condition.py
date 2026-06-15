"""
Clixpert S Pro Ultimate - Sound Condition Dialog
Управление звуковыми условиями (добавление, редактирование, тестирование)
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SoundConditionDialog:
    """
    Диалог управления звуковыми условиями.
    Позволяет добавлять, редактировать, удалять и тестировать условия по звуку.
    """

    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        self.create_window()

    def create_window(self):
        """Создание главного окна диалога"""
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Sound Conditions Manager")
        self.window.geometry("700x450")
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
            main_frame, text="Sound Conditions",
            bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Таблица условий
        columns = ('id', 'threshold', 'duration', 'action')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.tree.heading('id', text='ID')
        self.tree.heading('threshold', text='Threshold')
        self.tree.heading('duration', text='Duration (s)')
        self.tree.heading('action', text='Action on Match')

        self.tree.column('id', width=150)
        self.tree.column('threshold', width=100)
        self.tree.column('duration', width=100)
        self.tree.column('action', width=200)

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

        # Статус доступности звука
        self.status_label = tk.Label(
            main_frame,
            text="🎤 Sound detection status: " + (
                "✅ Available" if self._check_sound_available() else "❌ PyAudio not installed"),
            bg='#1e1e2f', fg='#88ff88' if self._check_sound_available() else '#ff8888'
        )
        self.status_label.pack(pady=5)

        self.refresh_list()

    def _check_sound_available(self):
        """Проверка доступности звука"""
        try:
            import pyaudio
            return True
        except ImportError:
            return False

    def add_condition(self, edit_item=None, existing_id=None):
        """Добавление или редактирование условия"""
        if not self._check_sound_available():
            messagebox.showerror("Error",
                                 "PyAudio not installed. Sound detection disabled.\nInstall with: pip install pyaudio")
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("Add Sound Condition" if not edit_item else "Edit Sound Condition")
        dialog.geometry("450x500")
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

        # Порог звука
        tk.Label(main_frame, text="Sound Threshold (higher = louder):", bg='#1e1e2f', fg='white').pack(anchor=tk.W,
                                                                                                       pady=(10, 0))
        threshold_frame = tk.Frame(main_frame, bg='#1e1e2f')
        threshold_frame.pack(fill=tk.X, pady=5)

        threshold_var = tk.IntVar(value=500)
        threshold_scale = tk.Scale(
            threshold_frame, from_=0, to=2000, orient=tk.HORIZONTAL,
            variable=threshold_var, bg='#1e1e2f', fg='white', troughcolor='#2a2a3c',
            length=300
        )
        threshold_scale.pack(side=tk.LEFT)
        threshold_label = tk.Label(threshold_frame, textvariable=threshold_var, bg='#1e1e2f', fg='#88ff88', width=5)
        threshold_label.pack(side=tk.LEFT, padx=10)

        # Длительность
        tk.Label(main_frame, text="Minimum Duration (seconds):", bg='#1e1e2f', fg='white').pack(anchor=tk.W,
                                                                                                pady=(10, 0))
        duration_var = tk.DoubleVar(value=0.5)
        duration_scale = tk.Scale(
            main_frame, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL,
            variable=duration_var, bg='#1e1e2f', fg='white', troughcolor='#2a2a3c',
            length=300
        )
        duration_scale.pack(fill=tk.X, pady=5)
        tk.Label(main_frame, textvariable=duration_var, bg='#1e1e2f', fg='#88ff88').pack()

        # Действие при совпадении
        action_frame = tk.LabelFrame(
            main_frame, text="Action on Match", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        action_frame.pack(fill=tk.X, pady=10)

        action_var = tk.StringVar(value='click_center')
        action_combo = ttk.Combobox(
            action_frame, textvariable=action_var,
            values=['click_center', 'click_at_coords', 'hover', 'save_screenshot']
        )
        action_combo.pack(fill=tk.X)

        # Координаты для click_at_coords
        coords_frame = tk.Frame(action_frame, bg='#1e1e2f')
        coords_frame.pack(fill=tk.X, pady=5)

        tk.Label(coords_frame, text="X:", bg='#1e1e2f', fg='white').pack(side=tk.LEFT)
        x_var = tk.IntVar(value=0)
        tk.Entry(coords_frame, textvariable=x_var, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        tk.Label(coords_frame, text="Y:", bg='#1e1e2f', fg='white').pack(side=tk.LEFT)
        y_var = tk.IntVar(value=0)
        tk.Entry(coords_frame, textvariable=y_var, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        # Загрузка данных при редактировании
        if edit_item and existing_id:
            cond = self.app.condition_manager.get_sound_condition(existing_id)
            if cond:
                id_var.set(cond.id)
                threshold_var.set(cond.threshold)
                duration_var.set(cond.duration)
                action_var.set(cond.action_on_match)
                x_var.set(cond.click_x)
                y_var.set(cond.click_y)

        # Кнопки
        btn_frame = tk.Frame(main_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=10)

        def save():
            cond_id = id_var.get().strip()
            if not cond_id:
                messagebox.showerror("Error", "Please enter a condition ID")
                return

            # Проверяем через ConditionManager
            if not edit_item and self.app.condition_manager.get_sound_condition(cond_id):
                messagebox.showerror("Error", f"Condition ID '{cond_id}' already exists")
                return

            # Сохраняем через ConditionManager
            if edit_item and existing_id:
                self.app.condition_manager.delete_sound_condition(existing_id)

            self.app.condition_manager.add_sound_condition(
                cond_id=cond_id,
                threshold=threshold_var.get(),
                duration=duration_var.get(),
                action_on_match=action_var.get(),
                click_x=x_var.get(),
                click_y=y_var.get()
            )

            # Обновляем отображение
            self.refresh_list()
            if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'tabs'):
                self.app.main_window.tabs['conditions'].refresh()

            dialog.destroy()
            self.app.update_status(f"Sound condition '{cond_id}' saved")

        tk.Button(
            btn_frame, text="💾 Save", command=save,
            bg='#2a8c4a', fg='white', bd=0, padx=20, pady=5
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="❌ Cancel", command=dialog.destroy,
            bg='#8c2a2a', fg='white', bd=0, padx=20, pady=5
        ).pack(side=tk.LEFT, padx=5)

    def _get_condition_by_item(self, item):
        """Получить условие по элементу дерева"""
        values = self.tree.item(item)['values']
        if not values:
            return None
        cond_id = values[0]
        return self.app.condition_manager.get_sound_condition(cond_id)

    def edit_selected(self, event=None):
        """Редактирование выбранного условия"""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            cond = self._get_condition_by_item(item)
            if cond:
                self.add_condition(edit_item=item, existing_id=cond.id)

    def delete_selected(self):
        """Удаление выбранных условий"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to delete")
            return
        if messagebox.askyesno("Confirm", f"Delete {len(selected)} condition(s)?"):
            for item in selected:
                cond = self._get_condition_by_item(item)
                if cond:
                    self.app.condition_manager.delete_sound_condition(cond.id)
            self.refresh_list()
            if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'tabs'):
                self.app.main_window.tabs['conditions'].refresh()
            self.app.update_status(f"Deleted {len(selected)} condition(s)")

    def test_condition(self):
        """Тестирование выбранного условия"""
        if not self._check_sound_available():
            messagebox.showerror("Error", "PyAudio not installed. Cannot test sound condition.")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to test")
            return

        cond = self._get_condition_by_item(selected[0])
        if not cond:
            return

        try:
            from modules.sound_analyzer import SoundCondition
            sound = SoundCondition()
            if not sound.init():
                messagebox.showerror("Error", "Failed to initialize audio device")
                return

            self.app.update_status(f"Listening for sound (threshold={cond.threshold})...")

            def test():
                # Запускаем прослушивание перед ожиданием
                if sound.start(cond.threshold):
                    result = sound.wait_for_sound(cond.threshold, timeout=10)
                    sound.stop()
                else:
                    result = False
                sound.cleanup()
                self.app.root.after(0, lambda: self._show_test_result(cond, result))

            import threading
            threading.Thread(target=test, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to test sound condition: {e}")

    def _show_test_result(self, cond, result):
        """Показать результат теста"""
        if result:
            messagebox.showinfo("Test Result",
                                f"✅ Sound detected!\n\nCondition: {cond.id}\nThreshold: {cond.threshold}")
            self.app.update_status(f"Sound condition '{cond.id}' PASSED")
        else:
            messagebox.showwarning("Test Result",
                                   f"❌ Sound not detected within timeout\n\nCondition: {cond.id}\nThreshold: {cond.threshold}")
            self.app.update_status(f"Sound condition '{cond.id}' FAILED")

    def clear_all(self):
        """Очистка всех условий"""
        if not self.tree.get_children():
            return
        if messagebox.askyesno("Confirm", "Delete ALL sound conditions?"):
            self.app.condition_manager.sound_conditions.clear()
            self.app.condition_manager.save()
            self.refresh_list()
            if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'tabs'):
                self.app.main_window.tabs['conditions'].refresh()
            self.app.update_status("All sound conditions cleared")

    def refresh_list(self):
        """Обновление списка условий из ConditionManager"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for cond in self.app.condition_manager.get_all_sound_conditions():
            action_text = cond.action_on_match
            if action_text == 'click_at_coords':
                action_text = f"click at ({cond.click_x}, {cond.click_y})"
            self.tree.insert('', tk.END, values=(
                cond.id,
                cond.threshold,
                cond.duration,
                action_text
            ))

    def show(self):
        """Показать окно"""
        self.refresh_list()  # Обновляем при показе
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.deiconify()
            self.window.lift()

    def hide(self):
        """Скрыть окно"""
        if self.window:
            self.window.withdraw()