# ============================================================================
# LEVELUP LIFE - MULTI-AGENT SYSTEM
# 5 Specialized CrewAI Agents for Life Management
# ============================================================================

"""
This module implements the multi-agent system:
1. User Profile Manager Agent - Manages user context and state
2. Quest Generator Agent - Creates personalized daily quests
3. Progress Tracker Agent - Validates completion and calculates rewards
4. Personalized Coach Agent - Provides motivation and guidance
5. Analytics & Evaluator Agent - Orchestrates and provides insights
"""

from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
import json

# ============================================================================
# LLM INITIALIZATION
# ============================================================================

def initialize_llm():
    """Initialize Google Gemini LLM"""
    return ChatGoogleGenerativeAI(
        model=Config.MODEL_NAME,
        google_api_key=Config.GEMINI_API_KEY,
        temperature=0.7
    )

# For demo purposes, we'll use a placeholder
# In actual Kaggle notebook, use: llm = initialize_llm()
llm = None  # Will be initialized when API key is available

# ============================================================================
# AGENT 1: USER PROFILE MANAGER
# ============================================================================

user_profile_manager = Agent(
    role='User Profile Manager',
    goal='Maintain accurate user context, preferences, stats, and progression data',
    backstory="""You are an expert data manager who keeps track of every aspect 
    of a user's journey. You understand their goals, track their progress, remember 
    their preferences, and maintain their complete profile. You're meticulous about 
    data accuracy and always provide complete context to other agents.""",
    verbose=True,
    allow_delegation=False,
    tools=[
        calculate_rank_and_level,
        track_and_update_streak,
        check_achievements
    ],
    llm=llm
)

# ============================================================================
# AGENT 2: QUEST GENERATOR
# ============================================================================

quest_generator = Agent(
    role='Quest Generator',
    goal='Create personalized, achievable quests across fitness, productivity, and learning domains',
    backstory="""You are a master quest designer who creates perfectly balanced 
    challenges. You understand that each person is unique - their goals, schedule, 
    energy levels, and current skills all matter. You design quests that are 
    challenging but achievable, varied but focused, and always aligned with what 
    the user wants to accomplish. You consider their work patterns, activity levels, 
    and past performance to create the perfect daily quest lineup.""",
    verbose=True,
    allow_delegation=False,
    tools=[
        adjust_quest_difficulty,
        generate_quest_ideas,
        calculate_xp_and_stats
    ],
    llm=llm
)

# ============================================================================
# AGENT 3: PROGRESS TRACKER
# ============================================================================

progress_tracker = Agent(
    role='Progress Tracker',
    goal='Accurately track quest completion, calculate rewards, and update user stats',
    backstory="""You are a precise accountant of progress and achievement. When 
    users complete quests, you validate their accomplishment, calculate their 
    earned XP and stat increases, update their rank and level, and maintain their 
    streaks. You celebrate their wins and ensure every bit of progress is properly 
    recorded and rewarded. You're the keeper of stats and the validator of growth.""",
    verbose=True,
    allow_delegation=False,
    tools=[
        calculate_xp_and_stats,
        calculate_rank_and_level,
        track_and_update_streak,
        check_achievements
    ],
    llm=llm
)

# ============================================================================
# AGENT 4: PERSONALIZED COACH
# ============================================================================

personalized_coach = Agent(
    role='Personalized Coach',
    goal='Provide contextual motivation, select appropriate quotes, and guide users toward their goals',
    backstory="""You are an empathetic and inspiring coach who deeply understands 
    human motivation. You know when to push and when to encourage, when to celebrate 
    and when to support through challenges. You select perfectly timed motivational 
    messages and quotes that resonate with each user's current situation - whether 
    they're starting fresh, building momentum, pushing through difficulties, or 
    celebrating success. You adapt your communication style to each user's mindset 
    and preferences, making every interaction feel personal and meaningful.""",
    verbose=True,
    allow_delegation=False,
    tools=[
        select_motivational_quote
    ],
    llm=llm
)

# ============================================================================
# AGENT 5: ANALYTICS & EVALUATOR (ORCHESTRATOR)
# ============================================================================

