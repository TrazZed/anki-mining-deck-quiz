"""
Review incorrect answers screen renderer.
"""

import pygame
from config import *


def draw_review_incorrect(game):
    """Draw the review incorrect answers screen."""
    game.screen.fill(game.bg_color)
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title = title_font.render("Review Incorrect Answers", True, game.incorrect_color)
    title_rect = title.get_rect(center=(game.width // 2, 40))
    game.screen.blit(title, title_rect)
    
    # Count
    count_text = f"{len(game.incorrect_answers)} incorrect answer(s)"
    count_surface = game.meaning_font.render(count_text, True, game.gray_color)
    count_rect = count_surface.get_rect(center=(game.width // 2, 80))
    game.screen.blit(count_surface, count_rect)
    
    # Scrolling hint if there are many items
    if len(game.incorrect_answers) > 7:
        hint_text = "(Scroll to see all)"
        hint_surface = game.score_font.render(hint_text, True, game.gray_color)
        hint_rect = hint_surface.get_rect(center=(game.width // 2, 100))
        game.screen.blit(hint_surface, hint_rect)
    
    # Create a scrollable area
    scroll_area_top = 120
    scroll_area_bottom = 560
    scroll_area_height = scroll_area_bottom - scroll_area_top
    
    # Calculate total content height
    item_height = 60
    total_content_height = len(game.incorrect_answers) * item_height
    
    # Clamp scroll position
    max_scroll = max(0, total_content_height - scroll_area_height)
    game.review_scroll = max(0, min(game.review_scroll, max_scroll))
    
    # Cache rendered content
    if (game.review_cache is None or 
        abs(game.review_cache_scroll - game.review_scroll) > 1):
        
        game.review_cache_scroll = game.review_scroll
        
        # Create a clipping surface for the scrollable area
        scroll_surface = pygame.Surface((game.width, scroll_area_height))
        scroll_surface.fill(game.bg_color)
        
        # Pre-render fonts
        if not hasattr(game, '_review_fonts_cached'):
            game._review_word_font = pygame.font.SysFont(
                game.reading_font.get_name() if hasattr(game.reading_font, 'get_name') else 'msgothic', 36)
            game._review_reading_font = pygame.font.SysFont(
                game.reading_font.get_name() if hasattr(game.reading_font, 'get_name') else 'msgothic', 24)
            game._review_fonts_cached = True
        
        # Draw items onto the scroll surface
        for i, ans in enumerate(game.incorrect_answers):
            y_pos = i * item_height - game.review_scroll
            
            # Only draw if visible
            if -item_height < y_pos < scroll_area_height + item_height:
                # Word
                word_surface = game._review_word_font.render(ans['word'], True, game.text_color)
                word_rect = word_surface.get_rect(center=(game.width // 2, y_pos + 20))
                scroll_surface.blit(word_surface, word_rect)
                
                # Correct reading
                correct_surface = game._review_reading_font.render(f"✓ {ans['correct_reading']}", True, game.correct_color)
                correct_rect = correct_surface.get_rect(center=(game.width // 2, y_pos + 45))
                scroll_surface.blit(correct_surface, correct_rect)
                
                # Your answer
                if ans['your_answer']:
                    your_surface = game._review_reading_font.render(f"✗ {ans['your_answer']}", True, game.incorrect_color)
                    your_rect = your_surface.get_rect(center=(game.width // 2 + 150, y_pos + 45))
                    scroll_surface.blit(your_surface, your_rect)
        
        game.review_cache = scroll_surface
    
    # Blit the cached scroll surface
    game.screen.blit(game.review_cache, (0, scroll_area_top))
    
    # Draw scrollbar if needed
    if total_content_height > scroll_area_height:
        scrollbar_x = game.width - 15
        scrollbar_height = max(30, int((scroll_area_height / total_content_height) * scroll_area_height))
        scrollbar_y = scroll_area_top + int((game.review_scroll / max_scroll) * (scroll_area_height - scrollbar_height))
        
        pygame.draw.rect(game.screen, game.gray_color, 
                       (scrollbar_x, scrollbar_y, 10, scrollbar_height), 
                       border_radius=5)
    
    # Back to menu button
    game.button_rect = pygame.Rect(game.width // 2 - 100, 580, 200, 50)
    button_color = game.button_hover_color if game.button_hover else game.button_color
    pygame.draw.rect(game.screen, button_color, game.button_rect, border_radius=10)
    button_surface = game.meaning_font.render("← Back to Menu", True, (255, 255, 255))
    button_text_rect = button_surface.get_rect(center=game.button_rect.center)
    game.screen.blit(button_surface, button_text_rect)
