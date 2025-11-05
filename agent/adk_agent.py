"""
Google ADK Agent Configuration for Nutrition AI
This file exposes the root_agent for the ADK CLI.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from agent.main_agent import get_agent


# Tool functions that ADK can call
async def chat_with_agent(
    message: str,
    health_goals: str = None,
    fitness_goals: str = None
) -> str:
    """
    Chat with the nutrition AI companion.

    Args:
        message: Your message or question
        health_goals: Optional health goals for context
        fitness_goals: Optional fitness goals for context

    Returns:
        AI companion's response
    """
    agent = get_agent()

    context = {}
    if health_goals or fitness_goals:
        context["user_profile"] = {
            "health_goals": health_goals,
            "fitness_goals": fitness_goals
        }

    response = await agent.chat(message, context if context else None)
    return response


# Create ADK agent with tools
root_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="nutrition_ai_companion",
    description="""A friendly AI nutrition companion that helps you make informed food choices.

I can:
- Provide personalized nutrition recommendations based on your goals
- Answer nutrition and fitness questions in a supportive way
- Offer guidance on healthy eating and lifestyle choices

I'm here to help you achieve your health and fitness goals!""",
    instruction="""You are a friendly, knowledgeable AI nutrition companion.

Your personality:
- Warm, supportive, and encouraging
- Knowledgeable but not preachy
- Focused on helping users achieve their specific goals
- Provide actionable, personalized advice

When users ask questions:
- Use chat_with_agent for conversational responses
- Be supportive and practical
- Tailor advice to their stated goals
- Provide specific recommendations (timing, portions, alternatives)

Always be encouraging and focus on progress, not perfection!""",
    tools=[
        FunctionTool(chat_with_agent),
    ],
)
