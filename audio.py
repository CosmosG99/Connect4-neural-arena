import pygame
import numpy as np
import threading
import time
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

class AudioSystem:
    def __init__(self):
        self.sounds = {}
        self.music_enabled = True
        self.sfx_enabled = True
        self._generate_sounds()
        self.music_channel = None

    def _generate_tone(self, frequency, duration, volume=0.5, wave_type='sine'):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        
        if wave_type == 'sine':
            wave = np.sin(frequency * t * 2 * np.pi)
        elif wave_type == 'square':
            wave = np.sign(np.sin(frequency * t * 2 * np.pi))
        elif wave_type == 'sawtooth':
            wave = 2 * (t * frequency - np.floor(0.5 + t * frequency))
        else:
            wave = np.sin(frequency * t * 2 * np.pi)
            
        # Apply envelope
        attack = int(0.05 * sample_rate)
        release = int(0.1 * sample_rate)
        if n_samples > attack + release:
            envelope = np.ones(n_samples)
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[-release:] = np.linspace(1, 0, release)
            wave *= envelope

        audio = wave * volume * 32767
        audio = audio.astype(np.int16)
        stereo_audio = np.empty((audio.size, 2), dtype=np.int16)
        stereo_audio[:, 0] = audio
        stereo_audio[:, 1] = audio
        
        return pygame.sndarray.make_sound(stereo_audio)

    def _generate_ambient_loop(self, gameplay=False):
        """Generates a high-quality soothing cinematic space ambient loop"""
        sample_rate = 44100
        duration = 20.0 
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        
        # Frequencies for a "Deep Space" vibe (F minor 7/9 chord palette)
        # F1, C2, F2, Ab2, C3, Eb3, G3
        freqs = [43.65, 65.41, 87.31, 103.83, 130.81, 155.56, 196.00]
        weights = [0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.15]
        
        if gameplay:
            # Add shimmering high-frequency "neural" layers
            freqs += [392.00, 523.25, 659.25, 783.99] # G4, C5, E5, G5
            weights += [0.1, 0.08, 0.05, 0.03]
            
        wave = np.zeros(n_samples)
        for f, w in zip(freqs, weights):
            # Complex LFOs for "living" sound modulation
            lfo_speed = 0.04 + random.uniform(0, 0.06)
            lfo = 0.7 + 0.3 * np.sin(2 * np.pi * lfo_speed * t + random.uniform(0, 20))
            # Richer harmonic content
            wave += w * lfo * (np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * f * 2 * t))
            
        # Add very subtle "space dust" white noise
        noise = (np.random.rand(n_samples) * 2 - 1) * 0.015
        wave += noise
            
        # Seamless loop crossfade envelope
        fade = int(3.0 * sample_rate)
        envelope = np.ones(n_samples)
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)
        wave *= envelope
        
        # Normalize and set volume
        max_val = np.max(np.abs(wave))
        if max_val > 0: wave = wave / max_val
        
        audio = wave * 0.35 * 32767 
        audio = audio.astype(np.int16)
        stereo_audio = np.empty((audio.size, 2), dtype=np.int16)
        stereo_audio[:, 0] = audio
        stereo_audio[:, 1] = audio
        
        return pygame.sndarray.make_sound(stereo_audio)

    def _generate_magnetic_drop(self):
        """Smooth magnetic frequency sweep for disc placement"""
        sample_rate = 44100
        duration = 0.35
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        
        # Frequency sweep from 200Hz down to 80Hz (Magnetic fall)
        freq = np.linspace(200, 80, n_samples)
        wave = np.sin(2 * np.pi * freq * t)
        
        envelope = np.ones(n_samples)
        attack = int(0.02 * sample_rate)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[attack:] = np.linspace(1, 0, n_samples - attack)
        wave *= envelope
        
        audio = wave * 0.4 * 32767
        audio = audio.astype(np.int16)
        stereo_audio = np.empty((audio.size, 2), dtype=np.int16)
        stereo_audio[:, 0] = audio
        stereo_audio[:, 1] = audio
        return pygame.sndarray.make_sound(stereo_audio)

    def _generate_victory_chord(self):
        """C Major Chord with a rising swell"""
        sample_rate = 44100
        duration = 2.5
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        
        # C Major (C4, E4, G4, C5)
        freqs = [261.63, 329.63, 392.00, 523.25]
        wave = np.zeros(n_samples)
        for f in freqs:
            wave += np.sin(2 * np.pi * f * t)
            
        envelope = np.ones(n_samples)
        # Rising swell
        envelope[:int(0.5*sample_rate)] = np.linspace(0, 1, int(0.5*sample_rate))
        # Long decay
        envelope[int(0.5*sample_rate):] = np.linspace(1, 0, n_samples - int(0.5*sample_rate))
        wave *= envelope
        
        audio = (wave / len(freqs)) * 0.6 * 32767
        audio = audio.astype(np.int16)
        stereo_audio = np.empty((audio.size, 2), dtype=np.int16)
        stereo_audio[:, 0] = audio
        stereo_audio[:, 1] = audio
        return pygame.sndarray.make_sound(stereo_audio)

    def _generate_defeat_chord(self):
        """A Minor Chord with a somber fall"""
        sample_rate = 44100
        duration = 3.0
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, False)
        
        # A Minor (A3, C4, E4, A4)
        freqs = [220.00, 261.63, 329.63, 440.00]
        wave = np.zeros(n_samples)
        for f in freqs:
            wave += np.sin(2 * np.pi * f * t)
            
        envelope = np.ones(n_samples)
        # Short attack
        envelope[:int(0.2*sample_rate)] = np.linspace(0, 1, int(0.2*sample_rate))
        # Very long fade out
        envelope[int(0.2*sample_rate):] = np.linspace(1, 0, n_samples - int(0.2*sample_rate))
        wave *= envelope
        
        audio = (wave / len(freqs)) * 0.5 * 32767
        audio = audio.astype(np.int16)
        stereo_audio = np.empty((audio.size, 2), dtype=np.int16)
        stereo_audio[:, 0] = audio
        stereo_audio[:, 1] = audio
        return pygame.sndarray.make_sound(stereo_audio)

    def _generate_sounds(self):
        try:
            # Soft futuristic tick (High-freq sine)
            self.sounds['hover'] = self._generate_tone(880, 0.04, 0.06, 'sine')
            # Minimalist magnetic click
            self.sounds['click'] = self._generate_tone(440, 0.06, 0.12, 'sine')
            # Smooth magnetic drop
            self.sounds['drop'] = self._generate_magnetic_drop()
            
            # Cinematic intro
            self.sounds['intro'] = self._generate_tone(110, 4.0, 0.25, 'sine')
            
            # Continuous Ambient Loops
            self.sounds['ambient_menu'] = self._generate_ambient_loop(gameplay=False)
            self.sounds['ambient_game'] = self._generate_ambient_loop(gameplay=True)
            
            self.sounds['victory'] = self._generate_victory_chord()
            self.sounds['defeat'] = self._generate_defeat_chord()
        except Exception as e:
            print("Audio generation failed:", e)
            self.sfx_enabled = False

    def play_sfx(self, name):
        if self.sfx_enabled and name in self.sounds:
            self.sounds[name].play()

    def start_music(self, gameplay=False):
        if self.music_enabled:
            # Select appropriate track
            track_name = 'ambient_game' if gameplay else 'ambient_menu'
            if track_name in self.sounds:
                # Stop current if different
                if self.music_channel:
                    self.music_channel.fadeout(1500)
                
                # Use dedicated channel for music to avoid conflicts with SFX
                self.music_channel = self.sounds[track_name].play(loops=-1, fade_ms=2500)

    def stop_music(self):
        if self.music_channel:
            self.music_channel.fadeout(1000)

audio_sys = AudioSystem()
