"""
Clixpert S Pro Ultimate - Hotkey Manager Module
Управление глобальными горячими клавишами
"""

import threading
import time
from typing import Dict, Callable, Optional, Any
from dataclasses import dataclass, field


@dataclass
class HotkeyAction:
    """Горячая клавиша и связанное с ней действие"""
    key: str
    callback: Callable
    description: str = ""
    enabled: bool = True
    modifiers: list = field(default_factory=list)


class HotkeyManager:
    """
    Управление глобальными горячими клавишами.
    Использует библиотеку keyboard для перехвата клавиш.
    """

    def __init__(self, app):
        self.app = app
        self.hotkeys: Dict[str, HotkeyAction] = {}
        self._registered = False
        self._listener_thread: Optional[threading.Thread] = None
        self._running = False

        # Предопределённые горячие клавиши
        self._default_hotkeys = {
            "toggle": HotkeyAction(
                key="f1",
                callback=self._on_toggle,
                description="Start/Stop cycle"
            ),
            "record_click": HotkeyAction(
                key="f2",
                callback=self._on_record_click,
                description="Record click at cursor position"
            ),
            "record_key": HotkeyAction(
                key="f3",
                callback=self._on_record_key,
                description="Record key press"
            ),
            "record_start": HotkeyAction(
                key="f8",
                callback=self._on_record_start,
                description="Start recording"
            ),
            "record_stop": HotkeyAction(
                key="f9",
                callback=self._on_record_stop,
                description="Stop recording"
            ),
            "run_script": HotkeyAction(
                key="ctrl+shift+r",
                callback=self._on_run_script,
                description="Run Expert Mode script"
            ),
            "stop_script": HotkeyAction(
                key="ctrl+shift+s",
                callback=self._on_stop_script,
                description="Stop Expert Mode script"
            ),
        }

    def _on_toggle(self):
        """Обработчик клавиши Start/Stop"""
        if self.app.running:
            self.app.stop_cycle()
        else:
            self.app.start_cycle()

    def _on_record_click(self):
        """Обработчик записи клика"""
        if hasattr(self.app, 'record_click_action'):
            self.app.record_click_action()

    def _on_record_key(self):
        """Обработчик записи клавиши"""
        if hasattr(self.app, 'start_key_recording'):
            self.app.start_key_recording()

    def _on_record_start(self):
        """Обработчик начала записи"""
        if hasattr(self.app, 'recorder') and hasattr(self.app.recorder, 'start_recording'):
            self.app.recorder.start_recording()

    def _on_record_stop(self):
        """Обработчик остановки записи"""
        if hasattr(self.app, 'recorder') and hasattr(self.app.recorder, 'stop_recording'):
            self.app.recorder.stop_recording()

    def _on_run_script(self):
        """Обработчик запуска скрипта"""
        if hasattr(self.app, 'run_script'):
            self.app.run_script()

    def _on_stop_script(self):
        """Обработчик остановки скрипта"""
        if hasattr(self.app, 'stop_script'):
            self.app.stop_script()

    def register(self, name: str, key: str, callback: Callable, description: str = "") -> bool:
        """
        Зарегистрировать горячую клавишу.

        Args:
            name: Уникальное имя клавиши
            key: Клавиша (например: 'f1', 'ctrl+c', 'alt+shift+x')
            callback: Функция для вызова
            description: Описание действия

        Returns:
            True если регистрация успешна
        """
        if name in self.hotkeys:
            return False

        self.hotkeys[name] = HotkeyAction(
            key=key,
            callback=callback,
            description=description
        )

        if self._registered:
            self._register_single(name, self.hotkeys[name])

        return True

    def unregister(self, name: str) -> bool:
        """
        Отменить регистрацию горячей клавиши.

        Args:
            name: Имя клавиши для удаления

        Returns:
            True если удаление успешно
        """
        if name not in self.hotkeys:
            return False

        if self._registered:
            self._unregister_single(self.hotkeys[name].key)

        del self.hotkeys[name]
        return True

    def _register_single(self, name: str, action: HotkeyAction) -> None:
        """Регистрация одной клавиши в системе"""
        try:
            import keyboard
            if action.enabled:
                keyboard.add_hotkey(action.key, action.callback)
        except Exception as e:
            print(f"Error registering hotkey {name}: {e}")

    def _unregister_single(self, key: str) -> None:
        """Отмена регистрации одной клавиши"""
        try:
            import keyboard
            keyboard.remove_hotkey(key)
        except Exception:
            pass

    def register_all(self) -> None:
        """Зарегистрировать все горячие клавиши"""
        try:
            import keyboard
            keyboard.unhook_all()

            # Регистрируем предустановленные клавиши
            for name, action in self._default_hotkeys.items():
                if action.enabled:
                    keyboard.add_hotkey(action.key, action.callback)

            # Регистрируем пользовательские
            for name, action in self.hotkeys.items():
                if action.enabled:
                    keyboard.add_hotkey(action.key, action.callback)

            self._registered = True

        except ImportError:
            print("Warning: keyboard module not available. Hotkeys disabled.")
        except Exception as e:
            print(f"Error registering hotkeys: {e}")

    def unregister_all(self) -> None:
        """Отменить регистрацию всех горячих клавиш"""
        try:
            import keyboard
            keyboard.unhook_all()
            self._registered = False
        except Exception:
            pass

    def set_hotkey(self, name: str, key: str) -> bool:
        """
        Изменить горячую клавишу.

        Args:
            name: Имя клавиши
            key: Новая клавиша

        Returns:
            True если изменение успешно
        """
        if name not in self._default_hotkeys and name not in self.hotkeys:
            return False

        action = self._default_hotkeys.get(name) or self.hotkeys.get(name)
        if action:
            if self._registered:
                self._unregister_single(action.key)
            action.key = key
            if self._registered:
                self._register_single(name, action)
            return True
        return False

    def enable_hotkey(self, name: str, enabled: bool) -> bool:
        """
        Включить/отключить горячую клавишу.

        Args:
            name: Имя клавиши
            enabled: True - включить, False - отключить

        Returns:
            True если изменение успешно
        """
        action = self._default_hotkeys.get(name) or self.hotkeys.get(name)
        if action:
            if self._registered and action.enabled != enabled:
                if enabled:
                    self._register_single(name, action)
                else:
                    self._unregister_single(action.key)
            action.enabled = enabled
            return True
        return False

    def get_hotkey(self, name: str) -> Optional[str]:
        """Получить клавишу по имени"""
        action = self._default_hotkeys.get(name) or self.hotkeys.get(name)
        return action.key if action else None

    def get_description(self, name: str) -> str:
        """Получить описание клавиши"""
        action = self._default_hotkeys.get(name) or self.hotkeys.get(name)
        return action.description if action else ""

    def get_all_hotkeys(self) -> Dict[str, Dict[str, Any]]:
        """Получить все горячие клавиши"""
        result = {}
        for name, action in self._default_hotkeys.items():
            result[name] = {
                "key": action.key,
                "description": action.description,
                "enabled": action.enabled,
                "default": True
            }
        for name, action in self.hotkeys.items():
            result[name] = {
                "key": action.key,
                "description": action.description,
                "enabled": action.enabled,
                "default": False
            }
        return result

    def add_custom_hotkey(self, name: str, key: str, callback: Callable, description: str = "") -> bool:
        """
        Добавить пользовательскую горячую клавишу.

        Args:
            name: Уникальное имя
            key: Клавиша
            callback: Функция
            description: Описание

        Returns:
            True если добавление успешно
        """
        if name in self._default_hotkeys or name in self.hotkeys:
            return False
        return self.register(name, key, callback, description)

    def remove_custom_hotkey(self, name: str) -> bool:
        """
        Удалить пользовательскую горячую клавишу.

        Args:
            name: Имя клавиши

        Returns:
            True если удаление успешно
        """
        if name in self._default_hotkeys:
            return False
        return self.unregister(name)

    def is_key_registered(self, key: str) -> bool:
        """Проверить, зарегистрирована ли клавиша"""
        for action in self._default_hotkeys.values():
            if action.key == key:
                return True
        for action in self.hotkeys.values():
            if action.key == key:
                return True
        return False

    def get_conflicts(self) -> Dict[str, str]:
        """Найти конфликты между горячими клавишами"""
        conflicts = {}
        keys = {}

        all_actions = {**self._default_hotkeys, **self.hotkeys}

        for name, action in all_actions.items():
            if action.key in keys:
                conflicts[name] = keys[action.key]
            else:
                keys[action.key] = name

        return conflicts

    def start_listener(self) -> None:
        """Запустить отдельный поток для прослушивания клавиш"""
        if self._listener_thread and self._listener_thread.is_alive():
            return

        self._running = True
        self._listener_thread = threading.Thread(target=self._listen, daemon=True)
        self._listener_thread.start()

    def _listen(self) -> None:
        """Поток прослушивания клавиш"""
        try:
            import keyboard
            while self._running:
                time.sleep(0.1)
        except Exception:
            pass

    def stop_listener(self) -> None:
        """Остановить прослушивание клавиш"""
        self._running = False
        if self._listener_thread:
            self._listener_thread.join(timeout=1.0)

    def simulate_hotkey(self, name: str) -> bool:
        """
        Имитировать нажатие горячей клавиши.

        Args:
            name: Имя клавиши

        Returns:
            True если клавиша найдена и выполнена
        """
        action = self._default_hotkeys.get(name) or self.hotkeys.get(name)
        if action and action.enabled:
            try:
                action.callback()
                return True
            except Exception as e:
                print(f"Error simulating hotkey {name}: {e}")
        return False


if __name__ == "__main__":
    # Тестирование модуля горячих клавиш
    print("=" * 50)
    print("Testing HotkeyManager Module")
    print("=" * 50)


    # Создаём мок-приложение
    class MockApp:
        def __init__(self):
            self.running = False

        def start_cycle(self):
            print("   -> Starting cycle")
            self.running = True

        def stop_cycle(self):
            print("   -> Stopping cycle")
            self.running = False

        def record_click_action(self):
            print("   -> Recording click")

        def start_key_recording(self):
            print("   -> Recording key")

        def run_script(self):
            print("   -> Running script")

        def stop_script(self):
            print("   -> Stopping script")


    app = MockApp()
    hotkeys = HotkeyManager(app)

    print("\n📋 Default hotkeys:")
    for name, info in hotkeys.get_all_hotkeys().items():
        print(f"   {name}: {info['key']} - {info['description']}")

    print("\n🔍 Checking conflicts:")
    conflicts = hotkeys.get_conflicts()
    if conflicts:
        print(f"   Conflicts found: {conflicts}")
    else:
        print("   No conflicts")

    print("\n✅ Module ready!")