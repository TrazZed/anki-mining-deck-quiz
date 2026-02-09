"""
Leaderboard screen renderer.
"""

import pygame
from config import *


def draw_leaderboard(game):
    """Draw the leaderboard screen with two sections."""
    game.screen.fill(game.bg_color)
    
    # Title
    title_font = pygame.font.Font(None, 48)
    title = title_font.render("Leaderboard", True, COLOR_GOLD)
    title_rect = title.get_rect(center=(game.width // 2, 40))
    game.screen.blit(title, title_rect)
    
    # Get high scores
    if not game.high_scores:
        from game import get_high_scores
        game.high_scores = get_high_scores()
    
    # Left section - Normal/Fast Mode
    left_x = 50
    section_title_font = pygame.font.Font(None, 32)
    
    normal_title = section_title_font.render("Normal / Fast Mode", True, game.button_color)
    normal_title_rect = normal_title.get_rect(x=left_x, y=90)
    game.screen.blit(normal_title, normal_title_rect)
    
    normal_scores = game.high_scores.get('normal', [])
    if normal_scores:
        y_start = 130
        for i, hs in enumerate(normal_scores[:5], 1):
            rank_color = game.correct_color if i <= 3 else game.text_color
            rank_text = f"{i}."
            rank_surface = game.score_font.render(rank_text, True, rank_color)
            game.screen.blit(rank_surface, (left_x, y_start + i * 45))
            
            score_text = f"{hs['points']} pts | {hs['percentage']}%"
            score_surface = game.score_font.render(score_text, True, game.text_color)
            game.screen.blit(score_surface, (left_x + 30, y_start + i * 45))
            
            date_text = f"{hs['date']}"
            date_surface = game.score_font.render(date_text, True, game.gray_color)
            game.screen.blit(date_surface, (left_x + 30, y_start + i * 45 + 18))
    else:
        no_scores = game.score_font.render("No scores yet!", True, game.gray_color)
        game.screen.blit(no_scores, (left_x, 150))
    
    # Right section - Time Attack Mode
    right_x = game.width // 2 + 20
    
    ta_title = section_title_font.render("⏱ Time Attack", True, COLOR_ORANGE)
    ta_title_rect = ta_title.get_rect(x=right_x, y=90)
    game.screen.blit(ta_title, ta_title_rect)
    
    time_attack_scores = game.high_scores.get('time_attack', [])
    if time_attack_scores:
        y_start = 130
        for i, hs in enumerate(time_attack_scores[:5], 1):
            rank_color = game.correct_color if i <= 3 else game.text_color
            rank_text = f"{i}."
            rank_surface = game.score_font.render(rank_text, True, rank_color)
            game.screen.blit(rank_surface, (right_x, y_start + i * 45))
            
            score_text = f"{hs['score']}/{hs['total']} | {hs['points']} pts"
            score_surface = game.score_font.render(score_text, True, game.text_color)
            game.screen.blit(score_surface, (right_x + 30, y_start + i * 45))
            
            date_text = f"{hs['date']}"
            date_surface = game.score_font.render(date_text, True, game.gray_color)
            game.screen.blit(date_surface, (right_x + 30, y_start + i * 45 + 18))
    else:
        no_scores = game.score_font.render("No scores yet!", True, game.gray_color)
        game.screen.blit(no_scores, (right_x, 150))
    
    # Back button
    back_color = game.button_hover_color if game.back_button_hover else game.button_color
    pygame.draw.rect(game.screen, back_color, game.back_button, border_radius=10)
    back_text = game.meaning_font.render("← Back to Menu", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=game.back_button.center)
    game.screen.blit(back_text, back_text_rect)
