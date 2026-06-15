"""
Clixpert S Pro Ultimate - Language Resources
Поддержка русского и английского языков
"""

from config import VERSION, APP_NAME

# ============== РУССКИЙ ЯЗЫК ==============
RUSSIAN = {
    # Основные
    "title": f"{APP_NAME} v{VERSION}",
    "version": f"Версия {VERSION}",
    "author": "Автор: Professional Automation Tool",
    "copyright": f"© 2024-2025 Clixpert S Pro. Все права защищены.",

    # Режим
    "mode": "Режим",
    "infinite": "Бесконечный цикл",
    "limited": "С ограничением",

    # Параметры ограничения
    "limit_params": "Параметры ограничения",
    "initial_count": "Начальное кол-во:",
    "default_deduction": "Вычет по умолчанию:",
    "deduction_mult": "Множитель вычета (0..1):",
    "deduction_hint": "(вычитается: Вычет × (1 - Множитель))",

    # Прогресс
    "progress": "Прогресс",
    "progress_label": "Прогресс: {:.2f} / {:.2f} ({:.1f}%)",
    "eta_label": "Осталось примерно: {}",
    "show_progress_window": "Показывать отдельное окно прогресса",

    # Действия
    "actions": "Последовательность действий",
    "clear": "Очистить",
    "delete": "Удалить",
    "edit": "Редактировать",
    "add_delay": "+ Задержка",
    "save_profile": "Сохранить профиль",
    "load_profile": "Загрузить профиль",
    "conditions": "Условия",
    "conditions_manager": "Управление условиями",

    # Настройки
    "settings": "Настройки",
    "global_delay": "Глоб. задержка (мс):",
    "record_click": "Клавиша записи клика:",
    "record_key": "Клавиша записи клавиши:",
    "toggle": "Клавиша запуска/остановки:",
    "always_on_top": "Окно всегда сверху",
    "color_tolerance": "Допуск цвета (0-50):",
    "use_conditions": "Применять условия (если заданы)",
    "apply_settings": "Применить настройки",

    # Управление
    "start": "Запустить",
    "stop": "Остановить",
    "tray": "Свернуть в трей",
    "exit": "Выход",

    # Статусы
    "waiting": "Ожидание",
    "cycle_running": "Цикл запущен...",
    "cycle_stopped": "Цикл остановлен",
    "cycle_finished": "Цикл завершён",
    "completion_title": "Цикл успешно завершен",
    "completion_message": "УСПЕШНОЕ ЗАВЕРШЕНИЕ",

    # Ошибки
    "error": "Ошибка",
    "no_actions": "Добавьте хотя бы одно действие.",
    "invalid_delay": "Глобальная задержка должна быть неотрицательным целым числом (мс)",
    "cannot_edit_running": "Нельзя редактировать во время работы цикла!",

    # Изображения
    "select_image": "Выберите изображение",
    "confidence": "Порог совпадения (0.5-1.0):",

    # Типы действий
    "click": "Клик",
    "key": "Клавиша",
    "delay": "Пауза",
    "params": "Параметры",
    "delay_ms": "Задержка (мс)",
    "hold_ms": "Удержание (мс)",
    "condition": "Условие",
    "contrib": "Вклад",

    # Редактирование
    "edit_action": "Редактировать действие",
    "save": "Сохранить",
    "cancel": "Отмена",
    "language": "Язык",

    # Горячие клавиши
    "hotkeys_hint": "{}: клик | {}: клавиша | {}: старт/стоп",

    # Типы условий
    "condition_type": "Тип условия",
    "none": "Нет",
    "pixel": "Пиксель",
    "color_area": "Цвет в области",
    "image_search": "Поиск изображения",
    "sound_detection": "Обнаружение звука",

    # Область поиска
    "search_area": "Область поиска",
    "x1": "X1:", "y1": "Y1:", "x2": "X2:", "y2": "Y2:",
    "target_color": "Целевой цвет (RGB)",
    "pick_color": "Взять цвет",
    "select_image_file": "Выбрать файл",

    # Действия при условии
    "skip_on_true": "Пропустить остальные, если условие выполнено",
    "skip_on_false": "Пропустить остальные, если условие НЕ выполнено",
    "progress_contrib": "Вклад в прогресс (пусто = стандартный)",
    "wait_condition": "Ждать выполнения условия (иначе пропустить действие)",

    # Expert Mode
    "expert_mode": "Expert Mode",
    "standard_mode": "Standard Mode",
    "script_editor": "Редактор сценариев",
    "run_script": "Выполнить сценарий",
    "syntax_help": "Помощь по синтаксису",
    "variables": "Переменные",
    "logs": "Логи",
    "clear_logs": "Очистить логи",
    "export_logs": "Экспорт логов",

    # Ошибки синтаксиса
    "syntax_error": "Ошибка синтаксиса",
    "line": "Строка",
    "expected": "Ожидалось",

    # Инструкции
    "loop_instruction": "ЦИКЛ: for {переменная} in {диапазон/список}:",
    "if_instruction": "УСЛОВИЕ: if {условие}:",
    "elif_instruction": "ELIF: elif {условие}:",
    "else_instruction": "ELSE: else:",
    "click_instruction": "КЛИК: click(x, y [, hold_ms])",
    "key_instruction": "КЛАВИША: key(\"клавиша\")",
    "wait_instruction": "ОЖИДАНИЕ: wait(ms)",
    "sleep_instruction": "СОН: sleep(ms)",
    "move_instruction": "ПЕРЕМЕЩЕНИЕ: move(x, y)",
    "scroll_instruction": "СКРОЛЛ: scroll(amount)",
    "type_instruction": "ПЕЧАТЬ: type(\"текст\")",
    "var_assign": "ПРИСВОЕНИЕ: var = значение",
    "print_instruction": "ВЫВОД: print(значение)",

    # Проверки условий
    "condition_check": "ПРОВЕРКА УСЛОВИЙ: exists_image(\"путь\"), color_match(x,y,r,g,b,tol), pixel_match(x,y,ref_id), find_text(\"текст\"), sound_detected(threshold)",

    "math_ops": "МАТЕМАТИКА: +, -, *, /, //, %, **",
    "comparisons": "СРАВНЕНИЯ: ==, !=, <, >, <=, >=",
    "logic_ops": "ЛОГИКА: and, or, not",

    # Recorder
    "record_mode": "Режим записи",
    "start_record": "Начать запись",
    "stop_record": "Остановить запись",
    "record_hint": "Запись действий... Нажмите Stop для завершения",
    "recording": "ИДЁТ ЗАПИСЬ...",
    "playback": "Воспроизведение",
    "copy_to_expert": "Копировать в Expert Mode",

    # Scheduler
    "scheduler": "Планировщик",
    "schedule_task": "Запланировать задачу",
    "task_name": "Имя задачи:",
    "task_time": "Время:",
    "task_days": "Дни:",
    "add_task": "Добавить задачу",
    "delete_task": "Удалить задачу",
    "refresh_tasks": "Обновить",
    "no_tasks": "Нет запланированных задач",
    "task_added": "Задача добавлена",
    "task_deleted": "Задача удалена",

    # Debug
    "debug_mode": "Режим отладки",
    "step_mode": "Пошаговый режим",
    "breakpoints": "Точки остановки",
    "slow_mode": "Slow Motion (мс/шаг):",
    "continue_debug": "Продолжить",
    "step_over": "Шаг с обходом",

    # Human behavior
    "human_behavior": "Человеческое поведение",
    "key_down": "Зажать клавишу",
    "key_up": "Отжать клавишу",
    "mouse_down": "Зажать кнопку мыши",
    "mouse_up": "Отжать кнопку мыши",
    "click_human": "Человеческий клик",
    "move_human": "Человеческое движение",
    "drag_human": "Человеческое перетаскивание",
    "type_human": "Человеческая печать",
    "key_human": "Человеческое нажатие клавиши",
    "scroll_human": "Человеческий скролл",

    # OCR
    "ocr_search": "Поиск текста (OCR)",
    "target_text": "Искомый текст:",
    "text_tolerance": "Допуск текста (%):",

    # Telegram
    "telegram_bot": "Telegram Бот",
    "bot_token": "Токен бота:",
    "chat_id": "Chat ID:",
    "send_test": "Отправить тест",
    "notify_on_error": "Уведомлять об ошибках",
    "telegram_test_sent": "Тестовое сообщение отправлено",
    "telegram_test_failed": "Ошибка отправки",

    # Heatmap
    "heatmap": "Тепловая карта кликов",
    "show_heatmap": "Показать тепловую карту",
    "reset_stats": "Сбросить статистику",
    "no_click_data": "Нет данных о кликах",

    # Performance
    "performance": "Производительность",
    "avg_response": "Ср. время отклика:",
    "success_rate": "Процент успеха:",
    "total_actions": "Всего действий:",
    "total_time": "Общее время:",

    # Действия при совпадении
    "click_on_match": "Кликнуть в центр найденного совпадения",
    "click_at_coords": "Кликнуть по указанным координатам",
    "image_tolerance": "Допуск изображения (0-100%):",
    "multi_scale_search": "Масштабирование поиска (для полупрозрачных)",
    "rotation_tolerance": "Допуск поворота (градусы):",
    "search_method": "Метод поиска:",
    "canny_edge": "Canny Edge Detection",
    "template_matching": "Template Matching",
    "feature_matching": "Feature Matching (SIFT)",
    "multiple_results": "Найти все совпадения",
    "max_matches": "Макс. кол-во совпадений:",
    "action_on_match": "Действие при совпадении:",
    "click_center": "Клик в центр",
    "click_random_offset": "Клик со смещением",
    "drag_to": "Перетащить в точку",
    "hover": "Навести курсор",
    "click_all": "Кликнуть по всем найденным",
    "save_screenshot": "Сохранить скриншот при совпадении",
    "loop_until_found": "Циклить до нахождения",
    "max_attempts": "Макс. попыток:",
    "delay_between_attempts": "Задержка между попытками (мс):",

    # Advanced
    "advanced_settings": "Расширенные настройки",
    "image_preprocessing": "Предобработка изображения",
    "grayscale": "Оттенки серого",
    "blur": "Размытие",
    "threshold": "Пороговая обработка",
    "edge_detection": "Детекция границ",
    "contrast_enhance": "Увеличение контраста",

    # ROI
    "roi_selector": "Выбрать область на экране",
    "select_roi": "Выделить область",
    "roi_selected": "Область выделена",
    "roi_clear": "Очистить область",

    # Preview и тестирование
    "preview_match": "Предпросмотр совпадения",
    "test_condition": "Проверить условие сейчас",
    "condition_passed": "Условие выполнено!",
    "condition_failed": "Условие не выполнено",

    # Переменные
    "variable_condition": "Условие на переменную",
    "compare_var": "Сравнить переменную",
    "set_variable": "Установить переменную",
    "increment_var": "Инкремент переменной",
    "decrement_var": "Декремент переменной",

    # Доп. настройки клика
    "random_click_offset": "Случайное смещение клика (пикс):",
    "click_delay_variation": "Вариация задержки (мс):",
    "humanize_mouse": "Имитация движения мыши",
    "bezier_curve": "Кривая Безье для движения",

    # Меню
    "about": "О программе",
    "check_updates": "Проверить обновления",
    "backup": "Резервное копирование",
    "restore": "Восстановление",
    "export_html": "Экспорт в HTML",
    "export_pdf": "Экспорт в PDF",
    "run_as_admin": "Запуск от администратора",
    "minimize_to_tray": "Сворачивать в трей",
    "show_notifications": "Показывать уведомления",
    "sound_alerts": "Звуковые оповещения",

    # Тема
    "theme": "Тема оформления",
    "dark_theme": "Тёмная тема",
    "light_theme": "Светлая тема",

    # Система
    "auto_start": "Автозапуск с Windows",
    "hotkey_config": "Настройка горячих клавиш",
    "record_mouse": "Запись движений мыши",
    "record_all": "Запись всех действий",
    "playback_speed": "Скорость воспроизведения",
    "loop_video": "Зациклить видео",
    "export_video": "Экспорт в видео",

    # Логирование
    "screenshot_on_error": "Скриншот при ошибке",
    "log_to_file": "Логировать в файл",
    "max_log_size": "Макс. размер лога (МБ):",

    # Прокси
    "proxy_settings": "Настройки прокси",
    "proxy_host": "Прокси хост:",
    "proxy_port": "Прокси порт:",
    "use_proxy": "Использовать прокси",

    # Звук
    "sound_detection": "Обнаружение звука",
    "sound_threshold": "Порог звука:",
    "wait_for_sound": "Ожидать звук",

    # Звуковые условия
    "sound_conditions": "🎵 Звуковые условия",
    "sound_threshold": "Порог звука",
    "sound_duration": "Длительность (с)",
    "sound_status": "Статус звука",
    "available": "Доступен",
    "not_installed": "PyAudio не установлен",

    # Вкладки
    "tab_main": "⚡ Главная",
    "tab_expert": "🎯 Expert Mode",
    "tab_conditions": "🎨 Условия",
    "tab_scheduler": "⏰ Планировщик",
    "tab_stats": "📊 Статистика",
    "tab_settings": "⚙ Настройки",
}

