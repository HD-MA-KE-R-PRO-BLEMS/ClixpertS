"""
Clixpert S Pro Ultimate - Performance Statistics Module
Модуль сбора статистики, аналитики и тепловой карты кликов
"""

import time
import random
import numpy as np
import cv2
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ActionRecord:
    """Запись о выполненном действии"""
    action_type: str
    success: bool
    duration_ms: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)


class PerformanceStats:
    """
    Сбор и анализ статистики выполнения действий.
    Включает: количество действий,成功率, время выполнения, тепловую карту кликов.
    """

    def __init__(self):
        self.stats: Dict[str, List[ActionRecord]] = defaultdict(list)
        self.total_actions = 0
        self.successful_actions = 0
        self.failed_actions = 0
        self.click_positions: List[Tuple[int, int]] = []
        self.start_time = datetime.now()
        self.session_duration = 0.0

        # Детальная статистика по типам действий
        self.action_type_counts: Dict[str, int] = defaultdict(int)
        self.action_type_success: Dict[str, int] = defaultdict(int)
        self.action_type_fail: Dict[str, int] = defaultdict(int)

    def record_action(
            self,
            action_type: str,
            success: bool,
            duration_ms: float,
            details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Запись выполнения действия.

        Args:
            action_type: Тип действия (click, key, delay, и т.д.)
            success: Успешно ли выполнено
            duration_ms: Длительность выполнения в миллисекундах
            details: Дополнительные детали
        """
        record = ActionRecord(
            action_type=action_type,
            success=success,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            details=details or {}
        )
        self.stats[action_type].append(record)
        self.total_actions += 1
        self.action_type_counts[action_type] += 1

        if success:
            self.successful_actions += 1
            self.action_type_success[action_type] += 1
        else:
            self.failed_actions += 1
            self.action_type_fail[action_type] += 1

    def record_click(self, x: int, y: int) -> None:
        """
        Запись позиции клика для тепловой карты.

        Args:
            x: Координата X
            y: Координата Y
        """
        self.click_positions.append((x, y))
        # Ограничиваем размер для производительности
        if len(self.click_positions) > 10000:
            self.click_positions = self.click_positions[-5000:]

    def get_success_rate(self) -> float:
        """
        Получить общий процент успешных действий.

        Returns:
            Процент успеха (0-100)
        """
        if self.total_actions == 0:
            return 0.0
        return (self.successful_actions / self.total_actions) * 100

    def get_success_rate_by_type(self, action_type: str) -> float:
        """
        Получить процент успеха для конкретного типа действий.

        Args:
            action_type: Тип действия

        Returns:
            Процент успеха (0-100)
        """
        total = self.action_type_counts.get(action_type, 0)
        if total == 0:
            return 0.0
        success = self.action_type_success.get(action_type, 0)
        return (success / total) * 100

    def get_avg_response_time(self, action_type: Optional[str] = None) -> float:
        """
        Получить среднее время выполнения.

        Args:
            action_type: Тип действия (если None - по всем)

        Returns:
            Среднее время в миллисекундах
        """
        if action_type:
            actions = self.stats.get(action_type, [])
            if not actions:
                return 0.0
            return sum(a.duration_ms for a in actions) / len(actions)
        else:
            all_durations = []
            for actions in self.stats.values():
                all_durations.extend([a.duration_ms for a in actions])
            if not all_durations:
                return 0.0
            return sum(all_durations) / len(all_durations)

    def get_min_response_time(self, action_type: Optional[str] = None) -> float:
        """Получить минимальное время выполнения"""
        if action_type:
            actions = self.stats.get(action_type, [])
            if not actions:
                return 0.0
            return min(a.duration_ms for a in actions)
        else:
            all_durations = []
            for actions in self.stats.values():
                all_durations.extend([a.duration_ms for a in actions])
            if not all_durations:
                return 0.0
            return min(all_durations)

    def get_max_response_time(self, action_type: Optional[str] = None) -> float:
        """Получить максимальное время выполнения"""
        if action_type:
            actions = self.stats.get(action_type, [])
            if not actions:
                return 0.0
            return max(a.duration_ms for a in actions)
        else:
            all_durations = []
            for actions in self.stats.values():
                all_durations.extend([a.duration_ms for a in actions])
            if not all_durations:
                return 0.0
            return max(all_durations)

    def get_total_time(self) -> float:
        """
        Получить общее время работы (с момента создания объекта).

        Returns:
            Время в секундах
        """
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0

    def get_actions_per_minute(self) -> float:
        """
        Получить скорость выполнения действий (действий в минуту).

        Returns:
            Действий в минуту
        """
        total_time = self.get_total_time()
        if total_time == 0 or self.total_actions == 0:
            return 0.0
        return (self.total_actions / total_time) * 60

    def get_heatmap_image(self, width: int = 1920, height: int = 1080) -> np.ndarray:
        """
        Генерация тепловой карты кликов.

        Args:
            width: Ширина изображения
            height: Высота изображения

        Returns:
            Цветное изображение тепловой карты (BGR)
        """
        if not self.click_positions:
            # Возвращаем пустое изображение
            return np.zeros((height, width, 3), dtype=np.uint8)

        # Создаём пустую тепловую карту
        heatmap = np.zeros((height, width), dtype=np.float32)

        # Заполняем точки кликов
        for x, y in self.click_positions:
            if 0 <= x < width and 0 <= y < height:
                heatmap[y, x] += 1

        # Нормализация
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()

        # Применяем Gaussian blur для сглаживания
        heatmap = cv2.GaussianBlur(heatmap, (51, 51), 0)

        # Конвертируем в цветное изображение (Jet colormap)
        heatmap_colored = cv2.applyColorMap((heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET)

        return heatmap_colored

    def get_click_density(self) -> Dict[Tuple[int, int], int]:
        """
        Получить плотность кликов по координатам.

        Returns:
            Словарь {координаты: количество}
        """
        density = {}
        for x, y in self.click_positions:
            # Округляем до 10 пикселей для группировки
            key = (x // 10 * 10, y // 10 * 10)
            density[key] = density.get(key, 0) + 1
        return density

    def get_most_clicked_area(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Получить область с наибольшей плотностью кликов.

        Returns:
            Кортеж (x1, y1, x2, y2) или None
        """
        if not self.click_positions:
            return None

        density = self.get_click_density()
        if not density:
            return None

        # Находим координаты с максимальной плотностью
        max_pos = max(density.items(), key=lambda x: x[1])
        x, y = max_pos[0]

        # Возвращаем область 100x100 пикселей
        return (x - 50, y - 50, x + 50, y + 50)

    def get_summary(self) -> Dict[str, Any]:
        """
        Получить сводную статистику.

        Returns:
            Словарь со статистикой
        """
        return {
            "total_actions": self.total_actions,
            "successful_actions": self.successful_actions,
            "failed_actions": self.failed_actions,
            "success_rate": self.get_success_rate(),
            "avg_response_ms": self.get_avg_response_time(),
            "min_response_ms": self.get_min_response_time(),
            "max_response_ms": self.get_max_response_time(),
            "total_time_sec": self.get_total_time(),
            "actions_per_minute": self.get_actions_per_minute(),
            "total_clicks": len(self.click_positions),
            "unique_click_positions": len(set(self.click_positions)),
            "action_types": dict(self.action_type_counts),
            "action_type_success_rates": {
                action_type: self.get_success_rate_by_type(action_type)
                for action_type in self.action_type_counts
            },
        }

    def reset(self) -> None:
        """Полный сброс всей статистики"""
        self.stats.clear()
        self.total_actions = 0
        self.successful_actions = 0
        self.failed_actions = 0
        self.click_positions = []
        self.start_time = datetime.now()
        self.action_type_counts.clear()
        self.action_type_success.clear()
        self.action_type_fail.clear()

    def export_to_json(self) -> str:
        """
        Экспорт статистики в JSON формат.

        Returns:
            JSON строка
        """
        import json

        data = {
            "summary": self.get_summary(),
            "timestamp": datetime.now().isoformat(),
            "click_positions": self.click_positions[:1000],  # Ограничиваем для JSON
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def export_to_csv(self) -> str:
        """
        Экспорт статистики в CSV формат.

        Returns:
            CSV строка
        """
        lines = ["timestamp,action_type,success,duration_ms"]
        for action_type, records in self.stats.items():
            for record in records:
                lines.append(f"{record.timestamp.isoformat()},{action_type},{record.success},{record.duration_ms:.2f}")
        return "\n".join(lines)


if __name__ == "__main__":
    # Тестирование модуля статистики
    print("=" * 50)
    print("Testing PerformanceStats Module")
    print("=" * 50)

    stats = PerformanceStats()

    # Симулируем действия
    for i in range(10):
        stats.record_action("click", success=True, duration_ms=random.uniform(50, 200))
        stats.record_click(random.randint(0, 1920), random.randint(0, 1080))

    for i in range(3):
        stats.record_action("key", success=False, duration_ms=random.uniform(10, 50))

    # Выводим статистику
    summary = stats.get_summary()
    print(f"\n📊 Statistics Summary:")
    print(f"   Total actions: {summary['total_actions']}")
    print(f"   Success rate: {summary['success_rate']:.1f}%")
    print(f"   Avg response: {summary['avg_response_ms']:.0f} ms")
    print(f"   Actions/min: {summary['actions_per_minute']:.1f}")
    print(f"   Total clicks: {summary['total_clicks']}")

    # Генерируем тепловую карту
    heatmap = stats.get_heatmap_image(800, 600)
    print(f"\n🔥 Heatmap generated: {heatmap.shape}")

    # Экспорт
    print(f"\n📄 JSON export: {len(stats.export_to_json())} chars")
    print(f"📄 CSV export: {len(stats.export_to_csv())} chars")

    print("\n✅ Module ready!")