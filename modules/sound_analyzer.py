"""
Clixpert S Pro Ultimate - Sound Analyzer Module
Анализ звука для создания условий (требует PyAudio)
"""

import time
import threading
from typing import Optional, Callable

# Флаг доступности звука
SOUND_AVAILABLE = False

try:
    import pyaudio
    import audioop
    import numpy as np

    SOUND_AVAILABLE = True
except ImportError:
    pass


class SoundAnalyzer:
    """
    Анализ звука с микрофона для обнаружения громких звуков.
    Требует установки PyAudio: pip install pyaudio
    """

    def __init__(self):
        self.audio = None
        self.stream = None
        self.is_listening = False
        self.callback: Optional[Callable] = None
        self.threshold = 500
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16 if SOUND_AVAILABLE else None

    def init_audio(self) -> bool:
        """
        Инициализация аудио устройства.

        Returns:
            True если инициализация успешна
        """
        if not SOUND_AVAILABLE:
            print("PyAudio not installed. Sound detection disabled.")
            return False

        try:
            self.audio = pyaudio.PyAudio()
            return True
        except Exception as e:
            print(f"Failed to initialize audio: {e}")
            return False

    def start_listening(self, threshold: int = 500, callback: Optional[Callable] = None) -> bool:
        """
        Начать прослушивание звука.

        Args:
            threshold: Порог срабатывания (0-2000)
            callback: Функция, вызываемая при превышении порога

        Returns:
            True если запуск успешен
        """
        if not SOUND_AVAILABLE or not self.audio:
            return False

        self.threshold = threshold
        self.callback = callback
        self.is_listening = True

        def audio_callback(in_data, frame_count, time_info, status):
            if self.is_listening:
                # Анализ уровня звука
                rms = audioop.rms(in_data, 2)
                if rms > self.threshold and self.callback:
                    self.callback(rms)
            return (None, pyaudio.paContinue)

        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=audio_callback
            )
            self.stream.start_stream()
            return True
        except Exception as e:
            print(f"Failed to start audio stream: {e}")
            return False

    def stop_listening(self) -> None:
        """Остановить прослушивание"""
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def get_sound_level(self) -> int:
        """
        Получить текущий уровень звука.

        Returns:
            Уровень звука (RMS)
        """
        if not SOUND_AVAILABLE or not self.stream:
            return 0

        try:
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            return audioop.rms(data, 2)
        except Exception:
            return 0

    def get_frequency(self, duration: float = 0.1) -> float:
        """
        Получить доминирующую частоту звука.

        Args:
            duration: Длительность анализа в секундах

        Returns:
            Частота в Гц
        """
        if not SOUND_AVAILABLE or not self.stream:
            return 0

        try:
            frames = []
            for _ in range(int(self.sample_rate / self.chunk_size * duration)):
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(np.frombuffer(data, dtype=np.int16))

            data = np.concatenate(frames)
            fft = np.fft.fft(data)
            freqs = np.fft.fftfreq(len(data), 1.0 / self.sample_rate)

            magnitude = np.abs(fft[:len(fft) // 2])
            dominant_freq = freqs[np.argmax(magnitude)]
            return abs(dominant_freq)
        except Exception:
            return 0

    def wait_for_sound(self, threshold: int, timeout: float = 30) -> bool:
        """
        Ожидание звука выше порога.

        Args:
            threshold: Порог срабатывания
            timeout: Таймаут в секундах

        Returns:
            True если звук обнаружен
        """
        if not SOUND_AVAILABLE or not self.stream:
            return False

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                rms = audioop.rms(data, 2)
                if rms > threshold:
                    return True
            except Exception:
                pass
            time.sleep(0.05)
        return False

    def cleanup(self) -> None:
        """Очистка ресурсов"""
        self.stop_listening()
        if self.audio:
            self.audio.terminate()
            self.audio = None


class SoundCondition:
    """
    Упрощённый класс для работы со звуковыми условиями.
    """

    def __init__(self):
        self.analyzer: Optional[SoundAnalyzer] = None
        self.threshold = 500

    def init(self) -> bool:
        """Инициализация анализатора"""
        if SOUND_AVAILABLE:
            self.analyzer = SoundAnalyzer()
            return self.analyzer.init_audio()
        return False

    def start(self, threshold: int = 500, callback: Optional[Callable] = None) -> bool:
        """Начать прослушивание"""
        if not self.analyzer:
            return False
        self.threshold = threshold
        return self.analyzer.start_listening(threshold, callback)

    def stop(self) -> None:
        """Остановить прослушивание"""
        if self.analyzer:
            self.analyzer.stop_listening()

    def get_level(self) -> int:
        """Получить уровень звука"""
        if self.analyzer:
            return self.analyzer.get_sound_level()
        return 0

    def wait_for_sound(self, threshold: int = None, timeout: float = 30) -> bool:
        """Ожидать звук"""
        if not self.analyzer:
            return False
        return self.analyzer.wait_for_sound(threshold or self.threshold, timeout)

    def check_condition(self, threshold: int = None, duration: float = 0.5) -> bool:
        """
        Проверить звуковое условие.

        Args:
            threshold: Порог срабатывания
            duration: Длительность проверки

        Returns:
            True если звук обнаружен
        """
        if not self.analyzer:
            return False

        start_time = time.time()
        while time.time() - start_time < duration:
            level = self.get_level()
            if level > (threshold or self.threshold):
                return True
            time.sleep(0.05)
        return False

    def cleanup(self) -> None:
        """Очистка ресурсов"""
        if self.analyzer:
            self.analyzer.cleanup()
            self.analyzer = None


if __name__ == "__main__":
    # Тестирование модуля звука
    print("=" * 50)
    print("Testing SoundAnalyzer Module")
    print("=" * 50)

    if SOUND_AVAILABLE:
        print("\n🎤 PyAudio available - sound detection enabled")

        sound = SoundCondition()
        if sound.init():
            print("✅ Audio initialized")

            level = sound.get_level()
            print(f"📊 Current sound level: {level}")

            sound.cleanup()
        else:
            print("❌ Failed to initialize audio")
    else:
        print("\n⚠️ PyAudio not installed")
        print("   Install with: pip install pyaudio")
        print("   Or download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")

    print("\n✅ Module ready!")