analytics_evaluator = Agent(
    role='Analytics & Evaluator',
    goal='Analyze patterns, optimize the system, coordinate agents, and provide actionable insights',
    backstory="""You are a strategic analyst and system orchestrator. You see the 
    big picture - patterns in user behavior, effectiveness of quests, optimization 
    opportunities, and areas for improvement. You coordinate the other agents to 
    work together seamlessly. You generate weekly reports with valuable insights, 
    identify what's working and what isn't, and make data-driven recommendations. 
    You're constantly evaluating and refining the entire system to better serve 
    each user's unique journey.""",
    verbose=True,
    allow_delegation=True,  # Can delegate to other agents
    tools=[
        adjust_quest_difficulty,
        check_achievements
    ],
    llm=llm
)

print("✅ All 5 agents initialized!")
print("\n📋 Agent Roster:")
print("   1. User Profile Manager - Context & state management")
print("   2. Quest Generator - Personalized quest creation")
print("   3. Progress Tracker - Validation & rewards")
print("   4. Personalized Coach - Motivation & guidance")
print("   5. Analytics & Evaluator - Orchestration & insights")

# ============================================================================
# AGENT TASK TEMPLATES
# ============================================================================

class TaskTemplates:
    """Templates for common agent tasks"""
    
    @staticmethod
    def create_profile_analysis_task(user_profile: UserProfile) -> Task:
        """Task for analyzing user profile"""
        return Task(
            description=f"""
            Analyze the user profile for {user_profile.name} and provide a comprehensive summary.
            
            Current Stats:
            - Level: {user_profile.level}
            - Total XP: {user_profile.total_xp}
            - Rank: {user_profile.rank}
            - Current Streak: {user_profile.current_streak} days
            - Total Quests Completed: {user_profile.total_quests_completed}
            
            Goals: {user_profile.goals}
            Mindset Profile: {user_profile.mindset_profile}
            Activity Level: {user_profile.activity_level}
            Work Style: {user_profile.work_style}
            
            Provide:
            1. Summary of current state
            2. Rank and level progression analysis
            3. Recent performance patterns
            4. User context for quest generation
            """,
            agent=user_profile_manager,
            expected_output="Detailed user profile analysis with current state and context"
        )
    
    @staticmethod
    def create_quest_generation_task(
        user_profile: UserProfile,
        date: str = None
    ) -> Task:
        """Task for generating daily quests"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        return Task(
            description=f"""
            Generate personalized daily quests for {user_profile.name} for {date}.
            
            User Context:
            - Level: {user_profile.level}
            - Goals: {user_profile.goals}
            - Activity Level: {user_profile.activity_level}
            - Work Style: {user_profile.work_style}
            - Recent Completion Rate: {user_profile.total_quests_completed / max(1, user_profile.level)}
            - Current Streak: {user_profile.current_streak}
            
            Requirements:
            1. Generate 3-5 quests across fitness, productivity, and learning
            2. Balance difficulty based on user level and recent performance
            3. Align with user's stated goals
            4. Consider user's schedule and work patterns
            5. Include variety while maintaining focus
            
            For each quest provide:
            - Title
            - Description
            - Domain
            - Difficulty
            - Estimated Duration
            - XP Reward
            - Stat Rewards
            """,
            agent=quest_generator,
            expected_output="List of 3-5 personalized quests with complete details"
        )
    
    @staticmethod
    def create_progress_tracking_task(
        completed_quest: Quest,
        user_profile: UserProfile
    ) -> Task:
        """Task for tracking quest completion"""
        return Task(
            description=f"""
            Process the completion of quest: {completed_quest.title}
            
            Quest Details:
            - Domain: {completed_quest.domain.value}
            - Difficulty: {completed_quest.difficulty.value}
            - XP Reward: {completed_quest.xp_reward}
            - Stat Rewards: {completed_quest.stat_rewards}
            
            Current User State:
            - Total XP: {user_profile.total_xp}
            - Current Streak: {user_profile.current_streak}
            - Last Active: {user_profile.last_active}
            
            Tasks:
            1. Calculate and apply XP rewards
            2. Update user stats
            3. Check and update rank/level
            4. Track streak continuation or break
            5. Check for new achievements
            6. Generate celebration message
            
            Provide complete updated stats and any achievements earned.
            """,
            agent=progress_tracker,
            expected_output="Updated user stats, achievements, and celebration message"
        )
    
    @staticmethod
    def create_coaching_task(
        user_profile: UserProfile,
        context_tags: List[str],
        situation: str
    ) -> Task:
        """Task for providing motivational coaching"""
        return Task(
            description=f"""
            Provide personalized coaching and motivation for {user_profile.name}.
            
            Situation: {situation}
            
            User Context:
            - Mindset Profile: {user_profile.mindset_profile}
            - Activity Level: {user_profile.activity_level}
            - Current Streak: {user_profile.current_streak}
            - Recent Performance: {user_profile.total_quests_completed} quests completed
            
            Context Tags: {', '.join(context_tags)}
            Time: {datetime.now().strftime('%H:%M')}
            
            Tasks:
            1. Select an appropriate motivational quote
            2. Craft a personalized message that:
               - Acknowledges their current situation
               - Provides relevant encouragement or guidance
               - Aligns with their mindset and goals
               - Feels authentic and supportive
            3. Suggest specific actionable next steps
            
            Match the tone to their current state - celebratory for wins,
            encouraging for struggles, energizing for fresh starts.
            """,
            agent=personalized_coach,
            expected_output="Motivational quote, personalized message, and actionable guidance"
        )
    
    @staticmethod
    def create_analytics_task(
        user_profile: UserProfile,
        quest_history: List[Quest],
        time_period: str = "week"
    ) -> Task:
        """Task for generating analytics and insights"""
        return Task(
            description=f"""
            Generate comprehensive analytics report for {user_profile.name} for the past {time_period}.
            
            User Stats:
            - Level: {user_profile.level}
            - Rank: {user_profile.rank}
            - Total XP: {user_profile.total_xp}
            - Current Streak: {user_profile.current_streak}
            - Quests by Domain: {user_profile.quests_by_domain}
            
            Available Quest History: {len(quest_history)} quests
            
            Analysis Required:
            1. Overall Performance Summary
               - Quest completion rate
               - XP earned this period
               - Streak consistency
               
            2. Domain Breakdown
               - Performance by domain (fitness, productivity, learning)
               - Time distribution
               - Difficulty balance
               
            3. Pattern Identification
               - Best performing times/days
               - Most successful quest types
               - Areas of struggle
               
            4. Insights & Recommendations
               - What's working well
               - Areas for improvement
               - Suggested focus areas
               - Difficulty adjustments needed
               
            5. Goal Progress
               - Progress toward stated goals
               - Recommended next steps
               
            Coordinate with other agents as needed to gather additional context.
            Provide actionable, data-driven insights.
            """,
            agent=analytics_evaluator,
            expected_output="Comprehensive analytics report with insights and recommendations"
        )

print("\n✅ Task templates defined!")

# ============================================================================
# CREW SETUP FUNCTIONS
# ============================================================================

def create_daily_quest_crew(user_profile: UserProfile) -> Crew:
    """Create a crew for daily quest generation workflow"""
    
    # Define tasks
    profile_analysis = TaskTemplates.create_profile_analysis_task(user_profile)
    quest_generation = TaskTemplates.create_quest_generation_task(user_profile)
    
    # Create crew with sequential process
    crew = Crew(
        agents=[user_profile_manager, quest_generator],
        tasks=[profile_analysis, quest_generation],
        process=Process.sequential,
        verbose=True
    )
    
    return crew

def create_quest_completion_crew(
    completed_quest: Quest,
    user_profile: UserProfile,
    situation_context: str
) -> Crew:
    """Create a crew for quest completion workflow"""
    
    # Define tasks
    progress_task = TaskTemplates.create_progress_tracking_task(completed_quest, user_profile)
    coaching_task = TaskTemplates.create_coaching_task(
        user_profile,
        context_tags=['celebration', 'progress'],
        situation="Quest completed successfully"
    )
    
    # Create crew
    crew = Crew(
        agents=[progress_tracker, personalized_coach],
        tasks=[progress_task, coaching_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew

def create_analytics_crew(
    user_profile: UserProfile,
    quest_history: List[Quest]
) -> Crew:
    """Create a crew for analytics and reporting"""
    
    # Define tasks
    profile_task = TaskTemplates.create_profile_analysis_task(user_profile)
    analytics_task = TaskTemplates.create_analytics_task(user_profile, quest_history)
    coaching_task = TaskTemplates.create_coaching_task(
        user_profile,
        context_tags=['review', 'planning'],
        situation="Weekly progress review"
    )
    
    # Create crew with evaluator as orchestrator
    crew = Crew(
        agents=[user_profile_manager, analytics_evaluator, personalized_coach],
        tasks=[profile_task, analytics_task, coaching_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew

print("✅ Crew setup functions ready!")
print("\n📦 Available Workflows:")
print("   1. Daily Quest Generation Crew")
print("   2. Quest Completion Crew")
print("   3. Analytics & Reporting Crew")