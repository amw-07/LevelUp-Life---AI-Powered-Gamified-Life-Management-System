from app.agents.agents import (
    create_user_profile_manager,
    create_quest_generator,
    create_personalized_coach,
    create_analytics_evaluator,
)
from app.agents.tasks import build_quest_generation_task


def create_daily_quest_crew(user):
    from crewai import Crew, Task, Process

    profile_agent = create_user_profile_manager()
    quest_agent = create_quest_generator()

    profile_task = Task(
        description=f"Analyze user profile for {user.username} at level {user.level}.",
        expected_output="A summary of user profile and context.",
        agent=profile_agent,
    )

    quest_task = Task(
        description=build_quest_generation_task(user),
        expected_output="Valid JSON with a 'quests' array containing 5 quest objects.",
        agent=quest_agent,
    )

    return Crew(
        agents=[profile_agent, quest_agent],
        tasks=[profile_task, quest_task],
        process=Process.sequential,
        verbose=False,
    )


def create_analytics_crew(user, week_data):
    """Create a crew for generating weekly analytics insights."""
    from crewai import Crew, Task, Process

    analytics_agent = create_analytics_evaluator()

    analytics_prompt = f"""
    User: {user.username}
    Level: {user.level} | Rank: {user.rank}
    Current Streak: {user.current_streak} days
    Weekly Stats: {week_data["metrics"]}
    Stats: {user.stats}
    Goals: {user.goals}

    Task: Analyze the user's weekly performance and provide 3-4 actionable insights.
    Focus on:
    1. Progress highlights (what went well)
    2. Areas for improvement
    3. Specific suggestions for next week
    4. Encouragement based on their journey

    Be concise, supportive, and specific. Keep response under 200 words.
    """

    analytics_task = Task(
        description=analytics_prompt,
        expected_output="3-4 concise, actionable insights about the user's weekly progress.",
        agent=analytics_agent,
    )

    return Crew(
        agents=[analytics_agent],
        tasks=[analytics_task],
        process=Process.sequential,
        verbose=False,
    )


def create_coach_crew(user):
    """Create a crew for generating personalized coaching messages."""
    from crewai import Crew, Task, Process

    coach_agent = create_personalized_coach()

    coach_prompt = f"""
    User: {user.username}
    Level: {user.level} | Rank: {user.rank}
    Current Streak: {user.current_streak} days
    Longest Streak: {user.longest_streak} days
    Total XP: {user.total_xp}
    Stats: {user.stats}
    Goals: {user.goals}
    Activity Level: {user.activity_level}
    Work Style: {user.work_style}

    Task: Generate a personalized, motivational coaching message.
    Consider their current streak, level, and goals.
    Be encouraging but realistic.
    Focus on their next step forward.
    Keep it to 1-2 sentences (max 50 words).
    """

    coach_task = Task(
        description=coach_prompt,
        expected_output="A short, motivational coaching message (1-2 sentences).",
        agent=coach_agent,
    )

    return Crew(
        agents=[coach_agent],
        tasks=[coach_task],
        process=Process.sequential,
        verbose=False,
    )
