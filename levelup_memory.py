# ============================================================================
# LEVELUP LIFE - MEMORY & STATE MANAGEMENT
# Session management, long-term memory, and state persistence
# ============================================================================

"""
This module implements the memory and state management system:
1. Session Service - Short-term session data
2. Memory Bank - Long-term user history and patterns
3. State Manager - Centralized state management
4. Demo Data Generator - Sample data for testing
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import uuid

# ============================================================================
# SESSION SERVICE (Short-term Memory)
# ============================================================================

class SessionService:
    """
    Manages short-term session data for active user sessions.
    Stores current day quests, temporary state, and session-specific context.
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, user_id: str) -> str:
        """Create a new session for a user"""
        session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.sessions[session_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'active_quests': [],
            'completed_quests_today': [],
            'context': {},
            'temp_data': {}
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session data"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, updates: Dict):
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)
            self.sessions[session_id]['last_activity'] = datetime.now().isoformat()
    
    def add_active_quest(self, session_id: str, quest: Quest):
        """Add a quest to active quests"""
        if session_id in self.sessions:
            self.sessions[session_id]['active_quests'].append(quest.to_dict())
    
    def complete_quest(self, session_id: str, quest_id: str):
        """Mark a quest as completed in the session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            # Move from active to completed
            active_quests = session['active_quests']
            for quest in active_quests:
                if quest['quest_id'] == quest_id:
                    quest['is_completed'] = True
                    quest['completed_at'] = datetime.now().isoformat()
                    session['completed_quests_today'].append(quest)
                    break
    
    def clear_session(self, session_id: str):
        """Clear session data"""
        if session_id in self.sessions:
            del self.sessions[session_id]

# ============================================================================
# MEMORY BANK (Long-term Memory)
# ============================================================================

class MemoryBank:
    """
    Manages long-term memory including user history, patterns, and preferences.
    Stores all historical quests, achievements, and behavioral patterns.
    """
    
    def __init__(self):
        self.user_histories: Dict[str, Dict] = {}
        self.quest_archive: Dict[str, List[Quest]] = defaultdict(list)
        self.pattern_analysis: Dict[str, Dict] = {}
    
    def initialize_user(self, user_profile: UserProfile):
        """Initialize memory for a new user"""
        self.user_histories[user_profile.user_id] = {
            'user_id': user_profile.user_id,
            'profile_history': [self._profile_snapshot(user_profile)],
            'quest_completion_history': [],
            'streak_history': [],
            'achievement_history': [],
            'goal_history': [],
            'preference_updates': []
        }
    
    def _profile_snapshot(self, profile: UserProfile) -> Dict:
        """Create a snapshot of user profile"""
        return {
            'timestamp': datetime.now().isoformat(),
            'level': profile.level,
            'total_xp': profile.total_xp,
            'rank': profile.rank,
            'stats': {
                'strength': profile.strength,
                'vitality': profile.vitality,
                'endurance': profile.endurance,
                'focus': profile.focus,
                'efficiency': profile.efficiency,
                'execution': profile.execution,
                'intelligence': profile.intelligence,
                'creativity': profile.creativity,
                'wisdom': profile.wisdom
            },
            'streak': profile.current_streak,
            'total_quests': profile.total_quests_completed
        }
    
    def store_quest_completion(self, user_id: str, quest: Quest, xp_earned: int):
        """Store completed quest in memory"""
        self.quest_archive[user_id].append(quest)
        
        if user_id in self.user_histories:
            self.user_histories[user_id]['quest_completion_history'].append({
                'quest_id': quest.quest_id,
                'timestamp': datetime.now().isoformat(),
                'domain': quest.domain.value,
                'difficulty': quest.difficulty.value,
                'xp_earned': xp_earned
            })
    
    def store_achievement(self, user_id: str, achievement: Dict):
        """Store new achievement"""
        if user_id in self.user_histories:
            self.user_histories[user_id]['achievement_history'].append({
                'timestamp': datetime.now().isoformat(),
                'achievement': achievement
            })
    
    def get_quest_history(self, user_id: str, days: int = 30) -> List[Quest]:
        """Get quest history for specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        quests = self.quest_archive.get(user_id, [])
        
        # Filter by date
        recent_quests = [
            q for q in quests 
            if datetime.fromisoformat(q.created_at) > cutoff_date
        ]
        return recent_quests
    
    def analyze_patterns(self, user_id: str) -> Dict:
        """Analyze user behavior patterns"""
        history = self.user_histories.get(user_id, {})
        quest_history = history.get('quest_completion_history', [])
        
        if not quest_history:
            return {}
        
        # Calculate completion patterns
        domain_counts = defaultdict(int)
        difficulty_counts = defaultdict(int)
        total_xp = 0
        
        for completion in quest_history:
            domain_counts[completion['domain']] += 1
            difficulty_counts[completion['difficulty']] += 1
            total_xp += completion['xp_earned']
        
        # Calculate completion rate (simplified)
        completion_rate = len(quest_history) / max(1, len(quest_history) * 1.2)
        
        patterns = {
            'total_completions': len(quest_history),
            'domain_distribution': dict(domain_counts),
            'difficulty_distribution': dict(difficulty_counts),
            'total_xp_earned': total_xp,
            'completion_rate': round(completion_rate, 2),
            'favorite_domain': max(domain_counts.items(), key=lambda x: x[1])[0] if domain_counts else None,
            'analysis_date': datetime.now().isoformat()
        }
        
        self.pattern_analysis[user_id] = patterns
        return patterns
    
    def get_user_context(self, user_id: str) -> Dict:
        """Get complete user context for agent consumption"""
        return {
            'history': self.user_histories.get(user_id, {}),
            'patterns': self.pattern_analysis.get(user_id, {}),
            'recent_quests': [q.to_dict() for q in self.get_quest_history(user_id, days=7)]
        }

