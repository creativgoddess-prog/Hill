#!/usr/bin/env python3
"""
Life Progression Goals — CBT / Social Anxiety / CNA Career Tracker

Three pillars:
  1. Social Anxiety (top priority) — daily exercises, graded exposure, CBT tools
  2. CBT Daily Practice — thought records, STOPP, behavioral activation
  3. CNA Career Track — step-by-step roadmap to certification and first job
"""

from src.advisor import ask_ai

# ─────────────────────────────────────────────────────────────
# SOCIAL ANXIETY — Graded Exposure Hierarchy
# ─────────────────────────────────────────────────────────────

EXPOSURE_HIERARCHY = [
    (1,  "Make eye contact with a cashier and smile"),
    (2,  "Say 'thank you' clearly to a stranger (store, bus, etc.)"),
    (3,  "Ask a store employee where to find something"),
    (4,  "Order food by speaking — no kiosk, no pointing"),
    (5,  "Make a phone call to a business (restaurant, doctor's office)"),
    (6,  "Start a short small-talk conversation with a neighbor or coworker"),
    (7,  "Introduce yourself to one new person"),
    (8,  "Join a class, club, or group activity and stay for the whole thing"),
    (9,  "Share your opinion out loud in a group (even just 1 sentence)"),
    (10, "Attend a social event alone for at least 30 minutes"),
]

ANXIETY_TIPS = [
    "Your anxiety is lying to you — people are far less focused on you than you think (spotlight effect).",
    "Anxiety peaks and then always comes down. If you stay in the situation, it WILL pass.",
    "Safety behaviors (checking phone, avoiding eye contact) feel helpful but keep anxiety alive.",
    "Imperfect action beats perfect avoidance every time.",
    "The goal isn't to feel zero anxiety — it's to act despite it.",
    "Each exposure rewires your brain. You are literally building new neural pathways.",
    "Rate your anxiety before and after each challenge. You'll see the pattern: it always drops.",
]

BREATHING_SCRIPTS = {
    "box": (
        "BOX BREATHING (4-4-4-4)\n\n"
        "1. Breathe IN slowly for 4 counts\n"
        "2. HOLD for 4 counts\n"
        "3. Breathe OUT for 4 counts\n"
        "4. HOLD for 4 counts\n\n"
        "Repeat 4 times. This activates your parasympathetic nervous system immediately.\n"
        "Use this before ANY anxiety-provoking situation."
    ),
    "478": (
        "4-7-8 BREATHING\n\n"
        "1. Exhale completely through your mouth\n"
        "2. Inhale through your nose for 4 counts\n"
        "3. Hold for 7 counts\n"
        "4. Exhale through mouth for 8 counts\n\n"
        "Repeat 4 cycles. The long exhale triggers your body's calm response.\n"
        "Best for: panic moments, racing thoughts before sleep."
    ),
    "physiological_sigh": (
        "PHYSIOLOGICAL SIGH (fastest anxiety reset)\n\n"
        "1. Take a full deep breath in through your nose\n"
        "2. At the top — take a SECOND short sniff in (to fully expand lungs)\n"
        "3. Now exhale SLOWLY and fully through your mouth\n\n"
        "Just 1-2 cycles lowers heart rate faster than any other technique.\n"
        "Use in the middle of any anxious moment — looks normal to others."
    ),
}

# ─────────────────────────────────────────────────────────────
# CBT TOOLS
# ─────────────────────────────────────────────────────────────

THOUGHT_RECORD_PROMPTS = [
    "What was the situation? (When, where, what happened?)",
    "What automatic thought popped into your head? (Write the exact words)",
    "What emotion(s) did you feel? Rate intensity 0-100%",
    "What evidence SUPPORTS this thought? (Be honest)",
    "What evidence CHALLENGES this thought? (What a friend might point out)",
    "What thinking errors are present?\n(e.g. mind reading, catastrophizing, all-or-nothing, fortune telling, personalization)",
    "Write a more balanced, realistic thought:",
    "After this exercise, how do you feel now? Rate the emotion 0-100% again",
]

