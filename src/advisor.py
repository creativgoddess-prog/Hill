"""
AI advisor — uses Claude to analyze research, interview the user,
build a personalized income plan, and act as an ongoing coach.
"""
import os
import json
import anthropic
from rich.console import Console
from rich.markdown import Markdown

console = Console()

MODEL = "claude-opus-4-7"  # Most capable for deep analysis


def get_client() -> anthropic.Anthropic:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
        )
    return anthropic.Anthropic(api_key=key)


# ──────────────────────────────────────────────────────────────
# PHASE 1 – Analyze research and produce top-5 methods
# ──────────────────────────────────────────────────────────────

ANALYSIS_SYSTEM = """You are an expert online income strategist who specializes in AI-powered businesses.
You have just completed deep internet research on ways to make money using AI in 2026.
Your job is to analyze that research and produce the definitive top-5 list with full detail.

For each method you MUST include:
1. Method name and 1-sentence summary
2. Which AI tool(s) power it best (be specific: ChatGPT, Claude, Gemini, Midjourney, etc.) and WHY
3. Realistic income range (low / realistic / high monthly)
4. Startup cost breakdown (must be achievable under $300)
5. Time investment required (hours/day)
6. Skills needed vs skills that can be learned in 2 weeks
7. Fastest path to first $1,000
8. Realistic timeline to $5,000/month
9. Risk level (Low / Medium / High) with explanation
10. Perfect for someone who: [describe ideal candidate]

Be brutally honest about realistic timelines. Do not hype. Give real numbers."""


