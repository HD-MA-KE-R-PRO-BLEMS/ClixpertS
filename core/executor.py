"""
Clixpert S Pro Ultimate - Script Executor Module
Интерпретатор DSL для Expert Mode с поддержкой:
- Переменных
- Условий (if/elif/else)
- Циклов (for)
- Функций поиска изображений
- Звуковых условий
- Человеческого поведения
"""

import re
import time
import random
import math
import traceback
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class ScriptExecutor:
    """
    Выполнение скриптов на DSL.
    Поддерживает Python-подобный синтаксис с отступами.
    """

    def __init__(self, app):
        self.app = app
        self.variables: Dict[str, Any] = {}
        self.logs: List[str] = []
        self.is_running = False
        self.break_flag = False
        self.last_match_pos: Optional[Tuple[int, int]] = None

        # Состояние удержаний
        self.held_keys = set()
        self.held_mouse = False
        self.held_mouse_pos = (0, 0)
        self.held_mouse_button = "left"

        # Инициализация модулей
        self._init_modules()

    def _init_modules(self):
        """Инициализация дополнительных модулей"""
        try:
            from modules.mouse_controller import HumanMouseController
            self.mouse = HumanMouseController
        except ImportError:
            self.mouse = None

        try:
            from modules.image_searcher import AdvancedImageSearcher
            self.image_searcher = AdvancedImageSearcher()
        except ImportError:
            self.image_searcher = None

        try:
            from modules.sound_analyzer import SoundCondition
            self.sound = SoundCondition()
            if hasattr(self.sound, 'init'):
                self.sound.init()
        except ImportError:
            self.sound = None

    def log(self, message: str, level: str = "INFO"):
        """Добавление записи в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)

        # Ограничиваем размер лога
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]

        if self.app:
            self.app.update_script_logs(log_entry)

    def parse_expression(self, expr: str) -> Any:
        """
        Парсинг математического выражения с переменными.

        Args:
            expr: Выражение для вычисления

        Returns:
            Результат вычисления
        """
        expr = str(expr).strip()

        # Замена переменных
        for var_name, var_value in self.variables.items():
            expr = expr.replace(var_name, str(var_value))

        try:
            # Разрешённые функции
            allowed_names = {
                'abs': abs,
                'min': min,
                'max': max,
                'round': round,
                'int': int,
                'float': float,
                'str': str,
                'len': len,
                'list': list,
                'range': range,
                'sum': sum,
                'dict': dict,
                'random': random,
                'math': math,
                'randint': random.randint,
                'uniform': random.uniform,
                'choice': random.choice,
            }
            allowed_names.update(self.variables)

            # Безопасное вычисление
            result = eval(expr, {"__builtins__": {}}, allowed_names)
            return result
        except Exception as e:
            self.log(f"Expression error: {expr} - {e}", "ERROR")
            return expr

    def evaluate_condition(self, condition: str) -> bool:
        """
        Вычисление условия.

        Args:
            condition: Условие для проверки

        Returns:
            True если условие выполнено
        """
        condition = condition.strip()

        # ========== ЗВУКОВЫЕ УСЛОВИЯ ==========
        if condition.startswith("sound_detected("):
            match = re.match(r'sound_detected\((\d+)(?:,\s*([\d.]+))?\)', condition)
            if match and self.sound:
                threshold = int(match.group(1))
                duration = float(match.group(2)) if match.group(2) else 0.5
                result = self.sound.check_condition(threshold, duration)
                self.log(f"sound_detected({threshold}, {duration}) = {result}")
                return result

        if condition.startswith("wait_for_sound("):
            match = re.match(r'wait_for_sound\((\d+)(?:,\s*(\d+))?\)', condition)
            if match and self.sound:
                threshold = int(match.group(1))
                timeout = int(match.group(2)) if match.group(2) else 30
                result = self.sound.wait_for_sound(threshold, timeout)
                self.log(f"wait_for_sound({threshold}, {timeout}) = {result}")
                return result

        if condition.startswith("sound_level()"):
            if self.sound:
                level = self.sound.get_sound_level()
                self.log(f"sound_level() = {level}")
                return level

        # ========== ИЗОБРАЖЕНИЯ ==========
        if condition.startswith("find_image_advanced("):
            match = re.match(r'find_image_advanced\(["\'](.+?)["\'](?:,\s*(?:confidence=)?([\d.]+))?\)', condition)
            if match and self.app:
                img_path = match.group(1)
                confidence = float(match.group(2)) if match.group(2) else self.app.settings.get("image_tolerance",
                                                                                                80) / 100.0
                try:
                    found, pos = self.app.find_image_advanced(img_path, confidence=confidence)
                    if found and pos:
                        self.last_match_pos = pos
                    self.log(f"find_image_advanced({img_path}) = {found} at {pos}")
                    return found
                except Exception as e:
                    self.log(f"find_image_advanced error: {e}", "ERROR")
                    return False

        if condition.startswith("exists_image("):
            match = re.match(r'exists_image\(["\'](.+?)["\']\)', condition)
            if match and self.app:
                img_path = match.group(1)
                try:
                    result = self.app.script_check_image_exists(img_path)
                    self.log(f"exists_image({img_path}) = {result}")
                    return result
                except Exception as e:
                    self.log(f"exists_image error: {e}", "ERROR")
                    return False

        # ========== ЦВЕТ ==========
        if condition.startswith("color_match("):
            match = re.match(r'color_match\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+))?\)', condition)
            if match:
                import pyautogui
                x, y, r, g, b = map(int, match.group(1, 2, 3, 4, 5))
                tolerance = int(match.group(6)) if match.group(6) else (
                    self.app.settings.get("color_tolerance", 10) if self.app else 10)
                try:
                    pixel = pyautogui.pixel(x, y)
                    result = all(abs(pixel[i] - [r, g, b][i]) <= tolerance for i in range(3))
                    self.log(f"color_match({x},{y}) = {result}")
                    return result
                except:
                    return False

        # ========== ПИКСЕЛЬНЫЕ УСЛОВИЯ ==========
        if condition.startswith("pixel_match("):
            match = re.match(r'pixel_match\((\d+),\s*(\d+),\s*["\'](.+?)["\']\)', condition)
            if match and self.app:
                import pyautogui
                x, y, ref_id = int(match.group(1)), int(match.group(2)), match.group(3)
                cond = self.app.get_pixel_condition(ref_id)
                if cond:
                    try:
                        pixel = pyautogui.pixel(x, y)
                        tolerance = self.app.settings.get("color_tolerance", 10)
                        result = all(abs(pixel[i] - cond['color'][i]) <= tolerance for i in range(3))
                        self.log(f"pixel_match({x},{y},{ref_id}) = {result}")
                        return result
                    except:
                        return False

        # ========== OCR ТЕКСТ ==========
        if condition.startswith("find_text("):
            match = re.match(r'find_text\(["\'](.+?)["\'](?:,\s*(\d+))?\)', condition)
            if match and self.app:
                target_text = match.group(1)
                tolerance = int(match.group(2)) if match.group(2) else 80
                try:
                    result = self.app.find_text_on_screen(target_text, tolerance)
                    self.log(f"find_text('{target_text}') = {result is not None}")
                    return result is not None
                except:
                    return False

        # ========== ЛОГИЧЕСКИЕ ВЫРАЖЕНИЯ ==========
        try:
            # Замена переменных
            cond_expr = condition
            for var_name, var_value in self.variables.items():
                cond_expr = cond_expr.replace(var_name, str(var_value))

            result = eval(cond_expr, {"__builtins__": {}}, self.variables)
            return bool(result)
        except Exception:
            return False

    def parse_command(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Парсинг одной команды.

        Args:
            line: Строка команды

        Returns:
            Словарь с командой или None
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        # ========== КОМАНДЫ ДВИЖЕНИЯ ==========
        if line == 'click_at_match_center()':
            return {'type': 'click_at_match_center'}

        if line.startswith('click_random(') and line.endswith(')'):
            params = line[12:-1].split(',')
            x = int(params[0].strip())
            y = int(params[1].strip())
            offset = int(params[2].strip()) if len(params) > 2 else 5
            return {'type': 'click_random', 'x': x, 'y': y, 'offset': offset}

        if line.startswith('click_human(') and line.endswith(')'):
            params = line[11:-1].split(',')
            x = int(params[0].strip())
            y = int(params[1].strip())
            hold_min = int(params[2].strip()) if len(params) > 2 else 50
            hold_max = int(params[3].strip()) if len(params) > 3 else 200
            return {'type': 'click_human', 'x': x, 'y': y, 'hold_min': hold_min, 'hold_max': hold_max}

        if line.startswith('move_human(') and line.endswith(')'):
            params = line[10:-1].split(',')
            x = int(params[0].strip())
            y = int(params[1].strip())
            speed = params[2].strip().strip('"\'') if len(params) > 2 else 'normal'
            return {'type': 'move_human', 'x': x, 'y': y, 'speed': speed}

        if line.startswith('drag_human(') and line.endswith(')'):
            params = line[10:-1].split(',')
            x1 = int(params[0].strip())
            y1 = int(params[1].strip())
            x2 = int(params[2].strip())
            y2 = int(params[3].strip())
            return {'type': 'drag_human', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}

        if line.startswith('type_human(') and line.endswith(')'):
            content = line[10:-1].strip().strip('"\'')
            return {'type': 'type_human', 'text': content}

        if line.startswith('key_human(') and line.endswith(')'):
            params = line[9:-1].split(',')
            key_name = params[0].strip().strip('"\'')
            hold_min = int(params[1].strip()) if len(params) > 1 else 50
            hold_max = int(params[2].strip()) if len(params) > 2 else 200
            return {'type': 'key_human', 'key': key_name, 'hold_min': hold_min, 'hold_max': hold_max}

        if line.startswith('scroll_human(') and line.endswith(')'):
            amount = int(line[12:-1].strip())
            return {'type': 'scroll_human', 'amount': amount}

        # ========== ПРИСВОЕНИЕ ==========
        if '=' in line and not line.startswith(('if', 'elif', 'else', 'for')):
            parts = line.split('=', 1)
            var_name = parts[0].strip()
            value_expr = parts[1].strip()
            return {'type': 'assign', 'var': var_name, 'value': value_expr}

        # ========== ВЫВОД ==========
        if line.startswith('print(') and line.endswith(')'):
            content = line[6:-1]
            return {'type': 'print', 'content': content}

        # ========== КЛИК ==========
        if line.startswith('click(') and line.endswith(')'):
            params = line[6:-1].split(',')
            x = int(params[0].strip())
            y = int(params[1].strip())
            hold = int(params[2].strip()) if len(params) > 2 else 0
            return {'type': 'click', 'x': x, 'y': y, 'hold_ms': hold}

        # ========== КЛАВИШИ ==========
        if line.startswith('key(') and line.endswith(')'):
            key_name = line[4:-1].strip().strip('"\'')
            return {'type': 'key', 'key': key_name}

        if line.startswith('key_down(') and line.endswith(')'):
            key_name = line[9:-1].strip().strip('"\'')
            return {'type': 'key_down', 'key': key_name}

        if line.startswith('key_up(') and line.endswith(')'):
            key_name = line[7:-1].strip().strip('"\'')
            return {'type': 'key_up', 'key': key_name}

        # ========== МЫШЬ ==========
        if line.startswith('mouse_down(') and line.endswith(')'):
            params = line[11:-1].split(',')
            x = int(params[0].strip())
            y = int(params[1].strip())
            button = params[2].strip().strip('"\'') if len(params) > 2 else 'left'
            return {'type': 'mouse_down', 'x': x, 'y': y, 'button': button}

        if line.startswith('mouse_up(') and line.endswith(')'):
            params = line[9:-1].split(',')
            x = int(params[0].strip())
            y = int(params[1].strip())
            button = params[2].strip().strip('"\'') if len(params) > 2 else 'left'
            return {'type': 'mouse_up', 'x': x, 'y': y, 'button': button}

        if line.startswith('move(') and line.endswith(')'):
            params = line[5:-1].split(',')
            x = int(params[0].strip())
            y = int(params[1].strip())
            return {'type': 'move', 'x': x, 'y': y}

        # ========== ЗАДЕРЖКИ ==========
        if line.startswith(('wait(', 'sleep(')) and line.endswith(')'):
            ms = int(line[line.index('(') + 1:-1].strip())
            return {'type': 'wait', 'ms': ms}

        # ========== СКРОЛЛ ==========
        if line.startswith('scroll(') and line.endswith(')'):
            amount = int(line[7:-1].strip())
            return {'type': 'scroll', 'amount': amount}

        # ========== ПЕЧАТЬ ==========
        if line.startswith('type(') and line.endswith(')'):
            text = line[5:-1].strip().strip('"\'')
            return {'type': 'type', 'text': text}

        # ========== ЦИКЛЫ ==========
        if line.startswith('for ') and ' in ' in line and line.endswith(':'):
            for_part = line[4:-1].strip()
            var_name, iterable_part = for_part.split(' in ', 1)
            var_name = var_name.strip()

            if iterable_part.startswith('range('):
                range_params = iterable_part[6:-1].split(',')
                if len(range_params) == 1:
                    iterable = list(range(int(range_params[0].strip())))
                elif len(range_params) == 2:
                    iterable = list(range(int(range_params[0].strip()), int(range_params[1].strip())))
                else:
                    iterable = list(
                        range(int(range_params[0].strip()), int(range_params[1].strip()), int(range_params[2].strip())))
            elif iterable_part.startswith('[') and iterable_part.endswith(']'):
                items = iterable_part[1:-1].split(',')
                iterable = [self.parse_expression(item.strip()) for item in items]
            else:
                iterable = self.parse_expression(iterable_part)
                if not isinstance(iterable, (list, range)):
                    iterable = [iterable]

            return {'type': 'for', 'var': var_name, 'iterable': iterable}

        # ========== УСЛОВИЯ ==========
        if line.startswith('if ') and line.endswith(':'):
            condition = line[3:-1].strip()
            return {'type': 'if', 'condition': condition}

        if line.startswith('elif ') and line.endswith(':'):
            condition = line[5:-1].strip()
            return {'type': 'elif', 'condition': condition}

        if line == 'else:':
            return {'type': 'else'}

        return None

    def parse_indented_block(self, lines: List[str], start_index: int = 0, indent_level: int = 0) -> Tuple[
        List[Dict], int]:
        """
        Парсинг блока с отступами.

        Args:
            lines: Список строк
            start_index: Начальный индекс
            indent_level: Уровень отступа

        Returns:
            (список команд, новый индекс)
        """
        block = []
        i = start_index
        lines_count = len(lines)

        while i < lines_count:
            line = lines[i].rstrip()
            if not line:
                i += 1
                continue

            # Проверка отступа
            spaces = len(line) - len(line.lstrip())
            if spaces < indent_level:
                break

            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                i += 1
                continue

            cmd = self.parse_command(stripped)
            if cmd:
                if cmd['type'] in ['for', 'if', 'elif', 'else']:
                    nested_block, i = self.parse_indented_block(lines, i + 1, spaces + 4)
                    cmd['block'] = nested_block
                block.append(cmd)
            i += 1

        return block, i

    def _execute_block(self, block: List[Dict]):
        """
        Выполнение блока команд.

        Args:
            block: Список команд для выполнения
        """
        if not self.is_running or self.break_flag:
            return

        for cmd in block:
            if not self.is_running or self.break_flag:
                break

            # ========== ПРИСВОЕНИЕ ==========
            if cmd['type'] == 'assign':
                value = self.parse_expression(cmd['value'])
                self.variables[cmd['var']] = value
                self.log(f"Variable {cmd['var']} = {value}")

            # ========== ВЫВОД ==========
            elif cmd['type'] == 'print':
                content = self.parse_expression(cmd['content'])
                self.log(f"PRINT: {content}")
                if self.app:
                    self.app.update_status(str(content))

            # ========== КЛИКИ ==========
            elif cmd['type'] == 'click_human':
                self.log(f"Human click at ({cmd['x']}, {cmd['y']})")
                if self.app and self.app.stats:
                    self.app.stats.record_click(cmd['x'], cmd['y'])
                if self.mouse:
                    hold_time = self.mouse.human_click(
                        cmd['x'], cmd['y'],
                        hold_min=cmd.get('hold_min', 50),
                        hold_max=cmd.get('hold_max', 200)
                    )
                    if self.app and self.app.stats:
                        self.app.stats.record_action('click_human', True, hold_time * 1000)

            elif cmd['type'] == 'click_random':
                import pyautogui
                offset = cmd.get('offset', 5)
                x = cmd['x'] + random.randint(-offset, offset)
                y = cmd['y'] + random.randint(-offset, offset)
                if self.app and self.app.stats:
                    self.app.stats.record_click(x, y)
                pyautogui.moveTo(x, y)
                pyautogui.click()
                self.log(f"Random click at ({x}, {y})")

            elif cmd['type'] == 'click_at_match_center':
                import pyautogui
                if self.last_match_pos:
                    x, y = self.last_match_pos
                    pyautogui.moveTo(x, y)
                    pyautogui.click()
                    self.log(f"Click at match center ({x}, {y})")
                else:
                    self.log("No match position available", "WARNING")

            elif cmd['type'] == 'click':
                import pyautogui
                if self.app and self.app.stats:
                    self.app.stats.record_click(cmd['x'], cmd['y'])
                if self.app and self.app.settings.get("humanize_mouse", False) and self.mouse:
                    start = pyautogui.position()
                    self.mouse.human_move(start, (cmd['x'], cmd['y']), 'normal')
                else:
                    pyautogui.moveTo(cmd['x'], cmd['y'])
                if cmd['hold_ms'] > 0:
                    pyautogui.mouseDown()
                    time.sleep(cmd['hold_ms'] / 1000.0)
                    pyautogui.mouseUp()
                else:
                    pyautogui.click()
                if self.app and self.app.stats:
                    self.app.stats.record_action('click', True, cmd['hold_ms'])
                self.log(f"Click at ({cmd['x']}, {cmd['y']})")

            # ========== ДВИЖЕНИЕ ==========
            elif cmd['type'] == 'move_human':
                import pyautogui
                self.log(f"Human move to ({cmd['x']}, {cmd['y']})")
                if self.mouse:
                    start = pyautogui.position()
                    self.mouse.human_move(start, (cmd['x'], cmd['y']), speed=cmd.get('speed', 'normal'))

            elif cmd['type'] == 'drag_human':
                import pyautogui
                self.log(f"Human drag from ({cmd['x1']}, {cmd['y1']}) to ({cmd['x2']}, {cmd['y2']})")
                if self.mouse:
                    self.mouse.human_drag((cmd['x1'], cmd['y1']), (cmd['x2'], cmd['y2']))

            elif cmd['type'] == 'move':
                import pyautogui
                pyautogui.moveTo(cmd['x'], cmd['y'])
                self.log(f"Move to ({cmd['x']}, {cmd['y']})")

            # ========== КЛАВИШИ ==========
            elif cmd['type'] == 'key_human':
                import keyboard
                self.log(f"Human key: {cmd['key']}")
                if self.mouse:
                    hold_time = self.mouse.human_key_hold(cmd['key'], cmd.get('hold_min', 50), cmd.get('hold_max', 200))
                    self.log(f"Key held for {hold_time:.3f}s")

            elif cmd['type'] == 'key':
                import keyboard
                keyboard.press_and_release(cmd['key'])
                self.log(f"Key: {cmd['key']}")

            elif cmd['type'] == 'key_down':
                import keyboard
                keyboard.press(cmd['key'])
                self.held_keys.add(cmd['key'])
                self.log(f"Key DOWN: {cmd['key']}")

            elif cmd['type'] == 'key_up':
                import keyboard
                keyboard.release(cmd['key'])
                self.held_keys.discard(cmd['key'])
                self.log(f"Key UP: {cmd['key']}")

            # ========== МЫШЬ (удержание) ==========
            elif cmd['type'] == 'mouse_down':
                import pyautogui
                pyautogui.moveTo(cmd['x'], cmd['y'])
                button_map = {'left': 'left', 'right': 'right', 'middle': 'middle'}
                pyautogui.mouseDown(button=button_map.get(cmd['button'], 'left'))
                self.held_mouse = True
                self.held_mouse_pos = (cmd['x'], cmd['y'])
                self.held_mouse_button = cmd['button']
                self.log(f"Mouse DOWN at ({cmd['x']}, {cmd['y']})")

            elif cmd['type'] == 'mouse_up':
                import pyautogui
                pyautogui.moveTo(cmd['x'], cmd['y'])
                button_map = {'left': 'left', 'right': 'right', 'middle': 'middle'}
                pyautogui.mouseUp(button=button_map.get(cmd['button'], 'left'))
                self.held_mouse = False
                self.log(f"Mouse UP at ({cmd['x']}, {cmd['y']})")

            # ========== ЗАДЕРЖКИ ==========
            elif cmd['type'] == 'wait':
                wait_ms = cmd['ms']
                if self.app and self.app.settings.get("random_delay_ms", 0) > 0:
                    variation = random.randint(-self.app.settings["random_delay_ms"],
                                               self.app.settings["random_delay_ms"])
                    wait_ms = max(0, wait_ms + variation)
                time.sleep(wait_ms / 1000.0)
                self.log(f"Wait {wait_ms}ms")

            # ========== СКРОЛЛ ==========
            elif cmd['type'] == 'scroll_human':
                if self.mouse:
                    self.mouse.human_scroll(cmd['amount'])
                    self.log(f"Human scroll: {cmd['amount']}")

            elif cmd['type'] == 'scroll':
                import pyautogui
                pyautogui.scroll(cmd['amount'])
                self.log(f"Scroll {cmd['amount']}")

            # ========== ПЕЧАТЬ ==========
            elif cmd['type'] == 'type_human':
                if self.mouse:
                    self.mouse.human_type(cmd['text'])
                    self.log(f"Human typing: {cmd['text']}")

            elif cmd['type'] == 'type':
                import pyautogui
                pyautogui.write(cmd['text'])
                self.log(f"Type: {cmd['text']}")

            # ========== ЦИКЛЫ ==========
            elif cmd['type'] == 'for':
                for value in cmd['iterable']:
                    if not self.is_running or self.break_flag:
                        break
                    self.variables[cmd['var']] = value
                    self._execute_block(cmd['block'])

            # ========== УСЛОВИЯ ==========
            elif cmd['type'] == 'if':
                if self.evaluate_condition(cmd['condition']):
                    self._execute_block(cmd['block'])
                    # Пропускаем elif/else (упрощённо)

            elif cmd['type'] == 'else':
                self._execute_block(cmd['block'])

            # Задержка между командами
            if self.app and self.app.settings.get("global_delay_ms", 0) > 0:
                delay = self.app.settings["global_delay_ms"]
                if self.app.settings.get("random_delay_ms", 0) > 0:
                    delay += random.randint(-self.app.settings["random_delay_ms"], self.app.settings["random_delay_ms"])
                    delay = max(0, delay)
                time.sleep(delay / 1000.0)

    def execute_script(self, script_lines: List[str]):
        """
        Выполнение скрипта.

        Args:
            script_lines: Список строк скрипта
        """
        self.is_running = True
        self.break_flag = False
        self.variables = {}
        self.logs = []
        self.held_keys = set()
        self.held_mouse = False
        self.last_match_pos = None

        def cleanup():
            import keyboard
            for key in self.held_keys:
                keyboard.release(key)
            if self.held_mouse:
                import pyautogui
                pyautogui.mouseUp()

        try:
            # Парсинг блока
            parsed, _ = self.parse_indented_block(script_lines)
            self._execute_block(parsed)
        except Exception as e:
            self.log(f"Script execution error: {e}\n{traceback.format_exc()}", "ERROR")
            cleanup()
            if self.app:
                self.app.update_status(f"Script error: {str(e)}")
        finally:
            cleanup()
            self.is_running = False
            self.log("Script execution finished")

    def stop(self):
        """Остановка выполнения скрипта"""
        self.break_flag = True
        self.is_running = False


if __name__ == "__main__":
    # Тестирование модуля выполнения скриптов
    print("=" * 50)
    print("Testing ScriptExecutor Module")
    print("=" * 50)


    # Создаём мок-приложение
    class MockApp:
        def __init__(self):
            self.settings = {
                "global_delay_ms": 0,
                "random_delay_ms": 0,
                "color_tolerance": 10,
                "humanize_mouse": False,
                "image_tolerance": 80,
            }

        def update_script_logs(self, msg):
            print(f"   LOG: {msg}")

        def update_status(self, msg):
            print(f"   STATUS: {msg}")

        def find_image_advanced(self, *args, **kwargs):
            return False, None

        def script_check_image_exists(self, *args):
            return False

        def get_pixel_condition(self, *args):
            return None

        def find_text_on_screen(self, *args):
            return None


    app = MockApp()
    executor = ScriptExecutor(app)

    # Тестовый скрипт
    test_script = '''
# Тестовый скрипт
counter = 0

for i in range(3):
    counter = counter + 1
    print("Iteration: " + str(i))

print("Total: " + str(counter))
'''

    print("\n📜 Test script:")
    print(test_script)

    print("\n▶ Executing...")
    executor.execute_script(test_script.split('\n'))

    print("\n📊 Variables:")
    for k, v in executor.variables.items():
        print(f"   {k} = {v}")

    print(f"\n📝 Logs: {len(executor.logs)} entries")

    print("\n✅ Module ready!")