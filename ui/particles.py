"""
Particle effects for visual feedback.
"""

import math
import random
import pygame


class Particle:
    """Base particle class for visual effects."""
    
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, lifetime=1.0, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255
    
    def update(self, dt):
        """
        Update particle state.
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            True if particle is still alive, False if expired
        """
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_y += 200 * dt  # Gravity
        self.lifetime -= dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        return self.lifetime > 0
    
    def draw(self, surface):
        """Draw particle to surface."""
        if self.alpha > 0:
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], self.alpha)
            pygame.draw.circle(s, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class FireParticle(Particle):
    """Particle that rises upward like fire."""
    
    def __init__(self, x, y):
        colors = [(255, 100, 0), (255, 200, 0), (255, 150, 0), (255, 69, 0)]
        color = random.choice(colors)
        velocity_x = random.uniform(-30, 30)
        velocity_y = random.uniform(-100, -50)
        lifetime = random.uniform(0.5, 1.0)
        size = random.uniform(3, 6)
        super().__init__(x, y, color, velocity_x, velocity_y, lifetime, size)
    
    def update(self, dt):
        """Update fire particle - rises upward."""
        self.velocity_y -= 50 * dt  # Rise up instead of fall
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.lifetime -= dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        return self.lifetime > 0


class StarParticle(Particle):
    """Star-shaped particle for burst effects."""
    
    def __init__(self, x, y, velocity_x, velocity_y):
        colors = [(255, 255, 0), (255, 255, 255), (255, 215, 0), (255, 250, 150)]
        color = random.choice(colors)
        lifetime = random.uniform(0.8, 1.5)
        size = random.uniform(4, 8)
        super().__init__(x, y, color, velocity_x, velocity_y, lifetime, size)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-360, 360)
    
    def update(self, dt):
        """Update star particle with rotation."""
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.velocity_y += 150 * dt  # Gravity
        self.velocity_x *= 0.98  # Air resistance
        self.velocity_y *= 0.98
        self.lifetime -= dt
        self.rotation += self.rotation_speed * dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        return self.lifetime > 0
    
    def draw(self, surface):
        """Draw a 5-pointed star."""
        if self.alpha > 0:
            # Draw a 5-pointed star
            points = []
            for i in range(10):
                angle = math.radians(self.rotation + i * 36)
                radius = self.size if i % 2 == 0 else self.size * 0.4
                px = self.x + radius * math.cos(angle)
                py = self.y + radius * math.sin(angle)
                points.append((px, py))
            
            if len(points) >= 3:
                s = pygame.Surface((int(self.size * 3), int(self.size * 3)), pygame.SRCALPHA)
                offset_x = self.size * 1.5
                offset_y = self.size * 1.5
                adjusted_points = [(px - self.x + offset_x, py - self.y + offset_y) for px, py in points]
                color_with_alpha = (*self.color[:3], self.alpha)
                pygame.draw.polygon(s, color_with_alpha, adjusted_points)
                surface.blit(s, (int(self.x - offset_x), int(self.y - offset_y)))
