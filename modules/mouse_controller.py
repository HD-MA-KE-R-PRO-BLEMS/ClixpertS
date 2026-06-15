"""
Clixpert S Pro Ultimate - Human Mouse Controller Module
Имитация человеческого движения мыши: кривые Безье, естественные задержки, дрожание
"""

import random
import time
import math
import pyautogui
from typing import Tuple, Optional


class HumanMouseController:
    """
    Имитация человеческого поведения мыши.
    Поддерживает:
    - Движение по кривой Безье
    - Естественное дрожание
    - Разную скорость движения
    - Человеческий клик с удержанием
    - Естественный скролл
    """

    # Предопределённые профили скорости
    SPEED_PROFILES = {
        'slow': (0.5, 0.8),  # медленное движение (0.5-0.8 сек)
        'normal': (0.2, 0.4),  # нормальное движение (0.2-0.4 сек)
        'fast': (0.05, 0.15),  # быстрое движение (0.05-0.15 сек)
        'instant': (0.01, 0.02),  # мгновенное движение (0.01-0.02 сек)
    }

    @staticmethod
    def bezier_curve(p0: Tuple[int, int], p1: Tuple[int, int],
                     p2: Tuple[int, int], p3: Tuple[int, int], t: float) -> Tuple[int, int]:
        """
        Кривая Безье 3-го порядка.

        Args:
            p0, p1, p2, p3: Контрольные точки
            t: Параметр кривой (0-1)

        Returns:
            Точка на кривой
        """
        x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
        return (int(x), int(y))

    @staticmethod
    def generate_control_points(
            start: Tuple[int, int],
            end: Tuple[int, int],
            randomness: int = 50
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Генерация контрольных точек для естественного движения.

        Args:
            start: Начальная точка
            end: Конечная точка
            randomness: Степень случайности (отклонение от прямой)

        Returns:
            Две контрольные точки
        """
        mid_x = (start[0] + end[0]) // 2
        mid_y = (start[1] + end[1]) // 2

        # Случайное смещение для естественности
        offset_x = random.randint(-randomness, randomness)
        offset_y = random.randint(-randomness, randomness)

        cp1 = (mid_x + offset_x // 2, mid_y + offset_y // 2)
        cp2 = (mid_x + offset_x, mid_y + offset_y)

        return cp1, cp2

    @staticmethod
    def human_move(
            start: Tuple[int, int],
            end: Tuple[int, int],
            speed: str = 'normal',
            bezier: bool = True,
            jitter: bool = True
    ) -> float:
        """
        Человеческое движение мыши.

        Args:
            start: Начальная позиция
            end: Конечная позиция
            speed: Скорость (slow, normal, fast, instant)
            bezier: Использовать кривую Безье
            jitter: Добавлять дрожание

        Returns:
            Время движения в секундах
        """
        # Проверка на маленькое расстояние
        distance = math.hypot(end[0] - start[0], end[1] - start[1])
        if distance < 5:
            pyautogui.moveTo(end[0], end[1])
            return 0.0

        # Получаем длительность движения
        duration_min, duration_max = HumanMouseController.SPEED_PROFILES.get(speed, (0.2, 0.4))
        duration = random.uniform(duration_min, duration_max)
        steps = max(30, int(duration * 100))

        if bezier:
            # Движение по кривой Безье
            cp1, cp2 = HumanMouseController.generate_control_points(start, end)

            for i in range(steps):
                t = i / steps
                x, y = HumanMouseController.bezier_curve(start, cp1, cp2, end, t)

                if jitter and random.random() < 0.3:
                    # Лёгкое дрожание
                    x += random.randint(-2, 2)
                    y += random.randint(-2, 2)

                pyautogui.moveTo(x, y)
                time.sleep(duration / steps)
        else:
            # Прямое движение с ускорением/замедлением
            for i in range(steps):
                # Кривая ускорения (sin для плавности)
                t = math.sin(i / steps * math.pi / 2)
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t

                if jitter and random.random() < 0.2:
                    x += random.randint(-1, 1)
                    y += random.randint(-1, 1)

                pyautogui.moveTo(int(x), int(y))
                time.sleep(duration / steps)

        # Финальная корректировка
        pyautogui.moveTo(end[0], end[1])
        return duration

    @staticmethod
    def human_click(
            x: int,
            y: int,
            hold_min: int = 50,
            hold_max: int = 200,
            pre_delay_min: int = 0,
            pre_delay_max: int = 50,
            button: str = 'left'
    ) -> float:
        """
        Человеческий клик с задержками и удержанием.

        Args:
            x, y: Координаты клика
            hold_min: Минимальное время удержания (мс)
            hold_max: Максимальное время удержания (мс)
            pre_delay_min: Минимальная задержка перед кликом (мс)
            pre_delay_max: Максимальная задержка перед кликом (мс)
            button: Кнопка мыши (left, right, middle)

        Returns:
            Время удержания в секундах
        """
        # Задержка перед кликом
        if pre_delay_max > 0:
            time.sleep(random.uniform(pre_delay_min, pre_delay_max) / 1000.0)

        # Движение к цели
        start = pyautogui.position()
        if abs(start[0] - x) > 5 or abs(start[1] - y) > 5:
            HumanMouseController.human_move(start, (x, y), 'normal')

        # Лёгкое дрожание перед кликом
        pyautogui.moveTo(x + random.randint(-2, 2), y + random.randint(-2, 2))
        time.sleep(random.uniform(0.01, 0.03))
        pyautogui.moveTo(x, y)

        # Нажатие
        button_map = {'left': 'left', 'right': 'right', 'middle': 'middle'}
        pyautogui.mouseDown(button=button_map.get(button, 'left'))

        # Удержание с микродрожанием
        hold_time = random.uniform(hold_min, hold_max) / 1000.0
        time.sleep(hold_time)

        if hold_time > 0.05:
            # Микродвижения во время удержания (дрожание пальца)
            for _ in range(random.randint(1, 3)):
                pyautogui.moveTo(x + random.randint(-1, 1), y + random.randint(-1, 1))
                time.sleep(hold_time / 3)
            pyautogui.moveTo(x, y)

        # Отпускание
        pyautogui.mouseUp(button=button_map.get(button, 'left'))

        return hold_time

    @staticmethod
    def human_drag(
            start: Tuple[int, int],
            end: Tuple[int, int],
            hold_min: int = 100,
            hold_max: int = 300,
            button: str = 'left'
    ) -> None:
        """
        Человеческое перетаскивание.

        Args:
            start: Начальная позиция
            end: Конечная позиция
            hold_min: Минимальное удержание перед перетаскиванием (мс)
            hold_max: Максимальное удержание перед перетаскиванием (мс)
            button: Кнопка мыши
        """
        # Движение к начальной точке
        HumanMouseController.human_move(pyautogui.position(), start, 'normal')

        # Нажатие
        button_map = {'left': 'left', 'right': 'right', 'middle': 'middle'}
        pyautogui.mouseDown(button=button_map.get(button, 'left'))

        # Удержание перед перетаскиванием
        time.sleep(random.uniform(hold_min, hold_max) / 1000.0)

        # Перетаскивание
        HumanMouseController.human_move(start, end, 'slow')

        # Отпускание
        time.sleep(random.uniform(0.05, 0.1))
        pyautogui.mouseUp(button=button_map.get(button, 'left'))

    @staticmethod
    def human_scroll(amount: int, duration: float = 0.3) -> None:
        """
        Человеческий скролл с неравномерными шагами.

        Args:
            amount: Количество шагов скролла (положительный - вверх, отрицательный - вниз)
            duration: Общая длительность скролла (сек)
        """
        steps = abs(amount) // 10
        if steps == 0:
            steps = 1

        direction = 1 if amount > 0 else -1

        for i in range(steps):
            # Неравномерный скролл
            scroll_amount = random.randint(5, 15) * direction
            pyautogui.scroll(scroll_amount)

            # Пауза между шагами
            step_delay = duration / steps * random.uniform(0.5, 1.5)
            time.sleep(step_delay)

    @staticmethod
    def human_type(
            text: str,
            speed_range: Tuple[float, float] = (0.05, 0.15),
            error_rate: float = 0.02
    ) -> None:
        """
        Человеческая печать с возможными ошибками.

        Args:
            text: Текст для печати
            speed_range: Диапазон задержки между нажатиями (сек)
            error_rate: Вероятность ошибки (0-1)
        """
        import keyboard

        for char in text:
            # Задержка между нажатиями
            time.sleep(random.uniform(speed_range[0], speed_range[1]))

            # Случайная ошибка (печать другой буквы и исправление)
            if random.random() < error_rate and len(char) == 1 and char.isalpha():
                error_char = random.choice('qwertyuiopasdfghjklzxcvbnm')
                keyboard.write(error_char)
                time.sleep(random.uniform(0.1, 0.3))
                keyboard.press_and_release('backspace')
                time.sleep(random.uniform(0.05, 0.15))

            keyboard.write(char)

    @staticmethod
    def human_key_hold(
            key: str,
            hold_min: int = 100,
            hold_max: int = 500
    ) -> float:
        """
        Человеческое удержание клавиши.

        Args:
            key: Клавиша
            hold_min: Минимальное удержание (мс)
            hold_max: Максимальное удержание (мс)

        Returns:
            Время удержания в секундах
        """
        import keyboard

        hold_time = random.uniform(hold_min, hold_max) / 1000.0
        keyboard.press(key)
        time.sleep(hold_time)
        keyboard.release(key)
        return hold_time

    @staticmethod
    def random_mouse_movement(
            area: Tuple[int, int, int, int],
            duration: float = 1.0,
            points: int = 10
    ) -> None:
        """
        Случайное движение мыши в заданной области.

        Args:
            area: Область (x1, y1, x2, y2)
            duration: Длительность движения (сек)
            points: Количество точек
        """
        x1, y1, x2, y2 = area

        for i in range(points):
            x = random.randint(x1, x2)
            y = random.randint(y1, y2)
            HumanMouseController.human_move(pyautogui.position(), (x, y), 'normal')
            time.sleep(duration / points)

    @staticmethod
    def get_natural_position() -> Tuple[int, int]:
        """
        Получить естественную позицию курсора (угол экрана).

        Returns:
            Координаты (x, y)
        """
        screen = pyautogui.size()
        # Чаще всего курсор в правом нижнем углу
        if random.random() < 0.7:
            return (screen.width - random.randint(10, 100),
                    screen.height - random.randint(10, 100))
        else:
            return (random.randint(0, screen.width),
                    random.randint(0, screen.height))


if __name__ == "__main__":
    # Тестирование модуля движения мыши
    print("=" * 50)
    print("Testing HumanMouseController Module")
    print("=" * 50)

    screen = pyautogui.size()
    print(f"\n🖥 Screen size: {screen.width}x{screen.height}")

    # Тестирование движения
    print("\n🖱 Testing human_move:")
    start = (100, 100)
    end = (300, 300)
    print(f"   Moving from {start} to {end}")

    # Сухое тестирование без реального движения
    duration = HumanMouseController.SPEED_PROFILES['normal']
    print(f"   Duration range: {duration[0]}-{duration[1]} sec")

    # Тестирование клика
    print("\n🖱 Testing human_click:")
    print("   Parameters: hold 50-200ms, pre-delay 0-50ms")

    print("\n✅ Module ready!")