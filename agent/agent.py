"""
Google ADK Agent Configuration for Nutrition AI
This file exposes the root_agent for the ADK CLI.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from agent.main_agent import get_agent
from agent.models import UserProfile
import asyncio


# Tool functions that ADK can call
async def scan_product(barcode: str) -> dict:
    """
    Scan a product barcode and retrieve product information.

    Args:
        barcode: The barcode number to scan

    Returns:
        Product information as a dictionary
    """
    agent = get_agent()
    product = await agent.scan_barcode(barcode)

    if not product:
        return {"error": "Product not found"}

    return {
        "barcode": product.barcode,
        "name": product.name,
        "brand": product.brand,
        "category": product.category,
        "price": product.price,
        "size": product.size,
        "nutrition": product.nutrition,
        "ingredients": product.ingredients
    }


async def evaluate_product(
    barcode: str,
    health_goals: str = "balanced nutrition",
    fitness_goals: str = "general fitness",
    dietary_restrictions: str = None,
    daily_calorie_target: int = None,
    daily_protein_target_g: int = None
) -> dict:
    """
    Evaluate a product for health, fitness, and pricing.

    Args:
        barcode: The product barcode
        health_goals: User's health goals (e.g., "low sugar, high protein")
        fitness_goals: User's fitness goals (e.g., "muscle building", "weight loss")
        dietary_restrictions: Any dietary restrictions (e.g., "vegan", "gluten-free")
        daily_calorie_target: Daily calorie target
        daily_protein_target_g: Daily protein target in grams

    Returns:
        Complete evaluation with scores and recommendations
    """
    agent = get_agent()

    # Scan product
    product = await agent.scan_barcode(barcode)
    if not product:
        return {"error": "Product not found"}

    # Create user profile
    user_profile = UserProfile(
        health_goals=health_goals,
        fitness_goals=fitness_goals,
        dietary_restrictions=dietary_restrictions,
        daily_calorie_target=daily_calorie_target,
        daily_protein_target_g=daily_protein_target_g
    )

    # Evaluate
    evaluation = await agent.evaluate_product(product, user_profile)
    return evaluation


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
- Scan product barcodes and retrieve detailed information
- Evaluate products for health, fitness, and price value
- Provide personalized recommendations based on your goals
- Answer nutrition and fitness questions in a supportive way

I'm here to help you achieve your health and fitness goals!""",
    instruction="""You are a friendly, knowledgeable AI nutrition companion.

Your personality:
- Warm, supportive, and encouraging
- Knowledgeable but not preachy
- Focused on helping users achieve their specific goals
- Provide actionable, personalized advice

When users ask about products:
1. Use scan_product to get product information
2. Use evaluate_product with their goals to get a comprehensive analysis
3. Explain results in a friendly, conversational way
4. Provide specific recommendations (timing, portions, alternatives)

When users ask general questions:
- Use chat_with_agent for conversational responses
- Be supportive and practical
- Tailor advice to their stated goals

Always be encouraging and focus on progress, not perfection!""",
    tools=[
        FunctionTool(scan_product),
        FunctionTool(evaluate_product),
        FunctionTool(chat_with_agent),
    ],
)
