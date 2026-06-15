"""
Clixpert S Pro Ultimate - Action Manager Module
Управление списком действий, их добавление, редактирование, удаление
"""

import random
import time
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class ActionType(Enum):
    """Типы действий"""
    CLICK = "click"
    KEY = "key"
    DELAY = "delay"


class ConditionType(Enum):
    """Типы условий"""
    NONE = "none"
    PIXEL = "pixel"
    COLOR_AREA = "color_area"
    IMAGE = "image_search"
    SOUND = "sound"


class ActionOnMatch(Enum):
    """Действие при выполнении условия"""
    CLICK_CENTER = "click_center"
    CLICK_COORDS = "click_at_coords"
    HOVER = "hover"
    DRAG = "drag_to"
    CLICK_ALL = "click_all"
    SAVE_SCREENSHOT = "save_screenshot"


@dataclass
class Action:
    """Представление одного действия"""
    type: ActionType
    delay_ms: int = 1000
    condition: Optional[Dict] = None
    action_on_match: str = "click_center"

    # Для клика
    x: int = 0
    y: int = 0
    hold_ms: int = 0
    random_offset: int = 0
    humanize: bool = False

    # Для клавиши
    key: str = ""
    key_hold: bool = False
    key_hold_ms: int = 100

    # Для задержки
    variation_ms: int = 0

    # Для условий
    alt_x: int = 0
    alt_y: int = 0
    loop_until_found: bool = False
    max_attempts: int = 10

    # Прогресс
    progress_contrib: Optional[float] = None

    # Внутренние
    tree_iid: str = ""
    match_pos: Optional[tuple] = None

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сохранения"""
        result = {
            "type": self.type.value if isinstance(self.type, ActionType) else self.type,
            "delay_ms": self.delay_ms,
            "action_on_match": self.action_on_match,
        }

        if self.condition:
            result["condition"] = self.condition

        if self.type == ActionType.CLICK or self.type == "click":
            result.update({
                "x": self.x,
                "y": self.y,
                "hold_ms": self.hold_ms,
                "random_offset": self.random_offset,
                "humanize": self.humanize,
            })
        elif self.type == ActionType.KEY or self.type == "key":
            result.update({
                "key": self.key,
                "key_hold": self.key_hold,
                "key_hold_ms": self.key_hold_ms,
            })
        elif self.type == ActionType.DELAY or self.type == "delay":
            result["variation_ms"] = self.variation_ms

        if self.progress_contrib is not None:
            result["progress_contrib"] = self.progress_contrib

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """Создание действия из словаря"""
        action_type = data.get("type", "click")

        if action_type == "click":
            return cls(
                type=ActionType.CLICK,
                delay_ms=data.get("delay_ms", 1000),
                condition=data.get("condition"),
                action_on_match=data.get("action_on_match", "click_center"),
                x=data.get("x", 0),
                y=data.get("y", 0),
                hold_ms=data.get("hold_ms", 0),
                random_offset=data.get("random_offset", 0),
                humanize=data.get("humanize", False),
                progress_contrib=data.get("progress_contrib"),
            )
        elif action_type == "key":
            return cls(
                type=ActionType.KEY,
                delay_ms=data.get("delay_ms", 1000),
                condition=data.get("condition"),
                action_on_match=data.get("action_on_match", "click_center"),
                key=data.get("key", ""),
                key_hold=data.get("key_hold", False),
                key_hold_ms=data.get("key_hold_ms", 100),
                progress_contrib=data.get("progress_contrib"),
            )
        else:  # delay
            return cls(
                type=ActionType.DELAY,
                delay_ms=data.get("delay_ms", 1000),
                condition=data.get("condition"),
                action_on_match=data.get("action_on_match", "click_center"),
                variation_ms=data.get("variation_ms", 0),
                progress_contrib=data.get("progress_contrib"),
            )


class ActionManager:
    """
    Управление списком действий.
    Обеспечивает CRUD операции и выполнение действий.
    """

    def __init__(self, app):
        self.app = app
        self.actions: List[Action] = []
        self._current_index = 0

    def add_action(self, action: Action) -> None:
        """Добавить действие в конец списка"""
        # Генерируем уникальный ID если его нет
        if not action.tree_iid:
            import uuid
            action.tree_iid = str(uuid.uuid4())
        self.actions.append(action)
        self._update_ui()

    def insert_action(self, index: int, action: Action) -> None:
        """Вставить действие в указанную позицию"""
        self.actions.insert(index, action)
        self._update_ui()

    def remove_action(self, index: int) -> Optional[Action]:
        """Удалить действие по индексу"""
        if 0 <= index < len(self.actions):
            removed = self.actions.pop(index)
            self._update_ui()
            return removed
        return None

    def remove_action_by_iid(self, iid: str) -> bool:
        """Удалить действие по tree_iid"""
        for i, action in enumerate(self.actions):
            if action.tree_iid == iid:
                self.actions.pop(i)
                self._update_ui()
                return True
        return False

    def update_action(self, index: int, action: Action) -> bool:
        """Обновить действие по индексу"""
        if 0 <= index < len(self.actions):
            self.actions[index] = action
            self._update_ui()
            return True
        return False

    def update_action_by_iid(self, iid: str, action: Action) -> bool:
        """Обновить действие по tree_iid"""
        for i, act in enumerate(self.actions):
            if act.tree_iid == iid:
                self.actions[i] = action
                self._update_ui()
                return True
        return False

    def get_action(self, index: int) -> Optional[Action]:
        """Получить действие по индексу"""
        if 0 <= index < len(self.actions):
            return self.actions[index]
        return None

    def get_action_by_iid(self, iid: str) -> Optional[Action]:
        """Получить действие по tree_iid"""
        for action in self.actions:
            if action.tree_iid == iid:
                return action
        return None

    def clear_actions(self) -> None:
        """Очистить все действия"""
        self.actions.clear()
        self._current_index = 0
        self._update_ui()

    def get_count(self) -> int:
        """Получить количество действий"""
        return len(self.actions)

    def is_empty(self) -> bool:
        """Проверить, пуст ли список"""
        return len(self.actions) == 0

    def _update_ui(self) -> None:
        """Обновить UI после изменения списка"""
        if self.app and self.app.main_window:
            self.app.main_window.update_actions_tree()

    def _move_mouse_during_delay(self, target_x: int, target_y: int, delay_ms: int, humanize: bool = False):
        """
        Плавно перемещает мышь к целевым координатам в течение указанной задержки.

        Args:
            target_x: Целевая координата X
            target_y: Целевая координата Y
            delay_ms: Время в миллисекундах для движения
            humanize: Использовать человеческое движение
        """
        import pyautogui

        start_x, start_y = pyautogui.position()

        # Если уже на месте или задержка слишком мала
        if (start_x == target_x and start_y == target_y) or delay_ms <= 0:
            return

        try:
            from modules.mouse_controller import HumanMouseController

            # Рассчитываем время движения (не больше delay_ms)
            move_duration = min(delay_ms / 1000.0, 0.5)  # Максимум 0.5 сек на движение

            if humanize and self.app and self.app.settings.get("humanize_mouse", False):
                # Человеческое движение
                thread = threading.Thread(
                    target=HumanMouseController.human_move,
                    args=((start_x, start_y), (target_x, target_y), 'normal', True, True),
                    daemon=True
                )
                thread.start()
                # Ждём окончания движения или оставшееся время
                thread.join(timeout=move_duration)
            else:
                # Прямое движение с разбивкой на шаги
                steps = max(10, int(move_duration * 60))
                step_delay = move_duration / steps

                for i in range(steps + 1):
                    t = i / steps
                    x = int(start_x + (target_x - start_x) * t)
                    y = int(start_y + (target_y - start_y) * t)
                    pyautogui.moveTo(x, y)
                    time.sleep(step_delay)

        except Exception as e:
            # Если что-то пошло не так, просто перемещаем мгновенно
            pyautogui.moveTo(target_x, target_y)

    def execute_action(self, action: Action) -> bool:
        """
        Выполнить одно действие.

        Args:
            action: Действие для выполнения

        Returns:
            True если действие выполнено успешно
        """
        try:
            # Расчёт задержки
            delay = action.delay_ms
            if action.variation_ms > 0:
                delay += random.randint(-action.variation_ms, action.variation_ms)
                delay = max(0, delay)

            # Для кликов: ДВИГАЕМ МЫШЬ ВО ВРЕМЯ ЗАДЕРЖКИ
            if action.type == ActionType.CLICK:
                # Целевые координаты для клика
                x, y = action.x, action.y

                if action.match_pos:
                    x, y = action.match_pos
                    action.match_pos = None

                # Случайное смещение
                if action.random_offset > 0:
                    x += random.randint(-action.random_offset, action.random_offset)
                    y += random.randint(-action.random_offset, action.random_offset)

                # Двигаем мышь к цели во время задержки
                if delay > 0:
                    self._move_mouse_during_delay(x, y, delay, action.humanize)
                    # Оставшееся время задержки (если движение заняло меньше времени)
                    # Не добавляем дополнительную задержку, так как движение уже заняло время
                else:
                    # Если задержки нет, просто перемещаемся мгновенно
                    import pyautogui
                    pyautogui.moveTo(x, y)

                # Проверка условия (после движения, перед кликом)
                if not self._check_condition(action):
                    return False

                # Выполняем клик
                self._execute_click_at_position(x, y, action)

            elif action.type == ActionType.KEY:
                # Задержка перед нажатием клавиши
                if delay > 0:
                    time.sleep(delay / 1000.0)

                # Проверка условия
                if not self._check_condition(action):
                    return False

                self._execute_key(action)

            elif action.type == ActionType.DELAY:
                # Простая задержка
                if delay > 0:
                    time.sleep(delay / 1000.0)

            return True

        except Exception as e:
            if self.app:
                self.app.update_status(f"Action failed: {e}")
                self.app.send_telegram_notification(f"❌ Action failed: {e}", screenshot=True)
            return False

    def _execute_click_at_position(self, x: int, y: int, action: Action) -> None:
        """
        Выполнение клика в указанной позиции (мышь уже должна быть на месте).

        Args:
            x: Координата X
            y: Координата Y
            action: Действие с параметрами клика
        """
        import pyautogui

        # Корректировка позиции (на случай, если мышь не точно на месте)
        current_x, current_y = pyautogui.position()
        if abs(current_x - x) > 2 or abs(current_y - y) > 2:
            pyautogui.moveTo(x, y)

        # Клик с удержанием
        if action.hold_ms > 0:
            pyautogui.mouseDown()
            time.sleep(action.hold_ms / 1000.0)
            pyautogui.mouseUp()
        else:
            pyautogui.click()

        if self.app and self.app.stats:
            self.app.stats.record_click(x, y)

    def _check_condition(self, action: Action) -> bool:
        """Проверка условия действия"""
        if not action.condition or not self.app or not self.app.settings.get("use_conditions", True):
            return True

        cond = action.condition

        if cond.get("type") == "pixel":
            cond_id = cond.get("id")
            if cond_id and hasattr(self.app, 'condition_manager'):
                pixel_cond = self.app.condition_manager.get_pixel_condition(cond_id)
                if pixel_cond:
                    try:
                        import pyautogui
                        pixel = pyautogui.pixel(pixel_cond.x, pixel_cond.y)
                        tolerance = pixel_cond.tolerance
                        match = all(abs(pixel[i] - pixel_cond.color[i]) <= tolerance for i in range(3))

                        if action.loop_until_found and not match:
                            for _ in range(action.max_attempts):
                                time.sleep(self.app.settings.get("attempt_delay", 500) / 1000.0)
                                pixel = pyautogui.pixel(pixel_cond.x, pixel_cond.y)
                                if all(abs(pixel[i] - pixel_cond.color[i]) <= tolerance for i in range(3)):
                                    return True
                            return False
                        return match
                    except:
                        return False
        elif cond.get("type") == "image":
            cond_id = cond.get("id")
            if cond_id and hasattr(self.app, 'condition_manager'):
                image_cond = self.app.condition_manager.get_image_condition(cond_id)
                if image_cond and hasattr(self.app, 'find_image_advanced'):
                    try:
                        found, pos = self.app.find_image_advanced(
                            image_cond.image_path,
                            confidence=image_cond.confidence,
                            multi_scale=image_cond.multi_scale,
                            rotation=image_cond.rotation_tolerance,
                            method=image_cond.search_method
                        )
                        if found and pos:
                            action.match_pos = pos
                        return found
                    except:
                        return False
        elif cond.get("type") == "sound":
            cond_id = cond.get("id")
            if cond_id and hasattr(self.app, 'condition_manager'):
                sound_cond = self.app.condition_manager.get_sound_condition(cond_id)
                if sound_cond:
                    try:
                        from modules.sound_analyzer import SoundCondition
                        sound = SoundCondition()
                        if sound.init():
                            result = sound.check_condition(sound_cond.threshold, sound_cond.duration)
                            sound.cleanup()
                            return result
                    except:
                        return False

        return True

    def _execute_click(self, action: Action) -> None:
        """Выполнение клика (устаревший метод, оставлен для совместимости)"""
        import pyautogui

        x, y = action.x, action.y

        if action.match_pos:
            x, y = action.match_pos
            action.match_pos = None

        if action.random_offset > 0:
            x += random.randint(-action.random_offset, action.random_offset)
            y += random.randint(-action.random_offset, action.random_offset)

        pyautogui.moveTo(x, y)

        if action.hold_ms > 0:
            pyautogui.mouseDown()
            time.sleep(action.hold_ms / 1000.0)
            pyautogui.mouseUp()
        else:
            pyautogui.click()

        if self.app and self.app.stats:
            self.app.stats.record_click(x, y)

    def _execute_key(self, action: Action) -> None:
        """Выполнение нажатия клавиши"""
        import keyboard

        if action.key_hold:
            keyboard.press(action.key)
            time.sleep(action.key_hold_ms / 1000.0)
            keyboard.release(action.key)
        else:
            keyboard.press_and_release(action.key)

    def execute_all(self, on_action_complete: Optional[Callable] = None) -> None:
        """
        Выполнить все действия последовательно.

        Args:
            on_action_complete: Callback после каждого действия
        """
        for i, action in enumerate(self.actions):
            if not self.app or not self.app.running:
                break

            success = self.execute_action(action)
            if on_action_complete:
                on_action_complete(i, action, success)

    def get_total_delay(self) -> int:
        """Получить суммарную задержку всех действий (мс)"""
        return sum(a.delay_ms for a in self.actions)

    def get_total_contrib(self) -> float:
        """Получить суммарный вклад в прогресс"""
        total = 0.0
        for action in self.actions:
            if action.progress_contrib is not None:
                total += action.progress_contrib
            elif action.type != ActionType.DELAY:
                if self.app:
                    deduct = self.app.settings.get("deduction", 10.0)
                    mult = self.app.settings.get("deduction_mult", 0.33)
                    total += deduct * (1.0 - mult)
        return total

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Конвертация всех действий в список словарей"""
        return [a.to_dict() for a in self.actions]

    def from_dict_list(self, data_list: List[Dict[str, Any]]) -> None:
        """Загрузка действий из списка словарей"""
        self.actions = [Action.from_dict(data) for data in data_list]
        self._update_ui()

    def create_click_action(
            self,
            x: int,
            y: int,
            delay_ms: Optional[int] = None,
            hold_ms: int = 0,
            random_offset: int = 0,
            humanize: bool = False
    ) -> Action:
        """Создать действие клика"""
        if delay_ms is None and self.app:
            delay_ms = self.app.settings.get("global_delay_ms", 1000)

        import uuid
        action = Action(
            type=ActionType.CLICK,
            delay_ms=delay_ms or 1000,
            x=x,
            y=y,
            hold_ms=hold_ms,
            random_offset=random_offset or (self.app.settings.get("random_click_offset", 0) if self.app else 0),
            humanize=humanize or (self.app.settings.get("humanize_mouse", False) if self.app else False)
        )
        action.tree_iid = str(uuid.uuid4())
        return action

    def create_key_action(
            self,
            key: str,
            delay_ms: Optional[int] = None,
            key_hold: bool = False,
            key_hold_ms: int = 100
    ) -> Action:
        """Создать действие клавиши"""
        if delay_ms is None and self.app:
            delay_ms = self.app.settings.get("global_delay_ms", 1000)

        import uuid
        action = Action(
            type=ActionType.KEY,
            delay_ms=delay_ms or 1000,
            key=key,
            key_hold=key_hold,
            key_hold_ms=key_hold_ms
        )
        action.tree_iid = str(uuid.uuid4())
        return action

    def create_delay_action(self, delay_ms: int, variation_ms: int = 0) -> Action:
        """Создать действие задержки"""
        import uuid
        action = Action(
            type=ActionType.DELAY,
            delay_ms=delay_ms,
            variation_ms=variation_ms
        )
        action.tree_iid = str(uuid.uuid4())
        return action


