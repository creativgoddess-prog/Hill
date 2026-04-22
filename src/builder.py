"""
Business Builder — the automation engine.

Researches the target audience's pain points, then generates:
  - Complete brand identity (name, tagline, colors, voice)
  - Full coded website (HTML/CSS/JS) ready to deploy
  - 30-day social media content calendar
  - Sales copy package (headlines, emails, ad copy)

All output is research-based and pain-point driven, not generic.
"""
import os
import json
import tempfile
from pathlib import Path
from src.advisor import ask_ai
from src.researcher import search_web

# ──────────────────────────────────────────────────────────────
# STEP 1 — Research audience pain points from the live web
# ──────────────────────────────────────────────────────────────

def research_pain_points(niche: str) -> dict:
    """
    Search the web for what this audience actually struggles with,
    fears, is embarrassed about, and desperately wants.
    """
    queries = [
        f"{niche} biggest struggles problems 2026",
        f"{niche} what people complain about forum reddit",
        f"why people fail at {niche} common mistakes",
        f"{niche} dream outcome transformation success stories",
        f"{niche} objections why people don't buy coaching",
    ]

    raw_results = []
    for q in queries:
        results = search_web(q, max_results=3)
        for r in results:
            raw_results.append(f"QUERY: {q}\nSOURCE: {r['title']}\nSNIPPET: {r['snippet']}")

    research_text = "\n\n".join(raw_results)

    system = """You are a world-class market researcher and consumer psychologist.
You specialize in identifying the deep emotional pain points, fears, desires, and
psychological triggers of specific audiences. Your research is used by the best
copywriters and marketers to create messaging that converts."""

    prompt = f"""Based on this live web research about the '{niche}' audience:

{research_text}

Extract and organize the following into a JSON object:
{{
  "top_pain_points": ["list of 5 specific, emotional pain points this audience feels"],
  "deep_fears": ["list of 3 things they are most afraid of or embarrassed about"],
  "failed_solutions": ["list of 3 things they've already tried that didn't work"],
  "dream_outcome": "the single most powerful transformation they want",
  "trigger_phrases": ["list of 5 exact phrases or words that resonate deeply with this audience"],
  "objections": ["list of 3 reasons they hesitate to invest in a solution"],
  "identity": "one sentence describing who this person is and how they see themselves"
}}

Be specific and emotional, not generic. Use the research to find real language this audience uses."""

    raw = ask_ai(system, [{"role": "user", "content": prompt}], max_tokens=1500)

    # Extract JSON from response
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {
            "top_pain_points": ["Feeling stuck and overwhelmed", "Not knowing where to start",
                                 "Wasted money on things that didn't work", "Lack of consistent results",
                                 "Imposter syndrome and self-doubt"],
            "deep_fears": ["Being judged or not taken seriously", "Failing again",
                           "Wasting more time and money"],
            "failed_solutions": ["Generic online courses", "Free YouTube advice",
                                  "Going it alone without support"],
            "dream_outcome": f"Finally achieving consistent results in {niche} with a clear system",
            "trigger_phrases": ["finally", "step-by-step", "proven", "without overwhelm", "real results"],
            "objections": ["Is this really different?", "I've tried before and it didn't work",
                           "I don't have time"],
            "identity": "Someone who knows they're capable of more but can't break through alone",
        }


# ──────────────────────────────────────────────────────────────
# STEP 2 — Generate complete brand identity
# ──────────────────────────────────────────────────────────────

