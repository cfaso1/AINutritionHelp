#!/usr/bin/env python3
"""
AI-Optimized Nutrition Label Scanner
Extracts nutrition data from images and outputs structured JSON for AI interpretation.

INSTALLATION:
    pip install pytesseract Pillow

USAGE:
    python nutrition_reader.py label.jpg
    python nutrition_reader.py label.jpg --json output.json
"""

import sys
import re
import json
from PIL import Image
import pytesseract


def extract_text_from_image(image_path):
    """Use OCR to extract text from an image file."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config='--psm 6')
        return text
    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading image: {e}")
        sys.exit(1)


def extract_numeric_value(text):
    """Extract just the numeric value from a string like '10g' -> '10'"""
    match = re.search(r'(\d+\.?\d*)', text)
    return match.group(1) if match else None


def parse_nutrition_info(ocr_text):
    """
    Parse OCR text to extract nutrition information.
    Returns detailed hierarchical JSON optimized for AI interpretation.
    """
    # Initialize detailed hierarchical structure for AI
    nutrition_data = {
        "serving_information": {
            "serving_size": None,
            "servings_per_container": None
        },
        "calories": {
            "total": None,
            "from_fat": None
        },
        "macronutrients": {
            "protein": {
                "amount_g": None
            },
            "fat": {
                "total_g": None,
                "saturated_g": None,
                "trans_g": None,
                "polyunsaturated_g": None,
                "monounsaturated_g": None
            },
            "carbohydrates": {
                "total_g": None,
                "fiber_g": None,
                "sugars_g": None,
                "added_sugars_g": None
            }
        },
        "micronutrients": {
            "cholesterol_mg": None,
            "sodium_mg": None,
            "potassium_mg": None,
            "calcium_mg": None,
            "iron_mg": None,
            "vitamin_a_mcg": None,
            "vitamin_c_mg": None,
            "vitamin_d_mcg": None
        }
    }

    text_lower = ocr_text.lower()

    # Also keep original text for some patterns
    lines = ocr_text.split('\n')

    # Extract Serving Size
    for pattern in [
        r'serving\s+size\s*[:.]?\s*([^\n]+)',
        r'serv\.?\s+size\s*[:.]?\s*([^\n]+)',
        r'servings?\s*[:.]?\s*([^\n]+)',
        r'serving[:\s]+([^\n]+)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            serving_text = match.group(1).strip()
            serving_text = re.sub(r'\s+', ' ', serving_text)
            nutrition_data['serving_information']['serving_size'] = serving_text[:60]
            break

    # Extract Servings Per Container
    for pattern in [
        r'servings?\s+per\s+container\s*[:.]?\s*(\d+\.?\d*)',
        r'servings?\s*[:.]?\s*(\d+\.?\d*)\s*per\s+container',
        r'container\s*[:.]?\s*(\d+\.?\d*)\s*servings?',
        r'about\s+(\d+\.?\d*)\s*servings?',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['serving_information']['servings_per_container'] = match.group(1)
            break

    # Extract Calories
    for pattern in [
        r'calories?\s*[:.]?\s*(\d+)',
        r'(\d+)\s*calories?',
        r'energy\s*[:.]?\s*(\d+)',
        r'cal\s*[:.]?\s*(\d+)',
        r'kcal\s*[:.]?\s*(\d+)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            cal_value = match.group(1)
            if int(cal_value) > 5:
                nutrition_data['calories']['total'] = cal_value
                break

    # Extract Calories from Fat
    for pattern in [
        r'calories?\s+from\s+fat\s*[:.]?\s*(\d+)',
        r'fat\s+calories?\s*[:.]?\s*(\d+)',
        r'cal\.?\s+from\s+fat\s*[:.]?\s*(\d+)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['calories']['from_fat'] = match.group(1)
            break

    # Extract Total Fat
    for pattern in [
        r'total\s+fat\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'total\s+fat\s*[:.]?\s*(\d+\.?\d*)',
        r'fat\s+total\s*[:.]?\s*(\d+\.?\d*)',
        r'(?:^|\n)\s*fat\s*[:.]?\s*(\d+\.?\d*)\s*g',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
        if match:
            nutrition_data['macronutrients']['fat']['total_g'] = match.group(1)
            break

    # Extract Saturated Fat
    for pattern in [
        r'saturated\s+fat\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'saturated\s+fat\s*[:.]?\s*(\d+\.?\d*)',
        r'sat\.?\s+fat\s*[:.]?\s*(\d+\.?\d*)',
        r'saturated\s*[:.]?\s*(\d+\.?\d*)\s*g',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['macronutrients']['fat']['saturated_g'] = match.group(1)
            break

    # Extract Trans Fat
    for pattern in [
        r'trans\s+fat\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'trans\s+fat\s*[:.]?\s*(\d+\.?\d*)',
        r'trans\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'trans[-\s]fat\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['macronutrients']['fat']['trans_g'] = match.group(1)
            break

    # Extract Polyunsaturated Fat
    for pattern in [
        r'polyunsaturated\s+fat\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'polyunsaturated\s+fat\s*[:.]?\s*(\d+\.?\d*)',
        r'poly\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'polyunsat\w*\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['macronutrients']['fat']['polyunsaturated_g'] = match.group(1)
            break

    # Extract Monounsaturated Fat
    for pattern in [
        r'monounsaturated\s+fat\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'monounsaturated\s+fat\s*[:.]?\s*(\d+\.?\d*)',
        r'mono\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'monounsat\w*\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['macronutrients']['fat']['monounsaturated_g'] = match.group(1)
            break

    # Extract Total Carbohydrate
    for pattern in [
        r'total\s+carbohydrate[s]?\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'total\s+carbohydrate[s]?\s*[:.]?\s*(\d+\.?\d*)',
        r'carbohydrate[s]?\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'carbohydrate[s]?\s*[:.]?\s*(\d+\.?\d*)',
        r'carb[s]?\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'total\s+carb[s]?\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['macronutrients']['carbohydrates']['total_g'] = match.group(1)
            break

    # Extract Dietary Fiber
    for pattern in [
        r'dietary\s+fiber\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'dietary\s+fiber\s*[:.]?\s*(\d+\.?\d*)',
        r'fiber\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'fiber\s*[:.]?\s*(\d+\.?\d*)',
        r'fibre\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['macronutrients']['carbohydrates']['fiber_g'] = match.group(1)
            break

    # Extract Total Sugars
    for pattern in [
        r'total\s+sugar[s]?\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'total\s+sugar[s]?\s*[:.]?\s*(\d+\.?\d*)',
        r'sugar[s]?\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'sugar[s]?\s*[:.]?\s*(\d+\.?\d*)',
        r'sugars\s+(\d+\.?\d*)\s*g',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['macronutrients']['carbohydrates']['sugars_g'] = match.group(1)
            break

    # Extract Added Sugars
    for pattern in [
        r'added\s+sugar[s]?\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'added\s+sugar[s]?\s*[:.]?\s*(\d+\.?\d*)',
        r'incl\.?\s+(\d+\.?\d*)\s*g\s+added\s+sugar',
        r'includes\s+(\d+\.?\d*)\s*g.*sugar',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['macronutrients']['carbohydrates']['added_sugars_g'] = match.group(1)
            break

    # Extract Protein
    for pattern in [
        r'protein[s]?\s*[:.]?\s*(\d+\.?\d*)\s*g',
        r'protein[s]?\s*[:.]?\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*g\s*protein',
        r'prot\.?\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['macronutrients']['protein']['amount_g'] = match.group(1)
            break

    # Extract Cholesterol
    for pattern in [
        r'cholesterol\s*[:.]?\s*(\d+\.?\d*)\s*mg',
        r'cholesterol\s*[:.]?\s*(\d+\.?\d*)',
        r'chol\.?\s*[:.]?\s*(\d+\.?\d*)',
        r'cholest\.?\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['micronutrients']['cholesterol_mg'] = match.group(1)
            break

    # Extract Sodium
    for pattern in [
        r'sodium\s*[:.]?\s*(\d+\.?\d*)\s*mg',
        r'sodium\s*[:.]?\s*(\d+\.?\d*)',
        r'na\s*[:.]?\s*(\d+\.?\d*)\s*mg',
        r'salt.*?(\d+\.?\d*)\s*mg',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['micronutrients']['sodium_mg'] = match.group(1)
            break

    # Extract Potassium
    for pattern in [
        r'potassium\s*[:.]?\s*(\d+\.?\d*)\s*mg',
        r'potassium\s*[:.]?\s*(\d+\.?\d*)',
        r'k\s*[:.]?\s*(\d+\.?\d*)\s*mg',
        r'potas\.?\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['micronutrients']['potassium_mg'] = match.group(1)
            break

    # Extract Calcium
    for pattern in [
        r'calcium\s*[:.]?\s*(\d+\.?\d*)\s*mg',
        r'calcium\s*[:.]?\s*(\d+\.?\d*)',
        r'ca\s*[:.]?\s*(\d+\.?\d*)\s*mg',
        r'calc\.?\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['micronutrients']['calcium_mg'] = match.group(1)
            break

    # Extract Iron
    for pattern in [
        r'iron\s*[:.]?\s*(\d+\.?\d*)\s*mg',
        r'iron\s*[:.]?\s*(\d+\.?\d*)',
        r'fe\s*[:.]?\s*(\d+\.?\d*)\s*mg',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['micronutrients']['iron_mg'] = match.group(1)
            break

    # Extract Vitamin D
    for pattern in [
        r'vitamin\s+d\s*[:.]?\s*(\d+\.?\d*)\s*(?:mcg|µg|ug)',
        r'vitamin\s+d\s*[:.]?\s*(\d+\.?\d*)',
        r'vit\.?\s+d\s*[:.]?\s*(\d+\.?\d*)',
        r'vit\s+d\d?\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['micronutrients']['vitamin_d_mcg'] = match.group(1)
            break

    # Extract Vitamin A
    for pattern in [
        r'vitamin\s+a\s*[:.]?\s*(\d+\.?\d*)\s*(?:mcg|µg|ug|iu)',
        r'vitamin\s+a\s*[:.]?\s*(\d+\.?\d*)',
        r'vit\.?\s+a\s*[:.]?\s*(\d+\.?\d*)',
        r'vit\s+a\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['micronutrients']['vitamin_a_mcg'] = match.group(1)
            break

    # Extract Vitamin C
    for pattern in [
        r'vitamin\s+c\s*[:.]?\s*(\d+\.?\d*)\s*mg',
        r'vitamin\s+c\s*[:.]?\s*(\d+\.?\d*)',
        r'vit\.?\s+c\s*[:.]?\s*(\d+\.?\d*)',
        r'ascorbic\s+acid\s*[:.]?\s*(\d+\.?\d*)',
    ]:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            nutrition_data['micronutrients']['vitamin_c_mg'] = match.group(1)
            break

    return nutrition_data


def print_ai_prompt_suggestion(nutrition_data):
    """Generate a suggested AI prompt based on the extracted data."""
    print("\n" + "="*70)
    print("AI INTERPRETATION PROMPT SUGGESTION")
    print("="*70)
    print("\nYou can send this JSON to an AI model with a prompt like:\n")
    print('"Analyze this nutrition label data and provide:')
    print('1. Health assessment (is this food healthy?)')
    print('2. Key nutritional highlights (high/low in specific nutrients)')
    print('3. Dietary compatibility (keto, low-carb, high-protein, etc.)')
    print('4. Warnings or concerns (high sodium, added sugars, trans fats)')
    print('5. Recommendations for who should/shouldn\'t eat this"')
    print("\n" + "="*70 + "\n")


def save_to_json(nutrition_data, output_file):
    """Save nutrition data to a JSON file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(nutrition_data, indent=2, fp=f)
        print(f"\n✓ Nutrition data saved to: {output_file}")
    except Exception as e:
        print(f"\n✗ Error saving JSON file: {e}")


def main():
    """Main function to run the nutrition label scanner."""
    if len(sys.argv) < 2:
        print("Usage: python nutrition_reader.py <image_file> [--json output.json]")
        print("\nExamples:")
        print("  python nutrition_reader.py label.jpg")
        print("  python nutrition_reader.py label.jpg --json nutrition_data.json")
        sys.exit(1)

    image_path = sys.argv[1]
    json_output_file = None

    if len(sys.argv) >= 4 and sys.argv[2] == '--json':
        json_output_file = sys.argv[3]

    # Extract and parse
    ocr_text = extract_text_from_image(image_path)
    nutrition_data = parse_nutrition_info(ocr_text)

    # Display results - just the JSON
    print(json.dumps(nutrition_data, indent=2))

    # Save to file if requested
    if json_output_file:
        save_to_json(nutrition_data, json_output_file)


if __name__ == "__main__":
    main()