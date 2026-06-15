"""
Clixpert S Pro Ultimate - Conditions Tab
Вкладка управления условиями (пиксельными и по изображению)
"""

import tkinter as tk
import os
from tkinter import ttk, messagebox


class ConditionsTab:
    """
    Вкладка управления условиями.
    Содержит список пиксельных условий и кнопки управления.
    """

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(parent, bg='#1a1a2e')
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов вкладки"""
        # Панель с ТРЕМЯ колонками
        paned = tk.PanedWindow(self.frame, bg='#1a1a2e', orient=tk.HORIZONTAL, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - пиксельные условия
        left_frame = tk.Frame(paned, bg='#1a1a2e')
        paned.add(left_frame, width=400)

        # Средняя панель - условия по изображению
        center_frame = tk.Frame(paned, bg='#1a1a2e')
        paned.add(center_frame, width=450)

        # Правая панель - звуковые условия
        right_frame = tk.Frame(paned, bg='#1a1a2e')
        paned.add(right_frame, width=450)

        # Создаём панели
        self._create_pixel_panel(left_frame)
        self._create_image_panel(center_frame)  # <-- ИСПРАВЛЕНО: убрали _no_refresh
        self._create_sound_panel(right_frame)

        # Информационная строка внизу
        info_label = tk.Label(
            self.frame,
            text="💡 Tip: Conditions can be used in actions to control execution flow",
            bg='#1a1a2e', fg='#888888'
        )
        info_label.pack(pady=5)

        # Обновляем все списки ПОСЛЕ создания всех панелей
        self.refresh()

    def _create_sound_panel(self, parent):
        """Создание панели звуковых условий"""
        sound_frame = tk.LabelFrame(
            parent, text="Sound Conditions",
            bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        sound_frame.pack(fill=tk.BOTH, expand=True)

        # Таблица условий
        columns = ('id', 'threshold', 'duration', 'action')
        self.sound_tree = ttk.Treeview(sound_frame, columns=columns, show='headings', height=12)
        self.sound_tree.heading('id', text='ID')
        self.sound_tree.heading('threshold', text='Threshold')
        self.sound_tree.heading('duration', text='Duration (s)')
        self.sound_tree.heading('action', text='Action')

        self.sound_tree.column('id', width=120)
        self.sound_tree.column('threshold', width=80)
        self.sound_tree.column('duration', width=80)
        self.sound_tree.column('action', width=150)

        self.sound_tree.pack(fill=tk.BOTH, expand=True)
        self.sound_tree.bind('<Double-1>', self._edit_sound_condition)

        # Кнопки управления
        btn_frame = tk.Frame(sound_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame, text="➕ Add", command=self._add_sound_condition,
            bg='#2a8c4a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="✏ Edit", command=self._edit_sound_condition,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="🗑 Delete", command=self._delete_sound_condition,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="📋 Test", command=self._test_sound_condition,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="🗑 Clear All", command=self._clear_all_sound,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        # Статус звука
        self.sound_status_label = tk.Label(
            sound_frame, text="🎤 PyAudio: " + ("✅ Available" if self._check_sound_available() else "❌ Not installed"),
            bg='#1e1e2f', fg='#88ff88' if self._check_sound_available() else '#ff8888',
            font=('Segoe UI', 9)
        )
        self.sound_status_label.pack(pady=5)

    def _check_sound_available(self):
        """Проверка доступности звука"""
        try:
            import pyaudio
            return True
        except ImportError:
            return False


    def _create_pixel_panel(self, parent):
        """Создание панели пиксельных условий"""
        pixel_frame = tk.LabelFrame(
            parent, text="Pixel Conditions",
            bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        pixel_frame.pack(fill=tk.BOTH, expand=True)

        # Таблица условий
        columns = ('id', 'x', 'y', 'r', 'g', 'b', 'tolerance')
        self.pixel_tree = ttk.Treeview(pixel_frame, columns=columns, show='headings', height=12)
        self.pixel_tree.heading('id', text='ID')
        self.pixel_tree.heading('x', text='X')
        self.pixel_tree.heading('y', text='Y')
        self.pixel_tree.heading('r', text='R')
        self.pixel_tree.heading('g', text='G')
        self.pixel_tree.heading('b', text='B')
        self.pixel_tree.heading('tolerance', text='Tolerance')

        self.pixel_tree.column('id', width=100)
        self.pixel_tree.column('x', width=60)
        self.pixel_tree.column('y', width=60)
        self.pixel_tree.column('r', width=50)
        self.pixel_tree.column('g', width=50)
        self.pixel_tree.column('b', width=50)
        self.pixel_tree.column('tolerance', width=70)

        self.pixel_tree.pack(fill=tk.BOTH, expand=True)
        self.pixel_tree.bind('<Double-1>', self._edit_pixel_condition)

        # Кнопки управления
        btn_frame = tk.Frame(pixel_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame, text="➕ Add", command=self._add_pixel_condition,
            bg='#2a8c4a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="✏ Edit", command=self._edit_pixel_condition,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="🗑 Delete", command=self._delete_pixel_condition,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="📋 Test", command=self._test_pixel_condition,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="🗑 Clear All", command=self._clear_all_pixel,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

    def _create_image_panel(self, parent):
        """Создание панели условий по изображению"""
        image_frame = tk.LabelFrame(
            parent, text="Image Conditions",
            bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        image_frame.pack(fill=tk.BOTH, expand=True)

        # Таблица условий
        columns = ('id', 'image', 'confidence', 'action')
        self.image_tree = ttk.Treeview(image_frame, columns=columns, show='headings', height=12)
        self.image_tree.heading('id', text='ID')
        self.image_tree.heading('image', text='Image')
        self.image_tree.heading('confidence', text='Confidence')
        self.image_tree.heading('action', text='Action')

        self.image_tree.column('id', width=120)
        self.image_tree.column('image', width=200)
        self.image_tree.column('confidence', width=80)
        self.image_tree.column('action', width=100)

        self.image_tree.pack(fill=tk.BOTH, expand=True)
        self.image_tree.bind('<Double-1>', self._edit_image_condition)

        # Кнопки управления
        btn_frame = tk.Frame(image_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            btn_frame, text="➕ Add", command=self._add_image_condition,
            bg='#2a8c4a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="✏ Edit", command=self._edit_image_condition,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="🗑 Delete", command=self._delete_image_condition,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="📋 Test", command=self._test_image_condition,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            btn_frame, text="🗑 Clear All", command=self._clear_all_image,
            bg='#8c2a2a', fg='white', bd=0, padx=10
        ).pack(side=tk.LEFT, padx=2)

    def refresh(self):
        """Обновление списков условий"""
        self._refresh_pixel_list()
        self._refresh_image_list()
        self._refresh_sound_list()

    def _refresh_pixel_list(self):
        """Обновление списка пиксельных условий"""
        for item in self.pixel_tree.get_children():
            self.pixel_tree.delete(item)

        if hasattr(self.app, 'condition_manager'):
            for cond in self.app.condition_manager.pixel_conditions:
                self.pixel_tree.insert('', tk.END, values=(
                    cond.id,
                    cond.x,
                    cond.y,
                    cond.color[0],
                    cond.color[1],
                    cond.color[2],
                    cond.tolerance
                ))

    def _refresh_image_list(self):
        """Обновление списка условий по изображению"""
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)

        if hasattr(self.app, 'condition_manager'):
            for cond in self.app.condition_manager.image_conditions:
                self.image_tree.insert('', tk.END, values=(
                    cond.id,
                    os.path.basename(cond.image_path) if cond.image_path else "N/A",
                    cond.confidence,
                    cond.action_on_match
                ))

    # ========== ПИКСЕЛЬНЫЕ УСЛОВИЯ ==========

    def _add_pixel_condition(self):
        """Добавление пиксельного условия - создаём НОВЫЙ диалог"""
        from ui.dialogs.pixel_condition import PixelConditionDialog
        # Создаём временный диалог для добавления
        dialog = PixelConditionDialog(self.app)
        dialog.add_condition()  # Открываем диалог добавления
        # Ждём закрытия и обновляем список
        self.app.root.update()
        self._refresh_pixel_list()

    def _edit_pixel_condition(self, event=None):
        """Редактирование пиксельного условия"""
        selected = self.pixel_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to edit")
            return

        item = selected[0]
        values = self.pixel_tree.item(item)['values']
        if not values:
            return

        cond_id = values[0]
        cond = self.app.condition_manager.get_pixel_condition(cond_id)
        if cond:
            from ui.dialogs.pixel_condition import PixelConditionDialog
            dialog = PixelConditionDialog(self.app)
            # Передаём существующее условие для редактирования
            dialog.add_condition(edit_item=item, existing_id=cond.id)
            self._refresh_pixel_list()

    def _delete_pixel_condition(self):
        """Удаление пиксельного условия"""
        selected = self.pixel_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to delete")
            return

        if messagebox.askyesno("Confirm", f"Delete {len(selected)} condition(s)?"):
            for item in selected:
                values = self.pixel_tree.item(item)['values']
                if values:
                    cond_id = values[0]
                    self.app.condition_manager.delete_pixel_condition(cond_id)
            self._refresh_pixel_list()
            self.app.update_status(f"Deleted {len(selected)} condition(s)")

    def _test_pixel_condition(self):
        """Тестирование пиксельного условия"""
        selected = self.pixel_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to test")
            return

        values = self.pixel_tree.item(selected[0])['values']
        if not values:
            return

        cond_id = values[0]
        cond = self.app.condition_manager.get_pixel_condition(cond_id)
        if not cond:
            return

        try:
            import pyautogui
            pixel = pyautogui.pixel(cond.x, cond.y)
            tolerance = cond.tolerance
            match = all(abs(pixel[i] - cond.color[i]) <= tolerance for i in range(3))

            result_text = f"""📊 Condition Test Result