def generate_brand_identity(niche: str, pain_points: dict) -> dict:
    system = """You are a top brand strategist who has built multi-million dollar personal brands.
You create brand identities that feel authentic, premium, and magnetic to the target audience.
Your brands speak directly to the customer's pain and position the founder as the guide, not the hero."""

    prompt = f"""Create a complete brand identity for a business in this niche: {niche}

TARGET AUDIENCE PSYCHOLOGY:
- Pain points: {json.dumps(pain_points.get('top_pain_points', []))}
- Deep fears: {json.dumps(pain_points.get('deep_fears', []))}
- Dream outcome: {pain_points.get('dream_outcome', '')}
- Trigger phrases they respond to: {json.dumps(pain_points.get('trigger_phrases', []))}
- Who they are: {pain_points.get('identity', '')}

Generate a JSON object with this exact structure:
{{
  "brand_name": "A memorable, unique brand name (1-3 words, not generic)",
  "tagline": "A powerful 7-10 word tagline that speaks directly to their dream outcome",
  "mission": "One sentence: what you exist to do for your clients",
  "brand_voice": "3 adjectives that describe how the brand speaks (e.g. bold, warm, direct)",
  "primary_color": "#hexcode (choose a color that fits the emotional tone)",
  "secondary_color": "#hexcode (complementary color)",
  "accent_color": "#hexcode (for CTAs and highlights)",
  "target_avatar_name": "A name for the ideal client avatar (e.g. 'Overwhelmed Emma')",
  "unique_mechanism": "The specific method/approach that makes this business different",
  "brand_promise": "The specific result clients can expect, with a timeframe",
  "name_alternatives": ["2 alternative brand name options"]
}}

The brand name must NOT include generic words like 'elite', 'pro', 'solutions', 'success'.
The tagline must reference the dream outcome or remove the #1 pain point."""

    raw = ask_ai(system, [{"role": "user", "content": prompt}], max_tokens=1000)
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return {
            "brand_name": "ClearPath",
            "tagline": "From stuck to thriving in 90 days or less",
            "mission": f"To give {niche} practitioners a proven system that finally works",
            "brand_voice": "direct, warm, real",
            "primary_color": "#1A1A2E",
            "secondary_color": "#E94560",
            "accent_color": "#F5A623",
            "target_avatar_name": "Struggling Sarah",
            "unique_mechanism": "The 3-Phase Clarity System",
            "brand_promise": "Measurable results within 30 days or we keep working",
            "name_alternatives": ["BreakThrough", "The Clear Method"],
        }


# ──────────────────────────────────────────────────────────────
# STEP 3 — Generate sales copy package
# ──────────────────────────────────────────────────────────────

def generate_sales_copy(brand: dict, niche: str, pain_points: dict, service: str) -> str:
    system = """You are a world-class direct response copywriter who charges $25,000 per sales page.
You use the PAS framework (Problem-Agitate-Solution), power words, and psychological triggers
to write copy that converts. You never use clichés. Every word earns its place.
You write with specificity — real numbers, real outcomes, real language the audience uses."""

    prompt = f"""Write a complete sales copy package for this business:

BRAND: {brand.get('brand_name')} — "{brand.get('tagline')}"
SERVICE: {service}
NICHE: {niche}
BRAND PROMISE: {brand.get('brand_promise')}
UNIQUE MECHANISM: {brand.get('unique_mechanism')}

AUDIENCE PSYCHOLOGY:
- Their #1 pain: {pain_points.get('top_pain_points', [''])[0]}
- What they fear most: {pain_points.get('deep_fears', [''])[0]}
- What they've tried: {json.dumps(pain_points.get('failed_solutions', []))}
- Dream outcome: {pain_points.get('dream_outcome')}
- Their objections: {json.dumps(pain_points.get('objections', []))}
- Trigger phrases: {json.dumps(pain_points.get('trigger_phrases', []))}

Write ALL of the following:

## HERO HEADLINES (5 options, ranked strongest to weakest)

## SUBHEADLINE (1, supports the hero headline)

## PROBLEM SECTION (3 short paragraphs using PAS — make them feel deeply understood)

## SOLUTION SECTION (3 paragraphs introducing the service as THE answer)

## BENEFITS LIST (7 specific, outcome-based bullet points — no vague promises)

## OBJECTION CRUSHERS (address the 3 objections above directly)

## EMAIL SEQUENCE (3 emails: Welcome, Pain Agitation, Offer)
Each email: subject line + full body, 150-200 words each

## AD COPY (Instagram/Facebook — 3 versions: Hook + Body + CTA, under 125 words each)

## CTA BUTTON TEXT (5 options — action-based, not generic 'click here')

Use specific language, real numbers, and make every word count. No fluff."""

    return ask_ai(system, [{"role": "user", "content": prompt}], max_tokens=4000)


# ──────────────────────────────────────────────────────────────
# STEP 4 — Generate 30-day social media content calendar
# ──────────────────────────────────────────────────────────────

