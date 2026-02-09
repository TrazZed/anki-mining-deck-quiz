"""
Scoring system and leaderboard management.
"""

import csv
import os
from datetime import datetime
from config import (
    SCORES_FILE, 
    POINTS_UNDER_2_SEC, 
    POINTS_UNDER_4_SEC,
    POINTS_UNDER_6_SEC,
    POINTS_UNDER_10_SEC,
    POINTS_OVER_10_SEC,
    MAX_STREAK_MULTIPLIER,
    STREAK_MULTIPLIER_STEP
)


def calculate_points(time_taken, streak):
    """
    Calculate points based on answer speed and current streak.
    
    Args:
        time_taken: Time in seconds to answer the question
        streak: Current streak count
        
    Returns:
        Tuple of (points_earned, base_points, streak_multiplier)
    """
    # Calculate base points based on speed
    if time_taken < 2:
        base_points = POINTS_UNDER_2_SEC
    elif time_taken < 4:
        base_points = POINTS_UNDER_4_SEC
    elif time_taken < 6:
        base_points = POINTS_UNDER_6_SEC
    elif time_taken < 10:
        base_points = POINTS_UNDER_10_SEC
    else:
        base_points = POINTS_OVER_10_SEC
    
    # Apply streak multiplier (1.0x to max based on streak)
    streak_multiplier = min(1.0 + (streak - 1) * STREAK_MULTIPLIER_STEP, MAX_STREAK_MULTIPLIER)
    points_earned = int(base_points * streak_multiplier)
    
    return points_earned, base_points, streak_multiplier


def save_score_to_csv(score, total, points, percentage, avg_points, mode='normal'):
    """
    Save the game score to a CSV file.
    
    Args:
        score: Number of correct answers
        total: Total number of questions
        points: Total points earned
        percentage: Percentage score
        avg_points: Average points per card
        mode: Game mode (normal, fast, time_attack)
    """
    file_exists = os.path.isfile(SCORES_FILE)
    
    with open(SCORES_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['date', 'time', 'score', 'total', 'percentage', 'points', 'avg_points', 'mode']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        now = datetime.now()
        writer.writerow({
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'score': score,
            'total': total,
            'percentage': percentage,
            'points': points,
            'avg_points': avg_points,
            'mode': mode
        })


def get_high_scores():
    """
    Get the top 5 high scores from CSV, separated by mode.
    
    Returns:
        Dict with 'normal' and 'time_attack' keys, each containing list of top 5 scores
    """
    if not os.path.isfile(SCORES_FILE):
        return {'normal': [], 'time_attack': []}
    
    normal_scores = []
    time_attack_scores = []
    
    with open(SCORES_FILE, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            score_data = {
                'date': row['date'],
                'points': int(row['points']),
                'percentage': int(row['percentage']),
                'score': int(row['score']),
                'total': int(row['total'])
            }
            # Handle old CSV files without mode column
            mode = row.get('mode', 'normal')
            if mode == 'time_attack':
                time_attack_scores.append(score_data)
            else:
                normal_scores.append(score_data)
    
    # Sort by points descending
    normal_scores.sort(key=lambda x: x['points'], reverse=True)
    time_attack_scores.sort(key=lambda x: x['points'], reverse=True)
    
    return {
        'normal': normal_scores[:5],
        'time_attack': time_attack_scores[:5]
    }
