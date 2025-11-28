# ============================================================================
# LEVELUP LIFE - CUSTOM TOOLS
# Tools used by agents for quest generation, XP calculation, and more
# ============================================================================

"""
This module contains custom tools that agents use to perform their tasks:
1. XP Calculator - Calculates XP and stat rewards
2. Rank Progression Calculator - Determines rank based on total XP
3. Quest Generator Helper - Generates quest details
4. Quote Selector - Selects contextually appropriate quotes
5. Streak Tracker - Manages user streaks
"""

from crewai.tools import tool
from typing import Dict, List, Any
import random
from datetime import datetime

# ============================================================================
# TOOL 1: XP CALCULATOR
# ============================================================================

@tool("xp_calculator")
def calculate_xp_and_stats(
    domain: str,
    difficulty: str,
    bonus_multiplier: float = 1.0
) -> Dict[str, Any]:
    """
    Calculate XP reward and stat increases for completing a quest.
    
    Args:
        domain: Quest domain (fitness, productivity, learning)
        difficulty: Quest difficulty (easy, medium, hard)
        bonus_multiplier: Bonus multiplier for streaks or special achievements
    
    Returns:
        Dictionary with xp_reward and stat_rewards
    """
    # Base XP from config
    base_xp = Config.XP_REWARDS.get(domain, {}).get(difficulty, 50)
    xp_reward = int(base_xp * bonus_multiplier)
    
    # Calculate stat increases based on domain
    stat_rewards = {}
    relevant_stats = Config.STAT_MAPPING.get(domain, [])
    
    # Distribute stat points based on difficulty
    stat_points = {
        'easy': 2,
        'medium': 5,
        'hard': 10
    }.get(difficulty, 2)
    
    for stat in relevant_stats:
        # Primary stat gets more points
        if stat == relevant_stats[0]:
            stat_rewards[stat] = stat_points
        else:
            stat_rewards[stat] = max(1, stat_points // 2)
    
    return {
        'xp_reward': xp_reward,
        'stat_rewards': stat_rewards,
        'base_xp': base_xp,
        'multiplier_applied': bonus_multiplier
    }

# ============================================================================
# TOOL 2: RANK PROGRESSION CALCULATOR
# ============================================================================

@tool("rank_calculator")
def calculate_rank_and_level(total_xp: int) -> Dict[str, Any]:
    """
    Calculate user's rank and level based on total XP.
    
    Args:
        total_xp: User's total accumulated XP
    
    Returns:
        Dictionary with rank, level, and progress to next rank
    """
    # Determine rank
    current_rank = 'E'
    next_rank = 'D'
    xp_for_next_rank = Config.RANK_THRESHOLDS['D']
    
    for rank in Config.RANKS:
        if total_xp >= Config.RANK_THRESHOLDS[rank]:
            current_rank = rank
            # Find next rank
            rank_index = Config.RANKS.index(rank)
            if rank_index < len(Config.RANKS) - 1:
                next_rank = Config.RANKS[rank_index + 1]
                xp_for_next_rank = Config.RANK_THRESHOLDS[next_rank]
            else:
                next_rank = 'MAX'
                xp_for_next_rank = total_xp
    
    # Calculate level (every 500 XP = 1 level)
    level = max(1, total_xp // 500 + 1)
    
    # Calculate progress percentage
    if next_rank != 'MAX':
        current_rank_threshold = Config.RANK_THRESHOLDS[current_rank]
        xp_in_current_rank = total_xp - current_rank_threshold
        xp_needed_for_next = xp_for_next_rank - current_rank_threshold
        progress_percentage = (xp_in_current_rank / xp_needed_for_next) * 100
    else:
        progress_percentage = 100.0
    
    return {
        'rank': current_rank,
        'level': level,
        'next_rank': next_rank,
        'xp_to_next_rank': max(0, xp_for_next_rank - total_xp),
        'progress_percentage': round(progress_percentage, 1)
    }

# ============================================================================
# TOOL 3: QUEST DIFFICULTY ADJUSTER
# ============================================================================

@tool("difficulty_adjuster")
def adjust_quest_difficulty(
    user_level: int,
    completion_rate: float,
    current_streak: int,
    domain: str
) -> Dict[str, Any]:
    """
    Determine appropriate quest difficulty based on user performance.
    
    Args:
        user_level: User's current level
        completion_rate: Recent completion rate (0.0 to 1.0)
        current_streak: Current active streak
        domain: Domain for the quest
    
    Returns:
        Dictionary with recommended difficulty and reasoning
    """
    # Start with base difficulty based on level
    if user_level < 5:
        base_difficulty = 'easy'
    elif user_level < 15:
        base_difficulty = 'medium'
    else:
        base_difficulty = 'hard'
    
    # Adjust based on completion rate
    if completion_rate < 0.5:
        # User is struggling, reduce difficulty
        difficulty = 'easy'
        reasoning = "Reducing difficulty to build confidence"
    elif completion_rate > 0.8 and current_streak > 5:
        # User is excelling, increase challenge
        if base_difficulty == 'easy':
            difficulty = 'medium'
        elif base_difficulty == 'medium':
            difficulty = 'hard'
        else:
            difficulty = 'hard'
        reasoning = "Increasing challenge based on strong performance"
    else:
        difficulty = base_difficulty
        reasoning = "Maintaining current difficulty level"
    
    # Calculate recommended quest distribution
    quest_distribution = {
        'easy': 2,
        'medium': 2,
        'hard': 1
    }
    
    if difficulty == 'easy':
        quest_distribution = {'easy': 3, 'medium': 1, 'hard': 0}
    elif difficulty == 'hard' and current_streak > 10:
        quest_distribution = {'easy': 1, 'medium': 2, 'hard': 2}
    
    return {
        'recommended_difficulty': difficulty,
        'reasoning': reasoning,
        'quest_distribution': quest_distribution,
        'challenge_level': 'appropriate'
    }

# ============================================================================
# TOOL 4: CONTEXTUAL QUOTE SELECTOR
# ============================================================================

@tool("quote_selector")
def select_motivational_quote(
    domain: str,
    context_tags: List[str],
    mindset_profile: List[str],
    activity_level: str,
    time_of_day: str = "morning"
) -> Dict[str, str]:
    """
    Select a contextually appropriate motivational quote.
    
    Args:
        domain: Current domain (fitness, productivity, learning)
        context_tags: Context tags (e.g., 'starting', 'struggling', 'streak')
        mindset_profile: User's mindset types
        activity_level: User's activity level
        time_of_day: Current time context
    
    Returns:
        Dictionary with quote text and metadata
    """
    # Convert string inputs to proper enums
    domain_enum = Domain[domain.upper()]
    mindset_enums = [MindsetType[m.upper()] for m in mindset_profile if m.upper() in MindsetType.__members__]
    
    # Get quote from database
    quote = quote_db.get_contextual_quote(
        domain=domain_enum,
        context_tags=context_tags,
        mindset_types=mindset_enums,
        activity_level=activity_level,
        time_of_day=time_of_day
    )
    
    if quote:
        return {
            'quote_text': quote.quote_text,
            'intensity': quote.intensity,
            'relevance_reason': f"Selected for {domain} context with tags: {', '.join(context_tags)}"
        }
    else:
        # Fallback quote
        return {
            'quote_text': "Every day is a new opportunity to level up.",
            'intensity': "moderate",
            'relevance_reason': "Default motivational quote"
        }

# ============================================================================
# TOOL 5: STREAK TRACKER
# ============================================================================

@tool("streak_tracker")
def track_and_update_streak(
    last_completion_date: str,
    current_streak: int,
    longest_streak: int
) -> Dict[str, Any]:
    """
    Track user streaks and determine if streak continues or breaks.
    
    Args:
        last_completion_date: ISO format date string of last completion
        current_streak: Current active streak count
        longest_streak: User's longest streak record
    
    Returns:
        Dictionary with updated streak information
    """
    today = datetime.now().date()
    last_date = datetime.fromisoformat(last_completion_date).date()
    days_since_last = (today - last_date).days
    
    if days_since_last == 0:
        # Same day completion
        streak_status = "maintained"
        new_streak = current_streak
        message = "Quest completed today! Streak maintained."
    elif days_since_last == 1:
        # Consecutive day
        streak_status = "increased"
        new_streak = current_streak + 1
        message = f"🔥 Streak increased to {new_streak} days!"
    else:
        # Streak broken
        streak_status = "broken"
        new_streak = 1
        message = f"Streak reset. Don't worry, start fresh today!"
    
    # Check if new record
    new_longest = max(longest_streak, new_streak)
    is_record = new_longest > longest_streak
    
    return {
        'current_streak': new_streak,
        'longest_streak': new_longest,
        'streak_status': streak_status,
        'is_record': is_record,
        'message': message,
        'days_since_last': days_since_last
    }

# ============================================================================
# TOOL 6: QUEST GENERATOR HELPER
# ============================================================================

@tool("quest_generator_helper")
def generate_quest_ideas(
    domain: str,
    difficulty: str,
    user_goals: List[str],
    user_level: int
) -> List[Dict[str, str]]:
    """
    Generate quest ideas based on domain, difficulty, and user goals.
    
    Args:
        domain: Quest domain
        difficulty: Difficulty level
        user_goals: User's stated goals for this domain
        user_level: User's current level
    
    Returns:
        List of quest idea dictionaries
    """
    quest_templates = {
        'fitness': {
            'easy': [
                {'title': '10-Minute Morning Stretch', 'duration': '10 min'},
                {'title': '15-Minute Walk', 'duration': '15 min'},
                {'title': 'Drink 8 Glasses of Water', 'duration': 'All day'},
                {'title': '5-Minute Meditation', 'duration': '5 min'}
            ],
            'medium': [
                {'title': '30-Minute Workout Session', 'duration': '30 min'},
                {'title': 'Complete 50 Push-ups (Throughout Day)', 'duration': 'All day'},
                {'title': '45-Minute Cardio Activity', 'duration': '45 min'},
                {'title': 'Yoga Flow Practice', 'duration': '30 min'}
            ],
            'hard': [
                {'title': 'High-Intensity Interval Training', 'duration': '45 min'},
                {'title': 'Complete 100 Burpees', 'duration': '30 min'},
                {'title': 'Advanced Strength Training', 'duration': '60 min'},
                {'title': 'Run 5 Kilometers', 'duration': '40 min'}
            ]
        },
        'productivity': {
            'easy': [
                {'title': 'Plan Tomorrow\'s Top 3 Tasks', 'duration': '10 min'},
                {'title': 'Organize Email Inbox', 'duration': '15 min'},
                {'title': 'Clean Workspace', 'duration': '10 min'},
                {'title': '25-Minute Focused Work Session', 'duration': '25 min'}
            ],
            'medium': [
                {'title': 'Complete Important Project Task', 'duration': '90 min'},
                {'title': 'Two 90-Minute Deep Work Blocks', 'duration': '180 min'},
                {'title': 'Finish Week\'s Priority Task', 'duration': '120 min'},
                {'title': 'Review and Optimize Workflow', 'duration': '45 min'}
            ],
            'hard': [
                {'title': 'Ship Major Project Milestone', 'duration': '240 min'},
                {'title': 'Complete Full Day Deep Work', 'duration': '480 min'},
                {'title': 'Launch New Initiative', 'duration': '360 min'},
                {'title': 'Tackle Challenging Problem', 'duration': '180 min'}
            ]
        },
        'learning': {
            'easy': [
                {'title': 'Read 10 Pages of Educational Book', 'duration': '20 min'},
                {'title': 'Watch Educational Video', 'duration': '15 min'},
                {'title': 'Practice New Skill for 15 Minutes', 'duration': '15 min'},
                {'title': 'Review Previous Learnings', 'duration': '10 min'}
            ],
            'medium': [
                {'title': 'Complete Online Course Module', 'duration': '60 min'},
                {'title': 'Practice Skill for 1 Hour', 'duration': '60 min'},
                {'title': 'Read Research Paper or Article', 'duration': '45 min'},
                {'title': 'Work on Learning Project', 'duration': '90 min'}
            ],
            'hard': [
                {'title': 'Complete Comprehensive Course Section', 'duration': '180 min'},
                {'title': 'Build Project Using New Skill', 'duration': '240 min'},
                {'title': 'Master Complex Concept', 'duration': '150 min'},
                {'title': 'Teach Someone What You Learned', 'duration': '120 min'}
            ]
        }
    }
    
    # Get templates for this domain and difficulty
    templates = quest_templates.get(domain, {}).get(difficulty, [])
    
    # Return 2-3 random quest ideas
    num_quests = min(3, len(templates))
    selected = random.sample(templates, num_quests)
    
    return selected

# ============================================================================
# TOOL 7: ACHIEVEMENT CHECKER
# ============================================================================

@tool("achievement_checker")
def check_achievements(
    user_profile_data: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Check if user has earned any new achievements.
    
    Args:
        user_profile_data: Dictionary containing user profile information
    
    Returns:
        List of newly earned achievements
    """
    new_achievements = []
    total_quests = user_profile_data.get('total_quests_completed', 0)
    current_streak = user_profile_data.get('current_streak', 0)
    total_xp = user_profile_data.get('total_xp', 0)
    
    # Quest milestone achievements
    if total_quests == 10:
        new_achievements.append({
            'name': 'Getting Started',
            'description': 'Completed 10 quests',
            'icon': '🎯'
        })
    elif total_quests == 50:
        new_achievements.append({
            'name': 'Quest Master',
            'description': 'Completed 50 quests',
            'icon': '⚔️'
        })
    elif total_quests == 100:
        new_achievements.append({
            'name': 'Legendary Adventurer',
            'description': 'Completed 100 quests',
            'icon': '👑'
        })
    
    # Streak achievements
    if current_streak == 7:
        new_achievements.append({
            'name': 'Week Warrior',
            'description': '7-day streak',
            'icon': '🔥'
        })
    elif current_streak == 30:
        new_achievements.append({
            'name': 'Monthly Master',
            'description': '30-day streak',
            'icon': '💪'
        })
    
    # XP achievements
    if total_xp >= 10000:
        new_achievements.append({
            'name': 'XP Collector',
            'description': 'Earned 10,000 XP',
            'icon': '⭐'
        })
    
    return new_achievements

# ============================================================================
# TOOLS REGISTRATION
# ============================================================================

# List of all available tools for agents
AVAILABLE_TOOLS = [
    calculate_xp_and_stats,
    calculate_rank_and_level,
    adjust_quest_difficulty,
    select_motivational_quote,
    track_and_update_streak,
    generate_quest_ideas,
    check_achievements
]

print("✅ Custom tools initialized!")
print(f"📦 {len(AVAILABLE_TOOLS)} tools available for agents")
print("\nAvailable Tools:")
for i, tool in enumerate(AVAILABLE_TOOLS, 1):
    print(f"   {i}. {tool.name}")