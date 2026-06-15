"""
Clixpert S Pro Ultimate - Image Condition Dialog
Управление условиями по изображению (добавление, редактирование, тестирование)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import base64
from PIL import Image, ImageTk


class ImageConditionDialog:
    """
    Диалог управления условиями по изображению.
    Позволяет добавлять, редактировать, удалять и тестировать условия.
    """

    def __init__(self, parent_app):
        self.app = parent_app
        self.window = None
        self.current_image_data = None
        self.create_window()

    def create_window(self):
        """Создание главного окна диалога"""
        self.window = tk.Toplevel(self.app.root)
        self.window.title("Image Conditions Manager")
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
            main_frame, text="Image Conditions",
            bg='#1e1e2f', fg='white', padx=5, pady=5
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Таблица условий
        columns = ('id', 'image', 'confidence', 'action')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.tree.heading('id', text='ID')
        self.tree.heading('image', text='Image')
        self.tree.heading('confidence', text='Confidence')
        self.tree.heading('action', text='Action')

        self.tree.column('id', width=150)
        self.tree.column('image', width=300)
        self.tree.column('confidence', width=100)
        self.tree.column('action', width=150)

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
            btn_frame, text="➕ Add Multiple", command=self.add_multiple_conditions,
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
            text="💡 Tip: Image conditions allow searching for images on screen",
            bg='#1e1e2f', fg='#888888'
        ).pack()

        self.refresh_list()

    def add_multiple_conditions(self):
        """Добавление нескольких изображений сразу"""
        filepaths = filedialog.askopenfilenames(
            title="Select Multiple Images",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )

        if not filepaths:
            return

        added_count = 0
        for filepath in filepaths:
            # Генерируем ID из имени файла
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            cond_id = base_name
            counter = 1

            # Если ID уже существует, добавляем номер
            while self.app.condition_manager.get_image_condition(cond_id):
                cond_id = f"{base_name}_{counter}"
                counter += 1

            # Добавляем условие
            self.app.condition_manager.add_image_condition(
                cond_id=cond_id,
                image_path=filepath,
                confidence=0.8,
                multi_scale=False,
                action_on_match='click_center'
            )
            added_count += 1

        self.refresh_list()
        if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'tabs'):
            self.app.main_window.tabs['conditions'].refresh()
        self.app.update_status(f"Added {added_count} image conditions")

    def add_condition(self, edit_item=None, existing_id=None):
        """Добавление или редактирование условия"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Image Condition" if not edit_item else "Edit Image Condition")
        dialog.geometry("550x650")
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

        # Выбор изображения
        image_frame = tk.LabelFrame(
            main_frame, text="Image File", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        image_frame.pack(fill=tk.X, pady=10)

        image_path_var = tk.StringVar()
        image_preview = tk.Label(image_frame, bg='gray', width=100, height=80)
        image_preview.pack(pady=5)

        def select_image():
            filepath = filedialog.askopenfilename(
                filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
            )
            if filepath:
                image_path_var.set(filepath)
                try:
                    img = Image.open(filepath)
                    img.thumbnail((150, 100))
                    photo = ImageTk.PhotoImage(img)
                    image_preview.config(image=photo, bg='#1e1e2f')
                    image_preview.image = photo
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load image: {e}")

        tk.Button(
            image_frame, text="📁 Select Image", command=select_image,
            bg='#3a3a5c', fg='white', bd=0, padx=10
        ).pack(pady=5)

        # Confidence
        conf_frame = tk.LabelFrame(
            main_frame, text="Confidence (0.5-1.0)", bg='#1e1e2f', fg='white', padx=10, pady=10
        )
        conf_frame.pack(fill=tk.X, pady=10)

        conf_var = tk.DoubleVar(value=0.8)
        conf_scale = tk.Scale(
            conf_frame, from_=0.5, to=1.0, resolution=0.01, variable=conf_var,
            orient=tk.HORIZONTAL, length=200, bg='#1e1e2f', fg='white', troughcolor='#2a2a3c'
        )
        conf_scale.pack()
        tk.Label(conf_frame, textvariable=conf_var, bg='#1e1e2f', fg='#88ff88').pack()

        # Multi-scale
        multi_scale_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            main_frame, text="Multi-scale search (for different sizes)", variable=multi_scale_var,
            bg='#1e1e2f', fg='white', selectcolor='#1e1e2f'
        ).pack(anchor=tk.W, pady=5)

        # Action on match
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
        offset_x_var = tk.IntVar(value=0)
        tk.Entry(coords_frame, textvariable=offset_x_var, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        tk.Label(coords_frame, text="Y:", bg='#1e1e2f', fg='white').pack(side=tk.LEFT)
        offset_y_var = tk.IntVar(value=0)
        tk.Entry(coords_frame, textvariable=offset_y_var, width=6, bg='#2a2a3c', fg='white').pack(side=tk.LEFT, padx=5)

        # Загрузка данных при редактировании
        if edit_item and existing_id:
            cond = self.app.condition_manager.get_image_condition(existing_id)
            if cond:
                id_var.set(cond.id)
                image_path_var.set(cond.image_path)
                conf_var.set(cond.confidence)
                multi_scale_var.set(cond.multi_scale)
                action_var.set(cond.action_on_match)
                offset_x_var.set(cond.offset_x)
                offset_y_var.set(cond.offset_y)

                # Загружаем предпросмотр
                if cond.image_path and os.path.exists(cond.image_path):
                    try:
                        img = Image.open(cond.image_path)
                        img.thumbnail((150, 100))
                        photo = ImageTk.PhotoImage(img)
                        image_preview.config(image=photo, bg='#1e1e2f')
                        image_preview.image = photo
                    except:
                        pass

        # Кнопки
        btn_frame = tk.Frame(main_frame, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=10)

        def save():
            cond_id = id_var.get().strip()
            if not cond_id:
                messagebox.showerror("Error", "Please enter a condition ID")
                return

            # Проверяем через ConditionManager
            if not edit_item and self.app.condition_manager.get_image_condition(cond_id):
                messagebox.showerror("Error", f"Condition ID '{cond_id}' already exists")
                return

            image_path = image_path_var.get().strip()
            if not image_path:
                messagebox.showerror("Error", "Please select an image file")
                return

            # Сохраняем через ConditionManager
            if edit_item and existing_id:
                self.app.condition_manager.delete_image_condition(existing_id)

            self.app.condition_manager.add_image_condition(
                cond_id=cond_id,
                image_path=image_path,
                confidence=conf_var.get(),
                multi_scale=multi_scale_var.get(),
                action_on_match=action_var.get(),
                offset_x=offset_x_var.get(),
                offset_y=offset_y_var.get()
            )

            # Обновляем отображение
            self.refresh_list()
            if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'tabs'):
                self.app.main_window.tabs['conditions'].refresh()

            dialog.destroy()
            self.app.update_status(f"Image condition '{cond_id}' saved")

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
        return self.app.condition_manager.get_image_condition(cond_id)

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
                    self.app.condition_manager.delete_image_condition(cond.id)
            self.refresh_list()
            if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'tabs'):
                self.app.main_window.tabs['conditions'].refresh()
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

    def clear_all(self):
        """Очистка всех условий"""
        if not self.tree.get_children():
            return
        if messagebox.askyesno("Confirm", "Delete ALL image conditions?"):
            self.app.condition_manager.image_conditions.clear()
            self.app.condition_manager.save()
            self.refresh_list()
            if hasattr(self.app, 'main_window') and hasattr(self.app.main_window, 'tabs'):
                self.app.main_window.tabs['conditions'].refresh()
            self.app.update_status("All image conditions cleared")

    def refresh_list(self):
        """Обновление списка условий из ConditionManager"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for cond in self.app.condition_manager.get_all_image_conditions():
            self.tree.insert('', tk.END, values=(
                cond.id,
                os.path.basename(cond.image_path) if cond.image_path else "N/A",
                cond.confidence,
                cond.action_on_match
            ))

    def show(self):
        """Показать окно"""
        self.refresh_list()
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.deiconify()
            self.window.lift()

    def hide(self):
        """Скрыть окно"""
        if self.window:
            self.window.withdraw()