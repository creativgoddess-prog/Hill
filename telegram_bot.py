#!/usr/bin/env python3
"""
AI Income Research Bot — Telegram Edition
Run this on any computer (or Railway/Render cloud) and chat with it
from your iPhone/iPad via the free Telegram app.

Required environment variables:
    TELEGRAM_BOT_TOKEN   — from @BotFather on Telegram
    ANTHROPIC_API_KEY    — from console.anthropic.com
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode, ChatAction

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Conversation states ──────────────────────────────────────
(
    MAIN_MENU,
    RESEARCHING,
    SHOWING_METHODS,
    INTERVIEW,
    RECOMMENDING,
    CHOOSING_METHOD,
    PLANNING,
    COACHING,
) = range(8)

# ── Interview questions ──────────────────────────────────────
INTERVIEW_QUESTIONS = [
    ("background",      "1️⃣ What's your current job or background?\n\n(e.g. marketing, writing, customer service, IT, student, stay-at-home parent, etc.)"),
    ("skills",          "2️⃣ What skills do you already have?\n\nList anything you're good at — writing, design, talking to people, organizing, tech, cooking, fitness, etc. Don't be modest!"),
    ("ai_experience",   "3️⃣ Have you used AI tools before? Which ones and for what?\n\n(ChatGPT, Claude, Canva AI, Midjourney, etc. — say 'none' if not yet)"),
    ("time",            "4️⃣ How many hours per day can you realistically commit?\n\n(Be honest — 1 hour vs 4 hours changes the plan significantly)"),
    ("budget",          "5️⃣ What is your actual startup budget?\n\n(How much can you spend on tools/subscriptions in Month 1?)"),
    ("income_goal",     "6️⃣ What are your income goals?\n\nMonth 1 target? Month 3? Month 6?\n\n(Be specific — '$2,000 Month 1, $5,000 Month 3' is better than 'as much as possible')"),
    ("platform",        "7️⃣ Are you comfortable with social media? Which platforms?\n\n(Instagram, TikTok, LinkedIn, YouTube, Facebook, X/Twitter, etc.)"),
    ("writing",         "8️⃣ On a scale of 1-10, how comfortable are you with writing?\n\n1 = I hate writing. 10 = I write well and enjoy it."),
    ("tech",            "9️⃣ On a scale of 1-10, how comfortable are you with technology and learning new software?\n\n1 = I struggle with new apps. 10 = I pick up any tool quickly."),
    ("avoid",           "🔟 Is there anything you absolutely do NOT want to do?\n\n(e.g. be on camera, cold call strangers, work weekends, create videos, etc.)"),
    ("strengths",       "1️⃣1️⃣ What do you think is your biggest strength that could be valuable to businesses or customers?"),
    ("why",             "1️⃣2️⃣ Last one: WHY do you want to do this?\n\nWhat's really motivating you — freedom, escaping a job, extra income, building something of your own?"),
]


# ── Helper: split long text into Telegram-safe chunks ────────
def split_message(text: str, limit: int = 4000) -> list[str]:
    """Split text into chunks that fit Telegram's 4096-char limit."""
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


async def send_long_message(update: Update, text: str, parse_mode=None):
    """Send a message, splitting into parts if needed."""
    chunks = split_message(text)
    for i, chunk in enumerate(chunks):
        if i == 0:
            await update.effective_message.reply_text(chunk, parse_mode=parse_mode)
        else:
            await update.effective_chat.send_message(chunk, parse_mode=parse_mode)


async def typing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )


