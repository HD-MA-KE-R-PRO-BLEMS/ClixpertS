"""
Clixpert S Pro Ultimate - Action Recorder Module
Запись действий пользователя (клики, клавиши, движение мыши)
"""

import time
import threading
import keyboard
import pyautogui
from typing import List, Dict, Any, Optional
from datetime import datetime
from pynput import mouse as pynput_mouse


class ActionRecorder:
    """
    Запись действий пользователя для последующего воспроизведения.
    Записывает: клики мыши, нажатия клавиш, движение мыши.
    """

    def __init__(self, app=None):
        self.app = app
        self.recording = False
        self.recorded_actions: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        self.last_pos: Optional[tuple] = None
        self.record_mouse_movement = True
        self.record_clicks = True
        self.record_keys = True
        self._tracking_thread: Optional[threading.Thread] = None
        self._mouse_listener: Optional[pynput_mouse.Listener] = None

    def start_recording(self, record_mouse: bool = True, record_clicks: bool = True, record_keys: bool = True) -> None:
        """
        Начать запись действий.

        Args:
            record_mouse: Записывать движение мыши
            record_clicks: Записывать клики мыши
            record_keys: Записывать нажатия клавиш
        """
        if self.recording:
            return

        self.recording = True
        self.recorded_actions = []
        self.start_time = time.time()
        self.last_pos = pyautogui.position()
        self.record_mouse_movement = record_mouse
        self.record_clicks = record_clicks
        self.record_keys = record_keys

        # Регистрируем хуки для клавиш
        if self.record_keys:
            keyboard.hook(self._on_key_event)

        # Регистрируем слушатель для кликов мыши
        if self.record_clicks:
            self._start_mouse_listener()

        # Запускаем отслеживание движения мыши
        if self.record_mouse_movement:
            self._start_mouse_tracking()

        if self.app:
            self.app.update_status("🎥 Recording started...")

    def _start_mouse_listener(self) -> None:
        """Запуск слушателя кликов мыши"""
        def on_click(x, y, button, pressed):
            if not self.recording:
                return

            button_name = self._get_button_name(button)
            if button_name:
                self._record_action('mouse', {
                    'x': x,
                    'y': y,
                    'button': button_name,
                    'event': 'down' if pressed else 'up'
                })

        self._mouse_listener = pynput_mouse.Listener(on_click=on_click)
        self._mouse_listener.start()

    def _get_button_name(self, button) -> Optional[str]:
        """Преобразование кнопки pynput в строковое имя"""
        if button == pynput_mouse.Button.left:
            return 'left'
        elif button == pynput_mouse.Button.right:
            return 'right'
        elif button == pynput_mouse.Button.middle:
            return 'middle'
        elif hasattr(pynput_mouse.Button, 'x1') and button == pynput_mouse.Button.x1:
            return 'x1'
        elif hasattr(pynput_mouse.Button, 'x2') and button == pynput_mouse.Button.x2:
            return 'x2'
        return None

    def _start_mouse_tracking(self) -> None:
        """Запуск отслеживания движения мыши"""
        def track_mouse():
            while self.recording:
                current_pos = pyautogui.position()
                if current_pos != self.last_pos:
                    self._record_action('mouse_move', {
                        'x': current_pos[0],
                        'y': current_pos[1],
                        'from_x': self.last_pos[0],
                        'from_y': self.last_pos[1]
                    })
                    self.last_pos = current_pos
                time.sleep(0.03)  # ~30 FPS для записи движения

        self._tracking_thread = threading.Thread(target=track_mouse, daemon=True)
        self._tracking_thread.start()

    def stop_recording(self) -> List[Dict[str, Any]]:
        """
        Остановить запись.

        Returns:
            Список записанных действий
        """
        if not self.recording:
            return []

        self.recording = False

        # Отключаем хуки клавиш
        if self.record_keys:
            keyboard.unhook(self._on_key_event)

        # Останавливаем слушатель мыши
        if self._mouse_listener and self._mouse_listener.is_alive():
            self._mouse_listener.stop()

        # Ожидаем завершения потока отслеживания
        if self._tracking_thread and self._tracking_thread.is_alive():
            self._tracking_thread.join(timeout=1.0)

        if self.app:
            self.app.update_status(f"🎥 Recording stopped. {len(self.recorded_actions)} actions recorded.")

        return self.recorded_actions

    def _on_key_event(self, event: keyboard.KeyboardEvent) -> None:
        """Обработка событий клавиатуры"""
        if not self.recording:
            return

        if event.event_type == keyboard.KEY_DOWN:
            self._record_action('key', {
                'key': event.name,
                'event': 'down',
                'scan_code': event.scan_code
            })
        elif event.event_type == keyboard.KEY_UP:
            self._record_action('key', {
                'key': event.name,
                'event': 'up',
                'scan_code': event.scan_code
            })

    def _record_action(self, action_type: str, data: Dict[str, Any]) -> None:
        """
        Запись одного действия.

        Args:
            action_type: Тип действия (key, mouse, mouse_move)
            data: Данные действия
        """
        timestamp = time.time() - self.start_time
        self.recorded_actions.append({
            'type': action_type,
            'data': data,
            'timestamp': timestamp
        })

    def record_mouse_click(self, x: int, y: int, button: str, pressed: bool) -> None:
        """
        Запись клика мыши (вызывается извне, для совместимости).

        Args:
            x: Координата X
            y: Координата Y
            button: Кнопка (left, right, middle)
            pressed: Нажата (True) или отпущена (False)
        """
        if not self.recording or not self.record_clicks:
            return

        self._record_action('mouse', {
            'x': x, 'y': y,
            'button': button,
            'event': 'down' if pressed else 'up'
        })

    def generate_script(self) -> str:
        """
        Генерация DSL скрипта из записанных действий.

        Returns:
            Строка скрипта
        """
        script_lines = [
            "# Auto-generated script from recording",
            f"# Recorded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Total actions: {len(self.recorded_actions)}",
            ""
        ]

        last_timestamp = 0
        held_keys = {}  # отслеживание удержаний клавиш

        for action in self.recorded_actions:
            # Добавляем задержку
            delay = action['timestamp'] - last_timestamp
            if delay > 0.05:  # Задержка больше 50мс
                script_lines.append(f"wait({int(delay * 1000)})")

            # Генерируем команду
            if action['type'] == 'mouse':
                data = action['data']
                if data['event'] == 'down':
                    script_lines.append(f'click({data["x"]}, {data["y"]})')
                else:
                    script_lines.append(f'mouse_up({data["x"]}, {data["y"]}, "{data["button"]}")')

            elif action['type'] == 'mouse_move':
                data = action['data']
                # Пропускаем слишком мелкие движения
                dist = ((data['x'] - data['from_x'])**2 + (data['y'] - data['from_y'])**2)**0.5
                if dist > 10:
                    script_lines.append(f'move({data["x"]}, {data["y"]})')

            elif action['type'] == 'key':
                data = action['data']
                if data['event'] == 'down':
                    # Запоминаем время нажатия для возможного удержания
                    held_keys[data['key']] = action['timestamp']
                    script_lines.append(f'key_down("{data["key"]}")')
                else:
                    # Проверяем, было ли удержание
                    press_time = held_keys.pop(data['key'], None)
                    if press_time is not None:
                        hold_duration = action['timestamp'] - press_time
                        if hold_duration > 0.1:  # Удержание больше 100мс
                            script_lines.append(f'key_up("{data["key"]}")')
                        else:
                            # Короткое нажатие - заменяем key_down + key_up на key
                            if script_lines and script_lines[-1] == f'key_down("{data["key"]}")':
                                script_lines.pop()  # удаляем key_down
                                script_lines.append(f'key("{data["key"]}")')
                            else:
                                script_lines.append(f'key_up("{data["key"]}")')

            last_timestamp = action['timestamp']

        return '\n'.join(script_lines)

    def get_script_preview(self, max_lines: int = 20) -> str:
        """
        Получить предпросмотр сгенерированного скрипта.

        Args:
            max_lines: Максимальное количество строк

        Returns:
            Первые max_lines строк скрипта
        """
        script = self.generate_script()
        lines = script.split('\n')
        if len(lines) <= max_lines:
            return script
        return '\n'.join(lines[:max_lines]) + f"\n... and {len(lines) - max_lines} more lines"

    def clear(self) -> None:
        """Очистить записанные действия"""
        self.recorded_actions = []

    def get_action_count(self) -> int:
        """Получить количество записанных действий"""
        return len(self.recorded_actions)

    def get_duration(self) -> float:
        """
        Получить длительность записи.

        Returns:
            Длительность в секундах
        """
        if not self.recorded_actions:
            return 0.0
        return self.recorded_actions[-1]['timestamp']

    def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику записи.

        Returns:
            Словарь со статистикой
        """
        key_count = sum(1 for a in self.recorded_actions if a['type'] == 'key')
        mouse_count = sum(1 for a in self.recorded_actions if a['type'] == 'mouse')
        move_count = sum(1 for a in self.recorded_actions if a['type'] == 'mouse_move')

        return {
            "total_actions": len(self.recorded_actions),
            "key_presses": key_count,
            "mouse_clicks": mouse_count,
            "mouse_movements": move_count,
            "duration_sec": self.get_duration(),
        }

    def save_to_file(self, filepath: str) -> bool:
        """
        Сохранить сгенерированный скрипт в файл.

        Args:
            filepath: Путь для сохранения

        Returns:
            True если сохранение успешно
        """
        try:
            script = self.generate_script()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(script)
            return True
        except Exception as e:
            print(f"Error saving script: {e}")
            return False


if __name__ == "__main__":
    # Тестирование модуля записи
    print("=" * 50)
    print("Testing ActionRecorder Module")
    print("=" * 50)

    recorder = ActionRecorder()

    print("\n📹 Starting recording (3 seconds)...")
    recorder.start_recording()
    time.sleep(3)

    # Симулируем действия
    recorder._record_action('mouse', {'x': 100, 'y': 100, 'button': 'left', 'event': 'down'})
    time.sleep(0.1)
    recorder._record_action('mouse', {'x': 100, 'y': 100, 'button': 'left', 'event': 'up'})
    recorder._record_action('key', {'key': 'space', 'event': 'down'})
    time.sleep(0.05)
    recorder._record_action('key', {'key': 'space', 'event': 'up'})

    actions = recorder.stop_recording()

    print(f"\n📊 Recording statistics:")
    stats = recorder.get_statistics()
    for k, v in stats.items():
        print(f"   {k}: {v}")

    print(f"\n📜 Generated script preview:")
    print(recorder.get_script_preview(15))

    print("\n✅ Module ready!")