Condition ID: {cond.id}
Position: ({cond.x}, {cond.y})
Target Color: RGB{cond.color}
Current Color: RGB{pixel}
Tolerance: {tolerance}

Result: {'✅ PASSED' if match else '❌ FAILED'}"""

            if match:
                messagebox.showinfo("Test Result - PASSED", result_text)
                self.app.update_status(f"Condition '{cond.id}' PASSED")
            else:
                messagebox.showwarning("Test Result - FAILED", result_text)
                self.app.update_status(f"Condition '{cond.id}' FAILED")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test condition: {e}")

    def _clear_all_pixel(self):
        """Очистка всех пиксельных условий"""
        if not self.pixel_tree.get_children():
            return
        if messagebox.askyesno("Confirm", "Delete ALL pixel conditions?"):
            self.app.condition_manager.clear_all()
            self._refresh_pixel_list()
            self.app.update_status("All pixel conditions cleared")

    # ========== УСЛОВИЯ ПО ИЗОБРАЖЕНИЮ ==========

    def _add_image_condition(self):
        """Добавление условия по изображению"""
        from ui.dialogs.image_condition import ImageConditionDialog
        dialog = ImageConditionDialog(self.app)
        dialog.add_condition()
        self.app.root.update()
        self._refresh_image_list()

    def _edit_image_condition(self, event=None):
        """Редактирование условия по изображению"""
        selected = self.image_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to edit")
            return

        item = selected[0]
        values = self.image_tree.item(item)['values']
        if not values:
            return

        cond_id = values[0]
        cond = self.app.condition_manager.get_image_condition(cond_id)
        if cond:
            from ui.dialogs.image_condition import ImageConditionDialog
            dialog = ImageConditionDialog(self.app)
            dialog.add_condition(edit_item=item, existing_id=cond.id)
            self._refresh_image_list()

    def _delete_image_condition(self):
        """Удаление условия по изображению"""
        selected = self.image_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to delete")
            return

        if messagebox.askyesno("Confirm", f"Delete {len(selected)} condition(s)?"):
            for item in selected:
                values = self.image_tree.item(item)['values']
                if values:
                    cond_id = values[0]
                    self.app.condition_manager.delete_image_condition(cond_id)
            self._refresh_image_list()
            self.app.update_status(f"Deleted {len(selected)} condition(s)")

    def _test_image_condition(self):
        """Тестирование условия по изображению"""
        selected = self.image_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to test")
            return

        values = self.image_tree.item(selected[0])['values']
        if not values:
            return

        cond_id = values[0]
        cond = self.app.condition_manager.get_image_condition(cond_id)
        if not cond:
            return

        if hasattr(self.app, 'find_image_advanced'):
            found, pos = self.app.find_image_advanced(
                cond.image_path,
                confidence=cond.confidence,
                multi_scale=cond.multi_scale,
                rotation=cond.rotation_tolerance,
                method=cond.search_method
            )

            if found:
                messagebox.showinfo("Test Result", f"✅ Image found at position: {pos}")
                self.app.update_status(f"Image condition '{cond.id}' PASSED")
            else:
                messagebox.showwarning("Test Result", "❌ Image not found")
                self.app.update_status(f"Image condition '{cond.id}' FAILED")

    def _clear_all_image(self):
        """Очистка всех условий по изображению"""
        if not self.image_tree.get_children():
            return
        if messagebox.askyesno("Confirm", "Delete ALL image conditions?"):
            self.app.condition_manager.image_conditions.clear()
            self.app.condition_manager.save()
            self._refresh_image_list()
            self.app.update_status("All image conditions cleared")

    def get_frame(self):
        """Получить фрейм вкладки"""
        return self.frame

    # ========== ЗВУКОВЫЕ УСЛОВИЯ ==========

    def _refresh_sound_list(self):
        """Обновление списка звуковых условий"""
        for item in self.sound_tree.get_children():
            self.sound_tree.delete(item)

        if hasattr(self.app, 'condition_manager') and hasattr(self.app.condition_manager, 'sound_conditions'):
            for cond in self.app.condition_manager.sound_conditions:
                action_text = cond.action_on_match
                if action_text == 'click_at_coords':
                    action_text = f"click at ({cond.click_x}, {cond.click_y})"
                self.sound_tree.insert('', tk.END, values=(
                    cond.id,
                    cond.threshold,
                    cond.duration,
                    action_text
                ))

    def _add_sound_condition(self):
        """Добавление звукового условия"""
        from ui.dialogs.sound_condition import SoundConditionDialog
        dialog = SoundConditionDialog(self.app)
        dialog.show()
        self._refresh_sound_list()

    def _edit_sound_condition(self, event=None):
        """Редактирование звукового условия"""
        selected = self.sound_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to edit")
            return

        item = selected[0]
        values = self.sound_tree.item(item)['values']
        if not values:
            return

        cond_id = values[0]
        if hasattr(self.app, 'condition_manager'):
            cond = self.app.condition_manager.get_sound_condition(cond_id)
            if cond:
                from ui.dialogs.sound_condition import SoundConditionDialog
                dialog = SoundConditionDialog(self.app)
                dialog.show()
                self._refresh_sound_list()

    def _delete_sound_condition(self):
        """Удаление звукового условия"""
        selected = self.sound_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to delete")
            return

        if messagebox.askyesno("Confirm", f"Delete {len(selected)} condition(s)?"):
            for item in selected:
                values = self.sound_tree.item(item)['values']
                if values:
                    cond_id = values[0]
                    self.app.condition_manager.delete_sound_condition(cond_id)
            self._refresh_sound_list()
            self.app.update_status(f"Deleted {len(selected)} condition(s)")

    def _test_sound_condition(self):
        """Тестирование звукового условия"""
        selected = self.sound_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Select a condition to test")
            return

        values = self.sound_tree.item(selected[0])['values']
        if not values:
            return

        cond_id = values[0]
        cond = self.app.condition_manager.get_sound_condition(cond_id)
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
                result = sound.wait_for_sound(cond.threshold, timeout=10)
                sound.cleanup()
                self.app.root.after(0, lambda: self._show_sound_test_result(cond, result))

            import threading
            threading.Thread(target=test, daemon=True).start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to test sound condition: {e}")

    def _show_sound_test_result(self, cond, result):
        """Показать результат теста звука"""
        if result:
            messagebox.showinfo("Test Result",
                                f"✅ Sound detected!\n\nCondition: {cond.id}\nThreshold: {cond.threshold}")
            self.app.update_status(f"Sound condition '{cond.id}' PASSED")
        else:
            messagebox.showwarning("Test Result",
                                   f"❌ Sound not detected within timeout\n\nCondition: {cond.id}\nThreshold: {cond.threshold}")
            self.app.update_status(f"Sound condition '{cond.id}' FAILED")

    def _clear_all_sound(self):
        """Очистка всех звуковых условий"""
        if not self.sound_tree.get_children():
            return
        if messagebox.askyesno("Confirm", "Delete ALL sound conditions?"):
            self.app.condition_manager.sound_conditions.clear()
            self.app.condition_manager.save()
            self._refresh_sound_list()
            self.app.update_status("All sound conditions cleared")

    def refresh_texts(self):
        """Обновление текстов интерфейса"""
        # Обновляем заголовки фреймов в PanedWindow
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for side in child.panes():
                    for sub in side.winfo_children():
                        if isinstance(sub, tk.LabelFrame):
                            text = sub.cget("text")
                            if text == "Pixel Conditions":
                                sub.config(text=self.app.get_text('pixel_conditions'))
                            elif text == "Image Conditions":
                                sub.config(text=self.app.get_text('image_conditions'))
                            elif text == "Sound Conditions":
                                sub.config(text=self.app.get_text('sound_conditions'))

        # Обновляем заголовки таблицы пиксельных условий
        if hasattr(self, 'pixel_tree'):
            self.pixel_tree.heading('id', text='ID')
            self.pixel_tree.heading('x', text='X')
            self.pixel_tree.heading('y', text='Y')
            self.pixel_tree.heading('r', text='R')
            self.pixel_tree.heading('g', text='G')
            self.pixel_tree.heading('b', text='B')
            self.pixel_tree.heading('tolerance', text=self.app.get_text('color_tolerance'))

        # Обновляем заголовки таблицы условий по изображению
        if hasattr(self, 'image_tree'):
            self.image_tree.heading('id', text='ID')
            self.image_tree.heading('image', text=self.app.get_text('select_image_file'))
            self.image_tree.heading('confidence', text=self.app.get_text('confidence'))
            self.image_tree.heading('action', text=self.app.get_text('action_on_match'))

        # Обновляем заголовки таблицы звуковых условий
        if hasattr(self, 'sound_tree'):
            self.sound_tree.heading('id', text='ID')
            self.sound_tree.heading('threshold', text=self.app.get_text('sound_threshold'))
            self.sound_tree.heading('duration', text=self.app.get_text('sound_duration'))
            self.sound_tree.heading('action', text=self.app.get_text('action_on_match'))

        # Обновляем статус звука
        if hasattr(self, 'sound_status_label'):
            status_text = "🎤 " + self.app.get_text('sound_status') + ": "
            if self._check_sound_available():
                status_text += "✅ " + self.app.get_text('available')
                self.sound_status_label.config(text=status_text, fg='#88ff88')
            else:
                status_text += "❌ " + self.app.get_text('not_installed')
                self.sound_status_label.config(text=status_text, fg='#ff8888')

        # Обновляем кнопки во всех панелях
        for child in self.frame.winfo_children():
            if isinstance(child, tk.PanedWindow):
                for side in child.panes():
                    for sub in side.winfo_children():
                        if isinstance(sub, tk.LabelFrame):
                            for btn_frame in sub.winfo_children():
                                if isinstance(btn_frame, tk.Frame):
                                    for btn in btn_frame.winfo_children():
                                        if isinstance(btn, tk.Button):
                                            text = btn.cget("text")
                                            if text == "➕ Add":
                                                btn.config(text="➕ " + self.app.get_text('add'))
                                            elif text == "✏ Edit":
                                                btn.config(text="✏ " + self.app.get_text('edit'))
                                            elif text == "🗑 Delete":
                                                btn.config(text="🗑 " + self.app.get_text('delete'))
                                            elif text == "📋 Test":
                                                btn.config(text="📋 " + self.app.get_text('test'))
                                            elif text == "🗑 Clear All":
                                                btn.config(text="🗑 " + self.app.get_text('clear_all'))

        # Обновляем информационную подсказку
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Label) and "Tip:" in child.cget("text"):
                child.config(text=self.app.get_text('conditions_tip'))