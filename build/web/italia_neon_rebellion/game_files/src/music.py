import math
import os
import random
import struct
import pygame


class MusicManager:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2)
            self.enabled = True
            self.sounds = {
                "laser": self._tone(0.07, 0.22, laser=True),
                "explosion": self._noise(0.22, 0.28),
                "ultimate": self._tone(0.65, 0.42),
                "pickup": self._tone(0.16, 0.25, pickup=True),
                "hit": self._noise(0.08, 0.16),
            }
        except (pygame.error, ValueError):
            self.enabled = False

    @staticmethod
    def _sound(samples):
        return pygame.mixer.Sound(buffer=bytes(samples))

    def _tone(self, duration, volume, laser=False, pickup=False):
        rate = 22050
        buffer = bytearray()
        for index in range(int(rate * duration)):
            t = index / rate
            envelope = max(0.0, 1.0 - t / duration)
            if laser:
                frequency = 1050 - 700 * t / duration
                value = math.sin(2 * math.pi * frequency * t)
            elif pickup:
                frequency = 440 + 500 * t / duration
                value = math.sin(2 * math.pi * frequency * t)
            else:
                value = 0.55 * math.sin(2 * math.pi * 110 * t) + 0.45 * math.sin(2 * math.pi * 220 * t)
            sample = int(14000 * value * envelope)
            buffer.extend(struct.pack("<hh", sample, sample))
        sound = self._sound(buffer)
        sound.set_volume(volume)
        return sound

    def _noise(self, duration, volume):
        rate = 22050
        buffer = bytearray()
        for index in range(int(rate * duration)):
            envelope = 1.0 - index / (rate * duration)
            sample = int(14000 * random.uniform(-1, 1) * envelope)
            buffer.extend(struct.pack("<hh", sample, sample))
        sound = self._sound(buffer)
        sound.set_volume(volume)
        return sound

    def play_music(self, filepath, volume=0.35):
        """Loads and plays background music safely if the file exists."""
        if not self.enabled:
            return
        try:
            if os.path.exists(filepath):
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(0.0 if self.muted else volume)
                pygame.mixer.music.play(-1)
            else:
                print(f"Manca il file audio: {filepath}. Il gioco continuerà senza musica.")
        except pygame.error:
            pass

    def stop_music(self):
        """Stops the background music smoothly."""
        if self.enabled:
            pygame.mixer.music.stop()

    def play(self, name):
        if self.enabled and not self.muted and name in self.sounds:
            try:
                self.sounds[name].play()
            except pygame.error:
                pass

    def toggle_mute(self):
        self.muted = not self.muted
        if self.enabled:
            if self.muted:
                pygame.mixer.music.set_volume(0.0)
            else:
                pygame.mixer.music.set_volume(0.35)
        return self.muted

    def play_laser(self):
        self.play("laser")

    def play_explosion(self):
        self.play("explosion")

    def play_ultimate(self):
        self.play("ultimate")

    def play_pickup(self):
        self.play("pickup")

    def play_hit(self):
        self.play("hit")

