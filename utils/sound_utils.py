"""
Sound generation utilities for game audio effects.
"""

import math
import pygame


def generate_sound(frequency, duration=0.1):
    """
    Generate a simple beep sound.
    
    Args:
        frequency: Frequency of the sound in Hz
        duration: Duration of the sound in seconds
        
    Returns:
        pygame.Sound object or None if generation fails
    """
    try:
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        buf = []
        for i in range(n_samples):
            value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            buf.append([value, value])
        sound = pygame.sndarray.make_sound(buf)
        return sound
    except:
        return None
