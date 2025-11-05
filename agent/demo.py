#!/usr/bin/env python3
"""
Nutrition AI Agent - Demo Script
Demonstrates the capabilities of the production-ready nutrition agent.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import get_agent
from agent.models import UserProfile, Product


async def main():
    """Main demo function."""
    print("\n" + "="*70)
    print("🥗 Nutrition AI Agent - Production Demo")
    print("="*70)
    print("\nInitializing AI Agent...")

    # Get the agent
    agent = get_agent()

    print("✓ AI Agent initialized!\n")

    # Demo user profile
    user_profile = UserProfile(
        health_goals="low sugar, high protein, heart healthy",
        fitness_goals="muscle building, weight loss",
        dietary_restrictions="",
        goal_type="muscle_gain",
        activity_level="very_active",
        diet_type="high_protein",
        daily_calorie_target=2500,
        daily_protein_target_g=150,
        daily_carbs_target_g=200,
        daily_fat_target_g=70
    )

    print("👤 User Profile:")
    print(f"   Health Goals: {user_profile.health_goals}")
    print(f"   Fitness Goals: {user_profile.fitness_goals}")
    print(f"   Daily Calorie Target: {user_profile.daily_calorie_target} cal")
    print(f"   Daily Protein Target: {user_profile.daily_protein_target_g}g")
    print("\n" + "-"*70 + "\n")

    # Test products with nutrition data
    test_products = [
        Product(
            name="Quest Protein Bar",
            brand="Quest",
            category="Protein Bar",
            price=2.49,
            nutrition={
                "calories": 200,
                "protein": 21,
                "carbs_total": 22,
                "sugar_total": 1,
                "fat_total": 8,
                "sodium": 270,
                "serving_size": "60g",
                "servings_per_container": 1
            }
        ),
        Product(
            name="Coca-Cola",
            brand="Coca-Cola",
            category="Beverage",
            price=1.99,
            nutrition={
                "calories": 140,
                "protein": 0,
                "carbs_total": 39,
                "sugar_total": 39,
                "fat_total": 0,
                "sodium": 45,
                "serving_size": "355ml",
                "servings_per_container": 1
            }
        ),
        Product(
            name="Cheerios",
            brand="General Mills",
            category="Cereal",
            price=4.99,
            nutrition={
                "calories": 110,
                "protein": 3,
                "carbs_total": 22,
                "sugar_total": 2,
                "fat_total": 2,
                "sodium": 190,
                "dietary_fiber": 3,
                "serving_size": "28g",
                "servings_per_container": 14
            }
        ),
    ]

    for product in test_products:
        print(f"📱 Analyzing: {product.name}")
        print(f"   Brand: {product.brand}")
        print(f"   Price: ${product.price}")

        if product.nutrition:
            print(f"   Calories: {product.nutrition.get('calories', 0)}")
            print(f"   Protein: {product.nutrition.get('protein', 0)}g")
            print(f"   Sugar: {product.nutrition.get('sugar_total', 0)}g")

        print("\n   🤖 Evaluating with AI Agent...\n")

        # Evaluate product
        evaluation = await agent.evaluate_product(product, user_profile)

        # Display results
        print(f"   📊 Overall Score: {evaluation['overall']['score']}/100")
        print(f"   {evaluation['overall']['recommendation_emoji']} {evaluation['overall']['recommendation']}")
        print(f"\n   ❤️  Health Score: {evaluation['health_analysis']['score']}/100")
        print(f"   💪 Fitness Score: {evaluation['fitness_analysis']['score']}/100")
        print(f"   💰 Price Rating: {evaluation['price_analysis']['rating']}")

        if 'companion_message' in evaluation:
            print(f"\n   💬 AI Companion Message:")
            print("   " + "-"*66)
            for line in evaluation['companion_message'].split('\n'):
                print(f"   {line}")
            print("   " + "-"*66)

        print("\n" + "="*70 + "\n")

    print("\n✓ Demo completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
