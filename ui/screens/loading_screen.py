"""
Loading screen renderers.
"""

import math
import pygame
from config import *


def draw_loading(game):
    """Draw the loading screen."""
    base_color = game.bg_color
    wave = int(15 * math.sin(game.background_time * 2))
    bg_color = (
        max(0, min(255, base_color[0] + wave)),
        max(0, min(255, base_color[1] + wave)),
        max(0, min(255, base_color[2] + wave))
    )
    game.screen.fill(bg_color)
    
    # Draw animated particles
    for i in range(15):
        base_x = (game.background_time * 45 + i * 119) % (game.width + 50)
        base_y = (i * 71) % game.height
        offset_x = 35 * math.sin(i * 2.97)
        offset_y = 30 * math.cos(i * 3.33)
        x = base_x + offset_x
        y = base_y + offset_y
        alpha = int(100 + 50 * math.sin(game.background_time * 2 + i))
        size = 3 + int(2 * math.sin(game.background_time * 3 + i * 0.5))
        s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*game.button_color[:3], alpha), (int(size), int(size)), int(size))
        game.screen.blit(s, (int(x), int(y)))
    
    # Title
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("Loading...", True, game.text_color)
    title_rect = title.get_rect(center=(game.width // 2, game.height // 2 - 50))
    game.screen.blit(title, title_rect)
    
    # Loading status
    if game.loading_error:
        status_color = game.incorrect_color
        status = game.loading_error
        status_font = pygame.font.Font(None, 24)
        game.draw_text_wrapped(status, status_font, status_color, game.height // 2 + 20, max_width=700)
        
        # Show retry button
        button_color = game.button_hover_color if game.retry_button_hover else game.button_color
        pygame.draw.rect(game.screen, button_color, game.retry_button, border_radius=8)
        
        retry_text = "Retry"
        retry_font = pygame.font.Font(None, 32)
        retry_surface = retry_font.render(retry_text, True, game.text_color)
        retry_rect = retry_surface.get_rect(center=game.retry_button.center)
        game.screen.blit(retry_surface, retry_rect)
        
        hint_text = "Press ESC to quit or R to retry"
        hint_surface = game.meaning_font.render(hint_text, True, game.gray_color)
        hint_rect = hint_surface.get_rect(center=(game.width // 2, game.height // 2 + 150))
        game.screen.blit(hint_surface, hint_rect)
    else:
        status_color = game.button_color
        status = game.loading_status
        status_font = pygame.font.Font(None, 28)
        status_surface = status_font.render(status, True, status_color)
        status_rect = status_surface.get_rect(center=(game.width // 2, game.height // 2 + 20))
        game.screen.blit(status_surface, status_rect)
        
        # Animated loading bar
        bar_width = 400
        bar_height = 20
        bar_x = (game.width - bar_width) // 2
        bar_y = game.height // 2 + 70
        
        pygame.draw.rect(game.screen, game.gray_color, 
                       (bar_x, bar_y, bar_width, bar_height), 
                       border_radius=10)
        
        progress_width = 100
        progress_x = bar_x + int((bar_width - progress_width) * (0.5 + 0.5 * math.sin(game.background_time * 3)))
        pygame.draw.rect(game.screen, game.button_color,
                       (progress_x, bar_y, progress_width, bar_height),
                       border_radius=10)


def draw_loading_save(game):
    """Draw the loading save screen."""
    base_color = game.bg_color
    wave = int(15 * math.sin(game.background_time * 2))
    bg_color = (
        max(0, min(255, base_color[0] + wave)),
        max(0, min(255, base_color[1] + wave)),
        max(0, min(255, base_color[2] + wave))
    )
    game.screen.fill(bg_color)
    
    # Draw animated particles
    for i in range(15):
        base_x = (game.background_time * 45 + i * 119) % (game.width + 50)
        base_y = (i * 71) % game.height
        offset_x = 35 * math.sin(i * 2.97)
        offset_y = 30 * math.cos(i * 3.33)
        x = base_x + offset_x
        y = base_y + offset_y
        alpha = int(100 + 50 * math.sin(game.background_time * 2 + i))
        size = 3 + int(2 * math.sin(game.background_time * 3 + i * 0.5))
        s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*game.correct_color[:3], alpha), (int(size), int(size)), int(size))
        game.screen.blit(s, (int(x), int(y)))
    
    # Title
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("Loading Game...", True, game.text_color)
    title_rect = title.get_rect(center=(game.width // 2, game.height // 2 - 50))
    game.screen.blit(title, title_rect)
    
    # Status
    if game.save_load_error:
        status_color = game.incorrect_color
        status = game.save_load_error
    else:
        status_color = game.correct_color
        status = game.save_load_status
    
    status_font = pygame.font.Font(None, 28)
    status_surface = status_font.render(status, True, status_color)
    status_rect = status_surface.get_rect(center=(game.width // 2, game.height // 2 + 20))
    game.screen.blit(status_surface, status_rect)
    
    # Animated loading bar
    if not game.save_load_error:
        bar_width = 400
        bar_height = 20
        bar_x = (game.width - bar_width) // 2
        bar_y = game.height // 2 + 70
        
        pygame.draw.rect(game.screen, game.gray_color, 
                       (bar_x, bar_y, bar_width, bar_height), 
                       border_radius=10)
        
        progress_width = 100
        progress_x = bar_x + int((bar_width - progress_width) * (0.5 + 0.5 * math.sin(game.background_time * 3)))
        pygame.draw.rect(game.screen, game.correct_color,
                       (progress_x, bar_y, progress_width, bar_height),
                       border_radius=10)


def draw_saving(game):
    """Draw the saving screen."""
    base_color = game.bg_color
    wave = int(15 * math.sin(game.background_time * 2))
    bg_color = (
        max(0, min(255, base_color[0] + wave)),
        max(0, min(255, base_color[1] + wave)),
        max(0, min(255, base_color[2] + wave))
    )
    game.screen.fill(bg_color)
    
    # Draw animated particles
    for i in range(15):
        base_x = (game.background_time * 45 + i * 119) % (game.width + 50)
        base_y = (i * 71) % game.height
        offset_x = 35 * math.sin(i * 2.97)
        offset_y = 30 * math.cos(i * 3.33)
        x = base_x + offset_x
        y = base_y + offset_y
        alpha = int(100 + 50 * math.sin(game.background_time * 2 + i))
        size = 3 + int(2 * math.sin(game.background_time * 3 + i * 0.5))
        s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*game.correct_color[:3], alpha), (int(size), int(size)), int(size))
        game.screen.blit(s, (int(x), int(y)))
    
    # Title
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("Saving Game...", True, game.text_color)
    title_rect = title.get_rect(center=(game.width // 2, game.height // 2 - 50))
    game.screen.blit(title, title_rect)
    
    # Status
    if game.save_load_error:
        status_color = game.incorrect_color
        status = game.save_load_error
    else:
        status_color = game.correct_color
        status = game.save_load_status
    
    status_font = pygame.font.Font(None, 28)
    status_surface = status_font.render(status, True, status_color)
    status_rect = status_surface.get_rect(center=(game.width // 2, game.height // 2 + 20))
    game.screen.blit(status_surface, status_rect)
    
    # Animated loading bar
    if not game.save_load_error:
        bar_width = 400
        bar_height = 20
        bar_x = (game.width - bar_width) // 2
        bar_y = game.height // 2 + 70
        
        pygame.draw.rect(game.screen, game.gray_color, 
                       (bar_x, bar_y, bar_width, bar_height), 
                       border_radius=10)
        
        progress_width = 100
        progress_x = bar_x + int((bar_width - progress_width) * (0.5 + 0.5 * math.sin(game.background_time * 3)))
        pygame.draw.rect(game.screen, game.correct_color,
                       (progress_x, bar_y, progress_width, bar_height),
                       border_radius=10)
