#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║           AI INCOME RESEARCH BOT — by Hill                  ║
║  Finds the best AI-powered income methods for YOU,           ║
║  builds a personalized 30-day plan, and coaches you daily.  ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python main.py              — Full new session (research + plan)
    python main.py --research   — Re-run internet research only
    python main.py --plan       — Skip to plan (use saved research)
    python main.py --coach      — Jump straight to coaching chat
    python main.py --resume     — Resume last saved session
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load .env if present
load_dotenv()

from src.researcher import run_deep_research, format_research_for_ai
from src.advisor import (
    analyze_research_and_rank_methods,
    run_interview,
    generate_personalized_recommendation,
    generate_business_plan,
    start_coaching_session,
)
from src.storage import save_session, load_latest_session, save_plan_as_text

console = Console()


# ──────────────────────────────────────────────────────────────
# BANNER
# ──────────────────────────────────────────────────────────────

BANNER = """
[bold cyan]
 █████╗ ██╗    ██╗███╗   ██╗ ██████╗ ███╗   ███╗███████╗    ██████╗  ██████╗ ████████╗
██╔══██╗██║    ██║████╗  ██║██╔════╝ ████╗ ████║██╔════╝    ██╔══██╗██╔═══██╗╚══██╔══╝
███████║██║    ██║██╔██╗ ██║██║      ██╔████╔██║█████╗      ██████╔╝██║   ██║   ██║
██╔══██║██║    ██║██║╚██╗██║██║      ██║╚██╔╝██║██╔══╝      ██╔══██╗██║   ██║   ██║
██║  ██║██║    ██║██║ ╚████║╚██████╗ ██║ ╚═╝ ██║███████╗    ██████╔╝╚██████╔╝   ██║
╚═╝  ╚═╝╚═╝    ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝    ╚═════╝  ╚═════╝    ╚═╝
[/bold cyan]
[bold white]        Your AI-Powered Income Research & Business Building Partner[/bold white]
[dim]           Deep Research · Personalized Plan · Daily Coaching · $5K/Month Goal[/dim]
"""


def print_banner():
    console.print(BANNER)
    console.print(
        Panel(
            "[bold]What this bot does:[/bold]\n"
            "1. [cyan]RESEARCHES[/cyan] the entire internet for top AI income methods in 2026\n"
            "2. [cyan]ANALYZES[/cyan] which specific AI tools generate the most money\n"
            "3. [cyan]INTERVIEWS[/cyan] you to understand your skills, time, and budget\n"
            "4. [cyan]MATCHES[/cyan] you with the best method for YOUR specific situation\n"
            "5. [cyan]BUILDS[/cyan] a step-by-step 30-day plan to reach $5,000/month\n"
            "6. [cyan]COACHES[/cyan] you daily as your AI business partner\n\n"
            "[bold yellow]Target: $5,000/month · Startup cost: Under $300 · Work: ~2 hrs/day[/bold yellow]",
            border_style="cyan",
            title="[bold]AI Income Research Bot[/bold]",
        )
    )


# ──────────────────────────────────────────────────────────────
# PHASE RUNNERS
# ──────────────────────────────────────────────────────────────

def phase_research() -> tuple[str, str]:
    """Run internet research. Returns (raw_research_dict_str, formatted_text)."""
    console.print("\n[bold cyan]━━━ PHASE 1: DEEP INTERNET RESEARCH ━━━[/bold cyan]")
    console.print("[dim]Searching the web for the most successful AI income methods...[/dim]\n")

    research_data = {}
    progress_messages = []

    def progress_cb(current, total, query):
        pct = int((current / total) * 100)
        console.print(f"  [green][{pct:3d}%][/green] Searching: [italic]{query[:70]}[/italic]")

    research_data = run_deep_research(progress_callback=progress_cb)
    formatted = format_research_for_ai(research_data)

    console.print(f"\n[green]✓ Research complete! Collected data from {len(research_data['findings'])} search topics.[/green]")
    return research_data, formatted


def phase_analysis(formatted_research: str) -> str:
    """Feed research to AI and get top-5 methods analysis."""
    console.print("\n[bold cyan]━━━ PHASE 2: AI ANALYSIS OF TOP METHODS ━━━[/bold cyan]")
    top_methods = analyze_research_and_rank_methods(formatted_research)
    return top_methods


def phase_interview() -> dict:
    """Run the user interview."""
    console.print("\n[bold cyan]━━━ PHASE 3: YOUR PERSONAL PROFILE ━━━[/bold cyan]")
    console.print(
        "[dim]I need to know about YOU to match you with the right method.\n"
        "Be honest — vague answers = generic advice. Specific answers = personalized plan.[/dim]"
    )
    return run_interview()


def phase_recommendation(top_methods: str, user_profile: dict) -> str:
    """Generate personalized method recommendation."""
    console.print("\n[bold cyan]━━━ PHASE 4: PERSONALIZED RECOMMENDATION ━━━[/bold cyan]")
    recommendation = generate_personalized_recommendation(top_methods, user_profile)
    return recommendation


def phase_choose_method(recommendation: str) -> str:
    """Let the user choose which method to build a plan for."""
    console.print("\n[bold yellow]━━━ YOUR CHOICE ━━━[/bold yellow]")
    console.print("[dim]Based on the recommendation above, what method do you want to build?[/dim]")
    console.print("[dim](You can type the full name or a short description)[/dim]\n")
    method = input("Enter your chosen method: ").strip()
    if not method:
        method = "AI Content Writing & Social Media Management"
    return method