if __name__ == "__main__":
    # Тестирование модуля действий
    print("=" * 50)
    print("Testing ActionManager Module")
    print("=" * 50)


    # Создаём мок-приложение
    class MockApp:
        def __init__(self):
            self.settings = {
                "global_delay_ms": 500,
                "random_click_offset": 5,
                "humanize_mouse": True,
                "use_conditions": True,
                "color_tolerance": 10,
            }

        def update_status(self, msg):
            print(f"   Status: {msg}")

        def send_telegram_notification(self, msg, screenshot=False):
            print(f"   Telegram: {msg}")


    app = MockApp()
    manager = ActionManager(app)

    print("\n📋 Creating actions:")

    # Создаём действия
    click_action = manager.create_click_action(500, 500, 1000)
    print(f"   Click: ({click_action.x}, {click_action.y}) delay={click_action.delay_ms}ms")

    key_action = manager.create_key_action("enter", 500)
    print(f"   Key: {key_action.key}")

    delay_action = manager.create_delay_action(2000, 100)
    print(f"   Delay: {delay_action.delay_ms}ms ±{delay_action.variation_ms}ms")

    # Добавляем в менеджер
    manager.add_action(click_action)
    manager.add_action(key_action)
    manager.add_action(delay_action)

    print(f"\n📊 Actions count: {manager.get_count()}")
    print(f"   Total delay: {manager.get_total_delay()}ms")
    print(f"   Total contrib: {manager.get_total_contrib()}")

    print("\n✅ Module ready!")