def analyze_research_and_rank_methods(research_text: str) -> str:
    client = get_client()

    prompt = f"""Here is the raw internet research I collected today on AI money-making methods in 2026:

{research_text}

Based on this research (plus your own extensive knowledge), produce the TOP 5 AI-POWERED INCOME METHODS for 2026.
Rank them by: (1) proven real-world results, (2) low barrier to entry, (3) fastest path to $5K/month with under $300 startup.

Format your response as clean markdown with a section for each method."""

    console.print("\n[cyan]Analyzing research with AI... (this may take 30-60 seconds)[/cyan]")

    with client.messages.stream(
        model=MODEL,
        max_tokens=4000,
        system=ANALYSIS_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        full_response = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text
        print()  # newline after streaming

    return full_response


# ──────────────────────────────────────────────────────────────
# PHASE 2 – Interview user and build skill profile
# ──────────────────────────────────────────────────────────────

INTERVIEW_QUESTIONS = [
    ("background", "What's your current job or background? (e.g. marketing, writing, customer service, IT, student, etc.)"),
    ("skills", "What skills do you already have? List anything you're good at — writing, design, talking to people, organizing, tech, etc."),
    ("ai_experience", "Have you used AI tools before? If yes, which ones and for what?"),
    ("time", "How many hours per day can you realistically commit to this? (Be honest — you mentioned ~2 hours)"),
    ("budget", "What is your actual startup budget? (You mentioned max $300 — confirm or update)"),
    ("income_goal", "What is your income goal for Month 1, Month 3, and Month 6?"),
    ("platform_comfort", "Are you comfortable with social media? Which platforms? (Instagram, TikTok, LinkedIn, YouTube, etc.)"),
    ("writing", "On a scale 1-10, how comfortable are you with writing? (1=hate it, 10=love it)"),
    ("tech_comfort", "On a scale 1-10, how comfortable are you with technology and learning new software?"),
    ("avoid", "Is there anything you absolutely do NOT want to do? (e.g. be on camera, cold call people, work on weekends, etc.)"),
    ("strengths", "What do you think is your biggest strength that could be valuable to businesses?"),
    ("why", "Why do you want to do this? What's motivating you — freedom, income, escape a job, etc.?"),
]


def run_interview() -> dict:
    """Ask the user the interview questions and collect their answers."""
    console.print("\n[bold green]━━━ SKILLS & GOALS INTERVIEW ━━━[/bold green]")
    console.print("[dim]I need to understand YOU so I can match you with the best method.[/dim]\n")

    answers = {}
    for key, question in INTERVIEW_QUESTIONS:
        console.print(f"[bold yellow]➤ {question}[/bold yellow]")
        answer = input("   Your answer: ").strip()
        answers[key] = answer
        print()

    return answers


# ──────────────────────────────────────────────────────────────
# PHASE 3 – Personalized recommendation
# ──────────────────────────────────────────────────────────────

RECOMMENDATION_SYSTEM = """You are a highly experienced online business coach who has helped hundreds of people
build AI-powered income streams. You are direct, encouraging, and realistic.

You have just seen:
1. The top 5 AI income methods discovered through deep internet research
2. A detailed profile of the specific person you are helping

Your job is to:
- Pick the BEST 2-3 methods for THIS specific person (not generic advice)
- Explain exactly WHY each fits their skills, time, and budget
- Rank them #1, #2, #3 with a clear recommendation on which to start with
- Give them an honest success probability score (0-100%) for each method
- Tell them exactly what their Week 1 looks like if they choose method #1"""


def generate_personalized_recommendation(top_methods: str, user_profile: dict) -> str:
    client = get_client()

    profile_text = "\n".join([f"- {k}: {v}" for k, v in user_profile.items()])

    prompt = f"""TOP 5 AI INCOME METHODS (from research):
{top_methods}

USER PROFILE:
{profile_text}

Based on this person's specific skills, budget, time availability, comfort level, and goals,
give me a PERSONALIZED recommendation. Be specific to THEM, not generic.
Include your honest assessment of whether $5,000 in Month 1 is realistic for them,
and if not, what the realistic Month 1 target is and when they can reach $5K/month."""

    console.print("\n[cyan]Building your personalized plan... (30-60 seconds)[/cyan]")

    with client.messages.stream(
        model=MODEL,
        max_tokens=3000,
        system=RECOMMENDATION_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        full_response = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text
        print()

    return full_response


# ──────────────────────────────────────────────────────────────
# PHASE 4 – Step-by-step business plan
# ──────────────────────────────────────────────────────────────

PLAN_SYSTEM = """You are a world-class online business strategist and step-by-step teacher.
You will create an extremely detailed, actionable 30-day launch plan for a specific person
starting a specific AI-powered income method.

The plan must be:
- DAILY for Week 1 (what to do each specific day, hour by hour if needed)
- WEEKLY for Weeks 2-4
- Include exact tools to use (with free vs paid options)
- Include exact scripts/templates they can copy-paste
- Include where to find their first clients/customers (specific platforms, groups, search terms)
- Include how much to charge and how to price their services
- Include what to say when reaching out to potential clients
- Be written so a complete beginner can follow it without any prior business experience"""


def generate_business_plan(method: str, user_profile: dict) -> str:
    client = get_client()

    profile_text = "\n".join([f"- {k}: {v}" for k, v in user_profile.items()])

    prompt = f"""Create a complete 30-DAY LAUNCH PLAN for this person:

CHOSEN METHOD: {method}

USER PROFILE:
{profile_text}

Include:
1. EXACT tools list with costs (must stay under $300 total startup)
2. Day-by-day plan for Week 1
3. Week-by-week plan for Weeks 2-4
4. First client acquisition strategy with specific platforms and outreach scripts
5. Pricing guide (what to charge and why)
6. Income milestones: Week 1, Week 2, Month 1, Month 3
7. The #1 mistake beginners make with this method and how to avoid it
8. How to use AI as your daily work partner (specific prompts to use)

Make this so detailed and actionable that they could start TODAY."""

    console.print("\n[cyan]Creating your 30-day launch plan... (this may take 60-90 seconds)[/cyan]")

    with client.messages.stream(
        model=MODEL,
        max_tokens=5000,
        system=PLAN_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        full_response = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text
        print()

    return full_response


# ──────────────────────────────────────────────────────────────
# PHASE 5 – Ongoing AI coach (chat loop)
# ──────────────────────────────────────────────────────────────

COACH_SYSTEM = """You are an AI income coach and business partner. You have:
1. Done deep research on the best AI money-making methods in 2026
2. Interviewed this specific person and understand their skills, goals, and constraints
3. Built them a personalized business plan

You are their ongoing partner. When they ask questions:
- Give specific, actionable advice (not vague motivational speech)
- Reference their specific situation and plan
- Teach them HOW things work, not just WHAT to do
- If they're stuck, diagnose the root cause and give a concrete fix
- Keep them accountable to their income goals
- Suggest specific AI prompts they can use right now

You are direct, encouraging, and results-focused."""


def start_coaching_session(user_profile: dict, plan_summary: str):
    """Interactive coaching chat loop."""
    client = get_client()
    conversation_history = []

    context = f"""USER PROFILE:
{json.dumps(user_profile, indent=2)}

THEIR BUSINESS PLAN SUMMARY:
{plan_summary[:2000]}"""

    system = COACH_SYSTEM + f"\n\nCONTEXT ABOUT THIS USER:\n{context}"

    console.print("\n[bold green]━━━ YOUR AI BUSINESS COACH IS READY ━━━[/bold green]")
    console.print("[dim]Ask me anything about your business, a specific method, how to get clients,")
    console.print("what to do today, how to use AI tools, or anything else.[/dim]")
    console.print("[dim]Type 'quit' or 'exit' to end the session.[/dim]\n")

    while True:
        try:
            user_input = input("[bold]You:[/bold] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Session ended. Come back anytime![/yellow]")
            break

        if user_input.lower() in ("quit", "exit", "q", "bye"):
            console.print("\n[green]Great session! Your plan is saved. See you tomorrow![/green]")
            break

        if not user_input:
            continue

        conversation_history.append({"role": "user", "content": user_input})

        console.print("\n[cyan]Coach:[/cyan] ", end="")
        response_text = ""

        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=2000,
                system=system,
                messages=conversation_history,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    response_text += text
            print("\n")
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")
            continue

        conversation_history.append({"role": "assistant", "content": response_text})

        # Keep context window manageable (last 20 exchanges)
        if len(conversation_history) > 40:
            conversation_history = conversation_history[-40:]
