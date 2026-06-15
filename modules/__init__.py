"""
Clixpert S Pro Ultimate - Modules Package
Дополнительные модули: поиск изображений, движение мыши, звук, и т.д.
"""

from modules.image_searcher import AdvancedImageSearcher
from modules.mouse_controller import HumanMouseController
from modules.sound_analyzer import SoundAnalyzer, SoundCondition
from modules.recorder import ActionRecorder
from modules.scheduler import TaskScheduler
from modules.stats import PerformanceStats
from modules.telegram import TelegramNotifier
from modules.debug import DebugExecutor

__all__ = [
    'AdvancedImageSearcher',
    'HumanMouseController',
    'SoundAnalyzer',
    'SoundCondition',
    'ActionRecorder',
    'TaskScheduler',
    'PerformanceStats',
    'TelegramNotifier',
    'DebugExecutor',
]