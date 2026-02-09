"""
Game screen renderers (playing, countdown, paused, game over).
"""

import math
import random
import threading
import pygame
from config import *


def draw_countdown(game):
    """Draw the countdown screen."""
    base_color = game.bg_color
    wave = int(15 * math.sin(game.background_time * 2))
    bg_color = (
        max(0, min(255, base_color[0] + wave)),
        max(0, min(255, base_color[1] + wave)),
        max(0, min(255, base_color[2] + wave))
    )
    game.screen.fill(bg_color)
    
    # Calculate countdown
    elapsed = pygame.time.get_ticks() - game.countdown_start
    game.countdown_number = 3 - (elapsed // 1000)
    
    # Start preloading cards during countdown
    if not hasattr(game, '_countdown_preload_started') or not game._countdown_preload_started:
        game._countdown_preload_started = True
        game.loading = True
        game.fetch_thread = threading.Thread(target=game._preload_cards, daemon=True)
        game.fetch_thread.start()
        print("Started preloading cards during countdown...")
    
    if game.countdown_number <= 0:
        game._countdown_preload_started = False
        game.state = STATE_PLAYING
        # Start time attack timer
        if game.game_mode == 'time_attack':
            game.time_attack_start_time = pygame.time.get_ticks()
        game.load_next_word()
        return
    
    # Draw countdown number with pulsing effect
    pulse = 0.7 + 0.3 * math.sin(elapsed / 150)
    countdown_font = pygame.font.Font(None, int(200 * pulse))
    countdown_text = countdown_font.render(str(game.countdown_number), True, game.text_color)
    countdown_rect = countdown_text.get_rect(center=(game.width // 2, game.height // 2))
    game.screen.blit(countdown_text, countdown_rect)
    
    # Draw "Get Ready!" text
    ready_font = pygame.font.Font(None, 36)
    ready_text = ready_font.render("Get Ready!", True, game.gray_color)
    ready_rect = ready_text.get_rect(center=(game.width // 2, game.height // 2 + 100))
    game.screen.blit(ready_text, ready_rect)


def draw_game(game):
    """Draw the main game screen."""
    # Streak-based background animation
    base_color = game.bg_color
    speed_multiplier = 1.0 + (game.streak * 0.6)
    wave_intensity = 10 + (game.streak * 3)
    wave = int(wave_intensity * math.sin(game.background_time * 0.5 * speed_multiplier))
    
    # Rainbow effect at 15+ streak
    if game.streak >= 15:
        time_factor = game.background_time * 2
        r = int(127 + 127 * math.sin(time_factor))
        g = int(127 + 127 * math.sin(time_factor + 2.094))
        b = int(127 + 127 * math.sin(time_factor + 4.189))
        blend = 0.3
        bg_color = (
            max(0, min(255, int(base_color[0] * (1 - blend) + r * blend + wave))),
            max(0, min(255, int(base_color[1] * (1 - blend) + g * blend + wave))),
            max(0, min(255, int(base_color[2] * (1 - blend) + b * blend + wave)))
        )
    elif game.streak >= 10:
        bg_color = (
            max(0, min(255, base_color[0] + wave + 20)),
            max(0, min(255, base_color[1] + wave + 10)),
            max(0, min(255, base_color[2] + wave))
        )
    elif game.streak >= 5:
        bg_color = (
            max(0, min(255, base_color[0] + wave + 10)),
            max(0, min(255, base_color[1] + wave + 5)),
            max(0, min(255, base_color[2] + wave))
        )
    else:
        bg_color = (
            max(0, min(255, base_color[0] + wave)),
            max(0, min(255, base_color[1] + wave)),
            max(0, min(255, base_color[2] + wave))
        )
    game.screen.fill(bg_color)
    
    # Create surface for screen shake
    if game.screen_shake_intensity > 0:
        game_surface = pygame.Surface((game.width, game.height))
        game_surface.fill(bg_color)
        draw_target = game_surface
    else:
        draw_target = game.screen
    
    # Draw background particles
    particle_count = 5 + (game.streak * 4)
    for i in range(min(particle_count, 80)):
        base_x = (game.background_time * (30 + game.streak * 5) + i * 150) % (game.width + 100)
        base_y = (i * 47) % game.height
        offset_x = 30 * math.sin(i * 2.7)
        offset_y = 25 * math.cos(i * 3.1)
        x = base_x + offset_x
        y = base_y + offset_y
        alpha = int(50 + 30 * math.sin(game.background_time * speed_multiplier + i))
        size = 3 + (game.streak * 0.2)
        s = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*game.text_color[:3], alpha), (int(size), int(size)), int(size))
        game.screen.blit(s, (int(x), int(y)))
    
    # Draw active particles
    for particle in game.particles:
        particle.draw(draw_target)
    
    # Draw timer for time attack mode
    if game.game_mode == 'time_attack' and game.time_attack_start_time > 0:
        elapsed_time = (pygame.time.get_ticks() - game.time_attack_start_time) / 1000.0
        time_remaining = max(0, game.time_attack_duration - elapsed_time)
        
        if time_remaining > 30:
            timer_color = game.correct_color
        elif time_remaining > 10:
            timer_color = COLOR_GOLD
        else:
            timer_color = game.incorrect_color
        
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        timer_text = f"{minutes:01d}:{seconds:02d}"
        
        timer_bg = pygame.Surface((120, 50), pygame.SRCALPHA)
        timer_bg.fill((0, 0, 0, 120))
        timer_bg_rect = timer_bg.get_rect(center=(game.width // 2, 25))
        draw_target.blit(timer_bg, timer_bg_rect)
        
        timer_font = pygame.font.Font(None, 48)
        timer_surface = timer_font.render(timer_text, True, timer_color)
        timer_rect = timer_surface.get_rect(center=(game.width // 2, 25))
        draw_target.blit(timer_surface, timer_rect)
    
    # Draw pause button
    pause_color = game.button_hover_color if game.pause_button_hover else game.button_color
    pygame.draw.rect(draw_target, pause_color, game.pause_button, border_radius=5)
    pause_text = game.score_font.render("Pause", True, (255, 255, 255))
    pause_text_rect = pause_text.get_rect(center=game.pause_button.center)
    draw_target.blit(pause_text, pause_text_rect)
    
    # Draw score and points
    score_bg = pygame.Surface((250, 45), pygame.SRCALPHA)
    score_bg.fill((0, 0, 0, 100))
    draw_target.blit(score_bg, (10, 5))
    
    score_font_large = pygame.font.Font(None, 32)
    score_text = f"{game.score}/{game.total}"
    score_surface = score_font_large.render(score_text, True, game.text_color)
    draw_target.blit(score_surface, (20, 10))
    
    points_text = f"+{game.points} pts"
    points_surface = game.score_font.render(points_text, True, COLOR_GOLD)
    draw_target.blit(points_surface, (20, 35))
    
    # Draw streak
    if game.streak > 0:
        streak_bg = pygame.Surface((150, 35), pygame.SRCALPHA)
        streak_bg.fill((0, 0, 0, 120))
        streak_rect_bg = streak_bg.get_rect(center=(game.width // 2, 45))
        draw_target.blit(streak_bg, streak_rect_bg)
        
        streak_font_large = pygame.font.Font(None, 36)
        streak_text = f"{game.streak}x Streak"
        streak_color = game.correct_color if game.streak >= 5 else game.text_color
        streak_surface = streak_font_large.render(streak_text, True, streak_color)
        streak_rect = streak_surface.get_rect(center=(game.width // 2, 45))
        draw_target.blit(streak_surface, streak_rect)
        
        # Fire particles for high streaks
        if game.streak >= 5:
            from ui.particles import FireParticle
            particle_chance = min(0.3 + (game.streak * 0.05), 0.95)
            if random.random() < particle_chance:
                edge = random.randint(0, 3)
                if edge == 0:
                    fire_x = random.randint(0, game.width)
                    fire_y = 0
                elif edge == 1:
                    fire_x = game.width
                    fire_y = random.randint(0, game.height)
                elif edge == 2:
                    fire_x = random.randint(0, game.width)
                    fire_y = game.height
                else:
                    fire_x = 0
                    fire_y = random.randint(0, game.height)
                game.particles.append(FireParticle(fire_x, fire_y))
    
    # Update word zoom animation
    if not game.animating and game.input_active:
        game.word_zoom = min(1.0, game.word_zoom + 0.001)
        eased_zoom = 1.0 - math.pow(1.0 - game.word_zoom, 3)
        game.word_distance = 1.0 - (eased_zoom * 0.5)
    
    # Draw word with zoom effect
    base_size = 90
    eased_zoom = 1.0 - math.pow(1.0 - game.word_zoom, 3)
    zoom_factor = 0.2 + (eased_zoom * 0.8)
    word_size = int(base_size * zoom_factor)
    word_font_zoom = pygame.font.SysFont(game.word_font.get_name() if hasattr(game.word_font, 'get_name') else 'msgothic', word_size)
    word_surface = word_font_zoom.render(game.word_text, True, game.word_color)
    word_y = 120 + int(40 * game.word_distance)
    word_rect = word_surface.get_rect(center=(game.width // 2 + game.shake_offset, word_y))
    draw_target.blit(word_surface, word_rect)
    
    if not game.game_over:
        # Draw "Reading:" label
        label_surface = game.meaning_font.render("Reading:", True, game.text_color)
        label_rect = label_surface.get_rect(center=(game.width // 2, 280))
        draw_target.blit(label_surface, label_rect)
        
        # Draw input box
        input_rect = pygame.Rect(game.width // 2 - 150, 310, 300, 45)
        pygame.draw.rect(draw_target, (255, 255, 255), input_rect)
        pygame.draw.rect(draw_target, (0, 0, 0), input_rect, 2)
        
        # Draw input text
        display_text = game.input_text + game.composition
        input_surface = game.reading_font.render(display_text, True, (0, 0, 0))
        input_text_rect = input_surface.get_rect(center=input_rect.center)
        draw_target.blit(input_surface, input_text_rect)
        
        # Draw submit button
        game.button_rect = pygame.Rect(game.width // 2 - 150, 380, 300, 50)
        button_color = game.button_hover_color if game.button_hover else game.button_color
        pygame.draw.rect(draw_target, button_color, game.button_rect, border_radius=5)
        button_text = "Submit"
        button_surface = game.meaning_font.render(button_text, True, (255, 255, 255))
        button_text_rect = button_surface.get_rect(center=game.button_rect.center)
        draw_target.blit(button_surface, button_text_rect)
    
    # Draw meanings
    if game.meaning_text:
        game.draw_text_wrapped(game.meaning_text, game.meaning_font, game.meaning_color, 480, draw_target=draw_target)
    
    # Draw status
    if game.status_text:
        status_surface = game.meaning_font.render(game.status_text, True, game.status_color)
        status_rect = status_surface.get_rect(center=(game.width // 2, 600))
        draw_target.blit(status_surface, status_rect)
    
    # Show correct answer when incorrect
    if game.animating and game.animation_type == 'incorrect':
        if hasattr(game, 'correct_answer_text'):
            correct_label_font = pygame.font.Font(None, 32)
            correct_label = correct_label_font.render("Correct:", True, game.text_color)
            correct_label_rect = correct_label.get_rect(center=(game.width // 2, 520))
            draw_target.blit(correct_label, correct_label_rect)
            
            correct_font = pygame.font.SysFont(game.reading_font.get_name() if hasattr(game.reading_font, 'get_name') else 'msgothic', 56)
            correct_surface = correct_font.render(game.correct_answer_text, True, game.incorrect_color)
            correct_rect = correct_surface.get_rect(center=(game.width // 2, 565))
            draw_target.blit(correct_surface, correct_rect)
    
    # Full-screen flash animation
    if game.animating and game.animation_type:
        elapsed = pygame.time.get_ticks() - game.animation_start
        if elapsed < 400:
            flash_alpha = int(180 * (1.0 - elapsed / 400))
            flash_surface = pygame.Surface((game.width, game.height))
            if game.animation_type == 'correct':
                flash_surface.fill(game.correct_color)
            else:
                flash_surface.fill(game.incorrect_color)
            flash_surface.set_alpha(flash_alpha)
            draw_target.blit(flash_surface, (0, 0))
    
    # Apply screen shake
    if game.screen_shake_intensity > 0:
        game.screen.blit(game_surface, (int(game.screen_shake_x), int(game.screen_shake_y)))


def draw_paused(game):
    """Draw the pause screen."""
    # Semi-transparent overlay
    overlay = pygame.Surface((game.width, game.height))
    overlay.set_alpha(200)
    overlay.fill((20, 30, 40))
    game.screen.blit(overlay, (0, 0))
    
    # Title
    title_font = pygame.font.Font(None, 72)
    title = title_font.render("PAUSED", True, game.text_color)
    title_rect = title.get_rect(center=(game.width // 2, 120))
    game.screen.blit(title, title_rect)
    
    # Current score
    score_text = f"Score: {game.score}/{game.total}  |  Points: {game.points}"
    if game.streak > 0:
        score_text += f"  |  Streak: {game.streak}x"
    score_surface = game.meaning_font.render(score_text, True, game.gray_color)
    score_rect = score_surface.get_rect(center=(game.width // 2, 180))
    game.screen.blit(score_surface, score_rect)
    
    # Resume button
    resume_color = game.button_hover_color if game.resume_button_hover else game.button_color
    pygame.draw.rect(game.screen, resume_color, game.resume_button, border_radius=10)
    resume_text = game.meaning_font.render("▶ Resume", True, (255, 255, 255))
    resume_text_rect = resume_text.get_rect(center=game.resume_button.center)
    game.screen.blit(resume_text, resume_text_rect)
    
    # Save & Quit button
    save_quit_color = game.button_hover_color if game.save_quit_button_hover else game.correct_color
    pygame.draw.rect(game.screen, save_quit_color, game.save_quit_button, border_radius=10)
    save_quit_text = game.meaning_font.render("💾 Save & Quit", True, (255, 255, 255))
    save_quit_text_rect = save_quit_text.get_rect(center=game.save_quit_button.center)
    game.screen.blit(save_quit_text, save_quit_text_rect)
    
    # Quit button
    quit_color = game.button_hover_color if game.quit_button_hover else game.incorrect_color
    pygame.draw.rect(game.screen, quit_color, game.quit_button, border_radius=10)
    quit_text = game.meaning_font.render("← Quit to Menu", True, (255, 255, 255))
    quit_text_rect = quit_text.get_rect(center=game.quit_button.center)
    game.screen.blit(quit_text, quit_text_rect)


def draw_game_over(game):
    """Draw the game over screen."""
    game.screen.fill(game.bg_color)
    
    # Title
    title_font = pygame.font.Font(None, 64)
    title = title_font.render("Game Over!", True, game.text_color)
    title_rect = title.get_rect(center=(game.width // 2, 80))
    game.screen.blit(title, title_rect)
    
    # Final score
    if game.status_text:
        status_surface = game.meaning_font.render(game.status_text, True, game.status_color)
        status_rect = status_surface.get_rect(center=(game.width // 2, 140))
        game.screen.blit(status_surface, status_rect)
    
    # High scores
    if hasattr(game, 'high_scores') and game.high_scores:
        hs_y = 180
        hs_title = game.meaning_font.render("🏆 High Scores 🏆", True, COLOR_GOLD)
        game.screen.blit(hs_title, hs_title.get_rect(center=(game.width // 2, hs_y)))
        
        # Get appropriate high scores list
        if game.game_mode == 'time_attack':
            scores_list = game.high_scores.get('time_attack', [])
        else:
            scores_list = game.high_scores.get('normal', [])
        
        for i, hs in enumerate(scores_list[:3], 1):
            hs_text = f"{i}. {hs['points']} pts ({hs['percentage']}%) - {hs['date']}"
            hs_surface = game.meaning_font.render(hs_text, True, game.text_color)
            hs_rect = hs_surface.get_rect(center=(game.width // 2, hs_y + 25 + i * 25))
            game.screen.blit(hs_surface, hs_rect)
    
    # Back to menu button
    game.button_rect = pygame.Rect(game.width // 2 - 100, 380, 200, 50)
    button_color = game.button_hover_color if game.button_hover else game.button_color
    pygame.draw.rect(game.screen, button_color, game.button_rect, border_radius=10)
    button_surface = game.meaning_font.render("← Back to Menu", True, (255, 255, 255))
    button_text_rect = button_surface.get_rect(center=game.button_rect.center)
    game.screen.blit(button_surface, button_text_rect)
