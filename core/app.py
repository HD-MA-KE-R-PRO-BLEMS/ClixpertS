"""
Clixpert S Pro Ultimate - Main Application Class
Главный класс приложения ClickerApp
"""

import tkinter as tk
import threading
import time
import random
import pyautogui
import keyboard
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime

from config import (
    VERSION, APP_NAME, WINDOW_SIZE, DEFAULT_SETTINGS,
    get_theme, get_settings_file_path, get_screenshot_path
)
from languages import get_text, switch_language
from core.actions import ActionManager, ActionType
from core.conditions import ConditionManager
from core.executor import ScriptExecutor
from core.hotkeys import HotkeyManager
from core.profile_manager import ProfileManager
from modules.stats import PerformanceStats
from modules.telegram import TelegramNotifier
from modules.scheduler import TaskScheduler
from modules.image_searcher import AdvancedImageSearcher
from modules.mouse_controller import HumanMouseController
from ui.main_window import MainWindow


class ClickerApp:
    """
    Главный класс приложения.
    Управляет всеми компонентами и связывает их между собой.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.lang = "ru"
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.script_break_flag = False
        self.current_count = 100.0
        self.waiting_for_key = False
        self.temp_key_hook = None

        # Настройки приложения
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()

        # Устанавливаем язык из настроек
        self.lang = self.settings.get("language", "ru")

        # Инициализация менеджеров
        self.action_manager = ActionManager(self)
        self.condition_manager = ConditionManager(self)
        self.hotkey_manager = HotkeyManager(self)
        self.profile_manager = ProfileManager(self)

        # Устанавливаем директорию для профилей
        from config import PROFILES_DIR
        self.profile_manager.set_profiles_dir(PROFILES_DIR)

        # Инициализация модулей
        self.stats = PerformanceStats()
        self.telegram = TelegramNotifier()
        self.scheduler = TaskScheduler(self)
        self.image_searcher = AdvancedImageSearcher()
        self.mouse_controller = HumanMouseController()
        self.script_executor: Optional[ScriptExecutor] = None

        # Диалог условий (будет создан в UI)
        self.pixel_conditions_dialog = None

        # Настройки из сохранённых данных
        self._apply_settings()

        # UI
        self.main_window: Optional[MainWindow] = None

        # Настройка главного окна
        self._setup_root()

        # Создание интерфейса
        self._create_ui()

        # Регистрация горячих клавиш
        self.hotkey_manager.register_all()

        # Запуск планировщика
        self.scheduler.start()

        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_root(self):
        """Настройка главного окна Tkinter"""
        self.root.title(get_text("title", self.lang))
        self.root.geometry(f"{WINDOW_SIZE['width']}x{WINDOW_SIZE['height']}")
        self.root.minsize(WINDOW_SIZE['min_width'], WINDOW_SIZE['min_height'])
        self.root.configure(bg=get_theme(self.settings.get("theme", "dark"))["bg"])
        self.root.attributes('-alpha', 0.96)

        # Установка always on top
        if self.settings.get("always_on_top", False):
            self.root.attributes('-topmost', True)

        # Применение стилей
        try:
            import pywinstyles
            pywinstyles.apply_style(self.root, "dark")
        except ImportError:
            pass

    def _create_ui(self):
        """Создание пользовательского интерфейса"""
        self.main_window = MainWindow(self)
        # Сохраняем ссылку на диалог условий из UI
        if hasattr(self.main_window, 'pixel_conditions_dialog'):
            self.pixel_conditions_dialog = self.main_window.pixel_conditions_dialog

    def _apply_settings(self):
        """Применение загруженных настроек"""
        # Основные настройки
        self.current_count = self.settings.get("initial_count", 100.0)

        # Настройки человеческого поведения
        self.humanize_mouse = self.settings.get("humanize_mouse", True)
        self.humanize_keys = self.settings.get("humanize_keys", True)
        self.humanize_scroll = self.settings.get("humanize_scroll", True)
        self.humanize_type = self.settings.get("humanize_type", True)
        self.random_click_offset = self.settings.get("random_click_offset", 5)
        self.click_hold_min = self.settings.get("click_hold_min", 50)
        self.click_hold_max = self.settings.get("click_hold_max", 200)

        # Настройки поиска изображений
        self.image_tolerance = self.settings.get("image_tolerance", 80)
        self.multi_scale_search = self.settings.get("multi_scale_search", False)
        self.rotation_tolerance = self.settings.get("rotation_tolerance", 0)
        self.search_method = self.settings.get("search_method", "template_matching")

        # Telegram
        if self.settings.get("telegram_token") and self.settings.get("telegram_chat_id"):
            self.telegram.set_config(
                self.settings["telegram_token"],
                self.settings["telegram_chat_id"]
            )

    def load_settings(self):
        """Загрузка настроек из файла"""
        import json
        settings_file = get_settings_file_path()
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.settings.update(saved)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        """Сохранение настроек в файл"""
        import json
        settings_file = get_settings_file_path()
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_text(self, key: str) -> str:
        """Получить текст на текущем языке"""
        return get_text(key, self.lang)

    def switch_language(self):
        """Переключение языка интерфейса"""
        self.lang = switch_language(self.lang)
        self.settings["language"] = self.lang
        self.save_settings()
        if self.main_window:
            self.main_window.refresh_texts()

    def update_status(self, message: str):
        """Обновление статуса в интерфейсе"""
        if self.main_window:
            self.main_window.update_status(message)
        print(f"[STATUS] {message}")

    def update_progress(self, current: float, total: float, percent: float, eta_text: str):
        """Обновление прогресса"""
        if self.main_window:
            self.main_window.update_progress(current, total, percent, eta_text)

    def update_script_logs(self, log_entry: str):
        """Обновление логов в Expert Mode"""
        if self.main_window:
            self.main_window.update_script_logs(log_entry)

    def update_variables(self, variables: dict):
        """Обновление переменных в Expert Mode"""
        if self.main_window:
            self.main_window.update_variables(variables)

    def update_always_on_top(self):
        """Обновление параметра always on top"""
        self.root.attributes('-topmost', self.settings.get("always_on_top", False))

    def hide_window(self):
        """Скрыть окно в трей"""
        if self.main_window:
            self.main_window.hide_window()

    # ========== ЗАПИСЬ ДЕЙСТВИЙ ==========

    def record_click_action(self):
        """Запись клика как действия"""
        if self.running:
            self.update_status(self.get_text("cannot_edit_running"))
            return
        x, y = pyautogui.position()
        action = self.action_manager.create_click_action(
            x, y,
            delay_ms=self.settings.get("global_delay_ms", 1000),
            random_offset=self.settings.get("random_click_offset", 0),
            humanize=self.settings.get("humanize_mouse", False)
        )
        self.action_manager.add_action(action)
        self.update_status(f"✅ Click added: ({x}, {y})")
        self.stats.record_click(x, y)

    def start_key_recording(self):
        """Запись клавиши"""
        if self.running:
            self.update_status(self.get_text("cannot_edit_running"))
            return
        self.update_status("⌨ Press any key...")
        self.waiting_for_key = True

        def handler(e):
            if self.waiting_for_key and e.name not in ('shift', 'ctrl', 'alt', 'windows',
                                                        'right shift', 'right ctrl', 'right alt'):
                self.waiting_for_key = False
                if self.temp_key_hook:
                    keyboard.unhook(self.temp_key_hook)
                self.root.after(0, lambda: self._add_key_action(e.name))

        self.temp_key_hook = keyboard.on_press(handler)
        self.root.after(10000, self._cancel_key_recording)

    def _cancel_key_recording(self):
        """Отмена записи клавиши"""
        if self.waiting_for_key:
            self.waiting_for_key = False
            if self.temp_key_hook:
                keyboard.unhook(self.temp_key_hook)
            self.update_status("⌨ Key recording cancelled")

    def _add_key_action(self, key_name: str):
        """Добавление клавиши в список действий"""
        action = self.action_manager.create_key_action(
            key_name,
            delay_ms=self.settings.get("global_delay_ms", 1000)
        )
        self.action_manager.add_action(action)
        self.update_status(f"✅ Key added: {key_name}")

    # ========== ПОИСК ИЗОБРАЖЕНИЙ ==========

    def find_image_advanced(
        self,
        image_path: str,
        area: Optional[tuple] = None,
        confidence: Optional[float] = None,
        multi_scale: Optional[bool] = None,
        rotation: Optional[int] = None,
        method: Optional[str] = None
    ) -> tuple:
        """
        Продвинутый поиск изображения.

        Returns:
            (found: bool, position: Optional[Tuple[int, int]])
        """
        if confidence is None:
            confidence = self.settings.get("image_tolerance", 80) / 100.0
        if multi_scale is None:
            multi_scale = self.settings.get("multi_scale_search", False)
        if rotation is None:
            rotation = self.settings.get("rotation_tolerance", 0)
        if method is None:
            method = self.settings.get("search_method", "template_matching")

        # Загрузка шаблона
        if image_path in self.image_searcher._template_cache:
            template = self.image_searcher._template_cache[image_path]
        else:
            template = cv2.imread(image_path)
            if template is None:
                return False, None
            self.image_searcher._template_cache[image_path] = template

        # Захват экрана
        if area:
            x1, y1, x2, y2 = area
            screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
        else:
            screenshot = pyautogui.screenshot()

        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Предобработка
        preprocess = {
            'grayscale': self.settings.get("preprocess_grayscale", False),
            'blur': self.settings.get("preprocess_blur", False),
            'threshold': self.settings.get("preprocess_threshold", False),
            'edge_detection': self.settings.get("preprocess_edge_detection", False),
            'contrast_enhance': self.settings.get("preprocess_contrast", False),
        }
        screenshot = self.image_searcher.preprocess_image(screenshot, preprocess)
        template_proc = self.image_searcher.preprocess_image(template, preprocess)

        # Поиск
        if method == 'feature_matching':
            match, conf = self.image_searcher.find_feature_matching(screenshot, template_proc, confidence)
            if match:
                x, y, w, h = match
                return True, (x + w // 2, y + h // 2)
            return False, None

        if multi_scale:
            match, conf, scale = self.image_searcher.find_template_multi_scale(
                screenshot, template_proc, confidence=confidence
            )
            if match:
                x, y, w, h = match
                return True, (x + w // 2, y + h // 2)
        elif rotation > 0:
            match, conf, angle = self.image_searcher.find_with_rotation(
                screenshot, template_proc, angle_range=(-rotation, rotation), confidence=confidence
            )
            if match:
                x, y, w, h = match
                return True, (x + w // 2, y + h // 2)
        else:
            result = cv2.matchTemplate(screenshot, template_proc, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val >= confidence:
                return True, (max_loc[0] + template_proc.shape[1] // 2, max_loc[1] + template_proc.shape[0] // 2)

        return False, None

    def script_check_image_exists(self, image_path: str) -> bool:
        """Проверка существования изображения на экране"""
        try:
            found, _ = self.find_image_advanced(image_path)
            return found
        except Exception:
            return False

    def find_text_on_screen(self, target_text: str, tolerance: int = 80) -> Optional[tuple]:
        """Поиск текста на экране с помощью OCR"""
        try:
            import pytesseract
            screenshot = pyautogui.screenshot()
            text = pytesseract.image_to_string(screenshot)
            if target_text.lower() in text.lower():
                return (100, 100)  # Примерная позиция (упрощённо)
        except ImportError:
            pass
        except Exception:
            pass
        return None

    def get_pixel_condition(self, cond_id: str) -> Optional[dict]:
        """Получить пиксельное условие по ID"""
        cond = self.condition_manager.get_pixel_condition(cond_id)
        if cond:
            return {
                'id': cond.id,
                'x': cond.x,
                'y': cond.y,
                'color': cond.color,
                'tolerance': cond.tolerance
            }
        return None

    # ========== УПРАВЛЕНИЕ ЦИКЛОМ ==========

    def start_cycle(self):
        """Запуск основного цикла действий"""
        if self.running:
            return
        if self.action_manager.is_empty():
            self.update_status(self.get_text("no_actions"))
            return

        if self.settings.get("mode", 0) == 1:
            try:
                if self.settings.get("initial_count", 100) <= 0:
                    raise ValueError
                self.current_count = self.settings.get("initial_count", 100)
            except:
                self.update_status("Invalid initial count")
                return

        self.running = True
        self.update_status(self.get_text("cycle_running"))
        if self.main_window:
            self.main_window.update_start_stop_button(True)

        self.thread = threading.Thread(target=self._run_cycle, daemon=True)
        self.thread.start()

    def stop_cycle(self):
        """Остановка основного цикла"""
        self.running = False
        self.update_status(self.get_text("cycle_stopped"))
        if self.main_window:
            self.main_window.update_start_stop_button(False)

    def _run_cycle(self):
        """Основной цикл выполнения действий"""
        mode = self.settings.get("mode", 0)
        actions = list(self.action_manager.actions)

        while self.running:
            skip_rest = False
            for action in actions:
                if not self.running or skip_rest:
                    break

                # Задержка перед действием
                delay = action.delay_ms
                if action.variation_ms > 0:
                    delay += random.randint(-action.variation_ms, action.variation_ms)
                    delay = max(0, delay)
                if delay > 0:
                    time.sleep(delay / 1000.0)
                if not self.running:
                    break

                # Проверка условия
                cond_met = True
                if action.condition and self.settings.get("use_conditions", True):
                    if action.loop_until_found:
                        attempts = 0
                        while self.running and attempts < action.max_attempts:
                            cond_met = self._check_action_condition(action)
                            if cond_met:
                                break
                            time.sleep(self.settings.get("attempt_delay", 500) / 1000.0)
                            attempts += 1
                    else:
                        cond_met = self._check_action_condition(action)

                    if action.condition and not cond_met:
                        continue

                # Выполнение действия
                self._execute_action(action)

                # Обновление прогресса для лимитированного режима
                if mode == 1:
                    if action.progress_contrib is not None:
                        self.current_count -= action.progress_contrib
                    elif action.type != ActionType.DELAY:
                        deduct = self.settings.get("deduction", 10.0)
                        mult = self.settings.get("deduction_mult", 0.33)
                        if mult < 0:
                            mult = 0
                        elif mult > 1:
                            mult = 1
                        self.current_count -= deduct * (1.0 - mult)

                    init_count = self.settings.get("initial_count", 100)
                    percent = (self.current_count / init_count) * 100 if init_count > 0 else 0
                    eta_text = self._calculate_eta()
                    self.root.after(0, lambda: self.update_progress(
                        self.current_count,
                        init_count,
                        max(0, percent),
                        eta_text
                    ))

                    if self.current_count <= 0:
                        self.running = False
                        self.root.after(0, self._show_completion_message)
                        self.send_telegram_notification("✅ Script completed successfully!")
                        break

        self.running = False
        self.root.after(0, lambda: self.update_status(self.get_text("cycle_finished")))
        if self.main_window:
            self.root.after(0, lambda: self.main_window.update_start_stop_button(False))

    def _check_action_condition(self, action) -> bool:
        """Проверка условия действия"""
        if not action.condition:
            return True

        cond = action.condition
        if cond.get("type") == "pixel":
            cond_id = cond.get("id")
            if cond_id:
                pixel_cond = self.condition_manager.get_pixel_condition(cond_id)
                if pixel_cond:
                    try:
                        pixel = pyautogui.pixel(pixel_cond.x, pixel_cond.y)
                        tolerance = pixel_cond.tolerance
                        return all(abs(pixel[i] - pixel_cond.color[i]) <= tolerance for i in range(3))
                    except:
                        return False
        return True

    def _execute_action(self, action):
        """Выполнение действия"""
        try:
            if action.type == ActionType.CLICK:
                x, y = action.x, action.y
                if action.match_pos:
                    x, y = action.match_pos
                    action.match_pos = None

                if action.random_offset > 0:
                    x += random.randint(-action.random_offset, action.random_offset)
                    y += random.randint(-action.random_offset, action.random_offset)

                if action.humanize and self.settings.get("humanize_mouse", False):
                    start = pyautogui.position()
                    self.mouse_controller.human_move(start, (x, y), 'normal')
                else:
                    pyautogui.moveTo(x, y)

                if action.hold_ms > 0:
                    pyautogui.mouseDown()
                    time.sleep(action.hold_ms / 1000.0)
                    pyautogui.mouseUp()
                else:
                    pyautogui.click()
                self.stats.record_click(x, y)

            elif action.type == ActionType.KEY:
                if action.key_hold:
                    keyboard.press(action.key)
                    time.sleep(action.key_hold_ms / 1000.0)
                    keyboard.release(action.key)
                else:
                    keyboard.press_and_release(action.key)

            elif action.type == ActionType.DELAY:
                pass  # Задержка уже была

        except Exception as e:
            self.update_status(f"Action failed: {e}")
            self.send_telegram_notification(f"❌ Action failed: {e}", screenshot=True)

    def _calculate_eta(self) -> str:
        """Рассчитать оставшееся время"""
        mode = self.settings.get("mode", 0)
        if mode == 0 or not self.running:
            return "—"

        try:
            total_delay = sum(a.delay_ms for a in self.action_manager.actions)
            cycle_time = total_delay / 1000.0
            contrib = self.action_manager.get_total_contrib()
            if contrib <= 0:
                return "∞"
            cycles = self.current_count / contrib
            secs = cycles * cycle_time
            if secs < 60:
                return f"{secs:.0f} sec"
            elif secs < 3600:
                return f"{secs / 60:.0f} min"
            else:
                return f"{secs / 3600:.1f} hours"
        except:
            return "—"

    def _show_completion_message(self):
        """Показать сообщение о завершении"""
        self.update_status(self.get_text("completion_title"))
        import tkinter.messagebox as messagebox
        messagebox.showinfo(self.get_text("completion_title"), self.get_text("completion_message"))

    # ========== УПРАВЛЕНИЕ СКРИПТАМИ ==========

    def run_script(self, script: str = None):
        """Запуск скрипта Expert Mode"""
        if self.script_executor and self.script_executor.is_running:
            return

        if script is None and self.main_window:
            script = self.main_window.get_expert_script()

        if not script or not script.strip():
            self.update_status("No script to execute")
            return

        self.script_break_flag = False
        self.script_executor = ScriptExecutor(self)
        thread = threading.Thread(
            target=self.script_executor.execute_script,
            args=(script.split('\n'),),
            daemon=True
        )
        thread.start()
        self.update_status("Running script...")

    def stop_script(self):
        """Остановка выполнения скрипта"""
        self.script_break_flag = True
        if self.script_executor:
            self.script_executor.is_running = False
        self.update_status("Script stopped")

    def send_telegram_notification(self, message: str, screenshot: bool = False):
        """Отправка уведомления в Telegram"""
        if self.settings.get("telegram_notify", False):
            self.telegram.send_notification(APP_NAME, message, screenshot)

    def on_closing(self):
        """Обработка закрытия приложения"""
        self.running = False
        self.script_break_flag = True
        self.scheduler.stop()
        self.hotkey_manager.unregister_all()
        self.save_settings()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

        self.root.quit()
        self.root.destroy()

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()