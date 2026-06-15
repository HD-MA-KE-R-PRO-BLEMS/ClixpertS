"""
Clixpert S Pro Ultimate - UI Package
Пользовательский интерфейс: главное окно, вкладки, диалоги
"""

from ui.main_window import MainWindow
from ui.tabs.main_tab import MainTab
from ui.tabs.expert_tab import ExpertTab
from ui.tabs.conditions_tab import ConditionsTab
from ui.tabs.scheduler_tab import SchedulerTab
from ui.tabs.stats_tab import StatsTab
from ui.tabs.settings_tab import SettingsTab
from ui.dialogs.action_editor import ActionEditorDialog
from ui.dialogs.pixel_condition import PixelConditionDialog
from ui.dialogs.image_condition import ImageConditionDialog
from ui.dialogs.roi_selector import ROISelector
from ui.dialogs.progress_window import ProgressWindow

__all__ = [
    'MainWindow',
    'MainTab',
    'ExpertTab',
    'ConditionsTab',
    'SchedulerTab',
    'StatsTab',
    'SettingsTab',
    'ActionEditorDialog',
    'PixelConditionDialog',
    'ImageConditionDialog',
    'ROISelector',
    'ProgressWindow',
]