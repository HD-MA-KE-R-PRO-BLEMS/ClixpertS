"""
Clixpert S Pro Ultimate - Condition Manager Module
Управление пиксельными условиями (цвет, координаты, допуск)
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# ========== ЗВУКОВЫЕ УСЛОВИЯ ==========

@dataclass
class SoundConditionData:
    """Звуковое условие"""
    id: str
    threshold: int = 500
    duration: float = 0.5
    action_on_match: str = "click_center"
    click_x: int = 0
    click_y: int = 0
    enabled: bool = True
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сохранения"""
        return {
            "id": self.id,
            "type": "sound",
            "threshold": self.threshold,
            "duration": self.duration,
            "action_on_match": self.action_on_match,
            "click_x": self.click_x,
            "click_y": self.click_y,
            "enabled": self.enabled,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SoundConditionData':
        """Создание из словаря"""
        return cls(
            id=data.get("id", ""),
            threshold=data.get("threshold", 500),
            duration=data.get("duration", 0.5),
            action_on_match=data.get("action_on_match", "click_center"),
            click_x=data.get("click_x", 0),
            click_y=data.get("click_y", 0),
            enabled=data.get("enabled", True),
            description=data.get("description", ""),
        )

    def check(self) -> bool:
        """Проверка звукового условия (требует отдельной реализации с audio)"""
        # Реальная проверка будет в SoundCondition из modules
        return False

@dataclass
class PixelCondition:
    """Пиксельное условие"""
    id: str
    x: int
    y: int
    color: Tuple[int, int, int]  # (R, G, B)
    tolerance: int = 10
    enabled: bool = True
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сохранения"""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "color": list(self.color),
            "tolerance": self.tolerance,
            "enabled": self.enabled,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PixelCondition':
        """Создание из словаря"""
        color = data.get("color", [0, 0, 0])
        if isinstance(color, list):
            color = tuple(color)
        return cls(
            id=data.get("id", ""),
            x=data.get("x", 0),
            y=data.get("y", 0),
            color=color,
            tolerance=data.get("tolerance", 10),
            enabled=data.get("enabled", True),
            description=data.get("description", ""),
        )

    def check(self, current_color: Tuple[int, int, int]) -> bool:
        """Проверка совпадения цвета с допуском"""
        return all(abs(current_color[i] - self.color[i]) <= self.tolerance for i in range(3))


@dataclass
class ImageCondition:
    """Условие поиска изображения"""
    id: str
    image_path: str
    image_data: Optional[str] = None  # base64
    area: Optional[Tuple[int, int, int, int]] = None  # x1, y1, x2, y2
    confidence: float = 0.8
    multi_scale: bool = False
    rotation_tolerance: int = 0
    search_method: str = "template_matching"
    action_on_match: str = "click_center"
    offset_x: int = 0
    offset_y: int = 0
    click_all: bool = False
    save_screenshot: bool = False
    enabled: bool = True
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сохранения"""
        result = {
            "id": self.id,
            "image_path": self.image_path,
            "confidence": self.confidence,
            "multi_scale": self.multi_scale,
            "rotation_tolerance": self.rotation_tolerance,
            "search_method": self.search_method,
            "action_on_match": self.action_on_match,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "click_all": self.click_all,
            "save_screenshot": self.save_screenshot,
            "enabled": self.enabled,
            "description": self.description,
        }
        if self.image_data:
            result["image_data"] = self.image_data
        if self.area:
            result["area"] = list(self.area)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImageCondition':
        """Создание из словаря"""
        area = data.get("area")
        if area and isinstance(area, list):
            area = tuple(area)
        return cls(
            id=data.get("id", ""),
            image_path=data.get("image_path", ""),
            image_data=data.get("image_data"),
            area=area,
            confidence=data.get("confidence", 0.8),
            multi_scale=data.get("multi_scale", False),
            rotation_tolerance=data.get("rotation_tolerance", 0),
            search_method=data.get("search_method", "template_matching"),
            action_on_match=data.get("action_on_match", "click_center"),
            offset_x=data.get("offset_x", 0),
            offset_y=data.get("offset_y", 0),
            click_all=data.get("click_all", False),
            save_screenshot=data.get("save_screenshot", False),
            enabled=data.get("enabled", True),
            description=data.get("description", ""),
        )


class ConditionManager:
    """
    Управление условиями (пиксельными и по изображению).
    Обеспечивает CRUD операции и проверку условий.
    """

    def __init__(self, app):
        self.app = app
        self.sound_conditions: List[SoundConditionData] = []
        self.pixel_conditions: List[PixelCondition] = []
        self.image_conditions: List[ImageCondition] = []
        self._conditions_file = None

    def set_storage_path(self, path: Path) -> None:
        """Установить путь для сохранения условий"""
        self._conditions_file = path / "conditions.json"
        self.load()

    def load(self) -> None:
        """Загрузка условий из файла"""
        if not self._conditions_file or not self._conditions_file.exists():
            return

        try:
            with open(self._conditions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.pixel_conditions = [
                PixelCondition.from_dict(c) for c in data.get("pixel_conditions", [])
            ]
            self.image_conditions = [
                ImageCondition.from_dict(c) for c in data.get("image_conditions", [])
            ]
            # ========== ДОБАВИТЬ ЗАГРУЗКУ ЗВУКОВЫХ УСЛОВИЙ ==========
            self.sound_conditions = [
                SoundConditionData.from_dict(c) for c in data.get("sound_conditions", [])
            ]
        except Exception as e:
            print(f"Error loading conditions: {e}")

    def save(self) -> None:
        """Сохранение условий в файл"""
        if not self._conditions_file:
            return

        try:
            data = {
                "pixel_conditions": [c.to_dict() for c in self.pixel_conditions],
                "image_conditions": [c.to_dict() for c in self.image_conditions],
                # ========== ДОБАВИТЬ СОХРАНЕНИЕ ЗВУКОВЫХ УСЛОВИЙ ==========
                "sound_conditions": [c.to_dict() for c in self.sound_conditions],
            }
            with open(self._conditions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving conditions: {e}")

    # ========== ПИКСЕЛЬНЫЕ УСЛОВИЯ ==========

    def add_pixel_condition(
            self,
            cond_id: str,
            x: int,
            y: int,
            color: Tuple[int, int, int],
            tolerance: int = 10,
            description: str = ""
    ) -> Optional[PixelCondition]:
        """
        Добавить пиксельное условие.

        Args:
            cond_id: Уникальный идентификатор
            x: Координата X
            y: Координата Y
            color: Цвет RGB
            tolerance: Допуск
            description: Описание

        Returns:
            Созданное условие или None при ошибке
        """
        if self.get_pixel_condition(cond_id):
            return None

        condition = PixelCondition(
            id=cond_id,
            x=x,
            y=y,
            color=color,
            tolerance=tolerance,
            description=description
        )
        self.pixel_conditions.append(condition)
        self.save()
        return condition

    def update_pixel_condition(
            self,
            cond_id: str,
            **kwargs
    ) -> Optional[PixelCondition]:
        """
        Обновить пиксельное условие.

        Args:
            cond_id: ID условия
            **kwargs: Поля для обновления (x, y, color, tolerance, enabled, description)

        Returns:
            Обновлённое условие или None
        """
        condition = self.get_pixel_condition(cond_id)
        if not condition:
            return None

        if "x" in kwargs:
            condition.x = kwargs["x"]
        if "y" in kwargs:
            condition.y = kwargs["y"]
        if "color" in kwargs:
            condition.color = kwargs["color"]
        if "tolerance" in kwargs:
            condition.tolerance = kwargs["tolerance"]
        if "enabled" in kwargs:
            condition.enabled = kwargs["enabled"]
        if "description" in kwargs:
            condition.description = kwargs["description"]

        self.save()
        return condition

    def delete_pixel_condition(self, cond_id: str) -> bool:
        """Удалить пиксельное условие"""
        for i, cond in enumerate(self.pixel_conditions):
            if cond.id == cond_id:
                self.pixel_conditions.pop(i)
                self.save()
                return True
        return False

    def get_pixel_condition(self, cond_id: str) -> Optional[PixelCondition]:
        """Получить пиксельное условие по ID"""
        for cond in self.pixel_conditions:
            if cond.id == cond_id:
                return cond
        return None

    def get_all_pixel_conditions(self) -> List[PixelCondition]:
        """Получить все пиксельные условия"""
        return self.pixel_conditions.copy()

    def get_pixel_conditions_list(self) -> List[Dict[str, Any]]:
        """Получить список условий для UI"""
        return [
            {
                "id": c.id,
                "x": c.x,
                "y": c.y,
                "color": f"({c.color[0]}, {c.color[1]}, {c.color[2]})",
                "tolerance": c.tolerance,
                "enabled": c.enabled,
            }
            for c in self.pixel_conditions
        ]

    def check_pixel_condition(self, cond_id: str) -> bool:
        """
        Проверить пиксельное условие.

        Args:
            cond_id: ID условия

        Returns:
            True если условие выполнено
        """
        import pyautogui

        condition = self.get_pixel_condition(cond_id)
        if not condition or not condition.enabled:
            return True

        try:
            current_color = pyautogui.pixel(condition.x, condition.y)
            return condition.check(current_color)
        except Exception:
            return False

    # ========== ИЗОБРАЖЕНИЯ УСЛОВИЯ ==========

    def add_image_condition(
            self,
            cond_id: str,
            image_path: str,
            image_data: Optional[str] = None,
            area: Optional[Tuple[int, int, int, int]] = None,
            confidence: float = 0.8,
            **kwargs
    ) -> Optional[ImageCondition]:
        """
        Добавить условие по изображению.

        Args:
            cond_id: Уникальный идентификатор
            image_path: Путь к изображению
            image_data: Base64 данные изображения
            area: Область поиска (x1, y1, x2, y2)
            confidence: Порог совпадения
            **kwargs: Дополнительные параметры

        Returns:
            Созданное условие или None
        """
        if self.get_image_condition(cond_id):
            return None

        condition = ImageCondition(
            id=cond_id,
            image_path=image_path,
            image_data=image_data,
            area=area,
            confidence=confidence,
            multi_scale=kwargs.get("multi_scale", False),
            rotation_tolerance=kwargs.get("rotation_tolerance", 0),
            search_method=kwargs.get("search_method", "template_matching"),
            action_on_match=kwargs.get("action_on_match", "click_center"),
            offset_x=kwargs.get("offset_x", 0),
            offset_y=kwargs.get("offset_y", 0),
            click_all=kwargs.get("click_all", False),
            save_screenshot=kwargs.get("save_screenshot", False),
            description=kwargs.get("description", ""),
        )
        self.image_conditions.append(condition)
        self.save()
        return condition

    def delete_image_condition(self, cond_id: str) -> bool:
        """Удалить условие по изображению"""
        for i, cond in enumerate(self.image_conditions):
            if cond.id == cond_id:
                self.image_conditions.pop(i)
                self.save()
                return True
        return False

    def get_image_condition(self, cond_id: str) -> Optional[ImageCondition]:
        """Получить условие по изображению по ID"""
        for cond in self.image_conditions:
            if cond.id == cond_id:
                return cond
        return None

    def get_all_image_conditions(self) -> List[ImageCondition]:
        """Получить все условия по изображению"""
        return self.image_conditions.copy()

    def check_image_condition(self, cond_id: str) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        Проверить условие по изображению.

        Args:
            cond_id: ID условия

        Returns:
            (True/False, позиция центра найденного изображения)
        """
        condition = self.get_image_condition(cond_id)
        if not condition or not condition.enabled:
            return True, None

        if not self.app or not hasattr(self.app, 'find_image_advanced'):
            return False, None

        try:
            found, pos = self.app.find_image_advanced(
                condition.image_path,
                area=condition.area,
                confidence=condition.confidence,
                multi_scale=condition.multi_scale,
                rotation=condition.rotation_tolerance,
                method=condition.search_method
            )
            if found and pos and (condition.offset_x != 0 or condition.offset_y != 0):
                pos = (pos[0] + condition.offset_x, pos[1] + condition.offset_y)
            return found, pos
        except Exception:
            return False, None

    # ========== ОБЩИЕ МЕТОДЫ ==========

    def get_condition_by_id(self, cond_id: str) -> Optional[Dict[str, Any]]:
        """Получить условие любого типа по ID"""
        pixel = self.get_pixel_condition(cond_id)
        if pixel:
            return {"type": "pixel", "data": pixel}

        image = self.get_image_condition(cond_id)
        if image:
            return {"type": "image", "data": image}

        return None

    def clear_all(self) -> None:
        """Очистить все условия"""
        self.pixel_conditions.clear()
        self.image_conditions.clear()
        self.sound_conditions.clear()
        self.save()

    def get_summary(self) -> Dict[str, int]:
        """Получить сводку по условиям"""
        return {
            "pixel_conditions": len(self.pixel_conditions),
            "enabled_pixel": sum(1 for c in self.pixel_conditions if c.enabled),
            "image_conditions": len(self.image_conditions),
            "enabled_image": sum(1 for c in self.image_conditions if c.enabled),
        }
    # ========== ЗВУКОВЫЕ УСЛОВИЯ ==========

    def add_sound_condition(
        self,
        cond_id: str,
        threshold: int = 500,
        duration: float = 0.5,
        action_on_match: str = "click_center",
        click_x: int = 0,
        click_y: int = 0,
        description: str = ""
    ) -> Optional[SoundConditionData]:
        """Добавить звуковое условие"""
        if self.get_sound_condition(cond_id):
            return None

        condition = SoundConditionData(
            id=cond_id,
            threshold=threshold,
            duration=duration,
            action_on_match=action_on_match,
            click_x=click_x,
            click_y=click_y,
            description=description
        )
        self.sound_conditions.append(condition)
        self.save()
        return condition

    def delete_sound_condition(self, cond_id: str) -> bool:
        """Удалить звуковое условие"""
        for i, cond in enumerate(self.sound_conditions):
            if cond.id == cond_id:
                self.sound_conditions.pop(i)
                self.save()
                return True
        return False

    def get_sound_condition(self, cond_id: str) -> Optional[SoundConditionData]:
        """Получить звуковое условие по ID"""
        for cond in self.sound_conditions:
            if cond.id == cond_id:
                return cond
        return None

    def get_all_sound_conditions(self) -> List[SoundConditionData]:
        """Получить все звуковые условия"""
        return self.sound_conditions.copy()


if __name__ == "__main__":
    # Тестирование модуля условий
    print("=" * 50)
    print("Testing ConditionManager Module")
    print("=" * 50)


    # Создаём мок-приложение
    class MockApp:
        def find_image_advanced(self, *args, **kwargs):
            return False, None


    app = MockApp()
    manager = ConditionManager(app)

    print("\n📋 Adding pixel condition:")
    cond = manager.add_pixel_condition("test_pixel", 100, 200, (255, 0, 0), tolerance=15)
    if cond:
        print(f"   Added: {cond.id} at ({cond.x}, {cond.y}) color={cond.color}")

    print("\n📋 Adding image condition:")
    img_cond = manager.add_image_condition(
        "test_image",
        "C:/test.png",
        confidence=0.85,
        multi_scale=True
    )
    if img_cond:
        print(f"   Added: {img_cond.id} from {img_cond.image_path}")

    print("\n📊 Summary:")
    summary = manager.get_summary()
    print(f"   Pixel conditions: {summary['pixel_conditions']}")
    print(f"   Image conditions: {summary['image_conditions']}")

    print("\n📋 Getting all pixel conditions:")
    for c in manager.get_pixel_conditions_list():
        print(f"   {c['id']}: ({c['x']}, {c['y']}) - {c['color']}")

    print("\n✅ Module ready!")