from app.agents.llm import get_llm


def create_user_profile_manager():
    from crewai import Agent
    return Agent(
        role="User Profile Manager",
        goal="Maintain user context, stats, and progression data accurately",
        backstory="You are an expert at analyzing user profiles and progression data for RPG systems.",
        llm=get_llm(),
        allow_delegation=False,
        verbose=False,
    )


def create_quest_generator():
    from crewai import Agent
    return Agent(
        role="Quest Generator",
        goal="Create personalized daily quests across fitness, productivity, and learning",
        backstory="You are a master quest designer who creates engaging, achievable daily challenges.",
        llm=get_llm(),
        allow_delegation=False,
        verbose=False,
    )


def create_progress_tracker():
    from crewai import Agent
    return Agent(
        role="Progress Tracker",
        goal="Validate quest completion and calculate accurate rewards",
        backstory="You track user progress with precision, ensuring fair XP and stat rewards.",
        llm=get_llm(),
        allow_delegation=False,
        verbose=False,
    )


def create_personalized_coach():
    from crewai import Agent
    return Agent(
        role="Personalized Coach",
        goal="Provide context-aware motivation and guidance to users",
        backstory="You are a supportive life coach who understands each user's unique journey.",
        llm=get_llm(),
        allow_delegation=False,
        verbose=False,
    )


def create_analytics_evaluator():
    from crewai import Agent
    return Agent(
        role="Analytics & Evaluator",
        goal="Orchestrate agents and provide actionable insights",
        backstory="You analyze patterns and coordinate the team to maximize user success.",
        llm=get_llm(),
        allow_delegation=True,
        verbose=False,
    )
