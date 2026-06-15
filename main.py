#!/usr/bin/env python3
"""
Clixpert S Pro Ultimate - Main Entry Point
Точка входа в приложение
"""

import sys
import threading
import tkinter as tk

# Добавляем текущую директорию в PATH для импортов
sys.path.insert(0, '.')

from config import APP_NAME, VERSION, check_dependencies, is_admin
from core.app import ClickerApp


def check_environment():
    """Проверка окружения перед запуском"""
    print("=" * 50)
    print(f"{APP_NAME} v{VERSION}")
    print("=" * 50)

    # Проверка зависимостей
    print("\n📦 Checking dependencies:")
    deps = check_dependencies()
    all_installed = True
    for dep, installed in deps.items():
        status = "✅" if installed else "❌"
        print(f"   {status} {dep}")
        if not installed:
            all_installed = False

    if not all_installed:
        print("\n⚠️  Some dependencies are missing!")
        print("   Run: pip install -r requirements.txt")

    # Проверка прав администратора
    if is_admin():
        print("\n👑 Running as Administrator")
    else:
        print("\n👤 Running as User (some features may be limited)")

    print("\n🚀 Starting application...")
    print("=" * 50)

    return all_installed


def create_tray_icon(app):
    """Создание иконки в системном трее"""
    try:
        from PIL import Image, ImageDraw
        import pystray

        # Создаём иконку
        image = Image.new('RGB', (64, 64), color='#1a1a2e')
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill='#5a9cff')
        draw.text((22, 22), "CS", fill='white')

        def show_window(icon, item):
            app.root.after(0, app.root.deiconify)

        def toggle_cycle(icon, item):
            if app.running:
                app.stop_cycle()
            else:
                app.start_cycle()

        def quit_app(icon, item):
            icon.stop()
            app.on_closing()

        menu = pystray.Menu(
            pystray.MenuItem("Show", show_window, default=True),
            pystray.MenuItem("Start/Stop", toggle_cycle),
            pystray.MenuItem("Exit", quit_app)
        )

        icon = pystray.Icon("clixpert", image, APP_NAME, menu)

        def run_tray():
            icon.run()

        threading.Thread(target=run_tray, daemon=True).start()
        return icon
    except ImportError:
        print("Warning: pystray not installed. Tray icon disabled.")
        return None


def main():
    """Главная функция"""
    # Проверка окружения
    check_environment()

    # Создание корневого окна
    root = tk.Tk()

    # Создание приложения
    app = ClickerApp(root)

    # Создание иконки в трее (опционально)
    tray_icon = create_tray_icon(app)
    app.tray_icon = tray_icon

    # Запуск приложения
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if tray_icon:
            tray_icon.stop()
        print("\nApplication terminated")


if __name__ == "__main__":
    main()