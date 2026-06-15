"""
Clixpert S Pro Ultimate - Core Package
Ядро программы: управление действиями, условиями, выполнение скриптов
"""

from core.app import ClickerApp
from core.actions import ActionManager
from core.conditions import ConditionManager
from core.executor import ScriptExecutor
from core.hotkeys import HotkeyManager
from core.profile_manager import ProfileManager

__all__ = [
    'ClickerApp',
    'ActionManager',
    'ConditionManager',
    'ScriptExecutor',
    'HotkeyManager',
    'ProfileManager',
]