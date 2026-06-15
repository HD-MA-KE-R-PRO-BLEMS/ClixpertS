"""
Clixpert S Pro Ultimate - Debug Executor Module
Пошаговая отладка, точки остановки, slow motion режим
"""

import time
import threading
from typing import Set, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class Breakpoint:
    """Точка остановки"""
    line: int
    enabled: bool = True
    condition: Optional[str] = None
    hit_count: int = 0


class DebugExecutor:
    """
    Управление отладкой выполнения скриптов.
    Поддерживает:
    - Пошаговый режим (Step Mode)
    - Точки остановки (Breakpoints)
    - Slow Motion режим
    """

    def __init__(self, app):
        self.app = app
        self.step_mode = False
        self.breakpoints: Set[int] = set()
        self.breakpoints_conditions: dict = {}
        self.current_line = 0
        self.paused = False
        self.slow_mode_ms = 0
        self.callback_on_pause: Optional[Callable] = None
        self.callback_on_resume: Optional[Callable] = None
        self._pause_event = threading.Event()

    def set_step_mode(self, enabled: bool) -> None:
        """
        Включить/выключить пошаговый режим.

        Args:
            enabled: True - пошаговый режим
        """
        self.step_mode = enabled
        if not enabled and self.paused:
            self.continue_execution()

    def set_slow_mode(self, ms: int) -> None:
        """
        Установить задержку для Slow Motion режима.

        Args:
            ms: Задержка в миллисекундах между шагами
        """
        self.slow_mode_ms = max(0, ms)

    def add_breakpoint(self, line: int, condition: Optional[str] = None) -> None:
        """
        Добавить точку остановки.

        Args:
            line: Номер строки
            condition: Условие для срабатывания
        """
        self.breakpoints.add(line)
        if condition:
            self.breakpoints_conditions[line] = condition

    def remove_breakpoint(self, line: int) -> None:
        """
        Удалить точку остановки.

        Args:
            line: Номер строки
        """
        self.breakpoints.discard(line)
        self.breakpoints_conditions.pop(line, None)

    def clear_breakpoints(self) -> None:
        """Очистить все точки остановки"""
        self.breakpoints.clear()
        self.breakpoints_conditions.clear()

    def get_breakpoints(self) -> Set[int]:
        """Получить все точки остановки"""
        return self.breakpoints.copy()

    def should_pause(self, line: int, variables: Optional[dict] = None) -> bool:
        """
        Проверить, нужно ли приостановить выполнение.

        Args:
            line: Текущая строка
            variables: Текущие переменные для проверки условий

        Returns:
            True если нужно приостановить
        """
        # Slow Motion пауза
        if self.slow_mode_ms > 0:
            time.sleep(self.slow_mode_ms / 1000.0)

        # Проверка точки остановки
        if line in self.breakpoints:
            condition = self.breakpoints_conditions.get(line)
            if condition and variables:
                try:
                    # Проверяем условие
                    if not self._evaluate_condition(condition, variables):
                        return False
                except:
                    pass

            if self.app and self.app.script_executor and self.app.script_executor.is_running:
                self._pause_at_line(line)
                return True

        # Пошаговый режим
        if self.step_mode:
            if self.app and self.app.script_executor and self.app.script_executor.is_running:
                self._pause_at_line(line)
                return True

        return False

    def _evaluate_condition(self, condition: str, variables: dict) -> bool:
        """Вычисление условия для точки остановки"""
        try:
            # Простая замена переменных
            cond = condition
            for var_name, var_value in variables.items():
                cond = cond.replace(var_name, str(var_value))
            return bool(eval(cond))
        except:
            return True

    def _pause_at_line(self, line: int) -> None:
        """Приостановка на указанной строке"""
        self.current_line = line
        self.paused = True

        if self.callback_on_pause:
            self.callback_on_pause(line)

        if self.app:
            self.app.update_status(f"⏸ Paused at line {line}")

        # Ждём продолжения
        self._pause_event.clear()
        self._pause_event.wait()

    def continue_execution(self) -> None:
        """Продолжить выполнение"""
        if self.paused:
            self.paused = False
            self._pause_event.set()
            if self.callback_on_resume:
                self.callback_on_resume()
            if self.app:
                self.app.update_status("▶ Continued")

    def step_over(self) -> None:
        """Выполнить шаг и остановиться на следующей строке"""
        self.step_mode = True
        self.continue_execution()

    def step_into(self) -> None:
        """Шаг с заходом в функции (аналог step_over для простоты)"""
        self.step_mode = True
        self.continue_execution()

    def step_out(self) -> None:
        """Шаг с выходом из функции"""
        self.step_mode = True
        self.continue_execution()

    def apply_slow_mode(self) -> None:
        """Применить задержку Slow Motion"""
        if self.slow_mode_ms > 0:
            time.sleep(self.slow_mode_ms / 1000.0)

    def set_callback_on_pause(self, callback: Callable) -> None:
        """Установить callback при паузе"""
        self.callback_on_pause = callback

    def set_callback_on_resume(self, callback: Callable) -> None:
        """Установить callback при возобновлении"""
        self.callback_on_resume = callback

    def is_paused(self) -> bool:
        """Проверить, находится ли выполнение на паузе"""
        return self.paused

    def get_current_line(self) -> int:
        """Получить текущую строку выполнения"""
        return self.current_line

    def get_status(self) -> dict:
        """Получить статус отладчика"""
        return {
            "step_mode": self.step_mode,
            "paused": self.paused,
            "slow_mode_ms": self.slow_mode_ms,
            "current_line": self.current_line,
            "breakpoints": list(self.breakpoints),
            "breakpoints_with_conditions": self.breakpoints_conditions,
        }


if __name__ == "__main__":
    # Тестирование модуля отладки
    print("=" * 50)
    print("Testing DebugExecutor Module")
    print("=" * 50)


    # Создаём мок-приложение
    class MockApp:
        def update_status(self, msg):
            print(f"   Status: {msg}")


    app = MockApp()
    debug = DebugExecutor(app)

    print("\n🔧 Initial state:")
    print(f"   Step mode: {debug.step_mode}")
    print(f"   Slow mode: {debug.slow_mode_ms}ms")
    print(f"   Breakpoints: {debug.get_breakpoints()}")

    print("\n➕ Adding breakpoints:")
    debug.add_breakpoint(10)
    debug.add_breakpoint(25, "x > 5")
    print(f"   Breakpoints: {debug.get_breakpoints()}")
    print(f"   Conditions: {debug.breakpoints_conditions}")

    print("\n⏸ Testing should_pause (without running script):")
    should = debug.should_pause(10)
    print(f"   Line 10 should pause: {should}")

    print("\n⏸ Testing should_pause with slow mode:")
    debug.set_slow_mode(100)
    print(f"   Slow mode: {debug.slow_mode_ms}ms")

    print("\n▶ Testing continue:")
    debug.continue_execution()
    print(f"   Paused after continue: {debug.is_paused()}")

    print("\n🗑 Removing breakpoints:")
    debug.remove_breakpoint(10)
    print(f"   Breakpoints: {debug.get_breakpoints()}")

    print("\n✅ Module ready!")