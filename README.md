# AI Income Research Bot

An AI-powered bot that searches the internet, finds the best ways to make money online using AI, matches them to your skills, and builds you a personalized 30-day business plan — then coaches you daily.

**Goal:** $5,000/month · Under $300 startup · ~2 hours/day work

---

## What It Does

1. **Deep Internet Research** — Searches the entire web for the most successful AI income methods in 2026, which AI tools generate the most money, and what startup costs look like
2. **AI Analysis** — Uses Claude AI to analyze the research and rank the top 5 methods by real-world results
3. **Personal Interview** — Asks you 12 questions to understand your skills, time, and budget
4. **Personalized Matching** — Picks the best 2-3 methods specifically for YOU (not generic advice)
5. **30-Day Business Plan** — Day-by-day action plan including scripts, pricing, and where to find clients
6. **Daily AI Coach** — Ongoing chat partner that teaches you how to execute and helps you solve problems

---

## Quick Start

### Step 1 — Get Your Free API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Click **API Keys** → **Create Key**
4. Copy the key

### Step 2 — Set Up
```bash
# Clone or navigate to this folder
cd Hill

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Open .env and paste your API key
```

### Step 3 — Run the Bot
```bash
# Full session (recommended for first time)
python main.py

# Just the research phase
python main.py --research

# Build a plan using saved research
python main.py --plan

# Jump straight to coaching chat
python main.py --coach
```

---

## Session Flow

```
PHASE 1: Research    → Searches 8 different queries across the web
PHASE 2: Analysis   → AI analyzes findings, ranks top 5 methods
PHASE 3: Interview  → 12 questions about your skills and goals
PHASE 4: Recommend  → Personalized top 2-3 methods for YOU
PHASE 5: Plan       → Full 30-day launch plan for your chosen method
PHASE 6: Coach      → Ongoing chat to help you execute
```

Sessions are automatically saved to `~/.ai_income_bot/` so you never lose your plan.

---

## Startup Cost Breakdown (Under $300)

| Tool | Monthly Cost | Free Alternative |
|------|-------------|-----------------|
| Claude API | ~$20-50 | Free tier available |
| ChatGPT Plus | $20 | ChatGPT free tier |
| Canva Pro | $13 | Canva free |
| Website/Domain | $10-15 | Carrd free |
| **Total** | **~$63-98** | **$0 to start** |

---

## Top 5 AI Income Methods (2026 Research)

Based on live research, these are the methods with the highest success rates:

1. **AI Content Writing & Social Media Management** — $2K-8K/month, fastest path to income
2. **AI Freelance Services (copywriting, email, SEO)** — $1.5K-6K/month, easiest to start
3. **AI Automation Agency (chatbots, workflows for businesses)** — $3K-15K/month, highest ceiling
4. **AI Digital Products (courses, templates, prompts)** — $500-5K/month, most passive
5. **AI Prompt Engineering & Consulting** — $2K-10K/month, growing demand

---

## Requirements

- Python 3.10+
- Anthropic API key (free tier works)
- Internet connection

---

## Files

```
Hill/
├── main.py              ← Run this
├── requirements.txt     ← Install these
├── .env.example         ← Copy to .env, add your API key
└── src/
    ├── researcher.py    ← Web search + scraping engine
    ├── advisor.py       ← Claude AI analysis + coaching
    └── storage.py       ← Save/load sessions
```

---

## Tips for Success

- **Be specific in the interview** — the more detail you give about your skills, the better the plan
- **Start with Method #1** recommended for you — don't overthink it
- **Use the coach daily** — ask it "what should I do today?" every morning
- **$5K Month 1 is possible** but requires hitting the ground running — the plan will tell you exactly how