THINKING_ERRORS = {
    "All-or-nothing": "Seeing things in black and white. 'I failed once so I'm a total failure.'",
    "Catastrophizing": "Expecting the worst possible outcome. 'What if everyone laughs at me?'",
    "Mind Reading": "Assuming you know what others are thinking. 'They think I'm stupid.'",
    "Fortune Telling": "Predicting a bad future. 'I know this will go wrong.'",
    "Personalization": "Taking blame for things outside your control.",
    "Filtering": "Focusing only on negatives, ignoring positives.",
    "Emotional Reasoning": "Feeling anxious means something IS dangerous. It doesn't.",
    "Should Statements": "'I should be more confident.' — This creates shame and pressure.",
    "Labeling": "Calling yourself names. 'I'm a loser' instead of 'I made a mistake.'",
    "Overgeneralization": "One bad event = 'This ALWAYS happens to me.'",
}

STOPP_STEPS = [
    "S — STOP! Pause right now. Don't react yet.",
    "T — TAKE a breath. One slow, deep breath in and out.",
    "O — OBSERVE. What am I thinking? What do I feel in my body? What's actually happening?",
    "P — PULL BACK. Zoom out. How important is this in a week? A year? What's the bigger picture?",
    "P — PRACTICE. What's the wisest thing to do right now? What would help most?",
]

BEHAVIORAL_ACTIVATION_INTRO = (
    "Depression and anxiety shrink your world — you stop doing things, feel worse, do even less.\n"
    "Behavioral Activation breaks this cycle. ACTION comes before MOTIVATION, not after.\n\n"
    "Today's exercise: Pick ONE thing you've been putting off or avoiding.\n"
    "Something small is fine — a 10-minute walk, texting a friend, stepping outside.\n\n"
    "Schedule it for a specific time TODAY. Then do it regardless of how you feel."
)

# ─────────────────────────────────────────────────────────────
# CNA CAREER ROADMAP
# ─────────────────────────────────────────────────────────────