# ============== АНГЛИЙСКИЙ ЯЗЫК ==============

ENGLISH = {
    # Основные
    "title": f"{APP_NAME} v{VERSION}",
    "version": f"Version {VERSION}",
    "author": "Author: Professional Automation Tool",
    "copyright": f"© 2024-2025 Clixpert S Pro. All rights reserved.",

    # Mode
    "mode": "Mode",
    "infinite": "Infinite loop",
    "limited": "Limited",

    # Limit parameters
    "limit_params": "Limit parameters",
    "initial_count": "Initial count:",
    "default_deduction": "Default deduction:",
    "deduction_mult": "Deduction multiplier (0..1):",
    "deduction_hint": "(subtracted: Deduction × (1 - Multiplier))",

    # Progress
    "progress": "Progress",
    "progress_label": "Progress: {:.2f} / {:.2f} ({:.1f}%)",
    "eta_label": "Estimated time left: {}",
    "show_progress_window": "Show separate progress window",

    # Actions
    "actions": "Action sequence",
    "clear": "Clear",
    "delete": "Delete",
    "edit": "Edit",
    "add_delay": "+ Delay",
    "save_profile": "Save profile",
    "load_profile": "Load profile",
    "conditions": "Conditions",
    "conditions_manager": "Conditions Manager",

    # Settings
    "settings": "Settings",
    "global_delay": "Global delay (ms):",
    "record_click": "Record click hotkey:",
    "record_key": "Record key hotkey:",
    "toggle": "Start/stop hotkey:",
    "always_on_top": "Always on top",
    "color_tolerance": "Color tolerance (0-50):",
    "use_conditions": "Apply conditions (if set)",
    "apply_settings": "Apply settings",

    # Control
    "start": "Start",
    "stop": "Stop",
    "tray": "Minimize to tray",
    "exit": "Exit",

    # Status
    "waiting": "Waiting",
    "cycle_running": "Cycle running...",
    "cycle_stopped": "Cycle stopped",
    "cycle_finished": "Cycle finished",
    "completion_title": "Cycle completed",
    "completion_message": "SUCCESSFUL COMPLETION",

    # Errors
    "error": "Error",
    "no_actions": "Add at least one action.",
    "invalid_delay": "Global delay must be a non-negative integer (ms)",
    "cannot_edit_running": "Cannot edit while cycle is running!",

    # Images
    "select_image": "Select image",
    "confidence": "Confidence threshold (0.5-1.0):",

    # Action types
    "click": "Click",
    "key": "Key",
    "delay": "Delay",
    "params": "Parameters",
    "delay_ms": "Delay (ms)",
    "hold_ms": "Hold (ms)",
    "condition": "Condition",
    "contrib": "Contrib",

    # Editing
    "edit_action": "Edit action",
    "save": "Save",
    "cancel": "Cancel",
    "language": "Language",

    # Hotkeys
    "hotkeys_hint": "{}: click | {}: key | {}: start/stop",

    # Condition types
    "condition_type": "Condition type",
    "none": "None",
    "pixel": "Pixel",
    "color_area": "Color in area",
    "image_search": "Image search",
    "sound_detection": "Sound detection",

    # Search area
    "search_area": "Search area",
    "x1": "X1:", "y1": "Y1:", "x2": "X2:", "y2": "Y2:",
    "target_color": "Target color (RGB)",
    "pick_color": "Pick color",
    "select_image_file": "Select file",

    # Condition actions
    "skip_on_true": "Skip rest if condition met",
    "skip_on_false": "Skip rest if condition NOT met",
    "progress_contrib": "Contrib (empty=default)",
    "wait_condition": "Wait for condition (otherwise skip action)",

    # Expert Mode
    "expert_mode": "Expert Mode",
    "standard_mode": "Standard Mode",
    "script_editor": "Script Editor",
    "run_script": "Run Script",
    "syntax_help": "Syntax Help",
    "variables": "Variables",
    "logs": "Logs",
    "clear_logs": "Clear Logs",
    "export_logs": "Export Logs",

    # Syntax errors
    "syntax_error": "Syntax Error",
    "line": "Line",
    "expected": "Expected",

    # Instructions
    "loop_instruction": "LOOP: for {var} in {range/list}:",
    "if_instruction": "CONDITION: if {condition}:",
    "elif_instruction": "ELIF: elif {condition}:",
    "else_instruction": "ELSE: else:",
    "click_instruction": "CLICK: click(x, y [, hold_ms])",
    "key_instruction": "KEY: key(\"key_name\")",
    "wait_instruction": "WAIT: wait(ms)",
    "sleep_instruction": "SLEEP: sleep(ms)",
    "move_instruction": "MOVE: move(x, y)",
    "scroll_instruction": "SCROLL: scroll(amount)",
    "type_instruction": "TYPE: type(\"text\")",
    "var_assign": "ASSIGN: var = value",
    "print_instruction": "PRINT: print(value)",

    # Condition checks
    "condition_check": "CONDITION CHECKS: exists_image(\"path\"), color_match(x,y,r,g,b,tol), pixel_match(x,y,ref_id), find_text(\"text\"), sound_detected(threshold)",

    "math_ops": "MATH: +, -, *, /, //, %, **",
    "comparisons": "COMPARISONS: ==, !=, <, >, <=, >=",
    "logic_ops": "LOGIC: and, or, not",

    # Recorder
    "record_mode": "Record Mode",
    "start_record": "Start Record",
    "stop_record": "Stop Record",
    "record_hint": "Recording actions... Press Stop to finish",
    "recording": "RECORDING...",
    "playback": "Playback",
    "copy_to_expert": "Copy to Expert Mode",

    # Scheduler
    "scheduler": "Scheduler",
    "schedule_task": "Schedule Task",
    "task_name": "Task name:",
    "task_time": "Time:",
    "task_days": "Days:",
    "add_task": "Add Task",
    "delete_task": "Delete Task",
    "refresh_tasks": "Refresh",
    "no_tasks": "No scheduled tasks",
    "task_added": "Task added",
    "task_deleted": "Task deleted",

    # Debug
    "debug_mode": "Debug Mode",
    "step_mode": "Step Mode",
    "breakpoints": "Breakpoints",
    "slow_mode": "Slow Motion (ms/step):",
    "continue_debug": "Continue",
    "step_over": "Step Over",

    # Human behavior
    "human_behavior": "Human Behavior",
    "key_down": "Hold Key",
    "key_up": "Release Key",
    "mouse_down": "Hold Mouse",
    "mouse_up": "Release Mouse",
    "click_human": "Human Click",
    "move_human": "Human Move",
    "drag_human": "Human Drag",
    "type_human": "Human Typing",
    "key_human": "Human Key Press",
    "scroll_human": "Human Scroll",

    # OCR
    "ocr_search": "OCR Text Search",
    "target_text": "Target text:",
    "text_tolerance": "Text tolerance (%):",

    # Telegram
    "telegram_bot": "Telegram Bot",
    "bot_token": "Bot token:",
    "chat_id": "Chat ID:",
    "send_test": "Send test",
    "notify_on_error": "Notify on error",
    "telegram_test_sent": "Test message sent",
    "telegram_test_failed": "Send failed",

    # Heatmap
    "heatmap": "Click Heatmap",
    "show_heatmap": "Show Heatmap",
    "reset_stats": "Reset Stats",
    "no_click_data": "No click data available",

    # Performance
    "performance": "Performance",
    "avg_response": "Avg response:",
    "success_rate": "Success rate:",
    "total_actions": "Total actions:",
    "total_time": "Total time:",

    # Match actions
    "click_on_match": "Click at match center",
    "click_at_coords": "Click at specified coordinates",
    "image_tolerance": "Image tolerance (0-100%):",
    "multi_scale_search": "Multi-scale search (for transparent)",
    "rotation_tolerance": "Rotation tolerance (degrees):",
    "search_method": "Search method:",
    "canny_edge": "Canny Edge Detection",
    "template_matching": "Template Matching",
    "feature_matching": "Feature Matching (SIFT)",
    "multiple_results": "Find all matches",
    "max_matches": "Max matches:",
    "action_on_match": "Action on match:",
    "click_center": "Click center",
    "click_random_offset": "Click with offset",
    "drag_to": "Drag to point",
    "hover": "Hover",
    "click_all": "Click all matches",
    "save_screenshot": "Save screenshot on match",
    "loop_until_found": "Loop until found",
    "max_attempts": "Max attempts:",
    "delay_between_attempts": "Delay between attempts (ms):",

    # Advanced
    "advanced_settings": "Advanced settings",
    "image_preprocessing": "Image preprocessing",
    "grayscale": "Grayscale",
    "blur": "Blur",
    "threshold": "Threshold",
    "edge_detection": "Edge detection",
    "contrast_enhance": "Contrast enhance",

    # ROI
    "roi_selector": "Select ROI on screen",
    "select_roi": "Select ROI",
    "roi_selected": "ROI selected",
    "roi_clear": "Clear ROI",

    # Preview & testing
    "preview_match": "Preview match",
    "test_condition": "Test condition now",
    "condition_passed": "Condition passed!",
    "condition_failed": "Condition failed",

    # Variables
    "variable_condition": "Variable condition",
    "compare_var": "Compare variable",
    "set_variable": "Set variable",
    "increment_var": "Increment variable",
    "decrement_var": "Decrement variable",

    # Click settings
    "random_click_offset": "Random click offset (px):",
    "click_delay_variation": "Click delay variation (ms):",
    "humanize_mouse": "Humanize mouse movement",
    "bezier_curve": "Bezier curve movement",

    # Menu
    "about": "About",
    "check_updates": "Check for updates",
    "backup": "Backup",
    "restore": "Restore",
    "export_html": "Export to HTML",
    "export_pdf": "Export to PDF",
    "run_as_admin": "Run as administrator",
    "minimize_to_tray": "Minimize to tray",
    "show_notifications": "Show notifications",
    "sound_alerts": "Sound alerts",

    # Theme
    "theme": "Theme",
    "dark_theme": "Dark theme",
    "light_theme": "Light theme",

    # System
    "auto_start": "Auto start with Windows",
    "hotkey_config": "Hotkey configuration",
    "record_mouse": "Record mouse movements",
    "record_all": "Record all actions",
    "playback_speed": "Playback speed",
    "loop_video": "Loop video",
    "export_video": "Export to video",

    # Logging
    "screenshot_on_error": "Screenshot on error",
    "log_to_file": "Log to file",
    "max_log_size": "Max log size (MB):",

    # Proxy
    "proxy_settings": "Proxy settings",
    "proxy_host": "Proxy host:",
    "proxy_port": "Proxy port:",
    "use_proxy": "Use proxy",

    # Sound
    "sound_detection": "Sound detection",
    "sound_threshold": "Sound threshold:",
    "wait_for_sound": "Wait for sound",

    # Sound conditions
    "sound_conditions": "🎵 Sound Conditions",
    "sound_threshold": "Sound Threshold",
    "sound_duration": "Duration (s)",
    "sound_status": "Sound Status",
    "available": "Available",
    "not_installed": "PyAudio not installed",

    # Tabs
    "tab_main": "⚡ Main",
    "tab_expert": "🎯 Expert Mode",
    "tab_conditions": "🎨 Conditions",
    "tab_scheduler": "⏰ Scheduler",
    "tab_stats": "📊 Stats",
    "tab_settings": "⚙ Settings",
}

