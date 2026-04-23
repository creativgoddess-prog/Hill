#!/usr/bin/env python3
"""
AI Income Research Bot — Telegram Edition

No state machine. The AI reads everything that's been said and done,
and picks up exactly where the conversation left off — every single time.

Required environment variables:
    TELEGRAM_BOT_TOKEN  — from @BotFather on Telegram
    GROQ_API_KEY        — from console.groq.com (free)
"""

import os
import json
import asyncio
import logging
import threading
from pathlib import Path
from dotenv import load_dotenv
from src.database import load_user, save_user, delete_user, is_available as db_available

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PicklePersistence,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction, ParseMode

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# Database helpers — load once, save on every meaningful change
# ─────────────────────────────────────────────────────────────

async def db_load(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Pull user data from Supabase into context.user_data (once per session)."""
    if context.user_data.get("_db_loaded"):
        return
    if not db_available():
        context.user_data["_db_loaded"] = True
        return
    saved = await asyncio.get_event_loop().run_in_executor(None, load_user, user_id)
    if saved:
        for k, v in saved.items():
            if k not in context.user_data:   # Don't overwrite in-memory changes
                context.user_data[k] = v
    context.user_data["_db_loaded"] = True


async def db_save(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Push current context.user_data to Supabase."""
    if not db_available():
        return
    data = {k: v for k, v in context.user_data.items() if not k.startswith("_")}
    await asyncio.get_event_loop().run_in_executor(None, save_user, user_id, data)


def split_message(text: str, limit: int = 4000) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


async def send_chunks(update: Update, text: str):
    for chunk in split_message(text):
        await update.effective_message.reply_text(chunk)


def run_in_thread(fn, *args, **kwargs):
    """Run a blocking function in a thread and return the result."""
    result = {}
    def target():
        try:
            result["value"] = fn(*args, **kwargs)
        except Exception as e:
            result["error"] = str(e)
    t = threading.Thread(target=target, daemon=True)
    t.start()
    return t, result


def profile_summary(data: dict) -> str:
    """One-line summary of what we know about the user."""
    parts = []
    if data.get("chosen_method"):
        parts.append(f"Method: {data['chosen_method']}")
    if data.get("interview_answers", {}).get("background"):
        parts.append(f"Background: {data['interview_answers']['background']}")
    if data.get("interview_answers", {}).get("income_goal"):
        parts.append(f"Goal: {data['interview_answers']['income_goal']}")
    return " · ".join(parts) if parts else "No profile yet"


# ─────────────────────────────────────────────────────────────
# Core AI brain — reads ALL context, always knows where we are
# ─────────────────────────────────────────────────────────────

MASTER_SYSTEM = """You are an AI income coach and business-building partner.
You have full memory of everything about this user — their profile, skills, goals,
chosen business method, 30-day plan, and entire conversation history.

YOUR JOB: Pick up EXACTLY where the last conversation left off.
- If they have a plan → coach them on executing it. Reference it specifically.
- If they don't have a plan yet → figure out what they need and guide them there.
- If they're asking a question → answer it with specifics from their situation.
- If they're stuck → diagnose the exact problem and give a concrete fix.
- If they want to build something (brand, website, content) → do it.

RULES:
- Never ask them to repeat information they've already given you.
- Never say "as I mentioned" — just reference it directly.
- Always be specific to THEIR situation, never generic.
- If you need to know something you don't have, ask ONE question at a time.
- Keep responses focused and actionable. No fluff.

THEIR FULL CONTEXT IS BELOW — read it before every response."""


def build_ai_context(user_data: dict) -> str:
    """Build a complete context block from everything saved in user_data."""
    sections = []

    profile = user_data.get("interview_answers", {})
    if profile:
        lines = [f"  {k}: {v}" for k, v in profile.items() if v]
        sections.append("USER PROFILE:\n" + "\n".join(lines))

    if user_data.get("chosen_method"):
        sections.append(f"CHOSEN METHOD: {user_data['chosen_method']}")

    if user_data.get("top_methods"):
        sections.append(f"RESEARCH FINDINGS (summary):\n{user_data['top_methods'][:800]}")

    if user_data.get("recommendation"):
        sections.append(f"PERSONALIZED RECOMMENDATION:\n{user_data['recommendation'][:600]}")

    if user_data.get("plan"):
        sections.append(f"THEIR 30-DAY BUSINESS PLAN:\n{user_data['plan'][:1500]}")

    if user_data.get("brand"):
        b = user_data["brand"]
        sections.append(
            f"BRAND BUILT:\n"
            f"  Name: {b.get('brand_name')}\n"
            f"  Tagline: {b.get('tagline')}\n"
            f"  Promise: {b.get('brand_promise')}"
        )

    if user_data.get("build_niche"):
        sections.append(f"BUILD NICHE: {user_data['build_niche']}")
    if user_data.get("build_service"):
        sections.append(f"BUILD SERVICE: {user_data['build_service']}")

    history = user_data.get("conversation_history", [])
    if history:
        last = history[-20:]  # Last 10 exchanges
        lines = []
        for msg in last:
            role = "User" if msg["role"] == "user" else "You"
            lines.append(f"{role}: {msg['content'][:300]}")
        sections.append("RECENT CONVERSATION:\n" + "\n".join(lines))

    if not sections:
        sections.append("No saved context yet — this is a new user.")

    return "\n\n".join(sections)


async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str):
    """Send user_message to AI with full context, reply to user, save to history."""
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )

    ctx = build_ai_context(context.user_data)
    system = MASTER_SYSTEM + f"\n\n{'='*40}\n{ctx}\n{'='*40}"

    history = context.user_data.setdefault("conversation_history", [])
    history.append({"role": "user", "content": user_message})

    messages = history[-30:]  # Keep last 15 exchanges in API call

    t, result = run_in_thread(__import__("src.advisor", fromlist=["ask_ai"]).ask_ai,
                               system, messages, 2000)
    while t.is_alive():
        await asyncio.sleep(1)

    if "error" in result:
        reply = f"I hit an error: {result['error']}\n\nTry again."
    else:
        reply = result.get("value", "Sorry, try again.")

    history.append({"role": "assistant", "content": reply})
    if len(history) > 60:
        context.user_data["conversation_history"] = history[-60:]

    await send_chunks(update, reply)

    # Save conversation to database after every AI exchange
    await db_save(context, update.effective_user.id)