CNA_ROADMAP = [
    {
        "step": 1,
        "title": "Research CNA Programs Near You",
        "icon": "🔍",
        "description": (
            "Find a state-approved CNA training program. Look at community colleges, "
            "vocational schools, Red Cross, and nursing homes that offer free training."
        ),
        "tasks": [
            "Search '[your city/state] CNA training program state-approved'",
            "Call 2-3 programs to ask about: start dates, cost, schedule, length",
            "Ask if they offer financial aid, payment plans, or employer-sponsored training",
            "Check if any local nursing homes will pay for training in exchange for a work commitment",
            "Note: Programs typically run 4-12 weeks and cost $300–$2,000",
        ],
        "resources": "Search: '[state] Board of Nursing approved CNA programs' for the official list",
    },
    {
        "step": 2,
        "title": "Check Prerequisites & Get Ready",
        "icon": "📋",
        "description": "Most programs require a few basic things before you can enroll.",
        "tasks": [
            "Verify you're 18+ (some states allow 16+ with parental consent)",
            "Get a background check done — nursing homes require this (most programs help with this)",
            "Get your immunizations up to date: TB test, flu shot, Hep B, MMR",
            "Get a physical exam (many programs require proof of good health)",
            "Gather: valid ID, Social Security card, high school diploma/GED",
        ],
        "resources": "Budget $50-$150 for background check + immunizations if not covered",
    },
    {
        "step": 3,
        "title": "Complete CNA Training Program",
        "icon": "📚",
        "description": "The training covers classroom instruction AND hands-on clinical skills.",
        "tasks": [
            "Attend every class — most programs have strict attendance policies",
            "Study these core skills: vital signs, personal care, transfers, range of motion, infection control",
            "Practice skills at home: watch YouTube CNA skills videos to reinforce learning",
            "Make flashcards for medical terminology (you'll need this for the exam)",
            "Complete all required clinical hours (usually 16-100 hours at a nursing facility)",
        ],
        "resources": "YouTube: search 'CNA skills demonstration' — free practice videos are excellent",
    },
    {
        "step": 4,
        "title": "Pass the CNA Competency Exam (NNAAP)",
        "icon": "🎯",
        "description": (
            "The National Nurse Aide Assessment Program (NNAAP) has two parts: "
            "written test + skills demonstration."
        ),
        "tasks": [
            "Written: 70 multiple-choice questions — study with Prometric practice tests (free online)",
            "Skills: You'll perform 5 random skills in front of an evaluator",
            "Study the most tested skills: hand washing, catheter care, bed bath, transfers, vital signs",
            "Schedule your exam as soon as your program ends (don't wait)",
            "Exam fee: ~$90-$150 (some states offer waivers)",
            "If you fail one part, you can retake — don't panic",
        ],
        "resources": "Free practice tests: prometric.com/cna — Study the Candidate Handbook for your state",
    },
    {
        "step": 5,
        "title": "Get Your State CNA License",
        "icon": "🪪",
        "description": "After passing the exam, you'll be added to your state's nurse aide registry.",
        "tasks": [
            "Your testing center submits results automatically in most states",
            "Verify your name appears on the state nurse aide registry (searchable online)",
            "Apply for your certificate/license if your state requires a separate application",
            "Keep your license active: renew every 1-2 years and complete required continuing education",
        ],
        "resources": "Search: '[your state] nurse aide registry lookup' to verify your certification",
    },
    {
        "step": 6,
        "title": "Build Your CNA Resume & Apply for Jobs",
        "icon": "📄",
        "description": "CNAs are in high demand — nursing homes, hospitals, home health agencies all hire.",
        "tasks": [
            "Write a 1-page resume: highlight your certification, clinical hours, any caregiving experience",
            "Where to apply: nursing homes, assisted living, hospitals, home health agencies, hospice",
            "Job boards: Indeed, ZipRecruiter, Care.com, local hospital career pages",
            "Apply to 5-10 places — don't wait for one to respond before applying to others",
            "Starting pay: $15-$22/hr depending on your state and facility type",
            "Hospitals pay more but prefer 1 year of experience — nursing homes are the best first job",
        ],
        "resources": "Tip: Tell every nurse and CNA you met during clinicals that you're job hunting",
    },
    {
        "step": 7,
        "title": "Prepare for CNA Interviews",
        "icon": "🗣️",
        "description": "CNA interviews focus on your attitude, reliability, and compassion — not just skills.",
        "tasks": [
            "Common questions: 'Why do you want to be a CNA?' 'How do you handle a difficult patient?'",
            "Prepare a story about why you want to help people (be genuine)",
            "Dress professionally: scrubs or business casual",
            "Bring: resume, ID, copy of your CNA certificate, references",
            "Ask about: shift times, staff-to-patient ratio, training/orientation length",
            "Send a thank-you email within 24 hours of each interview",
        ],
        "resources": (
            "Sample answer to 'Tell me about yourself': "
            "'I recently completed my CNA certification and my clinical hours gave me a real passion "
            "for patient care. I'm reliable, compassionate, and ready to grow in this field.'"
        ),
    },
    {
        "step": 8,
        "title": "Thrive & Grow in Your CNA Career",
        "icon": "🚀",
        "description": "Once hired, focus on being excellent — promotions and opportunities will follow.",
        "tasks": [
            "Show up early, stay late when needed — reliability is gold in healthcare",
            "Build relationships with the nurses — they are your advocates for advancement",
            "Ask questions and learn constantly — you're not expected to know everything",
            "Consider specializing: pediatrics, geriatrics, ICU, rehabilitation",
            "Use your CNA experience to move up: LPN, RN, or specialized certifications",
            "CNA → LPN takes ~12 months. RN → another 2 years. The path is clear from here.",
        ],
        "resources": "Many hospitals offer tuition reimbursement — ask HR about education benefits on Day 1",
    },
]


