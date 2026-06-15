"""
Clixpert S Pro Ultimate - Profile Manager Module
Управление профилями: сохранение, загрузка, экспорт/импорт
"""

import json
import os
import tkinter as tk
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from tkinter import filedialog, messagebox


class ProfileManager:
    """
    Управление профилями программы.
    Профиль содержит: действия, условия, настройки, скрипты.
    """

    PROFILE_EXTENSION = ".clixpro"
    BACKUP_EXTENSION = ".bak"

    def __init__(self, app):
        self.app = app
        self.profiles_dir: Optional[Path] = None

    def set_profiles_dir(self, path: Path) -> None:
        """Установить директорию для профилей"""
        self.profiles_dir = path
        os.makedirs(self.profiles_dir, exist_ok=True)

    def get_profile_path(self, name: str) -> Path:
        """Получить полный путь к файлу профиля"""
        if not name.endswith(self.PROFILE_EXTENSION):
            name += self.PROFILE_EXTENSION
        return self.profiles_dir / name if self.profiles_dir else Path(name)

    def save_profile(
        self,
        name: str,
        actions: List[Dict],
        pixel_conditions: List[Dict],
        image_conditions: List[Dict],
        settings: Dict,
        expert_script: str,
        additional_data: Optional[Dict] = None
    ) -> bool:
        """
        Сохранить профиль.

        Args:
            name: Имя профиля
            actions: Список действий
            pixel_conditions: Пиксельные условия
            image_conditions: Условия по изображению
            settings: Настройки
            expert_script: Текст скрипта Expert Mode
            additional_data: Дополнительные данные

        Returns:
            True если сохранение успешно
        """
        profile = {
            "version": "5.0",
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "name": name,
            "actions": actions,
            "pixel_conditions": pixel_conditions,
            "image_conditions": image_conditions,
            "settings": settings,
            "expert_script": expert_script,
        }

        if additional_data:
            profile.update(additional_data)

        filepath = self.get_profile_path(name)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

    def load_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Загрузить профиль.

        Args:
            name: Имя профиля или полный путь

        Returns:
            Данные профиля или None при ошибке
        """
        filepath = Path(name) if Path(name).exists() else self.get_profile_path(name)

        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None

    def delete_profile(self, name: str) -> bool:
        """
        Удалить профиль.

        Args:
            name: Имя профиля

        Returns:
            True если удаление успешно
        """
        filepath = self.get_profile_path(name)

        if not filepath.exists():
            return False

        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting profile: {e}")
            return False

    def get_profile_list(self) -> List[Dict[str, Any]]:
        """
        Получить список всех профилей.

        Returns:
            Список с информацией о профилях
        """
        if not self.profiles_dir or not self.profiles_dir.exists():
            return []

        profiles = []
        for filepath in self.profiles_dir.glob(f"*{self.PROFILE_EXTENSION}"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profiles.append({
                        "name": data.get("name", filepath.stem),
                        "filepath": str(filepath),
                        "size": filepath.stat().st_size,
                        "created": data.get("created"),
                        "modified": data.get("modified"),
                        "actions_count": len(data.get("actions", [])),
                        "conditions_count": len(data.get("pixel_conditions", [])),
                    })
            except Exception:
                profiles.append({
                    "name": filepath.stem,
                    "filepath": str(filepath),
                    "size": filepath.stat().st_size,
                    "created": None,
                    "modified": None,
                    "actions_count": 0,
                    "conditions_count": 0,
                })

        return sorted(profiles, key=lambda x: x.get("modified", ""), reverse=True)

    def backup_profile(self, name: str) -> Optional[str]:
        """
        Создать резервную копию профиля.

        Args:
            name: Имя профиля

        Returns:
            Путь к резервной копии или None
        """
        filepath = self.get_profile_path(name)
        if not filepath.exists():
            return None

        backup_path = filepath.with_suffix(self.BACKUP_EXTENSION + filepath.suffix)

        try:
            shutil.copy2(filepath, backup_path)
            return str(backup_path)
        except Exception as e:
            print(f"Error backing up profile: {e}")
            return None

    def restore_backup(self, name: str) -> bool:
        """
        Восстановить профиль из резервной копии.

        Args:
            name: Имя профиля

        Returns:
            True если восстановление успешно
        """
        filepath = self.get_profile_path(name)
        backup_path = filepath.with_suffix(self.BACKUP_EXTENSION + filepath.suffix)

        if not backup_path.exists():
            return False

        try:
            shutil.copy2(backup_path, filepath)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    def export_profile(self, name: str, export_path: str) -> bool:
        """
        Экспортировать профиль в указанное место.

        Args:
            name: Имя профиля
            export_path: Путь для экспорта

        Returns:
            True если экспорт успешен
        """
        filepath = self.get_profile_path(name)
        if not filepath.exists():
            return False

        try:
            shutil.copy2(filepath, export_path)
            return True
        except Exception as e:
            print(f"Error exporting profile: {e}")
            return False

    def import_profile(self, import_path: str) -> Optional[str]:
        """
        Импортировать профиль из файла.

        Args:
            import_path: Путь к файлу профиля

        Returns:
            Имя импортированного профиля или None
        """
        source = Path(import_path)
        if not source.exists():
            return None

        if not source.suffix == self.PROFILE_EXTENSION:
            return None

        try:
            # Проверяем валидность профиля
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "version" not in data:
                    return None

            # Копируем в директорию профилей
            dest = self.get_profile_path(source.stem)
            shutil.copy2(source, dest)
            return source.stem
        except Exception as e:
            print(f"Error importing profile: {e}")
            return None

    def get_profile_data(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Получить данные профиля (без загрузки в приложение).

        Args:
            name: Имя профиля

        Returns:
            Данные профиля или None
        """
        return self.load_profile(name)

    def apply_profile(self, name: str) -> bool:
        """
        Применить профиль к текущему приложению.

        Args:
            name: Имя профиля

        Returns:
            True если применение успешно
        """
        profile = self.load_profile(name)
        if not profile:
            return False

        if not self.app:
            return False

        # Загрузка действий
        if hasattr(self.app, 'action_manager'):
            self.app.action_manager.from_dict_list(profile.get("actions", []))
            if hasattr(self.app, 'main_window'):
                self.app.main_window.update_actions_tree()

        # Загрузка условий
        if hasattr(self.app, 'condition_manager'):
            # Очищаем существующие условия
            self.app.condition_manager.pixel_conditions.clear()
            self.app.condition_manager.image_conditions.clear()

            # Загружаем пиксельные условия
            pixel_conditions = profile.get("pixel_conditions", [])
            for cond_data in pixel_conditions:
                from core.conditions import PixelCondition
                cond = PixelCondition.from_dict(cond_data)
                self.app.condition_manager.pixel_conditions.append(cond)

            # Загружаем условия по изображению
            image_conditions = profile.get("image_conditions", [])
            for cond_data in image_conditions:
                from core.conditions import ImageCondition
                cond = ImageCondition.from_dict(cond_data)
                self.app.condition_manager.image_conditions.append(cond)

            self.app.condition_manager.save()

            # Обновляем UI
            if hasattr(self.app, 'main_window'):
                self.app.main_window.refresh_conditions()

        # Загрузка настроек
        settings = profile.get("settings", {})
        if hasattr(self.app, 'settings'):
            self.app.settings.update(settings)
            self.app.save_settings()

            # Применяем настройки Always on top
            if hasattr(self.app, 'update_always_on_top'):
                self.app.update_always_on_top()

        # Загрузка скрипта
        expert_script = profile.get("expert_script", "")
        if hasattr(self.app, 'main_window') and self.app.main_window:
            self.app.main_window.set_expert_script(expert_script)

        # Обновляем UI
        if hasattr(self.app, 'main_window'):
            self.app.main_window.update_status(f"✅ Profile '{name}' loaded")

        return True

    def create_empty_profile(self, name: str) -> bool:
        """
        Создать пустой профиль.

        Args:
            name: Имя профиля

        Returns:
            True если создание успешно
        """
        empty_profile = {
            "version": "5.0",
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "name": name,
            "actions": [],
            "pixel_conditions": [],
            "image_conditions": [],
            "settings": {},
            "expert_script": "# Clixpert S Pro Ultimate Script\n\nprint(\"Hello from new profile!\")\n",
        }

        filepath = self.get_profile_path(name)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(empty_profile, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error creating empty profile: {e}")
            return False

    def get_profile_size(self, name: str) -> int:
        """Получить размер профиля в байтах"""
        filepath = self.get_profile_path(name)
        return filepath.stat().st_size if filepath.exists() else 0

    def profile_exists(self, name: str) -> bool:
        """Проверить существование профиля"""
        return self.get_profile_path(name).exists()

    # ========== ДОБАВЛЕННЫЕ МЕТОДЫ ДЛЯ UI ==========

    def save_current_profile(self) -> bool:
        """
        Сохранить текущее состояние приложения в профиль.
        Открывает диалог выбора имени файла.
        """
        if not self.app:
            return False

        # Сбор данных для сохранения
        actions = self.app.action_manager.to_dict_list() if hasattr(self.app, 'action_manager') else []

        pixel_conditions = []
        if hasattr(self.app, 'condition_manager'):
            for cond in self.app.condition_manager.pixel_conditions:
                pixel_conditions.append(cond.to_dict())

        image_conditions = []
        if hasattr(self.app, 'condition_manager'):
            for cond in self.app.condition_manager.image_conditions:
                image_conditions.append(cond.to_dict())

        settings = self.app.settings.copy() if hasattr(self.app, 'settings') else {}

        expert_script = ""
        if hasattr(self.app, 'main_window') and self.app.main_window:
            expert_script = self.app.main_window.get_expert_script()

        # Диалог сохранения
        filepath = filedialog.asksaveasfilename(
            defaultextension=self.PROFILE_EXTENSION,
            filetypes=[("Clixpert Pro files", f"*{self.PROFILE_EXTENSION}"), ("JSON files", "*.json")],
            title="Save Profile"
        )

        if not filepath:
            return False

        name = Path(filepath).stem
        success = self.save_profile(
            name=name,
            actions=actions,
            pixel_conditions=pixel_conditions,
            image_conditions=image_conditions,
            settings=settings,
            expert_script=expert_script
        )

        if success and self.app:
            self.app.update_status(f"💾 Profile saved: {name}")

        return success

    def load_profile_dialog(self) -> bool:
        """
        Открыть диалог выбора профиля для загрузки.
        """
        if not self.app:
            return False

        # Диалог выбора файла
        filepath = filedialog.askopenfilename(
            filetypes=[("Clixpert Pro files", f"*{self.PROFILE_EXTENSION}"), ("JSON files", "*.json")],
            title="Load Profile"
        )

        if not filepath:
            return False

        name = Path(filepath).stem
        return self.apply_profile(name)

    def show_profile_list_dialog(self) -> Optional[str]:
        """
        Показать диалог со списком профилей для выбора.

        Returns:
            Имя выбранного профиля или None
        """
        profiles = self.get_profile_list()

        if not profiles:
            messagebox.showinfo("Info", "No profiles found")
            return None

        # Создаём диалог выбора
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Select Profile")
        dialog.geometry("500x400")
        dialog.configure(bg='#1e1e2f')
        dialog.transient(self.app.root)
        dialog.grab_set()

        tk.Label(
            dialog, text="Select a profile to load:",
            bg='#1e1e2f', fg='white', font=('Segoe UI', 12, 'bold')
        ).pack(pady=10)

        # Список профилей
        listbox = tk.Listbox(dialog, bg='#2a2a3c', fg='white', font=('Segoe UI', 10), height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for profile in profiles:
            display_text = f"{profile['name']} - {profile['actions_count']} actions, {profile['conditions_count']} conditions"
            listbox.insert(tk.END, display_text)

        result = [None]

        def on_select():
            selection = listbox.curselection()
            if selection:
                result[0] = profiles[selection[0]]['name']
                dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg='#1e1e2f')
        btn_frame.pack(fill=tk.X, pady=10)

        tk.Button(
            btn_frame, text="Load", command=on_select,
            bg='#2a8c4a', fg='white', bd=0, padx=20
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame, text="Cancel", command=on_cancel,
            bg='#8c2a2a', fg='white', bd=0, padx=20
        ).pack(side=tk.LEFT, padx=10)

        self.app.root.wait_window(dialog)
        return result[0]

    def backup_current_profile(self) -> bool:
        """
        Создать резервную копию текущего профиля.
        """
        if not self.profiles_dir:
            return False

        # Получаем список профилей
        profiles = self.get_profile_list()
        if not profiles:
            messagebox.showinfo("Info", "No profiles to backup")
            return False

        for profile in profiles:
            self.backup_profile(profile['name'])

        self.app.update_status("✅ Profiles backed up")
        return True


if __name__ == "__main__":
    # Тестирование модуля профилей
    print("=" * 50)
    print("Testing ProfileManager Module")
    print("=" * 50)

    # Создаём мок-приложение
    class MockApp:
        def __init__(self):
            self.settings = {}
            self.action_manager = None
            self.condition_manager = None
            self.main_window = None
            self.root = None

        def save_settings(self):
            pass

        def update_status(self, msg):
            print(f"   Status: {msg}")

    app = MockApp()
    manager = ProfileManager(app)

    # Создаём временную директорию для тестов
    test_dir = Path("./test_profiles")
    manager.set_profiles_dir(test_dir)

    print(f"\n📁 Profiles directory: {manager.profiles_dir}")

    # Создаём пустой профиль
    print("\n📋 Creating empty profile:")
    if manager.create_empty_profile("test_profile"):
        print("   Empty profile created")

    # Получаем список профилей
    print("\n📋 Profile list:")
    for p in manager.get_profile_list():
        print(f"   {p['name']} - {p['size']} bytes - {p['actions_count']} actions")

    # Очистка
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)

    print("\n✅ Module ready!")