QUEST_GENERATION_PROMPT = """
You are a master quest designer for a gamified life management app.

USER PROFILE:
- Name: {name}
- Level: {level} | Rank: {rank}
- Activity Level: {activity_level}
- Work Style: {work_style}
- Current Streak: {current_streak} days
- Goals:
  Fitness: {fitness_goals}
  Productivity: {productivity_goals}
  Learning: {learning_goals}
- Recent 7-day completion rate: {completion_rate:.0%}
- Quests by domain: {quests_by_domain}

TASK:
Generate exactly {num_quests} daily quests. Distribute:
- 1-2 fitness quests
- 1-2 productivity quests
- 1-2 learning quests

DIFFICULTY RULES (strictly enforced):
- Levels 1-4:   70% easy, 30% medium, 0% hard
- Levels 5-14:  30% easy, 50% medium, 20% hard
- Levels 15+:   10% easy, 40% medium, 50% hard
- If completion_rate < 50%: reduce all difficulties by one tier

XP RULES:
- easy: 40-60 XP | medium: 80-120 XP | hard: 160-240 XP

STAT RULES (only use stats for the quest's domain):
- fitness:      strength, vitality, endurance
- productivity: focus, efficiency, execution
- learning:     intelligence, creativity, wisdom

QUALITY RULES:
- Titles must be specific and action-oriented, not generic
- Descriptions are 1-2 sentences maximum
- estimated_duration must be realistic for the difficulty
- context_tags: 2-3 tags relevant to quest content

RESPOND WITH VALID JSON ONLY. No preamble. No markdown. No explanation.
{{
  "quests": [
    {{
      "title": "string",
      "description": "string",
      "domain": "fitness|productivity|learning",
      "difficulty": "easy|medium|hard",
      "xp_reward": integer,
      "stat_rewards": {{"StatName": integer}},
      "estimated_duration": "X min",
      "context_tags": ["tag1", "tag2"]
    }}
  ]
}}
"""


def build_quest_generation_task(user) -> str:
    goals = user.goals or {}
    qbd = user.quests_by_domain or {}
    completion_rate = 0.6

    return QUEST_GENERATION_PROMPT.format(
        name=user.username,
        level=user.level,
        rank=user.rank,
        activity_level=user.activity_level,
        work_style=user.work_style,
        current_streak=user.current_streak,
        fitness_goals=", ".join(goals.get("fitness", [])) or "General fitness",
        productivity_goals=", ".join(goals.get("productivity", [])) or "General productivity",
        learning_goals=", ".join(goals.get("learning", [])) or "General learning",
        completion_rate=completion_rate,
        quests_by_domain=str(qbd),
        num_quests=5,
    )
