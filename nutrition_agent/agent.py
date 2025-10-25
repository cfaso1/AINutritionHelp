"""
Extended quick check for ADK Nutrition Advisor agent
Uses the verified working API key setup.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.adk.agents import LlmAgent

# Import your tool functions
from agents.barcode_scanner import scan_barcode
from agents.health_evaluator import evaluate_health
from agents.price_evaluator import evaluate_price
from agents.fitness_evaluator import evaluate_fitness

# ✅ Keep this — your verified key loader
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_GENAI_API_KEY"))

# ✅ Sanity check (keep this exactly)
resp = client.models.generate_content(model="gemini-2.0-flash", contents="Say hello")
print("Gemini test response:", resp.text)

# 🧠 Now that we know the key works, initialize your ADK LLM agent
root_agent = LlmAgent(
    name="NutritionalAdvisor",
    model="gemini-2.5-flash",  # can use 2.0 or 2.5, depending on ADK support
    api_key=os.getenv("GOOGLE_GENAI_API_KEY"),
    instruction="""You are a nutritional goal advisor. Your task is to analyze grocery products' nutritional data and validate them against the user's specific health and fitness goals.

Your capabilities:
1. Scan product barcodes to retrieve detailed information
2. Evaluate products against health goals (low sugar, high protein, heart health, etc.)
3. Assess products for fitness goals (muscle building, weight loss, endurance, etc.)
4. Analyze pricing and value for money

When a user provides a barcode:
- First, use scan_barcode to get the product information
- Ask the user about their health and fitness goals if not provided
- Use evaluate_health to assess health goal alignment
- Use evaluate_fitness to assess fitness goal alignment
- Use evaluate_price to determine value
- Provide a comprehensive summary with actionable recommendations

Be friendly, informative, and focus on helping users make informed nutritional choices based on their specific goals.""",
    tools=[
        scan_barcode,
        evaluate_health,
        evaluate_price,
        evaluate_fitness
    ]
)

# 🧩 Optional: quick inline test to verify agent behavior
try:
    response = root_agent.run("Scan the barcode 737628064502 and tell me if it fits a high-protein diet.")
    print("Agent response:\n", response)
except Exception as e:
    print("Error during agent run:", e)