def generate_social_calendar(brand: dict, niche: str, pain_points: dict, platforms: list) -> str:
    system = """You are a social media strategist who has grown faceless accounts to 100K+ followers.
You create content that stops the scroll, speaks directly to pain points, and converts followers
to buyers — without the creator ever showing their face. Your content is a mix of:
educational, relatable pain-point posts, transformation proof, myth-busting, and soft CTAs."""

    platforms_str = ", ".join(platforms) if platforms else "Instagram, TikTok"

    prompt = f"""Create a 30-day social media content calendar for:

BRAND: {brand.get('brand_name')} — {niche}
PLATFORMS: {platforms_str}
AUDIENCE PAIN: {json.dumps(pain_points.get('top_pain_points', []))}
DREAM OUTCOME: {pain_points.get('dream_outcome')}
TRIGGER PHRASES: {json.dumps(pain_points.get('trigger_phrases', []))}
BRAND VOICE: {brand.get('brand_voice')}

IMPORTANT: All content must work WITHOUT showing a face (text-based, graphics, voiceover, or carousel).

For each of the 30 days provide:
- Day number
- Post type (e.g. Pain Point, Myth Bust, Tip, Story, Social Proof, Soft CTA)
- Platform
- Hook (the first line — must stop the scroll)
- Full caption (ready to copy-paste, with line breaks for readability)
- Hashtags (10-15 researched, mix of sizes)
- Visual direction (what the graphic/image should look like — no face required)

Distribute content types:
- 10 days: Pain point / relatable posts (make them say 'omg that's me')
- 8 days: Educational / tip posts (establish authority)
- 5 days: Myth-busting posts (remove objections)
- 4 days: Transformation / results posts (social proof framing)
- 3 days: Direct offer / CTA posts"""

    return ask_ai(system, [{"role": "user", "content": prompt}], max_tokens=5000)


# ──────────────────────────────────────────────────────────────
# STEP 5 — Generate complete website HTML/CSS/JS
# ──────────────────────────────────────────────────────────────

def generate_website(brand: dict, niche: str, pain_points: dict, copy: str, service: str) -> str:
    """Generate a complete, deployable HTML website with all copy baked in."""

    system = """You are a senior full-stack developer and conversion rate optimization specialist.
You write clean, modern HTML/CSS/JS websites that are:
- Mobile-first and fully responsive
- Conversion-optimized with clear CTAs
- Visually professional (comparable to $5,000+ custom sites)
- Fast-loading with no external dependencies except Google Fonts
- SEO-ready with proper meta tags

You write the complete HTML file in one block — no placeholders, no 'insert here' comments.
Everything is filled in and ready to deploy."""

    pain_1 = pain_points.get('top_pain_points', ['feeling stuck'])[0]
    pain_2 = pain_points.get('top_pain_points', ['', 'wasting time'])[1] if len(pain_points.get('top_pain_points', [])) > 1 else 'wasting time'
    pain_3 = pain_points.get('top_pain_points', ['', '', 'no results'])[2] if len(pain_points.get('top_pain_points', [])) > 2 else 'no results'
    dream = pain_points.get('dream_outcome', 'achieving real results')
    failed = pain_points.get('failed_solutions', ['generic advice'])[0]

    prompt = f"""Build a complete, single-file HTML website for this business.

BRAND DETAILS:
- Name: {brand.get('brand_name')}
- Tagline: {brand.get('tagline')}
- Mission: {brand.get('mission')}
- Primary Color: {brand.get('primary_color', '#1A1A2E')}
- Secondary Color: {brand.get('secondary_color', '#E94560')}
- Accent Color: {brand.get('accent_color', '#F5A623')}
- Brand Promise: {brand.get('brand_promise')}
- Unique Mechanism: {brand.get('unique_mechanism')}

SERVICE: {service}
NICHE: {niche}

AUDIENCE:
- Pain 1: {pain_1}
- Pain 2: {pain_2}
- Pain 3: {pain_3}
- Dream outcome: {dream}
- What they've tried: {failed}

COPY REFERENCE (use the best headlines and copy from this):
{copy[:2000]}

Build a COMPLETE single HTML file with these sections:
1. Navigation (brand name + "Book a Call" CTA button)
2. Hero (powerful headline addressing pain, subheadline about transformation, two CTA buttons, no image needed)
3. Pain Section ("Does this sound familiar?" — 3 pain points as cards)
4. Solution Section (introduce the unique mechanism)
5. Services/Packages (3 tiers with prices — use $X,XXX format, make them premium)
6. How It Works (3-step process with icons using CSS shapes)
7. Results/Transformation (before → after framing, no real testimonials, use aspirational outcomes)
8. FAQ (5 questions addressing the main objections)
9. Final CTA section (strong urgency)
10. Footer (brand name, tagline, email placeholder)

CSS REQUIREMENTS:
- Use CSS custom properties (variables) for colors
- Inter font from Google Fonts
- Smooth scroll behavior
- Hover effects on buttons and cards
- Mobile responsive with proper breakpoints at 768px and 480px
- Gradient backgrounds for hero and CTA sections
- Card components with subtle shadows
- Animated CTA buttons (pulse or glow effect)

Return ONLY the complete HTML file. No explanation. No markdown code blocks. Just raw HTML starting with <!DOCTYPE html>"""

    return ask_ai(system, [{"role": "user", "content": prompt}], max_tokens=6000)