# ─────────────────────────────────────────────────────────────
# AI Coaching helpers
# ─────────────────────────────────────────────────────────────

LIFE_COACH_SYSTEM = """You are a warm, no-BS life coach and therapist-trained assistant.

Your user is working on three things:
1. Overcoming social anxiety (TOP PRIORITY) — using evidence-based CBT and exposure therapy
2. Daily CBT practice for mental wellness
3. Getting a CNA (Certified Nursing Assistant) job

Your style:
- Warm but direct. No toxic positivity. No empty "you've got this!"
- Be specific and practical. Give actual steps, not vague advice.
- Acknowledge hard feelings without wallowing in them.
- Challenge avoidance gently but firmly.
- Celebrate small wins — they matter enormously.
- Never minimize their anxiety. Never tell them to "just relax."
- You understand that social anxiety is real, treatable, and not a character flaw.

When they share a thought record or anxiety situation: help them spot thinking errors and build a balanced thought.
When they're avoiding something: help them break it into the smallest possible step.
When they're discouraged: remind them that progress is not linear and avoidance makes anxiety stronger."""


def build_life_context(user_data: dict) -> str:
    """Build a context block for the life coaching AI."""
    parts = []

    goals = user_data.get("life_goals", {})
    if goals:
        anxiety = goals.get("anxiety_baseline")
        if anxiety:
            parts.append(f"Anxiety baseline (1-10): {anxiety}")
        streak = goals.get("cbt_streak", 0)
        if streak:
            parts.append(f"CBT practice streak: {streak} days")
        exposures = goals.get("exposure_completed", [])
        if exposures:
            done = [EXPOSURE_HIERARCHY[i - 1][1] for i in exposures if 1 <= i <= 10]
            parts.append(f"Exposure challenges completed: {', '.join(done[-3:])}")
        cna = goals.get("cna_steps_done", [])
        if cna:
            parts.append(f"CNA steps completed: {cna}")
        wins = goals.get("daily_wins", [])
        if wins:
            parts.append(f"Recent wins: {'; '.join(wins[-3:])}")

    if not parts:
        parts.append("New user — just starting their life goals journey.")

    return "\n".join(parts)


def ai_life_coach(user_data: dict, conversation_history: list, user_message: str) -> str:
    """Call the AI as a life coach with full context."""
    ctx = build_life_context(user_data)
    system = LIFE_COACH_SYSTEM + f"\n\nUSER CONTEXT:\n{ctx}"

    history = conversation_history[-8:] if len(conversation_history) > 8 else conversation_history
    messages = history + [{"role": "user", "content": user_message}]

    return ask_ai(system, messages, max_tokens=600)


# ─────────────────────────────────────────────────────────────
# Formatting helpers
# ─────────────────────────────────────────────────────────────

def format_exposure_list(completed: list) -> str:
    lines = []
    for level, task in EXPOSURE_HIERARCHY:
        if level in completed:
            lines.append(f"✅ Level {level}: {task}")
        else:
            lines.append(f"⬜ Level {level}: {task}")
    return "\n".join(lines)


def format_cna_roadmap(steps_done: list) -> str:
    lines = []
    for item in CNA_ROADMAP:
        step = item["step"]
        icon = "✅" if step in steps_done else item["icon"]
        lines.append(f"{icon} Step {step}: {item['title']}")
    return "\n".join(lines)


def format_cna_step_detail(step_num: int) -> str:
    for item in CNA_ROADMAP:
        if item["step"] == step_num:
            tasks = "\n".join(f"  • {t}" for t in item["tasks"])
            return (
                f"{item['icon']} *Step {step_num}: {item['title']}*\n\n"
                f"{item['description']}\n\n"
                f"*Your tasks:*\n{tasks}\n\n"
                f"_Tip: {item['resources']}_"
            )
    return "Step not found."


def format_thinking_errors() -> str:
    return "\n".join(
        f"• *{name}*: {desc}" for name, desc in THINKING_ERRORS.items()
    )