def phase_plan(method: str, user_profile: dict) -> str:
    """Generate the 30-day business plan."""
    console.print(f"\n[bold cyan]━━━ PHASE 5: YOUR 30-DAY PLAN FOR '{method.upper()}' ━━━[/bold cyan]")
    plan = generate_business_plan(method, user_profile)
    return plan


def phase_save(session_data: dict, plan_text: str):
    """Save everything to disk."""
    session_path = save_session(session_data)
    plan_path = save_plan_as_text(plan_text)
    console.print(f"\n[green]✓ Session saved: {session_path}[/green]")
    console.print(f"[green]✓ Business plan saved: {plan_path}[/green]")


# ──────────────────────────────────────────────────────────────
# FULL SESSION FLOW
# ──────────────────────────────────────────────────────────────

def run_full_session():
    """Run the complete flow: research → analyze → interview → recommend → plan → coach."""
    print_banner()

    console.print(
        "\n[bold]Ready to find you the best AI income method and build your business.[/bold]\n"
        "This session will take about 10-15 minutes to complete all research and planning.\n"
        "After that, you'll have a full 30-day business plan and your personal AI coach.\n"
    )

    input("Press ENTER to start the research... ")

    # Phase 1: Research
    research_data, formatted_research = phase_research()

    # Phase 2: Analysis
    top_methods = phase_analysis(formatted_research)

    console.print("\n[dim]Press ENTER to continue to your personal interview...[/dim]")
    input()

    # Phase 3: Interview
    user_profile = phase_interview()

    # Phase 4: Personalized recommendation
    recommendation = phase_recommendation(top_methods, user_profile)

    console.print("\n[dim]Press ENTER to choose your method and build your plan...[/dim]")
    input()

    # Phase 5: Choose method
    chosen_method = phase_choose_method(recommendation)

    # Phase 6: Build 30-day plan
    plan = phase_plan(chosen_method, user_profile)

    # Save everything
    session_data = {
        "top_methods": top_methods,
        "user_profile": user_profile,
        "recommendation": recommendation,
        "chosen_method": chosen_method,
        "plan": plan,
    }
    phase_save(session_data, plan)

    console.print("\n" + "═" * 60)
    console.print("[bold green]Your research is done and your plan is built![/bold green]")
    console.print("═" * 60)

    # Phase 7: Coaching
    console.print("\nWould you like to start your coaching session now?")
    start_coach = input("Enter 'yes' to start coaching, anything else to quit: ").strip().lower()
    if start_coach in ("yes", "y"):
        start_coaching_session(user_profile, plan)


def run_coach_only():
    """Resume coaching from last session."""
    session = load_latest_session()
    if not session:
        console.print("[red]No saved session found. Run 'python main.py' first to create a plan.[/red]")
        sys.exit(1)

    print_banner()
    console.print(f"\n[green]Loaded your saved plan for: {session.get('chosen_method', 'your business')}[/green]")
    start_coaching_session(
        session.get("user_profile", {}),
        session.get("plan", ""),
    )


def run_research_only():
    """Run just the research and analysis phases."""
    print_banner()
    research_data, formatted_research = phase_research()
    top_methods = phase_analysis(formatted_research)
    save_session({"top_methods": top_methods, "formatted_research": formatted_research})
    console.print("\n[green]Research complete and saved.[/green]")


def run_plan_from_saved():
    """Use saved research but run interview + plan again."""
    session = load_latest_session()
    if not session or "top_methods" not in session:
        console.print("[red]No saved research. Run 'python main.py --research' first.[/red]")
        sys.exit(1)

    print_banner()
    user_profile = phase_interview()
    recommendation = phase_recommendation(session["top_methods"], user_profile)
    chosen_method = phase_choose_method(recommendation)
    plan = phase_plan(chosen_method, user_profile)
    session.update({
        "user_profile": user_profile,
        "recommendation": recommendation,
        "chosen_method": chosen_method,
        "plan": plan,
    })
    phase_save(session, plan)


# ──────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Income Research Bot — find and build your AI-powered income stream",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--research", action="store_true", help="Run internet research only")
    parser.add_argument("--plan", action="store_true", help="Build plan from saved research")
    parser.add_argument("--coach", action="store_true", help="Start coaching session (resume saved plan)")
    parser.add_argument("--resume", action="store_true", help="Resume last session coaching")

    args = parser.parse_args()

    # Check for API key early
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print(
            Panel(
                "[bold red]ANTHROPIC_API_KEY not found![/bold red]\n\n"
                "To get your API key (free tier available):\n"
                "1. Go to [link=https://console.anthropic.com]console.anthropic.com[/link]\n"
                "2. Sign up / log in\n"
                "3. Click 'API Keys' → 'Create Key'\n"
                "4. Copy .env.example to .env and paste your key\n\n"
                "Then run this program again.",
                border_style="red",
                title="Setup Required",
            )
        )
        sys.exit(1)

    if args.research:
        run_research_only()
    elif args.plan:
        run_plan_from_saved()
    elif args.coach or args.resume:
        run_coach_only()
    else:
        run_full_session()


if __name__ == "__main__":
    main()
