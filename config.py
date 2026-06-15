"""
Clixpert S Pro Ultimate - Configuration File
Все константы и настройки приложения
"""

import os
from pathlib import Path
from datetime import datetime

# ============== ВЕРСИЯ И ИНФОРМАЦИЯ ==============
VERSION = "5.0.0"
VERSION_CODE = 5000
APP_NAME = "Clixpert S Pro Ultimate"
APP_NAME_SHORT = "Clixpert S"
AUTHOR = "Professional Automation Tool"
COPYRIGHT = f"© 2024-{datetime.now().year} {AUTHOR}"
WEBSITE = "https://clixpert.pro"
REPOSITORY = "https://github.com/clixpert/clixpert-s-pro"

# ============== ПУТИ ==============
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
PROFILES_DIR = DATA_DIR / "profiles"
LOGS_DIR = DATA_DIR / "logs"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
CACHE_DIR = DATA_DIR / "cache"
TEMP_DIR = DATA_DIR / "temp"
ICONS_DIR = BASE_DIR / "resources" / "icons"
STYLES_DIR = BASE_DIR / "resources" / "styles"

# Создаём все необходимые папки
for dir_path in [DATA_DIR, PROFILES_DIR, LOGS_DIR, SCREENSHOTS_DIR, CACHE_DIR, TEMP_DIR, ICONS_DIR, STYLES_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# ============== НАСТРОЙКИ ПО УМОЛЧАНИЮ ==============
DEFAULT_SETTINGS = {
    # Режим работы
    "mode": 0,  # 0 - бесконечный, 1 - ограниченный
    "initial_count": 100.0,
    "deduction": 10.0,
    "deduction_mult": 0.33,

    # Задержки
    "global_delay_ms": 1000,
    "random_delay_ms": 100,  # вариация задержки

    # Цвет и условия
    "color_tolerance": 10,
    "use_conditions": True,

    # Горячие клавиши
    "hotkey_record_click": "f2",
    "hotkey_record_key": "f3",
    "hotkey_toggle": "f1",
    "hotkey_record_start": "f8",
    "hotkey_record_stop": "f9",

    # UI
    "always_on_top": False,
    "show_progress_window": False,
    "language": "ru",
    "theme": "dark",
    "show_notifications": True,
    "sound_alerts": False,

    # Человеческое поведение
    "humanize_mouse": True,
    "humanize_keys": True,
    "humanize_scroll": True,
    "humanize_type": True,
    "bezier_movement": True,
    "random_click_offset": 5,
    "click_hold_min": 50,
    "click_hold_max": 200,
    "key_hold_min": 50,
    "key_hold_max": 150,
    "human_type_speed_min": 0.05,
    "human_type_speed_max": 0.15,
    "human_type_errors": 0.02,

    # Поиск изображений
    "image_tolerance": 80,
    "multi_scale_search": False,
    "rotation_tolerance": 0,
    "search_method": "template_matching",  # template_matching, feature_matching, canny_edge
    "max_matches": 10,

    # Предобработка изображений
    "preprocess_grayscale": False,
    "preprocess_blur": False,
    "preprocess_threshold": False,
    "preprocess_edge_detection": False,
    "preprocess_contrast": False,

    # Цикл поиска
    "loop_until_found": False,
    "max_attempts": 10,
    "attempt_delay": 500,
    "action_on_match": "click_center",
    "click_all_matches": False,
    "save_screenshot_on_match": False,

    # Telegram
    "telegram_token": "",
    "telegram_chat_id": "",
    "telegram_notify": False,

    # OCR
    "ocr_tolerance": 80,

    # Звук
    "sound_enabled": False,
    "sound_threshold": 500,

    # Логирование
    "log_to_file": True,
    "max_log_size_mb": 10,
    "screenshot_on_error": True,

    # Прокси
    "use_proxy": False,
    "proxy_host": "",
    "proxy_port": "",

    # Автозапуск
    "auto_start": False,
}

# ============== ЦВЕТА ТЕМ ==============
DARK_THEME = {
    "bg": "#1a1a2e",
    "bg_light": "#1e1e2f",
    "bg_dark": "#0d0d1a",
    "fg": "#ffffff",
    "fg_secondary": "#aaaaaa",
    "accent": "#5a9cff",
    "accent_hover": "#4a8aef",
    "accent_pressed": "#3a7adf",
    "secondary": "#3a3a5c",
    "secondary_hover": "#4a4a6c",
    "success": "#2a8c4a",
    "success_hover": "#3a9c5a",
    "error": "#8c2a2a",
    "error_hover": "#9c3a3a",
    "warning": "#cc8a2a",
    "info": "#5a9cff",
    "border": "#2a2a3c",
    "editor_bg": "#2a2a3c",
    "editor_fg": "#aaccff",
    "log_fg": "#88ff88",
    "log_error": "#ff8888",
    "log_warning": "#ffcc88",
    "progress_bg": "#2a2a3c",
    "progress_fg": "#5a9cff",
}

LIGHT_THEME = {
    "bg": "#f0f0f0",
    "bg_light": "#ffffff",
    "bg_dark": "#e0e0e0",
    "fg": "#1a1a2e",
    "fg_secondary": "#666666",
    "accent": "#4a7acc",
    "accent_hover": "#3a6abc",
    "accent_pressed": "#2a5aac",
    "secondary": "#cccccc",
    "secondary_hover": "#bbbbbb",
    "success": "#2a8c4a",
    "success_hover": "#3a9c5a",
    "error": "#cc4444",
    "error_hover": "#bb3333",
    "warning": "#cc8a2a",
    "info": "#4a7acc",
    "border": "#cccccc",
    "editor_bg": "#ffffff",
    "editor_fg": "#1a1a2e",
    "log_fg": "#2a6c3a",
    "log_error": "#cc4444",
    "log_warning": "#cc8a2a",
    "progress_bg": "#e0e0e0",
    "progress_fg": "#4a7acc",
}

# ============== НАСТРОЙКИ OKНОВ ==============
WINDOW_SIZE = {
    "width": 1400,
    "height": 950,
    "min_width": 1200,
    "min_height": 800,
}

PROGRESS_WINDOW_SIZE = {
    "width": 300,
    "height": 120,
}

# ============== ТАЙМАУТЫ ==============
TIMEOUTS = {
    "hotkey_recording": 10,  # секунд
    "wait_for_condition": 30,  # секунд
    "telegram_request": 5,  # секунд
    "scheduler_check": 1,  # секунд
}

# ============== ЛИМИТЫ ==============
LIMITS = {
    "max_actions": 1000,
    "max_logs": 5000,
    "max_click_positions": 10000,
    "max_image_cache": 50,
    "max_telegram_retries": 3,
}

# ============== ФОРМАТЫ ==============
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT_FILE = "%Y%m%d_%H%M%S"
TIME_FORMAT = "%H:%M"
TIME_FORMAT_FULL = "%H:%M:%S.%f"

# ============== ФАЙЛОВЫЕ РАСШИРЕНИЯ ==============
EXTENSIONS = {
    "profile": ".clixpro",
    "script": ".clix",
    "log": ".txt",
    "screenshot": ".png",
    "backup": ".bak",
}

# ============== SQL ЗАПРОСЫ ==============
SQL_CREATE_TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    script TEXT NOT NULL,
    task_time TEXT NOT NULL,
    days TEXT,
    enabled INTEGER DEFAULT 1,
    last_run TEXT,
    run_count INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
)
"""


# ============== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==============

def get_theme(theme_name: str = "dark") -> dict:
    """Получить цвета темы"""
    if theme_name == "light":
        return LIGHT_THEME
    return DARK_THEME


def get_settings_file_path() -> Path:
    """Получить путь к файлу настроек"""
    return DATA_DIR / "settings.json"


def get_db_path() -> Path:
    """Получить путь к базе данных планировщика"""
    return DATA_DIR / "clixpert_tasks.db"


def get_log_file_path() -> Path:
    """Получить путь к файлу лога"""
    today = datetime.now().strftime("%Y%m%d")
    return LOGS_DIR / f"clixpert_{today}.log"


def get_screenshot_path(prefix: str = "") -> Path:
    """Получить путь для сохранения скриншота"""
    timestamp = datetime.now().strftime(DATE_FORMAT_FILE)
    if prefix:
        filename = f"{prefix}_{timestamp}{EXTENSIONS['screenshot']}"
    else:
        filename = f"screenshot_{timestamp}{EXTENSIONS['screenshot']}"
    return SCREENSHOTS_DIR / filename


# ============== ПРОВЕРКА ЗАВИСИМОСТЕЙ ==============

def check_dependencies() -> dict:
    """Проверить установленные зависимости"""
    deps = {
        "opencv-python": False,
        "numpy": False,
        "pyautogui": False,
        "keyboard": False,
        "Pillow": False,
        "pystray": False,
        "pywinstyles": False,
        "requests": False,
        "pytesseract": False,
        "plyer": False,
        "pyaudio": False,
    }

    try:
        import cv2
        deps["opencv-python"] = True
    except ImportError:
        pass

    try:
        import numpy
        deps["numpy"] = True
    except ImportError:
        pass

    try:
        import pyautogui
        deps["pyautogui"] = True
    except ImportError:
        pass

    try:
        import keyboard
        deps["keyboard"] = True
    except ImportError:
        pass

    try:
        from PIL import Image
        deps["Pillow"] = True
    except ImportError:
        pass

    try:
        import pystray
        deps["pystray"] = True
    except ImportError:
        pass

    try:
        import pywinstyles
        deps["pywinstyles"] = True
    except ImportError:
        pass

    try:
        import requests
        deps["requests"] = True
    except ImportError:
        pass

    try:
        import pytesseract
        deps["pytesseract"] = True
    except ImportError:
        pass

    try:
        from plyer import notification
        deps["plyer"] = True
    except ImportError:
        pass

    try:
        import pyaudio
        deps["pyaudio"] = True
    except ImportError:
        pass

    return deps


def is_admin() -> bool:
    """Проверить, запущена ли программа от администратора"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


if __name__ == "__main__":
    # Тестирование конфигурации
    print("=" * 50)
    print(f"{APP_NAME} v{VERSION}")
    print("=" * 50)
    print(f"\n📁 Пути:")
    print(f"   База: {BASE_DIR}")
    print(f"   Данные: {DATA_DIR}")
    print(f"   Профили: {PROFILES_DIR}")
    print(f"   Логи: {LOGS_DIR}")
    print(f"\n🔧 Зависимости:")
    for dep, installed in check_dependencies().items():
        status = "✅" if installed else "❌"
        print(f"   {status} {dep}")
    print(f"\n👑 Администратор: {'✅' if is_admin() else '❌'}")
    print("=" * 50)