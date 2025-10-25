import asyncio
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agents.barcode_scanner import BarcodeScannerAgent
from agents.price_evaluator import PriceEvaluatorAgent
from agents.health_evaluator import HealthEvaluatorAgent
from agents.fitness_evaluator import FitnessEvaluatorAgent
from services.llm_service import LLMService
from services.barcode_api import BarcodeAPIService
from models.user_profile import UserProfile

# Load environment variables
load_dotenv()

console = Console()


async def main():
    """Main application entry point"""
    
    # Display welcome banner
    console.print(Panel.fit(
        "[bold cyan]🥗 Nutrition AI Agent System[/bold cyan]\n"
        "[dim]Scan. Analyze. Optimize your nutrition.[/dim]",
        border_style="cyan"
    ))
    
    # Initialize services
    try:
        llm_service = LLMService(api_key=os.getenv("ANTHROPIC_API_KEY"))
        barcode_service = BarcodeAPIService(api_key=os.getenv("BARCODE_LOOKUP_API_KEY"))
        
        # Initialize agents
        scanner_agent = BarcodeScannerAgent(barcode_service)
        price_agent = PriceEvaluatorAgent(llm_service)
        health_agent = HealthEvaluatorAgent(llm_service)
        fitness_agent = FitnessEvaluatorAgent(llm_service)
        
        console.print("[green]✓[/green] All agents initialized successfully\n")
    except Exception as e:
        console.print(f"[red]✗ Error initializing system: {e}[/red]")
        return
    
    # Get user input
    console.print("[bold]Enter barcode number:[/bold]", style="yellow")
    barcode = input("> ").strip()
    
    console.print("\n[bold]Enter your health goals (comma-separated):[/bold]", style="yellow")
    console.print("[dim]Examples: low sugar, high protein, heart healthy, low sodium[/dim]")
    health_goals = input("> ").strip()
    
    console.print("\n[bold]Enter your fitness goals (comma-separated):[/bold]", style="yellow")
    console.print("[dim]Examples: muscle building, weight loss, endurance, recovery[/dim]")
    fitness_goals = input("> ").strip()
    
    # Create user profile
    user_profile = UserProfile(
        health_goals=health_goals,
        fitness_goals=fitness_goals
    )
    
    console.print("\n[cyan]🔍 Analyzing product...[/cyan]\n")
    
    try:
        # Step 1: Scan barcode
        with console.status("[bold cyan]Scanning barcode..."):
            product = await scanner_agent.scan(barcode)
        
        if not product:
            console.print("[red]✗ Product not found. Please check the barcode number.[/red]")
            return
        
        console.print(f"[green]✓[/green] Found: {product.name}")
        
        # Step 2: Evaluate price
        with console.status("[bold cyan]Evaluating price..."):
            price_analysis = await price_agent.evaluate(product)
        
        # Step 3: Evaluate health alignment
        with console.status("[bold cyan]Analyzing health alignment..."):
            health_analysis = await health_agent.evaluate(product, user_profile)
        
        # Step 4: Evaluate fitness alignment
        with console.status("[bold cyan]Analyzing fitness alignment..."):
            fitness_analysis = await fitness_agent.evaluate(product, user_profile)
        
        # Display results
        display_results(product, price_analysis, health_analysis, fitness_analysis)
        
    except Exception as e:
        console.print(f"[red]✗ Error during analysis: {e}[/red]")


def display_results(product, price_analysis, health_analysis, fitness_analysis):
    """Display analysis results in a formatted way"""
    
    # Product Information
    console.print("\n" + "="*70 + "\n")
    console.print(Panel(
        f"[bold]{product.name}[/bold]\n"
        f"Brand: {product.brand}\n"
        f"Category: {product.category}\n"
        f"Price: ${product.price:.2f}",
        title="📦 Product Information",
        border_style="blue"
    ))
    
    # Nutritional Information
    if product.nutrition:
        nutrition_table = Table(title="Nutrition Facts (per serving)", show_header=True, header_style="bold magenta")
        nutrition_table.add_column("Nutrient", style="cyan")
        nutrition_table.add_column("Amount", justify="right", style="green")
        
        for key, value in product.nutrition.items():
            nutrition_table.add_row(key.replace("_", " ").title(), str(value))
        
        console.print("\n", nutrition_table)
    
    # Price Analysis
    price_color = "green" if price_analysis["is_good_deal"] else "yellow"
    console.print(f"\n[bold]💰 Price Analysis[/bold]")
    console.print(Panel(
        f"Rating: [{price_color}]{price_analysis['rating']}[/{price_color}]\n"
        f"{price_analysis['summary']}",
        border_style=price_color
    ))
    
    # Health Analysis
    health_score = health_analysis["score"]
    health_color = "green" if health_score >= 70 else "yellow" if health_score >= 40 else "red"
    console.print(f"\n[bold]❤️ Health Goal Alignment[/bold]")
    console.print(Panel(
        f"Score: [{health_color}]{health_score}/100[/{health_color}]\n"
        f"{health_analysis['summary']}\n\n"
        f"[bold]Pros:[/bold] {', '.join(health_analysis['pros'])}\n"
        f"[bold]Cons:[/bold] {', '.join(health_analysis['cons'])}",
        border_style=health_color
    ))
    
    # Fitness Analysis
    fitness_score = fitness_analysis["score"]
    fitness_color = "green" if fitness_score >= 70 else "yellow" if fitness_score >= 40 else "red"
    console.print(f"\n[bold]💪 Fitness Goal Alignment[/bold]")
    console.print(Panel(
        f"Score: [{fitness_color}]{fitness_score}/100[/{fitness_color}]\n"
        f"{fitness_analysis['summary']}\n\n"
        f"[bold]Best for:[/bold] {fitness_analysis['best_for']}\n"
        f"[bold]Recommendation:[/bold] {fitness_analysis['recommendation']}",
        border_style=fitness_color
    ))
    
    # Overall Recommendation
    overall_score = (health_score + fitness_score) / 2
    if overall_score >= 70:
        rec = "✅ Highly Recommended"
        rec_color = "green"
    elif overall_score >= 50:
        rec = "⚠️ Acceptable with Caution"
        rec_color = "yellow"
    else:
        rec = "❌ Not Recommended"
        rec_color = "red"
    
    console.print(f"\n[bold]📊 Overall Assessment[/bold]")
    console.print(Panel(
        f"[{rec_color}]{rec}[/{rec_color}]",
        border_style=rec_color
    ))
    console.print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
