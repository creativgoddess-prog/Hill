"""
AI advisor — uses Google Gemini (FREE) by default, or Claude if you prefer.

Free tier options:
  - Google Gemini: 1,500 free requests/day, no credit card needed
                   Get key at: aistudio.google.com (click "Get API Key")
  - Anthropic Claude: ~$5 free credit, then pay-as-you-go (~$1-5/month personal use)
                      Get key at: console.anthropic.com

Set GEMINI_API_KEY in your .env file to use Gemini (free).
Set ANTHROPIC_API_KEY to use Claude instead.
If both are set, Gemini is used by default.
"""
import os
import json
from rich.console import Console

console = Console()

GEMINI_MODEL = "gemini-2.0-flash"
CLAUDE_MODEL = "claude-opus-4-7"


# ──────────────────────────────────────────────────────────────
# Unified AI client — Gemini (free) or Claude
# ──────────────────────────────────────────────────────────────

def _get_provider() -> str:
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "claude"
    raise EnvironmentError(
        "\n\nNo AI API key found!\n\n"
        "EASIEST (FREE): Get a free Gemini key in 60 seconds:\n"
        "  1. Go to aistudio.google.com\n"
        "  2. Sign in with any Google account\n"
        "  3. Click 'Get API Key'\n"
        "  4. Add it to your .env file: GEMINI_API_KEY=your_key_here\n\n"
        "ALTERNATIVE (paid): Get a Claude key at console.anthropic.com\n"
        "  Add it to your .env file: ANTHROPIC_API_KEY=your_key_here"
    )


def ask_ai(system: str, messages: list[dict], max_tokens: int = 4000) -> str:
    """
    Send a message to Gemini (free) or Claude and return the response text.
    messages format: [{"role": "user"/"assistant", "content": "..."}]
    """
    provider = _get_provider()

    if provider == "gemini":
        return _ask_gemini(system, messages, max_tokens)
    else:
        return _ask_claude(system, messages, max_tokens)


def _ask_gemini(system: str, messages: list[dict], max_tokens: int) -> str:
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # Convert messages to Gemini format (role: "user"/"model", parts: [{text}])
    gemini_history = []
    for msg in messages[:-1]:  # All but last message go into history
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

    last_message = messages[-1]["content"] if messages else ""

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system,
        generation_config={"max_output_tokens": max_tokens, "temperature": 0.7},
    )

    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(last_message)
    return response.text


def _ask_claude(system: str, messages: list[dict], max_tokens: int) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Claude uses "assistant" role (same as our format)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text


# ──────────────────────────────────────────────────────────────
# System prompts
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


# ──────────────────────────────────────────────────────────────
# Phase functions (used by both main.py and telegram_bot.py)
# ──────────────────────────────────────────────────────────────

INTERVIEW_QUESTIONS = [
    ("background",      "What's your current job or background? (e.g. marketing, writing, customer service, IT, student, etc.)"),
    ("skills",          "What skills do you already have? List anything you're good at — writing, design, talking to people, organizing, tech, etc."),
    ("ai_experience",   "Have you used AI tools before? If yes, which ones and for what?"),
    ("time",            "How many hours per day can you realistically commit to this?"),
    ("budget",          "What is your actual startup budget?"),
    ("income_goal",     "What is your income goal for Month 1, Month 3, and Month 6?"),
    ("platform_comfort","Are you comfortable with social media? Which platforms?"),
    ("writing",         "On a scale 1-10, how comfortable are you with writing? (1=hate it, 10=love it)"),
    ("tech_comfort",    "On a scale 1-10, how comfortable are you with technology and learning new software?"),
    ("avoid",           "Is there anything you absolutely do NOT want to do? (e.g. be on camera, cold call people, work weekends)"),
    ("strengths",       "What do you think is your biggest strength that could be valuable to businesses?"),
    ("why",             "Why do you want to do this? What's motivating you — freedom, income, escape a job, etc.?"),
]


def analyze_research_and_rank_methods(research_text: str) -> str:
    prompt = (
        f"Here is the raw internet research I collected today on AI money-making methods in 2026:\n\n"
        f"{research_text}\n\n"
        "Based on this research (plus your own extensive knowledge), produce the TOP 5 AI-POWERED INCOME METHODS for 2026. "
        "Rank them by: (1) proven real-world results, (2) low barrier to entry, (3) fastest path to $5K/month with under $300 startup. "
        "Format as clean text without markdown symbols."
    )
    console.print("\n[cyan]Analyzing research with AI... (30-60 seconds)[/cyan]")
    return ask_ai(ANALYSIS_SYSTEM, [{"role": "user", "content": prompt}], max_tokens=4000)


