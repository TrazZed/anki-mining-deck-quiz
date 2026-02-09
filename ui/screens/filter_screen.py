"""
Filter selection screen renderer.
"""

import math
import pygame
from config import *
from game.filtering import (
    MATURITY_NEW, MATURITY_LEARNING, MATURITY_YOUNG, MATURITY_MATURE,
    MATURITY_DISPLAY_NAMES
)


def draw_filter_screen(game):
    """Draw the filter selection screen."""
    base_color = game.bg_color
    wave = int(10 * math.sin(game.background_time * 0.5))
    bg_color = (
        max(0, min(255, base_color[0] + wave)),
        max(0, min(255, base_color[1] + wave)),
        max(0, min(255, base_color[2] + wave))
    )
    game.screen.fill(bg_color)
    
    # Draw background particles
    for i in range(12):
        base_x = (game.background_time * 25 + i * 137) % (game.width + 50)
        base_y = (i * 83) % game.height
        offset_x = 40 * math.sin(i * 3.14)
        offset_y = 35 * math.cos(i * 2.71)
        x = base_x + offset_x
        y = base_y + offset_y
        alpha = int(50 + 30 * math.sin(game.background_time + i))
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*game.text_color[:3], alpha), (2, 2), 2)
        game.screen.blit(s, (int(x), int(y)))
    
    # Title
    title_font = pygame.font.Font(None, 56)
    title = title_font.render("Filter Cards", True, game.text_color)
    title_rect = title.get_rect(center=(game.width // 2, 80))
    game.screen.blit(title, title_rect)
    
    # Subtitle
    subtitle = game.meaning_font.render("Select which cards to practice", True, game.gray_color)
    subtitle_rect = subtitle.get_rect(center=(game.width // 2, 120))
    game.screen.blit(subtitle, subtitle_rect)
    
    # Get maturity counts if available
    if hasattr(game, 'maturity_counts') and game.maturity_counts:
        counts = game.maturity_counts
    else:
        counts = None
    
    # Maturity level checkboxes
    y_start = 180
    checkbox_size = 24
    spacing = 55
    
    maturity_levels = [MATURITY_NEW, MATURITY_LEARNING, MATURITY_YOUNG, MATURITY_MATURE]
    
    for i, level in enumerate(maturity_levels):
        y_pos = y_start + i * spacing
        
        # Checkbox
        checkbox_x = game.width // 2 - 180
        checkbox_rect = pygame.Rect(checkbox_x, y_pos, checkbox_size, checkbox_size)
        
        # Store checkbox rect for click detection
        if not hasattr(game, 'filter_checkboxes'):
            game.filter_checkboxes = {}
        game.filter_checkboxes[level] = checkbox_rect
        
        # Draw checkbox background
        pygame.draw.rect(game.screen, (255, 255, 255), checkbox_rect)
        pygame.draw.rect(game.screen, game.text_color, checkbox_rect, 2)
        
        # Draw checkmark if selected
        is_selected = level in game.card_filter.maturity_levels
        if is_selected:
            # Draw an X or checkmark
            pygame.draw.line(game.screen, game.correct_color, 
                           (checkbox_rect.left + 4, checkbox_rect.top + 4),
                           (checkbox_rect.right - 4, checkbox_rect.bottom - 4), 3)
            pygame.draw.line(game.screen, game.correct_color,
                           (checkbox_rect.right - 4, checkbox_rect.top + 4),
                           (checkbox_rect.left + 4, checkbox_rect.bottom - 4), 3)
        
        # Label
        label_x = checkbox_x + checkbox_size + 15
        label_text = MATURITY_DISPLAY_NAMES[level]
        
        # Add count if available
        if counts and level in counts:
            label_text = f"{label_text} ({counts[level]} cards)"
        
        label_surface = game.meaning_font.render(label_text, True, game.text_color)
        game.screen.blit(label_surface, (label_x, y_pos + 2))
    
    # Info text
    if game.card_filter.is_active():
        filter_summary = game.card_filter.get_summary()
        info_text = f"Playing with: {filter_summary}"
        info_color = game.correct_color
    else:
        info_text = "No filters selected - playing with all cards"
        info_color = game.gray_color
    
    info_surface = game.score_font.render(info_text, True, info_color)
    info_rect = info_surface.get_rect(center=(game.width // 2, y_start + 4 * spacing + 20))
    game.screen.blit(info_surface, info_rect)
    
    # Buttons
    button_y = game.height - 150
    
    # Clear Filters button
    clear_button = pygame.Rect(game.width // 2 - 250, button_y, 150, 50)
    game.clear_filter_button = clear_button
    clear_color = game.button_hover_color if game.clear_filter_button_hover else game.status_color
    pygame.draw.rect(game.screen, clear_color, clear_button, border_radius=10)
    clear_text = game.meaning_font.render("Clear All", True, (255, 255, 255))
    clear_text_rect = clear_text.get_rect(center=clear_button.center)
    game.screen.blit(clear_text, clear_text_rect)
    
    # Continue button
    continue_button = pygame.Rect(game.width // 2 + 100, button_y, 150, 50)
    game.continue_filter_button = continue_button
    continue_color = game.button_hover_color if game.continue_filter_button_hover else game.correct_color
    pygame.draw.rect(game.screen, continue_color, continue_button, border_radius=10)
    continue_text = game.meaning_font.render("Continue →", True, (255, 255, 255))
    continue_text_rect = continue_text.get_rect(center=continue_button.center)
    game.screen.blit(continue_text, continue_text_rect)
    
    # Back button
    back_button = pygame.Rect(game.width // 2 - 75, button_y + 60, 150, 40)
    game.filter_back_button = back_button
    back_color = game.button_hover_color if game.filter_back_button_hover else game.button_color
    pygame.draw.rect(game.screen, back_color, back_button, border_radius=10)
    back_text = game.score_font.render("← Back to Menu", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=back_button.center)
    game.screen.blit(back_text, back_text_rect)
