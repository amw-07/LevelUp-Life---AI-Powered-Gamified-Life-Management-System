# ============================================================================
# LEVELUP LIFE - AI-Powered Gamified Life Management System
# Kaggle Capstone Project - Agents Intensive
# Track: Concierge Agents
# ============================================================================

"""
PROJECT OVERVIEW:
An AI-powered multi-agent system that transforms real-life tasks across fitness,
productivity, and learning into an RPG-style progression system with personalized
quests, XP tracking, rank advancement, and context-aware motivational coaching.

ARCHITECTURE:
- 5 Specialized CrewAI Agents
- Custom Tools for XP calculation, quest generation, quote selection
- Memory system for user context and progression
- React UI for interactive demo
"""

# ============================================================================
# SECTION 1: DEPENDENCIES & INSTALLATION
# ============================================================================

# Install required packages
import sys
import subprocess

def install_packages():
    """Install all required packages for the project"""
    packages = [
        'crewai>=0.28.0',
        'crewai-tools',
        'langchain',
        'langchain-google-genai',
        'google-generativeai',
        'chromadb',
        'pydantic',
        'python-dotenv'
    ]
    
    print("📦 Installing dependencies...")
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])
    print("✅ All dependencies installed successfully!\n")

# Uncomment the line below when running in Kaggle notebook
# install_packages()

# ============================================================================
# SECTION 2: IMPORTS
# ============================================================================

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
import random

# CrewAI imports
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

# Pydantic for data validation
from pydantic import BaseModel, Field

print("✅ All imports successful!")

# ============================================================================
# SECTION 3: CONFIGURATION & CONSTANTS
# ============================================================================

class Config:
    """Central configuration for the LevelUp Life system"""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
    MODEL_NAME = "gemini-1.5-pro"
    
    # Game Mechanics
    RANKS = ['E', 'D', 'C', 'B', 'A', 'S', 'SS']
    RANK_THRESHOLDS = {
        'E': 0,
        'D': 1000,
        'C': 5000,
        'B': 15000,
        'A': 35000,
        'S': 70000,
        'SS': 150000
    }
    
    # XP Rewards by Domain
    XP_REWARDS = {
        'fitness': {'easy': 50, 'medium': 100, 'hard': 200},
        'productivity': {'easy': 40, 'medium': 90, 'hard': 180},
        'learning': {'easy': 60, 'medium': 120, 'hard': 240}
    }
    
    # Domain Stats
    STAT_MAPPING = {
        'fitness': ['Strength', 'Vitality', 'Endurance'],
        'productivity': ['Focus', 'Efficiency', 'Execution'],
        'learning': ['Intelligence', 'Creativity', 'Wisdom']
    }

print("⚙️ Configuration loaded!")

# ============================================================================
# SECTION 4: DATA MODELS
# ============================================================================

class DifficultyLevel(str, Enum):
    """Quest difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Domain(str, Enum):
    """Life domains for quest categorization"""
    FITNESS = "fitness"
    PRODUCTIVITY = "productivity"
    LEARNING = "learning"

class MindsetType(str, Enum):
    """User mindset categories for personalization"""
    GROWTH = "growth"
    DISCIPLINE = "discipline"
    ACHIEVEMENT = "achievement"
    EXPLORATION = "exploration"
    PERSISTENCE = "persistence"

@dataclass
class UserProfile:
    """User profile data model"""
    user_id: str
    name: str
    level: int = 1
    total_xp: int = 0
    rank: str = 'E'
    
    # Domain-specific stats (0-100 scale)
    strength: int = 10
    vitality: int = 10
    endurance: int = 10
    focus: int = 10
    efficiency: int = 10
    execution: int = 10
    intelligence: int = 10
    creativity: int = 10
    wisdom: int = 10
    
    # User preferences and context
    goals: Dict[str, List[str]] = field(default_factory=dict)
    mindset_profile: List[MindsetType] = field(default_factory=list)
    work_style: str = "balanced"
    activity_level: str = "intermediate"
    preferred_times: Dict[str, str] = field(default_factory=dict)
    
    # Progress tracking
    current_streak: int = 0
    longest_streak: int = 0
    total_quests_completed: int = 0
    quests_by_domain: Dict[str, int] = field(default_factory=lambda: {
        'fitness': 0, 'productivity': 0, 'learning': 0
    })
    achievements: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_active: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Quest:
    """Quest data model"""
    quest_id: str
    title: str
    description: str
    domain: Domain
    difficulty: DifficultyLevel
    xp_reward: int
    stat_rewards: Dict[str, int]
    
    # Quest metadata
    estimated_duration: str
    context_tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Completion tracking
    is_completed: bool = False
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert quest to dictionary"""
        return {
            'quest_id': self.quest_id,
            'title': self.title,
            'description': self.description,
            'domain': self.domain.value,
            'difficulty': self.difficulty.value,
            'xp_reward': self.xp_reward,
            'stat_rewards': self.stat_rewards,
            'estimated_duration': self.estimated_duration,
            'context_tags': self.context_tags,
            'is_completed': self.is_completed
        }