def run_interview() -> dict:
    """Terminal interview — used by main.py only."""
    console.print("\n[bold green]━━━ SKILLS & GOALS INTERVIEW ━━━[/bold green]")
    console.print("[dim]I need to understand YOU so I can match you with the best method.[/dim]\n")
    answers = {}
    for key, question in INTERVIEW_QUESTIONS:
        console.print(f"[bold yellow]➤ {question}[/bold yellow]")
        answers[key] = input("   Your answer: ").strip()
        print()
    return answers


def generate_personalized_recommendation(top_methods: str, user_profile: dict) -> str:
    profile_text = "\n".join([f"- {k}: {v}" for k, v in user_profile.items()])
    prompt = (
        f"TOP 5 AI INCOME METHODS (from research):\n{top_methods}\n\n"
        f"USER PROFILE:\n{profile_text}\n\n"
        "Based on this person's specific skills, budget, time, and goals, give a PERSONALIZED recommendation. "
        "Pick the best 2-3 methods for THIS person. Be specific to them, not generic. "
        "Include honest success probability (0-100%) for each. "
        "Tell them what Week 1 looks like for Method #1. "
        "Include honest assessment of whether $5,000 in Month 1 is realistic for them, "
        "and if not, what the realistic Month 1 target is. Use plain text."
    )
    console.print("\n[cyan]Building your personalized plan... (30-60 seconds)[/cyan]")
    return ask_ai(RECOMMENDATION_SYSTEM, [{"role": "user", "content": prompt}], max_tokens=3000)


def generate_business_plan(method: str, user_profile: dict) -> str:
    profile_text = "\n".join([f"- {k}: {v}" for k, v in user_profile.items()])
    prompt = (
        f"Create a complete 30-DAY LAUNCH PLAN for this person.\n\n"
        f"CHOSEN METHOD: {method}\n\n"
        f"USER PROFILE:\n{profile_text}\n\n"
        "Include:\n"
        "1. EXACT tools list with costs (must stay under $300 total startup)\n"
        "2. Day-by-day plan for Week 1\n"
        "3. Week-by-week plan for Weeks 2-4\n"
        "4. First client acquisition strategy with specific platforms and outreach scripts\n"
        "5. Pricing guide (what to charge and why)\n"
        "6. Income milestones: Week 1, Week 2, Month 1, Month 3\n"
        "7. The #1 mistake beginners make with this method and how to avoid it\n"
        "8. How to use AI as your daily work partner (specific prompts to use)\n\n"
        "Make this so detailed and actionable that they could start TODAY. Use plain text."
    )
    console.print("\n[cyan]Creating your 30-day launch plan... (60-90 seconds)[/cyan]")
    return ask_ai(PLAN_SYSTEM, [{"role": "user", "content": prompt}], max_tokens=5000)


def get_coaching_reply(user_message: str, history: list[dict],
                       user_profile: dict, plan: str, chosen_method: str) -> str:
    """Get a single coaching reply given conversation history and user context."""
    profile_text = "\n".join([f"- {k}: {v}" for k, v in user_profile.items()])
    context = (
        f"USER PROFILE:\n{profile_text}\n\n"
        f"CHOSEN METHOD: {chosen_method}\n\n"
        f"THEIR PLAN (first 1500 chars):\n{plan[:1500]}"
    )
    system = COACH_SYSTEM + f"\n\nCONTEXT:\n{context}"
    messages = history + [{"role": "user", "content": user_message}]
    return ask_ai(system, messages, max_tokens=2000)


def start_coaching_session(user_profile: dict, plan_summary: str):
    """Interactive terminal coaching loop — used by main.py only."""
    console.print("\n[bold green]━━━ YOUR AI BUSINESS COACH IS READY ━━━[/bold green]")
    console.print("[dim]Ask anything. Type 'quit' to exit.[/dim]\n")

    history = []
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Session ended.[/yellow]")
            break

        if user_input.lower() in ("quit", "exit", "q", "bye"):
            console.print("\n[green]Great session! Your plan is saved.[/green]")
            break
        if not user_input:
            continue

        try:
            reply = get_coaching_reply(user_input, history, user_profile, plan_summary, "your chosen method")
            console.print(f"\n[cyan]Coach:[/cyan] {reply}\n")
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": reply})
            if len(history) > 40:
                history = history[-40:]
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")