# ============================================================================
# STATE MANAGER (Centralized State)
# ============================================================================

class StateManager:
    """
    Centralized state manager that coordinates session and memory services.
    Provides a unified interface for state operations.
    """
    
    def __init__(self):
        self.session_service = SessionService()
        self.memory_bank = MemoryBank()
        self.active_profiles: Dict[str, UserProfile] = {}
    
    def load_user(self, user_profile: UserProfile) -> str:
        """Load user and create session"""
        # Store active profile
        self.active_profiles[user_profile.user_id] = user_profile
        
        # Initialize memory if new user
        if user_profile.user_id not in self.memory_bank.user_histories:
            self.memory_bank.initialize_user(user_profile)
        
        # Create session
        session_id = self.session_service.create_session(user_profile.user_id)
        
        return session_id
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get active user profile"""
        return self.active_profiles.get(user_id)
    
    def update_user_profile(self, user_profile: UserProfile):
        """Update user profile and store snapshot"""
        self.active_profiles[user_profile.user_id] = user_profile
        
        # Store snapshot in memory
        if user_profile.user_id in self.memory_bank.user_histories:
            self.memory_bank.user_histories[user_profile.user_id]['profile_history'].append(
                self.memory_bank._profile_snapshot(user_profile)
            )
    
    def complete_quest(
        self,
        session_id: str,
        quest: Quest,
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """
        Complete a quest and update all relevant state.
        Returns updated stats and achievements.
        """
        # Mark as completed
        quest.is_completed = True
        quest.completed_at = datetime.now().isoformat()
        
        # Calculate rewards
        xp_gained = quest.xp_reward
        user_profile.total_xp += xp_gained
        
        # Update stats
        for stat, value in quest.stat_rewards.items():
            current_value = getattr(user_profile, stat.lower(), 0)
            setattr(user_profile, stat.lower(), min(100, current_value + value))
        
        # Update quest counters
        user_profile.total_quests_completed += 1
        user_profile.quests_by_domain[quest.domain.value] += 1
        
        # Update rank/level
        rank_info = calculate_rank_and_level.func(user_profile.total_xp)
        user_profile.rank = rank_info['rank']
        user_profile.level = rank_info['level']
        
        # Update streak
        streak_info = track_and_update_streak.func(
            user_profile.last_active,
            user_profile.current_streak,
            user_profile.longest_streak
        )
        user_profile.current_streak = streak_info['current_streak']
        user_profile.longest_streak = streak_info['longest_streak']
        
        # Update last active
        user_profile.last_active = datetime.now().isoformat()
        
        # Check achievements
        achievements = check_achievements.func({
            'total_quests_completed': user_profile.total_quests_completed,
            'current_streak': user_profile.current_streak,
            'total_xp': user_profile.total_xp
        })
        
        # Store in memory
        self.memory_bank.store_quest_completion(user_profile.user_id, quest, xp_gained)
        for achievement in achievements:
            self.memory_bank.store_achievement(user_profile.user_id, achievement)
            user_profile.achievements.append(achievement['name'])
        
        # Update session
        self.session_service.complete_quest(session_id, quest.quest_id)
        
        # Update profile
        self.update_user_profile(user_profile)
        
        return {
            'xp_gained': xp_gained,
            'new_total_xp': user_profile.total_xp,
            'new_level': user_profile.level,
            'new_rank': user_profile.rank,
            'streak_info': streak_info,
            'new_achievements': achievements,
            'updated_stats': quest.stat_rewards
        }
    
    def get_analytics_data(self, user_id: str) -> Dict:
        """Get comprehensive analytics data"""
        profile = self.get_user_profile(user_id)
        patterns = self.memory_bank.analyze_patterns(user_id)
        context = self.memory_bank.get_user_context(user_id)
        
        return {
            'profile': profile,
            'patterns': patterns,
            'context': context
        }

# Initialize global state manager
state_manager = StateManager()

print("✅ Memory & State Management System initialized!")

# ============================================================================
# DEMO DATA GENERATOR
# ============================================================================

class DemoDataGenerator:
    """Generate demo data for testing and demonstration"""
    
    @staticmethod
    def create_demo_user(name: str = "Alex") -> UserProfile:
        """Create a demo user profile"""
        user_profile = UserProfile(
            user_id=f"user_{uuid.uuid4().hex[:8]}",
            name=name,
            level=5,
            total_xp=2500,
            rank='D',
            
            # Stats
            strength=25,
            vitality=20,
            endurance=22,
            focus=30,
            efficiency=28,
            execution=26,
            intelligence=35,
            creativity=32,
            wisdom=30,
            
            # Goals
            goals={
                'fitness': ['Build strength', 'Improve endurance', 'Morning routine'],
                'productivity': ['Deep work habits', 'Complete major project', 'Time management'],
                'learning': ['Master Python', 'Learn AI concepts', 'Read daily']
            },
            
            # Profile
            mindset_profile=[MindsetType.GROWTH, MindsetType.DISCIPLINE],
            work_style="focused",
            activity_level="intermediate",
            preferred_times={
                'fitness': 'morning',
                'productivity': 'afternoon',
                'learning': 'evening'
            },
            
            # Progress
            current_streak=7,
            longest_streak=14,
            total_quests_completed=45,
            quests_by_domain={'fitness': 15, 'productivity': 18, 'learning': 12},
            achievements=['Getting Started', 'Week Warrior']
        )
        
        return user_profile
    
    @staticmethod
    def create_demo_quests(user_profile: UserProfile) -> List[Quest]:
        """Generate demo quests for a user"""
        quests = []
        
        # Fitness quest
        fitness_quest = Quest(
            quest_id=f"quest_{uuid.uuid4().hex[:8]}",
            title="30-Minute Morning Workout",
            description="Complete a full-body workout routine focusing on strength and endurance",
            domain=Domain.FITNESS,
            difficulty=DifficultyLevel.MEDIUM,
            xp_reward=100,
            stat_rewards={'Strength': 5, 'Endurance': 3, 'Vitality': 2},
            estimated_duration="30 min",
            context_tags=['morning', 'strength', 'routine']
        )
        quests.append(fitness_quest)
        
        # Productivity quest
        productivity_quest = Quest(
            quest_id=f"quest_{uuid.uuid4().hex[:8]}",
            title="Deep Work Session: Project Milestone",
            description="Complete 90 minutes of focused work on your priority project",
            domain=Domain.PRODUCTIVITY,
            difficulty=DifficultyLevel.MEDIUM,
            xp_reward=90,
            stat_rewards={'Focus': 5, 'Execution': 4, 'Efficiency': 2},
            estimated_duration="90 min",
            context_tags=['deep_work', 'focus', 'project']
        )
        quests.append(productivity_quest)
        
        # Learning quest
        learning_quest = Quest(
            quest_id=f"quest_{uuid.uuid4().hex[:8]}",
            title="AI Course: Complete Module on Neural Networks",
            description="Watch lectures and complete exercises on neural network fundamentals",
            domain=Domain.LEARNING,
            difficulty=DifficultyLevel.HARD,
            xp_reward=180,
            stat_rewards={'Intelligence': 8, 'Wisdom': 4, 'Creativity': 3},
            estimated_duration="120 min",
            context_tags=['ai', 'learning', 'technical']
        )
        quests.append(learning_quest)
        
        # Easy productivity quest
        easy_quest = Quest(
            quest_id=f"quest_{uuid.uuid4().hex[:8]}",
            title="Plan Tomorrow's Top 3 Tasks",
            description="Review priorities and plan your three most important tasks for tomorrow",
            domain=Domain.PRODUCTIVITY,
            difficulty=DifficultyLevel.EASY,
            xp_reward=40,
            stat_rewards={'Efficiency': 2, 'Focus': 1},
            estimated_duration="10 min",
            context_tags=['planning', 'organization', 'quick']
        )
        quests.append(easy_quest)
        
        # Easy learning quest
        reading_quest = Quest(
            quest_id=f"quest_{uuid.uuid4().hex[:8]}",
            title="Read 15 Pages of Educational Book",
            description="Continue reading your current educational book and take notes",
            domain=Domain.LEARNING,
            difficulty=DifficultyLevel.EASY,
            xp_reward=60,
            stat_rewards={'Intelligence': 3, 'Wisdom': 2},
            estimated_duration="20 min",
            context_tags=['reading', 'knowledge', 'evening']
        )
        quests.append(reading_quest)
        
        return quests
    
    @staticmethod
    def simulate_quest_history(user_profile: UserProfile, days: int = 7) -> List[Quest]:
        """Simulate historical completed quests"""
        history = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            
            # Create 2-4 quests per day
            num_quests = random.randint(2, 4)
            domains = [Domain.FITNESS, Domain.PRODUCTIVITY, Domain.LEARNING]
            
            for _ in range(num_quests):
                domain = random.choice(domains)
                difficulty = random.choice([DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD])
                
                quest = Quest(
                    quest_id=f"hist_quest_{uuid.uuid4().hex[:8]}",
                    title=f"{domain.value.title()} Quest",
                    description=f"Historical {difficulty.value} {domain.value} quest",
                    domain=domain,
                    difficulty=difficulty,
                    xp_reward=Config.XP_REWARDS[domain.value][difficulty.value],
                    stat_rewards={},
                    estimated_duration="30 min",
                    context_tags=['historical'],
                    is_completed=True,
                    completed_at=date.isoformat()
                )
                quest.created_at = date.isoformat()
                history.append(quest)
        
        return history

demo_generator = DemoDataGenerator()
print("✅ Demo data generator ready!")

# ============================================================================
# DEMO SCENARIO
# ============================================================================

def run_demo_scenario():
    """Run a complete demo scenario"""
    print("\n" + "="*70)
    print("🎮 LEVELUP LIFE - DEMO SCENARIO")
    print("="*70 + "\n")
    
    # Create demo user
    print("📝 Creating demo user...")
    demo_user = demo_generator.create_demo_user("Alex")
    print(f"✅ User created: {demo_user.name}")
    print(f"   Level: {demo_user.level} | Rank: {demo_user.rank} | XP: {demo_user.total_xp}")
    print(f"   Current Streak: {demo_user.current_streak} days")
    
    # Load user into state manager
    print("\n💾 Loading user into state manager...")
    session_id = state_manager.load_user(demo_user)
    print(f"✅ Session created: {session_id}")
    
    # Generate quests
    print("\n🎯 Generating daily quests...")
    demo_quests = demo_generator.create_demo_quests(demo_user)
    print(f"✅ Generated {len(demo_quests)} quests:")
    for i, quest in enumerate(demo_quests, 1):
        print(f"   {i}. [{quest.domain.value.upper()}] {quest.title}")
        print(f"      Difficulty: {quest.difficulty.value} | XP: {quest.xp_reward}")
        state_manager.session_service.add_active_quest(session_id, quest)
    
    # Simulate completing a quest
    print("\n✨ Simulating quest completion...")
    quest_to_complete = demo_quests[0]
    print(f"Completing: {quest_to_complete.title}")
    
    completion_result = state_manager.complete_quest(
        session_id,
        quest_to_complete,
        demo_user
    )
    
    print(f"\n🎉 Quest Completed!")
    print(f"   XP Gained: +{completion_result['xp_gained']}")
    print(f"   New Total XP: {completion_result['new_total_xp']}")
    print(f"   Level: {completion_result['new_level']}")
    print(f"   Rank: {completion_result['new_rank']}")
    print(f"   Streak: {completion_result['streak_info']['message']}")
    
    if completion_result['new_achievements']:
        print(f"   🏆 New Achievements:")
        for ach in completion_result['new_achievements']:
            print(f"      {ach['icon']} {ach['name']}: {ach['description']}")
    
    # Get motivational quote
    print("\n💬 Getting motivational quote...")
    quote_result = select_motivational_quote.func(
        domain='fitness',
        context_tags=['celebration', 'progress'],
        mindset_profile=['growth', 'discipline'],
        activity_level='intermediate',
        time_of_day='morning'
    )
    print(f"   \"{quote_result['quote_text']}\"")
    
    # Simulate history
    print("\n📚 Simulating quest history...")
    historical_quests = demo_generator.simulate_quest_history(demo_user, days=7)
    for quest in historical_quests:
        state_manager.memory_bank.quest_archive[demo_user.user_id].append(quest)
    print(f"✅ Added {len(historical_quests)} historical quests")
    
    # Analyze patterns
    print("\n📊 Analyzing user patterns...")
    patterns = state_manager.memory_bank.analyze_patterns(demo_user.user_id)
    print(f"   Total Completions: {patterns['total_completions']}")
    print(f"   Completion Rate: {patterns['completion_rate']*100:.1f}%")
    print(f"   Favorite Domain: {patterns['favorite_domain']}")
    print(f"   Domain Distribution: {patterns['domain_distribution']}")
    
    print("\n" + "="*70)
    print("✅ DEMO SCENARIO COMPLETE")
    print("="*70 + "\n")
    
    return {
        'user': demo_user,
        'session_id': session_id,
        'quests': demo_quests,
        'patterns': patterns
    }

# Run demo when this section is executed
print("\n🚀 Memory system ready! Use run_demo_scenario() to test.")
print("="*70)