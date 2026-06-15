"""
Clixpert S Pro Ultimate - Telegram Notification Module
Отправка уведомлений в Telegram бот
"""

import os
import time
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class TelegramMessage:
    """Представление сообщения для Telegram"""
    text: str
    parse_mode: str = "HTML"
    disable_notification: bool = False
    reply_to_message_id: Optional[int] = None


class TelegramNotifier:
    """
    Отправка уведомлений в Telegram.
    Требует создания бота через @BotFather и получения Chat ID.
    """

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or ""
        self.chat_id = chat_id or ""
        self.enabled = bool(self.token and self.chat_id)
        self.last_error: Optional[str] = None
        self.last_send_time: Optional[datetime] = None
        self.retry_count = 0
        self.max_retries = 3
        self.timeout = 10

    def set_config(self, token: str, chat_id: str) -> None:
        """
        Установка конфигурации бота.

        Args:
            token: Токен бота от @BotFather
            chat_id: ID чата (можно получить через @userinfobot)
        """
        self.token = token.strip()
        self.chat_id = str(chat_id).strip()
        self.enabled = bool(self.token and self.chat_id)
        self.last_error = None

    def send_message(
            self,
            message: str,
            parse_mode: str = "HTML",
            disable_notification: bool = False
    ) -> bool:
        """
        Отправка текстового сообщения.

        Args:
            message: Текст сообщения
            parse_mode: Форматирование (HTML, Markdown, None)
            disable_notification: Отключить уведомление

        Returns:
            True если отправлено успешно
        """
        if not self.enabled:
            self.last_error = "Telegram not configured"
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification
        }

        try:
            response = requests.post(url, data=data, timeout=self.timeout)
            self.last_send_time = datetime.now()
            self.retry_count = 0

            if response.status_code == 200:
                self.last_error = None
                return True
            else:
                self.last_error = f"HTTP {response.status_code}: {response.text}"
                return False

        except requests.exceptions.Timeout:
            self.last_error = "Request timeout"
            return self._retry(message, parse_mode, disable_notification)
        except requests.exceptions.ConnectionError:
            self.last_error = "Connection error"
            return self._retry(message, parse_mode, disable_notification)
        except Exception as e:
            self.last_error = str(e)
            return False

    def _retry(self, message: str, parse_mode: str, disable_notification: bool) -> bool:
        """Повторная отправка при ошибке"""
        if self.retry_count >= self.max_retries:
            self.retry_count = 0
            return False

        self.retry_count += 1
        time.sleep(2)  # Ждём перед повтором
        return self.send_message(message, parse_mode, disable_notification)

    def send_photo(
            self,
            photo_path: str,
            caption: Optional[str] = None
    ) -> bool:
        """
        Отправка фото/скриншота.

        Args:
            photo_path: Путь к файлу изображения
            caption: Подпись к фото

        Returns:
            True если отправлено успешно
        """
        if not self.enabled:
            self.last_error = "Telegram not configured"
            return False

        if not os.path.exists(photo_path):
            self.last_error = f"File not found: {photo_path}"
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"

        try:
            with open(photo_path, 'rb') as f:
                files = {'photo': f}
                data = {'chat_id': self.chat_id}
                if caption:
                    data['caption'] = caption

                response = requests.post(url, files=files, data=data, timeout=self.timeout)

                if response.status_code == 200:
                    self.last_error = None
                    return True
                else:
                    self.last_error = f"HTTP {response.status_code}"
                    return False

        except Exception as e:
            self.last_error = str(e)
            return False

    def send_document(
            self,
            document_path: str,
            caption: Optional[str] = None
    ) -> bool:
        """
        Отправка документа/файла.

        Args:
            document_path: Путь к файлу
            caption: Подпись к файлу

        Returns:
            True если отправлено успешно
        """
        if not self.enabled:
            self.last_error = "Telegram not configured"
            return False

        if not os.path.exists(document_path):
            self.last_error = f"File not found: {document_path}"
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendDocument"

        try:
            with open(document_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': self.chat_id}
                if caption:
                    data['caption'] = caption

                response = requests.post(url, files=files, data=data, timeout=self.timeout)

                if response.status_code == 200:
                    self.last_error = None
                    return True
                else:
                    self.last_error = f"HTTP {response.status_code}"
                    return False

        except Exception as e:
            self.last_error = str(e)
            return False

    def send_notification(
            self,
            title: str,
            message: str,
            screenshot: bool = False,
            screenshot_path: Optional[str] = None
    ) -> bool:
        """
        Отправка уведомления с заголовком.

        Args:
            title: Заголовок уведомления
            message: Текст уведомления
            screenshot: Сделать и отправить скриншот
            screenshot_path: Путь к существующему скриншоту

        Returns:
            True если отправлено успешно
        """
        formatted = f"<b>{title}</b>\n\n{message}"

        if screenshot:
            if screenshot_path and os.path.exists(screenshot_path):
                return self.send_photo(screenshot_path, formatted)
            else:
                # Делаем новый скриншот
                import pyautogui
                temp_path = f"temp_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                pyautogui.screenshot(temp_path)
                result = self.send_photo(temp_path, formatted)
                os.remove(temp_path)
                return result
        else:
            return self.send_message(formatted)

    def send_error_report(
            self,
            error: str,
            context: Optional[Dict[str, Any]] = None,
            screenshot: bool = True
    ) -> bool:
        """
        Отправка отчёта об ошибке.

        Args:
            error: Текст ошибки
            context: Контекст выполнения
            screenshot: Сделать скриншот

        Returns:
            True если отправлено успешно
        """
        message = f"❌ <b>ERROR OCCURRED</b>\n\n<code>{error}</code>"

        if context:
            context_str = "\n".join([f"• {k}: {v}" for k, v in context.items()])
            message += f"\n\n📋 <b>Context:</b>\n{context_str}"

        message += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return self.send_notification("Error Report", message, screenshot=screenshot)

    def send_success_report(
            self,
            message: str,
            data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Отправка отчёта об успешном выполнении.

        Args:
            message: Основное сообщение
            data: Дополнительные данные

        Returns:
            True если отправлено успешно
        """
        full_message = f"✅ <b>SUCCESS</b>\n\n{message}"

        if data:
            data_str = "\n".join([f"• {k}: {v}" for k, v in data.items()])
            full_message += f"\n\n📊 <b>Details:</b>\n{data_str}"

        full_message += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return self.send_message(full_message)

    def test_connection(self) -> bool:
        """
        Проверка подключения к Telegram API.

        Returns:
            True если подключение успешно
        """
        if not self.token:
            self.last_error = "No bot token"
            return False

        url = f"https://api.telegram.org/bot{self.token}/getMe"

        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    self.last_error = None
                    return True
            self.last_error = "Invalid bot token"
            return False
        except Exception as e:
            self.last_error = str(e)
            return False

    def get_updates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Получение последних обновлений (для получения chat_id).

        Args:
            limit: Максимальное количество обновлений

        Returns:
            Список обновлений
        """
        if not self.token:
            return []

        url = f"https://api.telegram.org/bot{self.token}/getUpdates"

        try:
            response = requests.get(url, params={"limit": limit}, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('result', [])
            return []
        except Exception:
            return []

    def get_chat_id_from_updates(self) -> Optional[str]:
        """
        Получение chat_id из последних обновлений (полезно для настройки).

        Returns:
            Chat ID или None
        """
        updates = self.get_updates(1)
        if updates:
            try:
                return str(updates[0]['message']['chat']['id'])
            except (KeyError, IndexError):
                pass
        return None

    def is_configured(self) -> bool:
        """Проверка, настроен ли бот"""
        return self.enabled and self.token and self.chat_id

    def get_status(self) -> Dict[str, Any]:
        """Получить статус модуля"""
        return {
            "enabled": self.enabled,
            "configured": self.is_configured(),
            "last_error": self.last_error,
            "last_send_time": self.last_send_time.isoformat() if self.last_send_time else None,
            "retry_count": self.retry_count,
        }


if __name__ == "__main__":
    # Тестирование модуля Telegram
    print("=" * 50)
    print("Testing TelegramNotifier Module")
    print("=" * 50)

    notifier = TelegramNotifier()

    # Проверка без конфигурации
    print("\n📡 Without configuration:")
    print(f"   Configured: {notifier.is_configured()}")
    result = notifier.send_message("Test message")
    print(f"   Send result: {result}")
    print(f"   Error: {notifier.last_error}")

    # Проверка тестового подключения (без реального токена)
    print("\n🔧 Test connection (no token):")
    result = notifier.test_connection()
    print(f"   Connection test: {result}")

    # Инструкция по настройке
    print("\n📖 How to configure Telegram Bot:")
    print("   1. Message @BotFather on Telegram")
    print("   2. Send /newbot and follow instructions")
    print("   3. Copy your bot token")
    print("   4. Message @userinfobot to get your chat ID")
    print("   5. Set token and chat_id in settings")

    print("\n✅ Module ready!")