# ─────────────────────────────────────────────────────────────
# /start — smart resume, never asks for things it already knows
# ─────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Always pull from Supabase first — survives redeployments
    await db_load(context, update.effective_user.id)

    has_plan    = bool(context.user_data.get("plan"))
    has_profile = bool(context.user_data.get("interview_answers"))
    has_brand   = bool(context.user_data.get("brand"))
    method      = context.user_data.get("chosen_method", "")

    if has_plan and has_profile:
        built_note = " Your brand and website are also built." if has_brand else ""
        keyboard = [[InlineKeyboardButton("💬 Continue Coaching", callback_data="coach_resume")]]
        await update.message.reply_text(
            f"👋 *Welcome back!* I remember everything.\n\n"
            f"*Your plan:* {method}\n"
            f"*Profile:* {profile_summary(context.user_data)}\n"
            f"{built_note}\n\n"
            f"Just ask me anything — or tap below to keep going.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if has_profile and not has_plan:
        keyboard = [
            [InlineKeyboardButton("📋 Build My 30-Day Plan", callback_data="make_plan")],
            [InlineKeyboardButton("🏗️ Build My Business (Brand+Site)", callback_data="build_start")],
        ]
        await update.message.reply_text(
            "👋 *Welcome back!* I have your profile saved.\n\n"
            "You haven't built your plan yet — want to do that now?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # Truly new user
    keyboard = [
        [InlineKeyboardButton("🚀 Let's Go — Start Here", callback_data="onboard")],
        [InlineKeyboardButton("🏗️ Skip to Building My Business", callback_data="build_start")],
        [InlineKeyboardButton("🔍 Just Research Methods First", callback_data="research_start")],
    ]
    await update.message.reply_text(
        "👋 *Welcome! I'm your AI income bot.*\n\n"
        "I'll research what's actually working right now, match it to your skills, "
        "build you a 30-day plan, AND automate your brand, website, and content.\n\n"
        "Where do you want to start?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─────────────────────────────────────────────────────────────
# Universal message handler — EVERY text goes through the AI
# ─────────────────────────────────────────────────────────────

async def universal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Load from Supabase if this is the first message since a restart/redeploy
    await db_load(context, update.effective_user.id)

    text = update.message.text.strip()

    # If we're mid-build, collect the next piece of info
    build_step = context.user_data.get("build_step")
    if build_step == "waiting_niche":
        context.user_data["build_niche"] = text
        context.user_data["build_step"] = "waiting_service"
        await update.message.reply_text(
            f"Got it — *{text}*\n\nWhat specific service or product will you sell?\n\n"
            "Example: '1-on-1 coaching at $500/month' or 'done-for-you content packages'",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if build_step == "waiting_service":
        context.user_data["build_service"] = text
        context.user_data["build_step"] = "waiting_platforms"
        keyboard = [
            [InlineKeyboardButton("Instagram + TikTok", callback_data="plat_ig_tt")],
            [InlineKeyboardButton("Instagram + LinkedIn", callback_data="plat_ig_li")],
            [InlineKeyboardButton("TikTok only", callback_data="plat_tt")],
            [InlineKeyboardButton("LinkedIn only", callback_data="plat_li")],
            [InlineKeyboardButton("All platforms", callback_data="plat_all")],
        ]
        await update.message.reply_text(
            "Which platforms? (All content is faceless — no camera needed)",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # If mid-interview, collect the answer
    interview_step = context.user_data.get("interview_step")
    if interview_step is not None:
        await handle_interview_message(update, context, text, interview_step)
        return

    # Otherwise: full AI with everything we know
    await ai_reply(update, context, text)


# ─────────────────────────────────────────────────────────────
# Conversational onboarding — AI extracts profile from one response
# ─────────────────────────────────────────────────────────────

ONBOARD_QUESTIONS = [
    ("background",      "What's your background and current situation?\n(Job, skills, anything you're good at)"),
    ("time_budget",     "How many hours/day can you work on this, and what's your startup budget?"),
    ("goals_avoid",     "What are your income goals, and is there anything you refuse to do?\n(e.g. no camera, no cold calling)"),
    ("why",             "Last one — why are you doing this? What's the real motivation?"),
]


async def start_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["interview_step"] = 0
    context.user_data["interview_answers"] = {}
    _, question = ONBOARD_QUESTIONS[0]
    msg = (
        "Let's get your profile set up — 4 quick questions.\n\n"
        f"*Question 1 of 4:* {question}"
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def handle_interview_message(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    answer: str, step: int):
    key, _ = ONBOARD_QUESTIONS[step]
    context.user_data["interview_answers"][key] = answer
    next_step = step + 1

    if next_step < len(ONBOARD_QUESTIONS):
        context.user_data["interview_step"] = next_step
        _, question = ONBOARD_QUESTIONS[next_step]
        await update.message.reply_text(
            f"*Question {next_step + 1} of {len(ONBOARD_QUESTIONS)}:* {question}",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        # Interview done
        context.user_data.pop("interview_step", None)
        keyboard = [
            [InlineKeyboardButton("📋 Build My 30-Day Plan", callback_data="make_plan")],
            [InlineKeyboardButton("🏗️ Build My Business (Brand+Site+Content)", callback_data="build_start")],
            [InlineKeyboardButton("🔍 Research Methods First", callback_data="research_start")],
        ]
        await update.message.reply_text(
            "✅ *Profile saved!* I know exactly what you need now.\n\n"
            "What do you want to do first?",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        # Profile complete — save to Supabase permanently
        await db_save(context, update.effective_user.id)


# ─────────────────────────────────────────────────────────────
# Button callbacks
# ─────────────────────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Resume coaching
    if data == "coach_resume":
        ctx = build_ai_context(context.user_data)
        await query.edit_message_text(
            "💬 *Ready. What do you want to work on?*\n\n"
            "Ask me anything — what to do today, how to get clients, "
            "write a script, solve a problem — I have full context of your plan.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Onboarding
    if data == "onboard":
        await start_onboarding(update, context)
        return

    # Make plan
    if data == "make_plan":
        profile = context.user_data.get("interview_answers", {})
        method = context.user_data.get("chosen_method", "")
        if not method:
            await query.edit_message_text(
                "What method do you want to build your plan for?\n\n"
                "Type it — e.g. 'AI content writing for small businesses' "
                "or 'social media management'",
            )
            context.user_data["awaiting_method"] = True
            return
        context.user_data["telegram_user_id"] = query.from_user.id
        await query.edit_message_text(
            f"📋 Building your 30-day plan for *{method}*...\n\nGive me 60-90 seconds.",
            parse_mode=ParseMode.MARKDOWN,
        )
        asyncio.create_task(run_plan_task(query.message.chat_id, context))
        return

    # Research
    if data == "research_start":
        context.user_data["telegram_user_id"] = query.from_user.id
        await query.edit_message_text(
            "🔍 *Starting internet research...*\n\n"
            "Searching for the top AI income methods right now. "
            "This takes 10-15 minutes. I'll update you as each search completes.",
            parse_mode=ParseMode.MARKDOWN,
        )
        asyncio.create_task(run_research_task(query.message.chat_id, context))
        return

    # Build start
    if data == "build_start":
        context.user_data["build_step"] = "waiting_niche"
        await query.edit_message_text(
            "🏗️ *Building Your Business — Automated*\n\n"
            "I'll generate your brand, website, 30 days of content, and sales copy.\n\n"
            "*Question 1:* What is your niche?\n\n"
            "Be specific — e.g. 'life coaching for single moms' or "
            "'AI writing services for real estate agents'",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Platform selection for build
    if data.startswith("plat_"):
        plat_map = {
            "plat_ig_tt": ["Instagram", "TikTok"],
            "plat_ig_li": ["Instagram", "LinkedIn"],
            "plat_tt": ["TikTok"],
            "plat_li": ["LinkedIn"],
            "plat_all": ["Instagram", "TikTok", "LinkedIn", "Facebook"],
        }
        platforms = plat_map.get(data, ["Instagram", "TikTok"])
        context.user_data["build_platforms"] = platforms
        context.user_data["build_step"] = "running"
        context.user_data["telegram_user_id"] = query.from_user.id

        niche   = context.user_data.get("build_niche", "")
        service = context.user_data.get("build_service", "")
        await query.edit_message_text(
            f"🚀 *Build started!*\n\n"
            f"Niche: {niche}\nService: {service}\nPlatforms: {', '.join(platforms)}\n\n"
            "Running 5 steps automatically. Updates coming...",
            parse_mode=ParseMode.MARKDOWN,
        )
        asyncio.create_task(run_build_task(query.message.chat_id, context))
        return

    # Reset confirm
    if data == "confirm_reset":
        context.user_data.clear()
        await query.edit_message_text(
            "🔄 All data cleared. Send /start to begin fresh."
        )
        return


# ─────────────────────────────────────────────────────────────
# Background tasks: research, plan, build
# ─────────────────────────────────────────────────────────────

async def run_research_task(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    from src.researcher import run_deep_research, format_research_for_ai, RESEARCH_QUERIES
    from src.advisor import analyze_research_and_rank_methods

    progress_msg = await context.bot.send_message(
        chat_id=chat_id,
        text="🔍 Research progress:\n" + "\n".join([f"⬜ {q[:55]}..." for q in RESEARCH_QUERIES]),
    )
    completed = []

    def progress_cb(current, total, query):
        completed.append(query[:55] + "...")

    t, result = run_in_thread(run_deep_research, progress_callback=progress_cb)

    while t.is_alive():
        await asyncio.sleep(5)
        if completed:
            done = "\n".join(f"✅ {q}" for q in completed)
            remaining = "\n".join(f"⬜ {q[:55]}..." for q in RESEARCH_QUERIES[len(completed):])
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=progress_msg.message_id,
                    text=f"🔍 Research progress:\n{done}\n{remaining}",
                )
            except Exception:
                pass

    research_data = result.get("value", {})
    formatted = format_research_for_ai(research_data)
    context.user_data["formatted_research"] = formatted

    await context.bot.send_message(chat_id=chat_id,
        text="🧠 Analyzing with AI... (30-60 seconds)")

    t2, result2 = run_in_thread(analyze_research_and_rank_methods, formatted)
    while t2.is_alive():
        await asyncio.sleep(2)

    top_methods = result2.get("value", "")
    context.user_data["top_methods"] = top_methods

    # Save research results permanently
    user_id = context.user_data.get("telegram_user_id", 0)
    if user_id:
        await asyncio.get_event_loop().run_in_executor(
            None, save_user, user_id,
            {k: v for k, v in context.user_data.items() if not k.startswith("_")}
        )

    await context.bot.send_message(chat_id=chat_id,
        text="🎯 *TOP 5 AI INCOME METHODS FOR 2026:*", parse_mode=ParseMode.MARKDOWN)

    for chunk in split_message(top_methods):
        await context.bot.send_message(chat_id=chat_id, text=chunk)

    keyboard = [[InlineKeyboardButton("✅ Personalize this for me →", callback_data="onboard")]]
    await context.bot.send_message(
        chat_id=chat_id,
        text="Now let me match these to YOUR specific skills and goals.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def run_plan_task(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    from src.advisor import generate_business_plan

    method  = context.user_data.get("chosen_method", "AI content writing")
    profile = context.user_data.get("interview_answers", {})

    t, result = run_in_thread(generate_business_plan, method, profile)
    while t.is_alive():
        await asyncio.sleep(2)

    plan = result.get("value", "")
    if not plan:
        await context.bot.send_message(chat_id=chat_id,
            text=f"❌ Plan error: {result.get('error', 'unknown')}")
        return

    context.user_data["plan"] = plan

    await context.bot.send_message(chat_id=chat_id,
        text="📋 *YOUR 30-DAY LAUNCH PLAN:*", parse_mode=ParseMode.MARKDOWN)

    for chunk in split_message(plan):
        await context.bot.send_message(chat_id=chat_id, text=chunk)
        await asyncio.sleep(0.4)

    # Save plan to Supabase permanently
    user_id = context.user_data.get("telegram_user_id", 0)
    if user_id:
        await asyncio.get_event_loop().run_in_executor(
            None, save_user, user_id,
            {k: v for k, v in context.user_data.items() if not k.startswith("_")}
        )

    await context.bot.send_message(
        chat_id=chat_id,
        text="✅ Plan saved permanently. Just talk to me — ask anything about your business. "
             "I'll remember everything even if the bot restarts.",
    )


async def run_build_task(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    from src.builder import build_full_business, save_assets

    niche     = context.user_data.get("build_niche", "")
    service   = context.user_data.get("build_service", "")
    platforms = context.user_data.get("build_platforms", ["Instagram", "TikTok"])

    steps = {
        1: "🔍 Step 1/5 — Researching audience pain points...",
        2: "🎨 Step 2/5 — Building brand identity...",
        3: "✍️  Step 3/5 — Writing sales copy...",
        4: "📅 Step 4/5 — Generating 30-day social calendar...",
        5: "💻 Step 5/5 — Coding your website...",
    }
    progress_msg = await context.bot.send_message(chat_id=chat_id, text="⏳ Starting...")
    current_step = {"n": 0}

    def progress_cb(step, msg):
        current_step["n"] = step

    t, result = run_in_thread(build_full_business, niche, service, platforms, progress_cb)
    last = 0
    while t.is_alive():
        await asyncio.sleep(3)
        s = current_step["n"]
        if s != last and s in steps:
            last = s
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=progress_msg.message_id,
                    text=steps[s],
                )
            except Exception:
                pass

    assets = result.get("value")
    if not assets:
        await context.bot.send_message(chat_id=chat_id,
            text=f"❌ Build error: {result.get('error', 'unknown')}")
        return

    paths = save_assets(assets)
    brand = assets["brand"]

    context.user_data["brand"]          = brand
    context.user_data["pain_points"]    = assets.get("pain_points", {})
    context.user_data["build_step"]     = None  # Build complete

    # Save brand + assets to Supabase permanently
    user_id = context.user_data.get("telegram_user_id", 0)
    if user_id:
        await asyncio.get_event_loop().run_in_executor(
            None, save_user, user_id,
            {k: v for k, v in context.user_data.items() if not k.startswith("_")}
        )

    # Send brand summary
    b_msg = (
        f"🎨 *BRAND IDENTITY*\n\n"
        f"*Name:* {brand.get('brand_name')}\n"
        f"*Tagline:* _{brand.get('tagline')}_\n"
        f"*Promise:* {brand.get('brand_promise')}\n"
        f"*Voice:* {brand.get('brand_voice')}\n"
        f"*Colors:* `{brand.get('primary_color')}` · `{brand.get('secondary_color')}` · `{brand.get('accent_color')}`"
    )
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=progress_msg.message_id,
        text=b_msg, parse_mode=ParseMode.MARKDOWN,
    )

    # Send files
    for label, path_key, caption in [
        ("💻 *Website* — upload to netlify.com/drop to go live free:", "website",
         f"{brand.get('brand_name', 'website').replace(' ','_')}_website.html"),
        ("✍️ *Sales copy* — headlines, emails, ads:", "sales_copy", "sales_copy.txt"),
        ("📅 *30-day social calendar* — faceless, copy-paste ready:", "social_calendar",
         "30_day_social_calendar.txt"),
    ]:
        await context.bot.send_message(chat_id=chat_id, text=label, parse_mode=ParseMode.MARKDOWN)
        with open(paths[path_key], "rb") as f:
            await context.bot.send_document(chat_id=chat_id, document=f, filename=caption)

    await context.bot.send_message(
        chat_id=chat_id,
        text="🎉 *Done.* Everything is saved.\n\n"
             "Just talk to me going forward — I have your full brand, plan, and profile. "
             "Ask me what to do today, how to get clients, what to post — anything.",
        parse_mode=ParseMode.MARKDOWN,
    )


# ─────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data.clear()
    # Wipe from Supabase too so redeployments don't restore old data
    if db_available():
        await asyncio.get_event_loop().run_in_executor(None, delete_user, user_id)
    await update.message.reply_text("🔄 All data wiped. Send /start to begin fresh.")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    has_profile = bool(context.user_data.get("interview_answers"))
    has_plan    = bool(context.user_data.get("plan"))
    has_brand   = bool(context.user_data.get("brand"))
    method      = context.user_data.get("chosen_method", "None yet")
    history_len = len(context.user_data.get("conversation_history", []))

    await update.message.reply_text(
        f"📊 *Your Bot Status*\n\n"
        f"Profile saved: {'✅' if has_profile else '❌'}\n"
        f"Business plan: {'✅' if has_plan else '❌'}\n"
        f"Brand built: {'✅' if has_brand else '❌'}\n"
        f"Chosen method: {method}\n"
        f"Messages in memory: {history_len}",
        parse_mode=ParseMode.MARKDOWN,
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Update error:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Something went wrong. Just send your message again."
        )


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise EnvironmentError("TELEGRAM_BOT_TOKEN not set.")

    if not any([os.getenv("GROQ_API_KEY"),
                os.getenv("GEMINI_API_KEY"),
                os.getenv("ANTHROPIC_API_KEY")]):
        raise EnvironmentError(
            "No AI key found. Add GROQ_API_KEY from console.groq.com to your .env"
        )

    persistence = PicklePersistence(filepath="bot_sessions.pkl")
    app = Application.builder().token(token).persistence(persistence).build()

    # Commands
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("reset",  cmd_reset))
    app.add_handler(CommandHandler("status", cmd_status))

    # All button taps
    app.add_handler(CallbackQueryHandler(button_handler))

    # Every text message — the AI handles it with full context
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, universal_handler))

    app.add_error_handler(error_handler)

    print("Bot running — all messages handled by context-aware AI.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
