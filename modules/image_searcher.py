"""
Clixpert S Pro Ultimate - Advanced Image Searcher Module
Продвинутый поиск изображений с поддержкой:
- Multi-scale поиск (разные размеры)
- Поворот изображения
- Feature matching (SIFT) для устойчивости к трансформациям
- Предобработка изображений
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List, Dict, Any


class AdvancedImageSearcher:
    """
    Продвинутый поиск изображений на экране.
    Поддерживает поиск с изменением масштаба, поворотом, feature matching.
    """

    def __init__(self):
        self.sift_available = False
        self.sift = None
        self.flann = None

        # Инициализация SIFT если доступен
        try:
            self.sift = cv2.SIFT_create() if hasattr(cv2, 'SIFT_create') else cv2.xfeatures2d.SIFT_create()
            self.flann_params = dict(algorithm=1, trees=5)
            self.flann = cv2.FlannBasedMatcher(self.flann_params, {})
            self.sift_available = True
        except Exception:
            self.sift_available = False

        # Кэш для предобработанных шаблонов
        self._template_cache: Dict[str, np.ndarray] = {}
        self._max_cache_size = 50

    def preprocess_image(
            self,
            image: np.ndarray,
            preprocessing_flags: Dict[str, bool]
    ) -> np.ndarray:
        """
        Предобработка изображения для улучшения поиска.

        Args:
            image: Исходное изображение
            preprocessing_flags: Флаги предобработки

        Returns:
            Обработанное изображение
        """
        img = image.copy()

        # Оттенки серого
        if preprocessing_flags.get('grayscale', False):
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Размытие
        if preprocessing_flags.get('blur', False):
            img = cv2.GaussianBlur(img, (5, 5), 0)

        # Пороговая обработка
        if preprocessing_flags.get('threshold', False):
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

        # Детекция границ
        if preprocessing_flags.get('edge_detection', False):
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.Canny(img, 50, 150)

        # Увеличение контраста (CLAHE)
        if preprocessing_flags.get('contrast_enhance', False):
            if len(img.shape) == 3:
                lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                l = clahe.apply(l)
                img = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
            else:
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                img = clahe.apply(img)

        return img

    def find_template_multi_scale(
            self,
            screenshot: np.ndarray,
            template: np.ndarray,
            scale_range: Tuple[float, float] = (0.5, 1.5),
            scale_step: float = 0.1,
            confidence: float = 0.7
    ) -> Tuple[Optional[Tuple[int, int, int, int]], float, float]:
        """
        Поиск изображения с изменением масштаба.

        Args:
            screenshot: Скриншот экрана
            template: Шаблон для поиска
            scale_range: Диапазон масштабов (min, max)
            scale_step: Шаг изменения масштаба
            confidence: Порог уверенности

        Returns:
            (позиция (x, y, w, h), уверенность, использованный масштаб)
        """
        best_match = None
        best_conf = 0
        best_scale = 1.0

        scales = np.arange(scale_range[0], scale_range[1], scale_step)

        for scale in scales:
            if scale == 1.0:
                scaled_template = template
            else:
                new_w = int(template.shape[1] * scale)
                new_h = int(template.shape[0] * scale)
                scaled_template = cv2.resize(template, (new_w, new_h))

            if scaled_template.shape[0] > screenshot.shape[0] or scaled_template.shape[1] > screenshot.shape[1]:
                continue

            try:
                result = cv2.matchTemplate(screenshot, scaled_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val > best_conf and max_val >= confidence:
                    best_conf = max_val
                    best_match = (max_loc[0], max_loc[1], scaled_template.shape[1], scaled_template.shape[0])
                    best_scale = scale
            except Exception:
                continue

        return best_match, best_conf, best_scale

    def find_feature_matching(
            self,
            screenshot: np.ndarray,
            template: np.ndarray,
            confidence: float = 0.6
    ) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
        """
        Поиск по ключевым точкам (SIFT) - устойчив к повороту и масштабу.

        Args:
            screenshot: Скриншот экрана
            template: Шаблон для поиска
            confidence: Порог уверенности

        Returns:
            (позиция (x, y, w, h), уверенность)
        """
        if not self.sift_available or self.sift is None:
            return None, 0

        try:
            # Находим ключевые точки и дескрипторы
            kp1, des1 = self.sift.detectAndCompute(template, None)
            kp2, des2 = self.sift.detectAndCompute(screenshot, None)

            if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
                return None, 0

            # Сопоставление
            matches = self.flann.knnMatch(des1, des2, k=2)

            # Lowe's ratio test
            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)

            if len(good_matches) < 4:
                return None, 0

            # Находим гомографию
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if M is not None:
                h, w = template.shape[:2]
                pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)

                x = int(min(dst[0][0][0], dst[3][0][0]))
                y = int(min(dst[0][0][1], dst[1][0][1]))
                width = int(max(dst[2][0][0], dst[1][0][0]) - x)
                height = int(max(dst[2][0][1], dst[3][0][1]) - y)

                confidence_score = len(good_matches) / max(len(kp1), 1)
                return (x, y, width, height), confidence_score

            return None, 0

        except Exception:
            return None, 0

    def find_with_rotation(
            self,
            screenshot: np.ndarray,
            template: np.ndarray,
            angle_range: Tuple[int, int] = (-30, 30),
            angle_step: int = 10,
            confidence: float = 0.7
    ) -> Tuple[Optional[Tuple[int, int, int, int]], float, int]:
        """
        Поиск изображения с поворотом.

        Args:
            screenshot: Скриншот экрана
            template: Шаблон для поиска
            angle_range: Диапазон углов (min, max)
            angle_step: Шаг изменения угла
            confidence: Порог уверенности

        Returns:
            (позиция (x, y, w, h), уверенность, использованный угол)
        """
        best_match = None
        best_conf = 0
        best_angle = 0
        h, w = template.shape[:2]
        center = (w // 2, h // 2)

        for angle in range(angle_range[0], angle_range[1] + 1, angle_step):
            # Поворачиваем шаблон
            rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(template, rot_mat, (w, h))

            if rotated.shape[0] > screenshot.shape[0] or rotated.shape[1] > screenshot.shape[1]:
                continue

            try:
                result = cv2.matchTemplate(screenshot, rotated, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val > best_conf and max_val >= confidence:
                    best_conf = max_val
                    best_match = (max_loc[0], max_loc[1], w, h)
                    best_angle = angle
            except Exception:
                continue

        return best_match, best_conf, best_angle

    def find_all_matches(
            self,
            screenshot: np.ndarray,
            template: np.ndarray,
            confidence: float = 0.7,
            max_matches: int = 10,
            min_distance: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Найти все совпадения на экране.

        Args:
            screenshot: Скриншот экрана
            template: Шаблон для поиска
            confidence: Порог уверенности
            max_matches: Максимальное количество совпадений
            min_distance: Минимальное расстояние между совпадениями

        Returns:
            Список совпадений с координатами и уверенностью
        """
        matches = []
        try:
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= confidence)

            for pt in zip(*locations[::-1]):
                matches.append({
                    'x': pt[0] + template.shape[1] // 2,
                    'y': pt[1] + template.shape[0] // 2,
                    'confidence': float(result[pt[1], pt[0]])
                })

            # Убираем дубликаты (слишком близкие)
            unique_matches = []
            for match in matches:
                is_unique = True
                for existing in unique_matches:
                    if (abs(match['x'] - existing['x']) < min_distance and
                            abs(match['y'] - existing['y']) < min_distance):
                        if match['confidence'] > existing['confidence']:
                            unique_matches.remove(existing)
                        else:
                            is_unique = False
                        break
                if is_unique:
                    unique_matches.append(match)

            return sorted(unique_matches, key=lambda x: x['confidence'], reverse=True)[:max_matches]

        except Exception:
            return []

    def find_best_match(
            self,
            screenshot: np.ndarray,
            template: np.ndarray,
            method: str = "template_matching",
            confidence: float = 0.7,
            multi_scale: bool = False,
            rotation: int = 0,
            preprocessing: Optional[Dict[str, bool]] = None
    ) -> Tuple[Optional[Tuple[int, int]], float, Dict[str, Any]]:
        """
        Универсальный метод поиска лучшего совпадения.

        Args:
            screenshot: Скриншот экрана
            template: Шаблон для поиска
            method: Метод поиска (template_matching, feature_matching)
            confidence: Порог уверенности
            multi_scale: Использовать multi-scale поиск
            rotation: Максимальный угол поворота
            preprocessing: Флаги предобработки

        Returns:
            (позиция центра, уверенность, метаданные)
        """
        # Предобработка
        if preprocessing:
            screenshot = self.preprocess_image(screenshot, preprocessing)
            template = self.preprocess_image(template, preprocessing)

        metadata = {"method": method, "confidence": confidence}

        # Feature matching (устойчив к трансформациям)
        if method == "feature_matching" and self.sift_available:
            match, conf = self.find_feature_matching(screenshot, template, confidence)
            if match:
                x, y, w, h = match
                metadata["match_type"] = "feature_matching"
                metadata["box"] = (x, y, w, h)
                return (x + w // 2, y + h // 2), conf, metadata

        # Multi-scale поиск
        if multi_scale:
            match, conf, scale = self.find_template_multi_scale(
                screenshot, template, confidence=confidence
            )
            if match:
                x, y, w, h = match
                metadata["match_type"] = "multi_scale"
                metadata["scale"] = scale
                metadata["box"] = (x, y, w, h)
                return (x + w // 2, y + h // 2), conf, metadata

        # Поиск с поворотом
        if rotation > 0:
            match, conf, angle = self.find_with_rotation(
                screenshot, template, angle_range=(-rotation, rotation), confidence=confidence
            )
            if match:
                x, y, w, h = match
                metadata["match_type"] = "rotation"
                metadata["angle"] = angle
                metadata["box"] = (x, y, w, h)
                return (x + w // 2, y + h // 2), conf, metadata

        # Обычный template matching
        try:
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= confidence:
                x, y = max_loc
                h, w = template.shape[:2]
                metadata["match_type"] = "template_matching"
                metadata["box"] = (x, y, w, h)
                return (x + w // 2, y + h // 2), max_val, metadata

        except Exception:
            pass

        return None, 0, metadata

    def clear_cache(self) -> None:
        """Очистить кэш шаблонов"""
        self._template_cache.clear()

    def get_cache_info(self) -> Dict[str, Any]:
        """Получить информацию о кэше"""
        return {
            "size": len(self._template_cache),
            "max_size": self._max_cache_size,
            "keys": list(self._template_cache.keys())
        }


if __name__ == "__main__":
    # Тестирование модуля поиска изображений
    print("=" * 50)
    print("Testing AdvancedImageSearcher Module")
    print("=" * 50)

    searcher = AdvancedImageSearcher()

    print(f"\n🔧 SIFT available: {searcher.sift_available}")

    # Создаём тестовое изображение
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (20, 20), (80, 80), (255, 255, 255), -1)

    print(f"\n📸 Test image created: {test_image.shape}")

    # Тестирование предобработки
    print("\n🖼 Testing preprocessing:")
    preprocessing = {"grayscale": True}
    processed = searcher.preprocess_image(test_image, preprocessing)
    print(f"   Grayscale: {processed.shape}")

    print("\n✅ Module ready!")