# ============== СЛОВАРЬ ЯЗЫКОВ ==============
LANGUAGES = {
    "ru": RUSSIAN,
    "en": ENGLISH,
}


# ============== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==============

def get_text(key: str, lang: str = "ru") -> str:
    """Получить текст на нужном языке"""
    if lang not in LANGUAGES:
        lang = "ru"
    return LANGUAGES[lang].get(key, key)


def get_available_languages() -> list:
    """Получить список доступных языков"""
    return list(LANGUAGES.keys())


def get_language_name(lang: str) -> str:
    """Получить название языка на его родном языке"""
    names = {
        "ru": "Русский",
        "en": "English",
    }
    return names.get(lang, lang)


def switch_language(current_lang: str) -> str:
    """Переключить язык между русским и английским"""
    if current_lang == "ru":
        return "en"
    return "ru"


if __name__ == "__main__":
    # Тестирование языков
    print("=" * 50)
    print("Language Test")
    print("=" * 50)
    for lang in ["ru", "en"]:
        print(f"\n{lang.upper()}:")
        print(f"  {get_text('title', lang)}")
        print(f"  {get_text('start', lang)}")
        print(f"  {get_text('stop', lang)}")
        print(f"  {get_text('conditions', lang)}")
        print(f"  {get_text('expert_mode', lang)}")
    print("=" * 50)