@dataclass
class MotivationalQuote:
    """Motivational quote with context metadata"""
    quote_text: str
    domains: List[Domain]
    context_tags: List[str]
    intensity: str  # soft, moderate, intense
    time_context: List[str]  # morning, afternoon, evening
    mindset_types: List[MindsetType]
    activity_levels: List[str]  # beginner, intermediate, advanced

@dataclass
class ProgressReport:
    """User progress report"""
    user_id: str
    report_date: str
    
    # Summary stats
    quests_completed_this_period: int
    xp_gained_this_period: int
    current_streak: int
    
    # Domain breakdown
    domain_breakdown: Dict[str, Dict[str, Any]]
    
    # Insights
    top_performing_domain: str
    areas_for_improvement: List[str]
    recommended_actions: List[str]
    
    # Motivational content
    personalized_message: str
    selected_quote: str

print("📊 Data models defined!")

# ============================================================================
# SECTION 5: QUOTE DATABASE
# ============================================================================

class QuoteDatabase:
    """Manages the motivational quote database"""
    
    def __init__(self):
        self.quotes = self._initialize_quotes()
    
    def _initialize_quotes(self) -> List[MotivationalQuote]:
        """Initialize curated quote database"""
        quotes = [
            # Fitness - Discipline & Consistency
            MotivationalQuote(
                quote_text="The body achieves what the mind believes.",
                domains=[Domain.FITNESS],
                context_tags=["starting", "motivation", "mindset"],
                intensity="moderate",
                time_context=["morning", "afternoon"],
                mindset_types=[MindsetType.GROWTH, MindsetType.DISCIPLINE],
                activity_levels=["beginner", "intermediate"]
            ),
            MotivationalQuote(
                quote_text="Consistency is the key to unlocking your potential.",
                domains=[Domain.FITNESS, Domain.PRODUCTIVITY, Domain.LEARNING],
                context_tags=["consistency", "habits", "daily_practice"],
                intensity="soft",
                time_context=["morning", "evening"],
                mindset_types=[MindsetType.DISCIPLINE, MindsetType.PERSISTENCE],
                activity_levels=["beginner", "intermediate", "advanced"]
            ),
            MotivationalQuote(
                quote_text="Your only limit is the one you set for yourself.",
                domains=[Domain.FITNESS, Domain.LEARNING],
                context_tags=["breakthrough", "pushing_limits", "growth"],
                intensity="intense",
                time_context=["afternoon"],
                mindset_types=[MindsetType.GROWTH, MindsetType.ACHIEVEMENT],
                activity_levels=["intermediate", "advanced"]
            ),
            
            # Productivity - Focus & Execution
            MotivationalQuote(
                quote_text="Focus on being productive instead of busy.",
                domains=[Domain.PRODUCTIVITY],
                context_tags=["focus", "efficiency", "time_management"],
                intensity="moderate",
                time_context=["morning", "afternoon"],
                mindset_types=[MindsetType.DISCIPLINE, MindsetType.ACHIEVEMENT],
                activity_levels=["intermediate", "advanced"]
            ),
            MotivationalQuote(
                quote_text="Small daily improvements lead to stunning results.",
                domains=[Domain.PRODUCTIVITY, Domain.LEARNING],
                context_tags=["incremental", "consistency", "progress"],
                intensity="soft",
                time_context=["morning", "evening"],
                mindset_types=[MindsetType.GROWTH, MindsetType.PERSISTENCE],
                activity_levels=["beginner", "intermediate"]
            ),
            MotivationalQuote(
                quote_text="Execution is the bridge between goals and accomplishment.",
                domains=[Domain.PRODUCTIVITY],
                context_tags=["action", "execution", "results"],
                intensity="intense",
                time_context=["morning", "afternoon"],
                mindset_types=[MindsetType.ACHIEVEMENT, MindsetType.DISCIPLINE],
                activity_levels=["intermediate", "advanced"]
            ),
            
            # Learning - Growth & Mastery
            MotivationalQuote(
                quote_text="Learning is a treasure that follows its owner everywhere.",
                domains=[Domain.LEARNING],
                context_tags=["value_of_learning", "wisdom", "growth"],
                intensity="soft",
                time_context=["morning", "afternoon", "evening"],
                mindset_types=[MindsetType.GROWTH, MindsetType.EXPLORATION],
                activity_levels=["beginner", "intermediate", "advanced"]
            ),
            MotivationalQuote(
                quote_text="The expert in anything was once a beginner.",
                domains=[Domain.LEARNING, Domain.FITNESS],
                context_tags=["starting", "beginner_friendly", "encouragement"],
                intensity="soft",
                time_context=["morning", "afternoon"],
                mindset_types=[MindsetType.GROWTH, MindsetType.PERSISTENCE],
                activity_levels=["beginner"]
            ),
            MotivationalQuote(
                quote_text="Mastery is not perfection, but a constant pursuit of improvement.",
                domains=[Domain.LEARNING, Domain.FITNESS, Domain.PRODUCTIVITY],
                context_tags=["mastery", "continuous_improvement", "journey"],
                intensity="moderate",
                time_context=["afternoon", "evening"],
                mindset_types=[MindsetType.GROWTH, MindsetType.PERSISTENCE],
                activity_levels=["intermediate", "advanced"]
            ),
            
            # Universal - Starting & Momentum
            MotivationalQuote(
                quote_text="A journey of a thousand miles begins with a single step.",
                domains=[Domain.FITNESS, Domain.PRODUCTIVITY, Domain.LEARNING],
                context_tags=["starting", "first_step", "momentum"],
                intensity="soft",
                time_context=["morning"],
                mindset_types=[MindsetType.GROWTH, MindsetType.PERSISTENCE],
                activity_levels=["beginner"]
            ),
            MotivationalQuote(
                quote_text="Progress, not perfection, is what we should be asking for.",
                domains=[Domain.FITNESS, Domain.PRODUCTIVITY, Domain.LEARNING],
                context_tags=["progress", "self_compassion", "realistic"],
                intensity="soft",
                time_context=["evening"],
                mindset_types=[MindsetType.GROWTH],
                activity_levels=["beginner", "intermediate"]
            ),
            
            # Struggle & Perseverance
            MotivationalQuote(
                quote_text="Obstacles are opportunities in disguise.",
                domains=[Domain.FITNESS, Domain.PRODUCTIVITY, Domain.LEARNING],
                context_tags=["struggling", "obstacles", "reframe"],
                intensity="moderate",
                time_context=["afternoon", "evening"],
                mindset_types=[MindsetType.PERSISTENCE, MindsetType.GROWTH],
                activity_levels=["intermediate", "advanced"]
            ),
            MotivationalQuote(
                quote_text="The comeback is always stronger than the setback.",
                domains=[Domain.FITNESS, Domain.PRODUCTIVITY, Domain.LEARNING],
                context_tags=["recovery", "comeback", "resilience"],
                intensity="intense",
                time_context=["morning", "afternoon"],
                mindset_types=[MindsetType.PERSISTENCE, MindsetType.ACHIEVEMENT],
                activity_levels=["intermediate", "advanced"]
            ),
        ]
        
        return quotes
    
    def get_contextual_quote(
        self,
        domain: Domain,
        context_tags: List[str],
        mindset_types: List[MindsetType],
        activity_level: str,
        time_of_day: str
    ) -> Optional[MotivationalQuote]:
        """
        Get a contextually relevant quote based on user context
        """
        # Filter quotes by domain
        relevant_quotes = [q for q in self.quotes if domain in q.domains]
        
        # Score each quote based on context matching
        scored_quotes = []
        for quote in relevant_quotes:
            score = 0
            
            # Context tags matching
            matching_tags = set(context_tags) & set(quote.context_tags)
            score += len(matching_tags) * 3
            
            # Mindset matching
            matching_mindsets = set(mindset_types) & set(quote.mindset_types)
            score += len(matching_mindsets) * 2
            
            # Activity level matching
            if activity_level in quote.activity_levels:
                score += 2
            
            # Time context matching
            if time_of_day in quote.time_context:
                score += 1
            
            scored_quotes.append((score, quote))
        
        # Sort by score and get top quotes
        scored_quotes.sort(reverse=True, key=lambda x: x[0])
        
        # Return highest scoring quote or random from top 3
        if scored_quotes:
            top_quotes = [q for s, q in scored_quotes[:3] if s > 0]
            return random.choice(top_quotes) if top_quotes else scored_quotes[0][1]
        
        return None

quote_db = QuoteDatabase()
print(f"💬 Quote database initialized with {len(quote_db.quotes)} quotes!")

# ============================================================================
# SECTION 6: SYSTEM STATUS
# ============================================================================

print("\n" + "="*70)
print("✅ LEVELUP LIFE - INITIALIZATION COMPLETE")
print("="*70)
print("\n📋 System Components Ready:")
print("   ✓ Dependencies installed")
print("   ✓ Configuration loaded")
print("   ✓ Data models defined")
print("   ✓ Quote database initialized")
print("\n🚀 Ready to proceed to Agent implementation!")
print("="*70 + "\n")