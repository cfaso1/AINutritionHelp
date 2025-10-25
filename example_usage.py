#!/usr/bin/env python3
"""
Example usage of the nutrition app database.
Demonstrates user creation, profile updates, and nutrition logging.
"""

from database import (
    init_database,
    create_user,
    authenticate_user,
    update_user_profile,
    get_user_profile,
    log_nutrition,
    get_nutrition_logs,
    add_weight_entry,
    get_weight_history,
    calculate_bmi
)
import json


def main():
    """Demonstrate database functionality."""

    # 1. Initialize database
    print("=" * 60)
    print("STEP 1: Initialize Database")
    print("=" * 60)
    init_database()
    print()

    # 2. Create a new user
    print("=" * 60)
    print("STEP 2: Create New User")
    print("=" * 60)
    user_id = create_user(
        username="john_doe",
        email="john@example.com",
        password="SecurePassword123"
    )

    if user_id:
        print(f"✓ User created successfully! User ID: {user_id}")
    else:
        print("✗ User creation failed (user may already exist)")
        # For demo, let's authenticate existing user
        auth = authenticate_user("john_doe", "SecurePassword123")
        if auth:
            user_id = auth['user_id']
            print(f"✓ Authenticated existing user. User ID: {user_id}")
    print()

    # 3. Authenticate user
    print("=" * 60)
    print("STEP 3: Authenticate User")
    print("=" * 60)
    auth_result = authenticate_user("john_doe", "SecurePassword123")
    if auth_result:
        print(f"✓ Authentication successful!")
        print(f"  Username: {auth_result['username']}")
        print(f"  Email: {auth_result['email']}")
    else:
        print("✗ Authentication failed")
    print()

    # 4. Update user profile
    print("=" * 60)
    print("STEP 4: Update User Profile")
    print("=" * 60)

    # Calculate BMI
    height_cm = 175
    weight_kg = 75
    bmi = calculate_bmi(weight_kg, height_cm)

    profile_data = {
        'date_of_birth': '1990-05-15',
        'gender': 'male',
        'height_cm': height_cm,
        'current_weight_kg': weight_kg,
        'goal_type': 'muscle_gain',
        'target_weight_kg': 80,
        'activity_level': 'moderately_active',
        'diet_type': 'high_protein',
        'allergies': 'peanuts, shellfish',
        'dietary_restrictions': 'none',
        'bmi': bmi,
        'daily_calorie_target': 2500,
        'daily_protein_target_g': 150,
        'daily_carbs_target_g': 250,
        'daily_fat_target_g': 80
    }

    success = update_user_profile(user_id, profile_data)
    if success:
        print("✓ Profile updated successfully!")
        print(f"  BMI: {bmi}")
        print(f"  Goal: {profile_data['goal_type']}")
        print(f"  Daily Calorie Target: {profile_data['daily_calorie_target']} kcal")
    print()

    # 5. Get user profile
    print("=" * 60)
    print("STEP 5: Retrieve User Profile")
    print("=" * 60)
    profile = get_user_profile(user_id)
    if profile:
        print("✓ Profile retrieved:")
        print(f"  Name: {profile['username']}")
        print(f"  Age (DOB): {profile['date_of_birth']}")
        print(f"  Height: {profile['height_cm']} cm")
        print(f"  Weight: {profile['current_weight_kg']} kg")
        print(f"  BMI: {profile['bmi']}")
        print(f"  Goal: {profile['goal_type']}")
        print(f"  Activity: {profile['activity_level']}")
    print()

    # 6. Log nutrition from scanned label
    print("=" * 60)
    print("STEP 6: Log Nutrition Data")
    print("=" * 60)

    # Example nutrition data (from nutrition_reader.py output)
    nutrition_example = {
        "serving_information": {
            "serving_size": "1 bar (50g)",
            "servings_per_container": "2"
        },
        "calories": {
            "total": "210",
            "from_fat": "70"
        },
        "macronutrients": {
            "protein": {
                "amount_g": "12"
            },
            "fat": {
                "total_g": "8",
                "saturated_g": "3",
                "trans_g": "0",
                "polyunsaturated_g": None,
                "monounsaturated_g": None
            },
            "carbohydrates": {
                "total_g": "25",
                "fiber_g": "3",
                "sugars_g": "10",
                "added_sugars_g": "8"
            }
        },
        "micronutrients": {
            "cholesterol_mg": "5",
            "sodium_mg": "150",
            "potassium_mg": None,
            "calcium_mg": "100",
            "iron_mg": "2",
            "vitamin_a_mcg": None,
            "vitamin_c_mg": "0",
            "vitamin_d_mcg": None
        }
    }

    log_id = log_nutrition(
        user_id=user_id,
        nutrition_json=json.dumps(nutrition_example),
        meal_type='snack',
        food_name='Protein Bar',
        notes='Post-workout snack'
    )

    if log_id:
        print(f"✓ Nutrition logged successfully! Log ID: {log_id}")
        print(f"  Food: Protein Bar")
        print(f"  Calories: {nutrition_example['calories']['total']} kcal")
        print(f"  Protein: {nutrition_example['macronutrients']['protein']['amount_g']}g")
    print()

    # 7. Get nutrition logs
    print("=" * 60)
    print("STEP 7: Retrieve Nutrition Logs")
    print("=" * 60)
    logs = get_nutrition_logs(user_id)
    if logs:
        print(f"✓ Found {len(logs)} nutrition log(s) for today:")
        for log in logs:
            print(f"  - {log['food_name']}: {log['calories']} kcal, {log['protein_g']}g protein ({log['meal_type']})")
    print()

    # 8. Add weight entry
    print("=" * 60)
    print("STEP 8: Track Weight")
    print("=" * 60)
    weight_id = add_weight_entry(
        user_id=user_id,
        weight_kg=75.5,
        notes="Morning weigh-in"
    )

    if weight_id:
        print(f"✓ Weight entry added! Weight ID: {weight_id}")
        print(f"  Weight: 75.5 kg")
    print()

    # 9. Get weight history
    print("=" * 60)
    print("STEP 9: View Weight History")
    print("=" * 60)
    history = get_weight_history(user_id, limit=5)
    if history:
        print(f"✓ Weight history (last {len(history)} entries):")
        for entry in history:
            print(f"  - {entry['recorded_at']}: {entry['weight_kg']} kg")
    print()

    print("=" * 60)
    print("DATABASE DEMO COMPLETE!")
    print("=" * 60)
    print("\nThe database is ready for your hackathon web app!")
    print(f"Database location: nutrition_app.db")


if __name__ == "__main__":
    main()