# ── /start ───────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()

    keyboard = [
        [InlineKeyboardButton("🔍 Search the Internet for Methods", callback_data="research")],
        [InlineKeyboardButton("⚡ Skip Research, Start Interview", callback_data="interview")],
        [InlineKeyboardButton("💬 Jump to Coaching Chat", callback_data="coach")],
        [InlineKeyboardButton("ℹ️ How This Works", callback_data="howto")],
    ]

    await update.message.reply_text(
        "👋 *Welcome to your AI Income Research Bot!*\n\n"
        "I will:\n"
        "🔍 Search the internet for the best AI money-making methods in 2026\n"
        "🎯 Match them to YOUR specific skills and goals\n"
        "📋 Build you a step-by-step 30-day business plan\n"
        "💬 Coach you daily as your AI business partner\n\n"
        "*Target: $5,000/month · Under $300 startup · ~2 hrs/day*\n\n"
        "What do you want to do first?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return MAIN_MENU


# ── How it works ─────────────────────────────────────────────
async def how_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]]

    await query.edit_message_text(
        "ℹ️ *How This Bot Works*\n\n"
        "*Step 1 — Research (10-15 min)*\n"
        "I search the internet across 8 different queries to find what's actually working for people making money with AI in 2026.\n\n"
        "*Step 2 — Analysis*\n"
        "I feed all that research to Claude AI, which ranks the Top 5 methods by real-world results, startup cost, and income potential.\n\n"
        "*Step 3 — Your Interview*\n"
        "I ask you 12 questions about your skills, time, budget, and goals. The more honest you are, the better your plan.\n\n"
        "*Step 4 — Personalized Match*\n"
        "Based on YOU, I pick the 2-3 best methods with a success probability and explain exactly why.\n\n"
        "*Step 5 — 30-Day Plan*\n"
        "Day-by-day action plan: what to do, what tools to use, what to charge, where to find clients, copy-paste scripts.\n\n"
        "*Step 6 — Daily Coaching*\n"
        "Chat with me anytime. Ask 'what should I do today?' or any question about your business.\n\n"
        "💡 *Tip: The research phase takes 10-15 minutes. You can skip it if you want to go straight to the interview.*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return MAIN_MENU


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔍 Search the Internet for Methods", callback_data="research")],
        [InlineKeyboardButton("⚡ Skip Research, Start Interview", callback_data="interview")],
        [InlineKeyboardButton("💬 Jump to Coaching Chat", callback_data="coach")],
        [InlineKeyboardButton("ℹ️ How This Works", callback_data="howto")],
    ]
    await query.edit_message_text(
        "What do you want to do?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return MAIN_MENU


# ── RESEARCH PHASE ───────────────────────────────────────────
async def start_research(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🔍 *Starting deep internet research...*\n\n"
        "I'm searching the web for the best AI income methods in 2026. "
        "This takes about 10-15 minutes.\n\n"
        "⏳ I'll message you as each search topic completes. Sit tight!",
        parse_mode=ParseMode.MARKDOWN,
    )

    # Run research in background
    asyncio.create_task(run_research_task(update, context))
    return RESEARCHING


async def run_research_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run research in a background task and message the user with progress."""
    chat_id = update.effective_chat.id

    from src.researcher import run_deep_research, format_research_for_ai, RESEARCH_QUERIES
    from src.advisor import analyze_research_and_rank_methods

    total = len(RESEARCH_QUERIES)
    progress_msg = await context.bot.send_message(
        chat_id=chat_id,
        text="🔍 Research progress:\n" + "\n".join([f"⬜ {q[:50]}..." for q in RESEARCH_QUERIES]),
    )

    completed = []

    def progress_cb(current, total, query):
        completed.append(query[:50] + "...")

    import threading

    research_result = {}

    def do_research():
        research_result["data"] = run_deep_research(progress_callback=progress_cb)

    thread = threading.Thread(target=do_research, daemon=True)
    thread.start()

    # Poll progress every 5 seconds and update the message
    while thread.is_alive():
        await asyncio.sleep(5)
        if completed:
            done_lines = "\n".join([f"✅ {q}" for q in completed])
            remaining = [q[:50] + "..." for q in RESEARCH_QUERIES[len(completed):]]
            remaining_lines = "\n".join([f"⬜ {q}" for q in remaining])
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=progress_msg.message_id,
                    text=f"🔍 Research progress:\n{done_lines}\n{remaining_lines}",
                )
            except Exception:
                pass

    # Mark all done
    try:
        done_lines = "\n".join([f"✅ {q[:50]}..." for q in RESEARCH_QUERIES])
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=progress_msg.message_id,
            text=f"✅ All searches complete!\n{done_lines}",
        )
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=chat_id,
        text="🧠 *Analyzing everything with AI...*\n\nReading all the research and ranking the top 5 methods. Give me 30-60 seconds...",
        parse_mode=ParseMode.MARKDOWN,
    )

    # Analyze with AI
    formatted = format_research_for_ai(research_result["data"])
    context.user_data["formatted_research"] = formatted

    try:
        from src.advisor import analyze_research_and_rank_methods
        import threading

        result_holder = {}

        def do_analysis():
            result_holder["text"] = analyze_research_and_rank_methods(formatted)

        t = threading.Thread(target=do_analysis, daemon=True)
        t.start()
        while t.is_alive():
            await asyncio.sleep(2)
        top_methods = result_holder.get("text", "")
        context.user_data["top_methods"] = top_methods

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Analysis error: {e}")
        return

    # Send results in chunks
    await context.bot.send_message(
        chat_id=chat_id,
        text="🎯 *Here are the TOP 5 AI INCOME METHODS for 2026:*",
        parse_mode=ParseMode.MARKDOWN,
    )

    for chunk in split_message(top_methods):
        await context.bot.send_message(chat_id=chat_id, text=chunk)

    keyboard = [
        [InlineKeyboardButton("✅ Great! Now personalize this for me →", callback_data="interview")],
    ]
    await context.bot.send_message(
        chat_id=chat_id,
        text="Now I need to learn about YOU so I can pick the best method for your specific skills and goals.\n\nReady for a quick 12-question interview?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ── INTERVIEW PHASE ──────────────────────────────────────────
async def start_interview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        await update.callback_query.answer()
        send_fn = update.callback_query.message.reply_text
    else:
        send_fn = update.message.reply_text

    context.user_data["interview_index"] = 0
    context.user_data["interview_answers"] = {}

    await send_fn(
        "📋 *Personal Skills & Goals Interview*\n\n"
        "I need to understand YOU so I can match you with the best method.\n\n"
        "Be as honest and specific as possible — vague answers get generic plans, "
        "specific answers get a plan built exactly for you.\n\n"
        "Let's go! 12 questions total.",
        parse_mode=ParseMode.MARKDOWN,
    )

    key, question = INTERVIEW_QUESTIONS[0]
    await send_fn(question)
    return INTERVIEW


async def handle_interview_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip()
    idx = context.user_data.get("interview_index", 0)
    answers = context.user_data.setdefault("interview_answers", {})

    key, _ = INTERVIEW_QUESTIONS[idx]
    answers[key] = answer
    idx += 1
    context.user_data["interview_index"] = idx

    if idx < len(INTERVIEW_QUESTIONS):
        _, next_question = INTERVIEW_QUESTIONS[idx]
        await update.message.reply_text(next_question)
        return INTERVIEW

    # All questions answered → generate recommendation
    await update.message.reply_text(
        "✅ *Interview complete!*\n\n"
        "🧠 Analyzing your profile and matching you with the best methods...\n\n"
        "This takes about 30-60 seconds.",
        parse_mode=ParseMode.MARKDOWN,
    )

    asyncio.create_task(run_recommendation_task(update, context))
    return RECOMMENDING


# ── RECOMMENDATION PHASE ─────────────────────────────────────
async def run_recommendation_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_profile = context.user_data.get("interview_answers", {})
    top_methods = context.user_data.get("top_methods", "")

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # If no prior research, use built-in knowledge
    if not top_methods:
        top_methods = (
            "Top AI income methods in 2026: "
            "1) AI Content Writing & Social Media Management, "
            "2) AI Freelance Services (copywriting, email, SEO), "
            "3) AI Automation Agency (chatbots, workflows), "
            "4) AI Digital Products (courses, templates, prompts), "
            "5) AI Prompt Engineering & Consulting."
        )

    try:
        import threading
        from src.advisor import generate_personalized_recommendation

        result_holder = {}

        def do_recommendation():
            result_holder["text"] = generate_personalized_recommendation(top_methods, user_profile)

        t = threading.Thread(target=do_recommendation, daemon=True)
        t.start()
        while t.is_alive():
            await asyncio.sleep(2)

        recommendation = result_holder.get("text", "")
        context.user_data["recommendation"] = recommendation

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: {e}")
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text="🎯 *YOUR PERSONALIZED RECOMMENDATION:*",
        parse_mode=ParseMode.MARKDOWN,
    )

    for chunk in split_message(recommendation):
        await context.bot.send_message(chat_id=chat_id, text=chunk)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "💬 *Which method do you want to build your 30-day plan for?*\n\n"
            "Type the name or a short description of the method you're choosing. "
            "(e.g. 'AI content writing' or 'social media management' or 'chatbot agency')"
        ),
        parse_mode=ParseMode.MARKDOWN,
    )

    context.user_data["awaiting_method_choice"] = True


async def handle_method_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not context.user_data.get("awaiting_method_choice"):
        return await handle_coaching_message(update, context)

    chosen_method = update.message.text.strip()
    context.user_data["chosen_method"] = chosen_method
    context.user_data["awaiting_method_choice"] = False

    await update.message.reply_text(
        f"🚀 *Building your 30-day plan for: {chosen_method}*\n\n"
        "This is the detailed, day-by-day plan. It may take 60-90 seconds to write. Hang tight!",
        parse_mode=ParseMode.MARKDOWN,
    )

    asyncio.create_task(run_plan_task(update, context))
    return PLANNING


# ── PLANNING PHASE ───────────────────────────────────────────
async def run_plan_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    method = context.user_data.get("chosen_method", "AI content writing")
    user_profile = context.user_data.get("interview_answers", {})

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        import threading
        from src.advisor import generate_business_plan

        result_holder = {}

        def do_plan():
            result_holder["text"] = generate_business_plan(method, user_profile)

        t = threading.Thread(target=do_plan, daemon=True)
        t.start()
        while t.is_alive():
            await asyncio.sleep(2)

        plan = result_holder.get("text", "")
        context.user_data["plan"] = plan

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error generating plan: {e}")
        return

    # Save session
    from src.storage import save_session, save_plan_as_text
    session_data = {
        "top_methods": context.user_data.get("top_methods", ""),
        "user_profile": user_profile,
        "recommendation": context.user_data.get("recommendation", ""),
        "chosen_method": method,
        "plan": plan,
    }
    try:
        session_path = save_session(session_data)
        plan_path = save_plan_as_text(plan)
    except Exception:
        pass

    await context.bot.send_message(
        chat_id=chat_id,
        text="📋 *YOUR 30-DAY BUSINESS LAUNCH PLAN:*",
        parse_mode=ParseMode.MARKDOWN,
    )

    for chunk in split_message(plan):
        await context.bot.send_message(chat_id=chat_id, text=chunk)
        await asyncio.sleep(0.5)

    keyboard = [
        [InlineKeyboardButton("💬 Start Daily Coaching Chat", callback_data="coach")],
        [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_menu")],
    ]
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "✅ *Your plan is ready and saved!*\n\n"
            "Now what? Start your coaching session. Ask me:\n"
            "• 'What should I do today?'\n"
            "• 'How do I find my first client?'\n"
            "• 'Write me an outreach message'\n"
            "• 'What AI prompt should I use for this?'\n"
            "• Any question about your business\n\n"
            "I'm your daily AI business partner."
        ),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    context.user_data["coaching_active"] = True


# ── COACHING PHASE ───────────────────────────────────────────
async def start_coaching(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        await update.callback_query.answer()
        send_fn = update.callback_query.message.reply_text
    else:
        send_fn = update.message.reply_text

    context.user_data["coaching_active"] = True
    context.user_data.setdefault("conversation_history", [])

    await send_fn(
        "💬 *Your AI Business Coach is ready!*\n\n"
        "Ask me anything:\n"
        "• 'What should I do today?'\n"
        "• 'How do I find my first client?'\n"
        "• 'Write me an outreach message for Instagram'\n"
        "• 'What AI prompt should I use to write a blog post?'\n"
        "• 'I'm stuck on [specific problem] — help!'\n\n"
        "Type your question below 👇",
        parse_mode=ParseMode.MARKDOWN,
    )
    return COACHING


async def handle_coaching_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_message = update.message.text.strip()
    chat_id = update.effective_chat.id

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    user_profile = context.user_data.get("interview_answers", {})
    plan = context.user_data.get("plan", "")
    chosen_method = context.user_data.get("chosen_method", "AI online business")
    history = context.user_data.setdefault("conversation_history", [])

    # Keep history manageable
    if len(history) > 30:
        history = history[-30:]
        context.user_data["conversation_history"] = history

    try:
        import threading
        from src.advisor import get_coaching_reply

        result_holder = {}

        def do_coaching():
            result_holder["text"] = get_coaching_reply(
                user_message, history, user_profile, plan, chosen_method
            )

        t = threading.Thread(target=do_coaching, daemon=True)
        t.start()
        while t.is_alive():
            await asyncio.sleep(1)

        reply = result_holder.get("text", "Sorry, try again.")
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})

    except Exception as e:
        reply = f"Sorry, I hit an error: {e}\nTry again in a moment."

    for chunk in split_message(reply):
        await update.message.reply_text(chunk)

    return COACHING


# ── /menu command ────────────────────────────────────────────
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("🔍 Search the Internet for Methods", callback_data="research")],
        [InlineKeyboardButton("⚡ Start Interview", callback_data="interview")],
        [InlineKeyboardButton("💬 Coaching Chat", callback_data="coach")],
        [InlineKeyboardButton("ℹ️ How This Works", callback_data="howto")],
    ]
    await update.message.reply_text(
        "Main Menu — what do you want to do?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return MAIN_MENU


# ── /reset command ───────────────────────────────────────────
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "🔄 Session reset! Type /start to begin again.",
    )
    return ConversationHandler.END


# ── Error handler ────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Something went wrong. Type /menu to get back on track."
        )


# ── Main ─────────────────────────────────────────────────────
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise EnvironmentError(
            "TELEGRAM_BOT_TOKEN not set. Create a bot with @BotFather on Telegram "
            "and add the token to your .env file."
        )

    gemini_key = os.getenv("GEMINI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not gemini_key and not anthropic_key:
        raise EnvironmentError(
            "No AI API key found!\n"
            "FREE option: Get a Gemini key at aistudio.google.com → add GEMINI_API_KEY to .env\n"
            "Paid option: Get a Claude key at console.anthropic.com → add ANTHROPIC_API_KEY to .env"
        )

    app = Application.builder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("menu", menu_command),
        ],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(start_research, pattern="^research$"),
                CallbackQueryHandler(start_interview, pattern="^interview$"),
                CallbackQueryHandler(start_coaching, pattern="^coach$"),
                CallbackQueryHandler(how_to, pattern="^howto$"),
                CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
            ],
            RESEARCHING: [
                CallbackQueryHandler(start_interview, pattern="^interview$"),
                CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
            ],
            SHOWING_METHODS: [
                CallbackQueryHandler(start_interview, pattern="^interview$"),
            ],
            INTERVIEW: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interview_answer),
            ],
            RECOMMENDING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_method_choice),
            ],
            CHOOSING_METHOD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_method_choice),
            ],
            PLANNING: [
                CallbackQueryHandler(start_coaching, pattern="^coach$"),
                CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_coaching_message),
            ],
            COACHING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_coaching_message),
                CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"),
                CallbackQueryHandler(start_coaching, pattern="^coach$"),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("menu", menu_command),
            CommandHandler("reset", reset_command),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_error_handler(error_handler)

    print("=" * 50)
    print("AI Income Research Bot — Telegram Edition")
    print("Bot is running. Open Telegram on your iPhone and")
    print("search for your bot by username to start chatting!")
    print("Press Ctrl+C to stop.")
    print("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
