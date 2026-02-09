"""
Menu screen renderers.
"""

import math
import pygame
from config import *


def draw_menu(game):
    """Draw the main menu."""
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
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("Japanese Vocab Quiz", True, game.text_color)
    title_rect = title.get_rect(center=(game.width // 2, 100))
    game.screen.blit(title, title_rect)
    
    # Subtitle (using Japanese-capable font)
    subtitle_font = pygame.font.SysFont(game.reading_font.get_name() if hasattr(game.reading_font, 'get_name') else 'msgothic', 20)
    subtitle = subtitle_font.render("日本語語彙クイズ", True, game.gray_color)
    subtitle_rect = subtitle.get_rect(center=(game.width // 2, 140))
    game.screen.blit(subtitle, subtitle_rect)
    
    # Play button
    play_color = game.button_hover_color if game.play_button_hover else game.button_color
    pygame.draw.rect(game.screen, play_color, game.play_button, border_radius=10)
    play_text = game.meaning_font.render("Play", True, (255, 255, 255))
    play_text_rect = play_text.get_rect(center=game.play_button.center)
    game.screen.blit(play_text, play_text_rect)
    
    # Resume Game button (only if save file exists)
    if game.has_save_file():
        resume_color = game.button_hover_color if game.resume_game_button_hover else game.correct_color
        pygame.draw.rect(game.screen, resume_color, game.resume_game_button, border_radius=10)
        resume_text = game.meaning_font.render("▶ Resume Game", True, (255, 255, 255))
        resume_text_rect = resume_text.get_rect(center=game.resume_game_button.center)
        game.screen.blit(resume_text, resume_text_rect)
    
    # Leaderboard button
    lb_color = game.button_hover_color if game.leaderboard_button_hover else game.button_color
    pygame.draw.rect(game.screen, lb_color, game.leaderboard_button, border_radius=10)
    lb_text = game.meaning_font.render("🏆 Leaderboard", True, (255, 255, 255))
    lb_text_rect = lb_text.get_rect(center=game.leaderboard_button.center)
    game.screen.blit(lb_text, lb_text_rect)


def draw_mode_select(game):
    """Draw the mode selection screen."""
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
    title = title_font.render("Select Game Mode", True, game.text_color)
    title_rect = title.get_rect(center=(game.width // 2, 120))
    game.screen.blit(title, title_rect)
    
    # Normal mode button
    normal_color = game.button_hover_color if game.normal_mode_hover else game.button_color
    pygame.draw.rect(game.screen, normal_color, game.normal_mode_button, border_radius=10)
    normal_title = pygame.font.Font(None, 36).render("Normal", True, (255, 255, 255))
    normal_title_rect = normal_title.get_rect(center=(game.normal_mode_button.centerx, game.normal_mode_button.centery - 15))
    game.screen.blit(normal_title, normal_title_rect)
    normal_desc = game.score_font.render("Full animations", True, (255, 255, 255))
    normal_desc_rect = normal_desc.get_rect(center=(game.normal_mode_button.centerx, game.normal_mode_button.centery + 10))
    game.screen.blit(normal_desc, normal_desc_rect)
    normal_desc2 = game.score_font.render("& feedback", True, (255, 255, 255))
    normal_desc2_rect = normal_desc2.get_rect(center=(game.normal_mode_button.centerx, game.normal_mode_button.centery + 28))
    game.screen.blit(normal_desc2, normal_desc2_rect)
    
    # Fast mode button
    fast_color = game.button_hover_color if game.fast_mode_hover else game.correct_color
    pygame.draw.rect(game.screen, fast_color, game.fast_mode_button, border_radius=10)
    fast_title = pygame.font.Font(None, 36).render("Fast", True, (255, 255, 255))
    fast_title_rect = fast_title.get_rect(center=(game.fast_mode_button.centerx, game.fast_mode_button.centery - 15))
    game.screen.blit(fast_title, fast_title_rect)
    fast_desc = game.score_font.render("No animations", True, (255, 255, 255))
    fast_desc_rect = fast_desc.get_rect(center=(game.fast_mode_button.centerx, game.fast_mode_button.centery + 10))
    game.screen.blit(fast_desc, fast_desc_rect)
    fast_desc2 = game.score_font.render("Instant next word", True, (255, 255, 255))
    fast_desc2_rect = fast_desc2.get_rect(center=(game.fast_mode_button.centerx, game.fast_mode_button.centery + 28))
    game.screen.blit(fast_desc2, fast_desc2_rect)
    
    # Time Attack mode button
    time_attack_color = game.button_hover_color if game.time_attack_hover else COLOR_ORANGE
    pygame.draw.rect(game.screen, time_attack_color, game.time_attack_button, border_radius=10)
    ta_title = pygame.font.Font(None, 36).render("⏱ Time Attack", True, (255, 255, 255))
    ta_title_rect = ta_title.get_rect(center=(game.time_attack_button.centerx, game.time_attack_button.centery - 15))
    game.screen.blit(ta_title, ta_title_rect)
    ta_desc = game.score_font.render("60 seconds", True, (255, 255, 255))
    ta_desc_rect = ta_desc.get_rect(center=(game.time_attack_button.centerx, game.time_attack_button.centery + 10))
    game.screen.blit(ta_desc, ta_desc_rect)
    ta_desc2 = game.score_font.render("Get as many as you can!", True, (255, 255, 255))
    ta_desc2_rect = ta_desc2.get_rect(center=(game.time_attack_button.centerx, game.time_attack_button.centery + 28))
    game.screen.blit(ta_desc2, ta_desc2_rect)
    
    # Back button
    back_color = game.button_hover_color if game.back_button_hover else game.status_color
    pygame.draw.rect(game.screen, back_color, game.back_button, border_radius=10)
    back_text = game.meaning_font.render("← Back", True, (255, 255, 255))
    back_text_rect = back_text.get_rect(center=game.back_button.center)
    game.screen.blit(back_text, back_text_rect)