# ──────────────────────────────────────────────────────────────
# ORCHESTRATOR — runs the full build pipeline
# ──────────────────────────────────────────────────────────────

def build_full_business(niche: str, service: str, platforms: list,
                        progress_callback=None) -> dict:
    """
    Run the complete business build pipeline.
    Returns a dict with all generated assets.
    """
    def update(step, msg):
        if progress_callback:
            progress_callback(step, msg)

    update(1, "Researching your audience's pain points across the web...")
    pain_points = research_pain_points(niche)

    update(2, "Building your brand identity...")
    brand = generate_brand_identity(niche, pain_points)

    update(3, "Writing your sales copy package (headlines, emails, ads)...")
    sales_copy = generate_sales_copy(brand, niche, pain_points, service)

    update(4, "Generating your 30-day social media content calendar...")
    social_calendar = generate_social_calendar(brand, niche, pain_points, platforms)

    update(5, "Coding your complete website...")
    website_html = generate_website(brand, niche, pain_points, sales_copy, service)

    return {
        "brand": brand,
        "pain_points": pain_points,
        "sales_copy": sales_copy,
        "social_calendar": social_calendar,
        "website_html": website_html,
    }


def save_assets(assets: dict, output_dir: Path = None) -> dict:
    """Save all generated assets to files. Returns dict of file paths."""
    if output_dir is None:
        output_dir = Path.home() / ".ai_income_bot" / "business_assets"
    output_dir.mkdir(parents=True, exist_ok=True)

    brand_name = assets["brand"].get("brand_name", "mybrand").replace(" ", "_").lower()

    paths = {}

    # Website HTML
    html_path = output_dir / f"{brand_name}_website.html"
    html_path.write_text(assets["website_html"], encoding="utf-8")
    paths["website"] = str(html_path)

    # Sales copy
    copy_path = output_dir / f"{brand_name}_sales_copy.txt"
    copy_path.write_text(assets["sales_copy"], encoding="utf-8")
    paths["sales_copy"] = str(copy_path)

    # Social calendar
    social_path = output_dir / f"{brand_name}_30day_social_calendar.txt"
    social_path.write_text(assets["social_calendar"], encoding="utf-8")
    paths["social_calendar"] = str(social_path)

    # Brand identity
    brand_path = output_dir / f"{brand_name}_brand_identity.txt"
    brand_summary = (
        f"BRAND IDENTITY — {assets['brand'].get('brand_name')}\n"
        f"{'='*50}\n\n"
        f"Tagline: {assets['brand'].get('tagline')}\n"
        f"Mission: {assets['brand'].get('mission')}\n"
        f"Brand Voice: {assets['brand'].get('brand_voice')}\n"
        f"Brand Promise: {assets['brand'].get('brand_promise')}\n"
        f"Unique Mechanism: {assets['brand'].get('unique_mechanism')}\n"
        f"Target Avatar: {assets['brand'].get('target_avatar_name')}\n\n"
        f"Colors:\n"
        f"  Primary: {assets['brand'].get('primary_color')}\n"
        f"  Secondary: {assets['brand'].get('secondary_color')}\n"
        f"  Accent: {assets['brand'].get('accent_color')}\n\n"
        f"Alternative Names: {', '.join(assets['brand'].get('name_alternatives', []))}\n\n"
        f"AUDIENCE PAIN POINTS\n{'='*50}\n"
        + "\n".join(f"• {p}" for p in assets["pain_points"].get("top_pain_points", [])) + "\n\n"
        f"TRIGGER PHRASES\n{'='*50}\n"
        + "\n".join(f'• "{p}"' for p in assets["pain_points"].get("trigger_phrases", []))
    )
    brand_path.write_text(brand_summary, encoding="utf-8")
    paths["brand"] = str(brand_path)

    return paths
