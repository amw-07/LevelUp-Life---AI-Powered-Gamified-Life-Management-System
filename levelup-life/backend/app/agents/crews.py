from app.agents.agents import create_user_profile_manager, create_quest_generator
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
