#!/usr/bin/env python3
"""
SULSUL Blog Content Engine v2
- SEO + GEO optimized prompt
- Brand guardrails (Monetization Blueprint Phase 1, 2026-08-01)
- Publish gate (banned phrases, H1, FAQ, length, cannibalization)
"""

import os
import re
import glob
import time
import argparse
from collections import Counter
import subprocess
import sys
import random
from datetime import datetime
from urllib.parse import urlparse
from openai import OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
from check_public_copy import check_text as scan_public_copy

def install_package(package):
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("duckduckgo-search")
from duckduckgo_search import DDGS

# Lazy so sibling scripts can import helpers without requiring a key at import time.
_client = None
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from load_env import load_env
from romanize import romanize as rr, spell_numbers

load_env(ROOT)
MODEL = os.environ.get("SULSUL_BLOG_MODEL", "gpt-4o")


def get_client():
    global _client
    if _client is None:
        load_env(ROOT)
        _client = OpenAI()
    return _client
OBSIDIAN_VAULT_PATH = os.path.join(ROOT, "obsidian_data")
LIBRARY_DIR = os.path.join(OBSIDIAN_VAULT_PATH, "3.Library")
VOICE_DIR = os.path.join(OBSIDIAN_VAULT_PATH, "2.Voice")
BLOG_POSTS_DIR = os.path.join(ROOT, "_posts")
REJECTED_DIR = os.path.join(ROOT, "_rejected")
# Drafts written to be read, not published. The site never loads this folder.
PREVIEW_DIR = os.path.join(ROOT, "_preview")

# Enforced here rather than in the workflow files so a stale schedule
# can never push us back into scaled-content territory.
MAX_PER_RUN = {"trend": 2, "textbook": 3}
# 2026-08-04: cut again after CEO feedback — FAQ duplicated the body and
# posts still read too long on a phone. Target a tight teaching post + CTA only.
MIN_WORDS = 320
MAX_WORDS = 650
MIN_DISTINCT_PHRASES = 5
MAX_PHRASE_REPEATS = 5
MIN_EXCHANGES = 1
MAX_H2 = 6
MIN_INLINE_IMAGES = 2
MAX_INLINE_IMAGES = 3
MAX_TABLE_COLS = 2
MAX_TABLE_ROWS = 5

# Trend seeds come from a news index rather than a web search, and the query
# rotates by day so two runs do not open with the same story.
# K-culture traffic hooks only — not finance, not generic "Korean + anything".
TREND_QUERIES = [
    "k-pop",
    "k-drama",
    "korean idol",
    "korean movie film",
    "korean food k-culture",
]
TREND_BACKOFF_SECONDS = 25

# A seed has to be about Korea or the Korean wave.
TREND_REQUIRED = re.compile(
    r"\bkorea\w*\b|\bk-?pop\b|\bk-?drama\b|\bk-?beauty\b|\bhallyu\b|\bseoul\b"
    r"|\bhangul\b|\bhanbok\b|\bkimchi\b|\bbts\b|\bblackpink\b|\bstray kids\b"
    r"|\btwice\b|\baespa\b|\bnewjeans\b|\bseventeen\b|\benhypen\b",
    re.I,
)

# Encyclopedia entries and shop fronts can mention Korea and still carry no
# story. These are the shapes that actually got published and had to be deleted.
TREND_EXCLUDED = re.compile(
    r"wikipedia|wikiwand|wiktionary|\bwiki\b|나무위키|namu\.wiki|britannica"
    r"|dictionary|\bused car\b|중고차|abcmouse|starfall|cbeebies|sofatutor"
    r"|\bclinic\b|\bhospital\b|nasal|congestion|\bstuffy\b"
    r"|\bstock\b|\bstocks\b|\bshare price\b|\binvestor|\binvestment\b|\bwall street\b"
    r"|\bmarket cap\b|\bnasdaq\b|\bnyse\b|\bipo\b|\bearnings\b|\bdividend\b"
    r"|\btrading\b|\bequity\b|\bportfolio\b|\bfinancial\b|\bsec filing\b",
    re.I,
)

# "Korean" alone is not enough — finance and business wires slip through without this.
TREND_HOOK_STOPWORDS = frozenset(
    "korean korea south north the and for with from that this their about into over "
    "after will says said year years week weeks month months news new latest".split()
)

# Topic -> cover image routing. Keep in sync with src/lib/images.ts
SCENES = {
    "cafe": "/assets/blog/scenes/cafe.jpg",
    "convenience": "/assets/blog/scenes/convenience-store.jpg",
    "transport": "/assets/blog/scenes/transport.jpg",
    "taxi": "/assets/blog/scenes/taxi.jpg",
    "bus": "/assets/blog/scenes/bus.jpg",
    "lost_wallet": "/assets/blog/scenes/lost-wallet.jpg",
    "hotel": "/assets/blog/scenes/hotel.jpg",
    "ask_help": "/assets/blog/scenes/ask-help.jpg",
    "greeting": "/assets/blog/scenes/greeting.jpg",
    "home_cooking": "/assets/blog/scenes/home-cooking.jpg",
    "market": "/assets/blog/scenes/market.jpg",
    "boutique": "/assets/blog/scenes/boutique.jpg",
    "restaurant": "/assets/blog/scenes/restaurant.jpg",
    "shopping": "/assets/blog/scenes/shopping.jpg",
    "small_talk": "/assets/blog/scenes/small-talk.jpg",
    "messaging": "/assets/blog/scenes/messaging.jpg",
    "kdrama": "/assets/blog/scenes/kdrama-night.jpg",
    "comfort": "/assets/blog/scenes/comfort-night.jpg",
    "concert": "/assets/blog/scenes/concert.jpg",
    "pharmacy": "/assets/blog/scenes/pharmacy.jpg",
    "bts_fans": "/assets/blog/scenes/bts-fans.jpg",
    "bbq": "/assets/blog/scenes/bbq.jpg",
    "convenience_heat": "/assets/blog/scenes/convenience-heat.jpg",
}

BRAND_COVERS = {
    "wrong_way": "/assets/blog/covers/wrong-way.png",
    "not_your_fault": "/assets/blog/covers/not-your-fault.png",
    "start_speaking": "/assets/blog/covers/start-speaking.png",
    "app_access": "/assets/blog/covers/app-access.png",
    "whats_inside": "/assets/blog/covers/whats-inside.png",
    "book": "/assets/blog/covers/book.png",
}

# (regex, image) — first match wins. Specific scenes before broad ones.
IMAGE_RULES = [
    (r"pharmacy|약|medicine|두통|drugstore|\bchemist\b", SCENES["pharmacy"]),
    (r"\bbbq\b|samgyeopsal|grill|가위|korean barbecue|korean barbeque", SCENES["bbq"]),
    (r"bts|army|weverse|보고 싶었어|힘이 됐", SCENES["bts_fans"]),
    (r"데워|microwave|heating food|편의점.*heat", SCENES["convenience_heat"]),
    (r"cafe|coffee|barista|americano|latte", SCENES["cafe"]),
    (r"convenience store|\bgs25\b|7-?eleven|\bsnack|\bkiosk\b", SCENES["convenience"]),
    (r"\btaxi\b", SCENES["taxi"]),
    (r"\bbus\b", SCENES["bus"]),
    (r"wallet|lost|stolen|police", SCENES["lost_wallet"]),
    (r"hotel|check.?in|checkout", SCENES["hotel"]),
    (r"concert|k-?pop|lightstick|hwaiting|fan sign|idol", SCENES["concert"]),
    (r"spooky|comfort|괜찮|scared|museowoyo", SCENES["comfort"]),
    (r"k-?drama|drama phrase|romantic drama", SCENES["kdrama"]),
    (r"bargain|market|traditional market|\b시장\b", SCENES["market"]),
    (r"clothes|clothing|boutique|try on|\bsize\b|fitting", SCENES["boutique"]),
    (r"cook|cooking|banchan|맛있|compliment.*food|friend.*cooking", SCENES["home_cooking"]),
    (r"politely ask|ask for help|help me|excuse me", SCENES["ask_help"]),
    (r"greeting|politeness|안녕하세요|bow", SCENES["greeting"]),
    (r"subway|train|\bktx\b|airport|transport|direction|metro", SCENES["transport"]),
    (r"restaurant|order\w* food|food\b|\bmenu\b|dining|\bbbq\b|delivery|\beat\b|\bmeal\b", SCENES["restaurant"]),
    (r"\bbook\b|textbook|\bpdf\b|workbook|amazon|100 pattern", BRAND_COVERS["book"]),
    (r"kakao|\btext(ing|s)?\b|\bmessage|\bchat\b|\bdm\b|social media|comment", SCENES["messaging"]),
    (r"\bshop|\bstore\b|\bbuy\b|\bprice|myeongdong|refund", SCENES["shopping"]),
    (r"friend|small talk|introduce|\bhello\b|\bmeet\b|\bage\b|\bname\b", SCENES["small_talk"]),
    (r"duolingo|streak|not working|stuck|plateau|waste|\bfail", BRAND_COVERS["wrong_way"]),
    (r"freez|nervous|anxiet|\bshy\b|afraid|confiden|go blank|embarrass", BRAND_COVERS["not_your_fault"]),
    (r"speak|pronunciation|shadow|out loud|conversation|fluen|accent", BRAND_COVERS["start_speaking"]),
    (r"\bapp\b|sulsul|mission|ai coach|my sentence", BRAND_COVERS["app_access"]),
]

FALLBACK_COVERS = [
    BRAND_COVERS["start_speaking"],
    BRAND_COVERS["whats_inside"],
    "/assets/blog/covers/app-screen-1.png",
    "/assets/blog/covers/app-screen-2.png",
    "/assets/blog/covers/app-screen-3.png",
    "/assets/blog/covers/app-screen-4.png",
]


def relevant_inline_images(topic_text, cover):
    """2026-08-03: giving the model the full image list (even with accurate
    descriptions) still produced an off-topic pick — a cafe-counter photo
    used to pad out a convenience-store post to three images, just because
    it needed a third slot. Restrict the offered pool instead of trusting
    the choice: only the scene(s) that actually match this topic, plus the
    four generic SULSUL app/mascot screens, which fit any topic because they
    show no specific location."""
    text = (topic_text or "").lower()
    matched_scenes = {
        img for pattern, img in IMAGE_RULES
        if img in SCENES.values() and re.search(pattern, text)
    }
    app_screens = {p for p in INLINE_IMAGE_PATHS if "app-screen" in p}
    pool = (matched_scenes | app_screens) - {cover}
    return sorted(pool)


def pick_cover(topic_text):
    """Choose a cover image that actually matches the post topic."""
    text = (topic_text or "").lower()
    for pattern, image in IMAGE_RULES:
        if re.search(pattern, text):
            return image
    return random.choice(FALLBACK_COVERS)

BANNED_PHRASES = [
    "money-back",
    "money back",
    "satisfaction guarantee",
    "refund guarantee",
    "% off",
    "percent off",
    "$299",
    "early bird",
    "limited time",
    "free trial",
    "ultimate guide to",
    "unlock your full potential",
    "dive into",
    "delve",
    "game-changer",
    "embark on a journey",
    "in today's fast-paced world",
    "look no further",
    "in conclusion",
]

INLINE_IMAGE_PATHS = {
    *SCENES.values(),
    "/assets/blog/covers/app-screen-1.png",
    "/assets/blog/covers/app-screen-2.png",
    "/assets/blog/covers/app-screen-3.png",
    "/assets/blog/covers/app-screen-4.png",
}

# 2026-08-03: the model never actually sees these image files, so it wrote
# plausible-sounding alt text for the surrounding paragraph instead of a
# description of the photo — e.g. shopping.jpg (a clothing boutique) got
# captioned "Paying at a Korean restaurant". Checked every file by hand once
# and the code now forces this exact text every time, the same way
# fix_romanization overrides a guessed pronunciation.
INLINE_IMAGE_ALT = {
    SCENES["cafe"]: "Counter of a cozy Korean cafe with pastries and a coffee machine",
    SCENES["convenience"]: "Shelves and checkout counter inside a Korean convenience store",
    SCENES["transport"]: "Turnstiles and platform signage at a Seoul subway station",
    SCENES["taxi"]: "Yellow Korean taxi waiting on a Seoul street at dusk",
    SCENES["bus"]: "Interior of a Seoul city bus with blue seats and hand straps",
    SCENES["lost_wallet"]: "A lost wallet on a wet Seoul sidewalk near a police box",
    SCENES["hotel"]: "Modern boutique hotel lobby check-in desk in Seoul",
    SCENES["ask_help"]: "Travelers asking for directions on a Seoul sidewalk",
    SCENES["greeting"]: "People exchanging a polite Korean greeting outside a cafe",
    SCENES["home_cooking"]: "Korean home-cooked dishes on a dining table",
    SCENES["market"]: "Colorful produce stalls at a Korean outdoor market",
    SCENES["boutique"]: "Interior of a bright clothing boutique in Seoul",
    SCENES["restaurant"]: "A Korean BBQ restaurant dining room set for a meal",
    SCENES["shopping"]: "Racks of clothes inside a Korean clothing boutique",
    SCENES["small_talk"]: "A riverside park near a Seoul university at sunset",
    SCENES["messaging"]: "A cozy bedroom at night, set up for texting a friend in Korean",
    SCENES["kdrama"]: "Cozy living room at night with a TV glowing softly",
    SCENES["comfort"]: "Quiet Seoul street at night under soft streetlights",
    SCENES["concert"]: "Concert crowd holding glowing lightsticks toward the stage",
    SCENES["pharmacy"]: "Clean Korean pharmacy interior with medicine shelves and counter",
    SCENES["bts_fans"]: "Concert crowd holding glowing purple and pink lightsticks",
    SCENES["bbq"]: "Korean BBQ grill with scissors, tongs, and side dishes",
    SCENES["convenience_heat"]: "Convenience-store counter with food ready for the microwave",
    "/assets/blog/covers/app-screen-1.png": "SULSUL mascot Sulsuli waving hello, with the tagline Don't freeze in Seoul, speak Korean for real",
    "/assets/blog/covers/app-screen-2.png": "SULSUL mascot Sulsuli looking upset beside the question Are you learning Korean the wrong way?",
    "/assets/blog/covers/app-screen-3.png": "SULSUL web app screen showing a Korean phrase card with a microphone icon for voice practice",
    "/assets/blog/covers/app-screen-4.png": "SULSUL mascot Sulsuli next to a breakdown of the app's 100 patterns and practice features",
}

SYSTEM_PROMPT = """# ROLE
You are the lead SEO + GEO (Generative Engine Optimization) editor for SULSUL — a Korean speaking-practice app at https://sulsul.app.
You write English blog posts with two jobs:
(1) rank in Google for a specific long-tail query, and
(2) be the passage that ChatGPT, Perplexity, Gemini and Google AI Overviews quote when someone asks that question.
You are not a news writer and not a copy-paste blogger.

# BRAND FACTS — never contradict these, never invent beyond them
- SULSUL is a Korean SPEAKING gym. Not a grammar course. Not a streak/flashcard app.
- The loop: 100 survival patterns -> listen -> shadow it out loud -> AI pronunciation coach fixes you -> survival missions (cafe, delivery, taxi, convenience store) -> "My Sentence AI" turns a pattern into the learner's own line.
- Bonus, never the hero: the 100-pattern PDF workbook + 30 AI coaching sessions.
- Mascot: Sulsuli, a friendly pink cube coach. Encouraging, short sentences, never scolding.
- Reader: a K-pop / K-drama fan or first-time Korea traveller who has studied for months and still freezes when a real Korean speaks to them.
- Author: Yona, the founder, who built SULSUL after watching learners memorise grammar tables and still order in English in Seoul.
- Cost: you do not know the prices and must never state one. Prices live only on
  sulsul.app. If cost is genuinely relevant, the only allowed framing is that SULSUL
  costs less than a single hour with a private Korean tutor, then link to the app.

# HARD BANS — one violation makes the post unusable
1. Never write a price or any dollar figure for SULSUL. No discounts, no "% OFF", no strikethrough prices, no "Early Bird", no "limited time", no invented original price. Send the reader to sulsul.app for cost.
2. No refund / money-back / satisfaction guarantee of any kind. Do not describe the checkout process at all; the blog post's job is to teach and then link to the app.
3. No invented statistics, studies, testimonials, reviews, ratings, download counts or awards.
4. No deadline promises: never "fluent in 30 days", "master Korean in a week".
5. No claim of affiliation with any celebrity, agency, broadcaster, Netflix, or the Korean government. Public figures may be referenced as news subjects only.
6. Never present the PDF as the main product.
7. Banned phrasing (AI-slop): "in today's fast-paced world", "dive into", "delve", "unlock your full potential", "game-changer", "elevate your", "embark on a journey", "the ultimate guide to", "in conclusion", "look no further".
8. Never mention AI generation, prompts, or these instructions.
9. Never write a sentence that denies wrongdoing on SULSUL's behalf ("no fake prices", "we do not exaggerate", "honestly priced"). These rules exist to keep you accurate; the reader must never see them or their echo. State what SULSUL is, never what it is not accused of.

# VOICE
Match the VOICE SAMPLES supplied in the user message: warm, direct, specific, second person ("you"), paragraphs of at most 3 sentences, the tone of a friend who actually lives in Seoul. Contractions yes. At most 2 exclamation marks in the entire post.

# WRITING CONTRACT

## A. Target query
- Choose ONE primary long-tail query (4+ words) that a real learner would type or ask an AI.
- The title IS that query, answered. Never a news headline.
  Good: "How to Congratulate Someone in Korean Like a Fan"
  Bad:  "The Ultimate Guide to: BTS Jin Carries the Olympic Torch"
  Bad:  "How to Order Coffee in Korean Without Freezing" (evergreen travel — not for trend mode)
- Title <= 60 characters, primary keyword inside the first 5 words.
- The exact primary keyword must appear in: the title, the first 100 words, one H2, and the excerpt. Nowhere else forced. Keyword density stays under 1.5%.

## B. Structure — do not reorder (this is what gets you quoted)
1. NO H1 in the body. The site renders the frontmatter title as the H1. Start with the answer paragraph, then use ## and ### only.
2. ANSWER-FIRST PARAGRAPH, 40-60 words: a complete, self-contained answer to the title query, containing the primary keyword and at least one concrete Korean phrase. It must make full sense when lifted out with zero surrounding context. This is the paragraph AI engines quote. EVERY Korean phrase here has *italic Revised Romanization* right next to it — a reader who cannot read Hangul yet must still be able to say it. Never drop the romanization to save words; cut something else instead.
3. A "> " blockquote right after it, 3-5 bullets, each a full standalone sentence carrying one concrete fact (a phrase, a rule, a situation), and each Korean phrase in it followed by *italic Revised Romanization*, the same rule as above. No vague bullets. The answer paragraph and the blockquote may each name a phrase once; do not then re-teach that same phrase with a full block in the body.
4. HARD LIMIT: at most 6 "##" headings in the whole file, counting the CTA. Use 3-4 teaching "##" sections, then the CTA "##" last. Do NOT include a Frequently Asked Questions section — FAQ answers just repeat the body and make the post too long for a phone. Every teaching H2 is a real question ("What do you actually say at a Korean cafe counter?") or a concrete task. Never "Understanding the Basics", never "Conclusion", never a label like "Table of Situations and Phrases" — put the markdown table and the numbered step list INSIDE a teaching section, under its "##", with NO heading of their own (not "##", not "###") introducing them.
5. Each "##" section runs 60-110 words and must carry material found nowhere else in the post. Write in short, scannable paragraphs of 1-3 sentences — a reader skimming on a phone should be able to grab the point without reading every word. A section that only restates a phrase already taught is a failed section: delete it and write a different one.
6. At least 1 section shows BOTH sides of the exchange. Understanding the reply is the part that actually defeats people, so write it out. An exchange is exactly three lines, in this order, and nothing else — no "Literal:", no "Use it when:", those belong only to the teaching blocks in section C:

   You: **한국어** — *romanization* — "English"
   Them: **한국어** — *romanization* — "English"
   You: **한국어** — *romanization* — "English"

   Each of those three lines is a plain paragraph line. NEVER put a "#", "##" or
   "###" in front of "You:" or "Them:" — that turns three lines of dialogue into
   three separate document headings and breaks the post's structure.
   The "Them" line is what the Korean speaker says to you. Never describe when a
   staff member should use a phrase; the reader is the customer, not the staff.

7. At least 1 section carries a "What usually goes wrong" line: the specific mistake a learner makes at this exact moment, and what to do instead.
8. Never use the same Korean phrase in more than two places in the whole post. A row in the table counts as one of those two.
9. Every section stands alone: repeat the entity names ("SULSUL", "Korean", the situation) instead of "it / this / that" across sections.
10. Include exactly ONE markdown TABLE with AT MOST 2 columns and AT MOST 5 rows (e.g. situation -> phrase, or Korean -> English meaning). Every cell is short — one phrase or a few words, never a full sentence, never a third column — so it renders cleanly on a phone screen without breaking. Every Korean phrase in the table still gets its *italic romanization* inside the same cell, right after the phrase — a table cell is not exempt from the romanization rule.
11. Include one numbered step-by-step section, 3-5 steps, each step ONE short sentence starting with a verb, written so it could be lifted as a HowTo.
12. Do NOT write an FAQ section. No "## Frequently Asked Questions", no "###" question blocks. Put the one fact a reader would ask into the teaching sections instead.
13. CTA block LAST, using the template in section E. Its heading is "##", never "###".
14. Length 320-650 English WORDS. Longer is not better: a reader on a phone abandons a wall of text. Cut ruthlessly — every sentence must teach something new.
15. Add TWO to THREE inline Markdown images, spaced through the teaching sections
    so the reader is never far from a visual break. Use only the image paths
    supplied in the user message, never the same one twice, and never the same
    file already used as COVER IMAGE — the cover renders once at the top of the
    page already, so repeating it in the body wastes a slot on a photo the
    reader already saw. Choose images whose description in the brief actually
    matches the section they sit in. Copy the alt text exactly as given in the
    brief. Mix real-life scenes with speaking-practice screens. Do not put an
    image before the answer or inside the CTA.

## C. Korean examples — mandatory format
Teach 5-6 DISTINCT phrases — never the same phrase twice. Fewer, carefully chosen phrases beat many thin ones; pick only what this exact query needs. Every phrase uses exactly this block:

**한국어 문장** — *romanization*
"Natural English"
Literal: word-by-word meaning
Use it when: one concrete situation

Rules: 해요체 by default (합쇼체 only where the situation demands it). Revised Romanization. Check every particle. If you are not fully certain a phrase is natural, use a simpler phrase you are certain of. Never invent slang. Never write a bracket placeholder like [Destination] or [Name] inside a Korean phrase — every phrase must be a complete, real, romanizable example (a specific place, a specific name), never a fill-in-the-blank template.

## D. Real-world accuracy
- Every You / Them / You exchange must follow the actual order of the interaction.
  The "Them" line must logically answer or react to the line immediately before it.
- Never invent a discount percentage, shop policy, hotel policy, police procedure,
  cultural custom, or claim that something is "common in Korea".
- Never tell the reader to "always" ask for a discount. Fixed-price shops are fixed
  price; negotiation belongs only where a seller explicitly signals it.
- A generic homepage is not evidence. Omit a source rather than attaching an
  unrelated homepage to a claim.

## E. Trust signals (E-E-A-T)
- One short first-person note from Yona, 1-2 sentences, specific and plausible (what learners actually get wrong at the counter). No invented numbers, no named students.
- If SOURCE URL is supplied, cite it once inline as a markdown link in the first 3 sections, attributed to the outlet by name.
- Add 1-2 external links only to pages you are certain exist (e.g. Visit Korea, the National Institute of Korean Language). If unsure a URL exists, omit it. Never fabricate a URL.
- Add 2-3 internal links from the EXISTING POSTS list with descriptive anchor text. If that list is empty, skip internal links.

## F. CTA block — keep the structure, rewrite the first two lines to fit this post

---

## Say it out loud, not just in your head

<one line naming the exact situation this post covers, and the fact that reading it is not the same as saying it when someone is waiting for your answer>

SULSUL is a speaking gym for exactly that moment: pick a survival pattern, say it out loud, get an instant fix from the AI pronunciation coach, then run the real situation as a mission. The 100-pattern PDF workbook comes along as a bonus.

**[Start speaking with SULSUL here!!](https://sulsul.app/?utm_source=blog&utm_medium=post&utm_campaign=seo)**

## G. Output format
Output ONLY the finished markdown file. Start with "---" on line 1. No code fences around it, no preface, no closing remarks.

Frontmatter schema (fill every field, keep this key order):

---
title: "<=60 chars, primary keyword first"
excerpt: "140-160 characters. One complete sentence that answers the title query and contains the primary keyword. This is the meta description: no teasing, no 'read on to find out'."
slug: "kebab-case, max 6 words, contains the primary keyword"
date: "ISO_DATE_PLACEHOLDER"
updated: "ISO_DATE_PLACEHOLDER"
coverImage: "COVER_IMAGE_PLACEHOLDER"
ogImage:
  url: "COVER_IMAGE_PLACEHOLDER"
author:
  name: Yona
  picture: "/assets/blog/authors/yona.png"
category: "one of: Survival Korean | Travel Korean | K-Culture & Language | Speaking Practice | Korean Basics"
primaryKeyword: "the exact query you targeted"
keywords: ["4-8 related long-tail queries this post actually answers"]
faq: []
sources:
  - title: "outlet or site name"
    url: "https://..."
---

## G. Self-check before you output (verify silently, fix, then output)
[ ] Title is a query, <=60 chars, no banned phrasing
[ ] Body has no H1
[ ] First paragraph works as a standalone 40-60 word answer
[ ] exactly 1 table (<=2 columns, <=5 rows), >= 1 numbered step list, NO FAQ section
[ ] frontmatter faq is an empty list []
[ ] Every Korean phrase uses the 4-line block and is natural
[ ] Every bold Korean phrase, everywhere in the file — opening paragraph, blockquote, exchanges, table cells — has *italic Revised Romanization* in the same sentence the first time it appears
[ ] No banned claim, no invented number, no fabricated URL
[ ] CTA block is last and links to sulsul.app with the UTM
[ ] 400-550 words, 2-3 inline images spaced through the post, no wall of text
"""

def read_markdown_files(directory):
    content = ""
    if not os.path.exists(directory):
        return content
    paths = sorted(
        glob.glob(os.path.join(directory, "*.md"))
        + glob.glob(os.path.join(directory, "*.txt"))
    )
    for filepath in paths:
        with open(filepath, "r", encoding="utf-8") as f:
            content += f"\n\n--- Source: {os.path.basename(filepath)} ---\n"
            content += f.read()
    return content


def api_call_with_retry(messages, temperature=0.5, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = get_client().chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            wait_time = (2 ** attempt) + 2
            print(f"API delay. Retry in {wait_time}s... ({e})")
            time.sleep(wait_time)
    raise Exception("OpenAI API failed after retries.")


def list_existing_posts(dirs=None):
    posts = []
    for directory in dirs or [BLOG_POSTS_DIR]:
        if not os.path.exists(directory):
            continue
        for filepath in glob.glob(os.path.join(directory, "*.md")):
            slug = os.path.basename(filepath)[:-3]
            title = slug
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, re.M)
                if m:
                    title = m.group(1).strip()
            except Exception:
                pass
            posts.append({"slug": slug, "title": title})
    return posts


def existing_posts_block(posts):
    if not posts:
        return "(none yet — skip internal links)"
    return "\n".join(f"- {p['slug']} — {p['title']}" for p in posts)


def library_slice(library_content, seed_text="", max_chars=12000):
    if not library_content:
        return ""
    if len(library_content) <= max_chars:
        return library_content
    tokens = re.findall(r"[A-Za-z]{4,}|[가-힣]{2,}", seed_text or "")
    for token in tokens[:8]:
        idx = library_content.lower().find(token.lower())
        if idx != -1:
            start = max(0, idx - max_chars // 3)
            return library_content[start : start + max_chars]
    start = random.randint(0, max(0, len(library_content) - max_chars))
    return library_content[start : start + max_chars]


def domain_of(url):
    try:
        return urlparse(url).netloc.replace("www.", "") or "source"
    except Exception:
        return "source"


def strip_code_fences(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:markdown|md)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def extract_frontmatter_slug(text):
    m = re.search(r'^slug:\s*["\']?([a-z0-9\-]+)["\']?\s*$', text, re.M)
    if m:
        return m.group(1)
    m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, re.M)
    if m:
        raw = m.group(1).lower()
        raw = re.sub(r"[^a-z0-9\s\-]", "", raw)
        raw = re.sub(r"\s+", "-", raw).strip("-")
        return raw[:60].rstrip("-") or f"post-{int(time.time())}"
    return f"post-{int(time.time())}"


def extract_title(text):
    m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, re.M)
    return m.group(1) if m else "untitled"


def title_similarity(a, b):
    ta = set(re.findall(r"[a-z0-9]+", a.lower()))
    tb = set(re.findall(r"[a-z0-9]+", b.lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta | tb), 1)


def trend_seed_ok(item):
    title = item["title"]
    text = f"{title} {item['snippet']}"
    if len(title) < 15:
        return False, "title is a site name, not a story"
    if TREND_EXCLUDED.search(text):
        return False, "reference page, finance, or unrelated topic"
    if not TREND_REQUIRED.search(text):
        return False, "nothing to do with Korea"
    return True, ""


def news_hook_tokens(news):
    """Distinctive words from the seed — not generic 'korean' / 'entertainment'."""
    text = f"{news.get('title', '')} {news.get('snippet', '')}"
    tokens = re.findall(r"[a-z0-9]{4,}", text.lower())
    seen = []
    for token in tokens:
        if token in TREND_HOOK_STOPWORDS or token in seen:
            continue
        seen.append(token)
    return seen[:10]


def opening_references_news(body, news):
    """Trend posts must hook the seed in the first ~120 words, not jump to a template."""
    words = re.findall(r"\b[\w']+\b", body)
    opening = " ".join(words[:120]).lower()
    if not opening.strip():
        return False
    outlet = domain_of(news.get("link", "")).lower()
    if outlet and outlet not in ("source",) and outlet.split(".")[0] in opening:
        return True
    for token in news_hook_tokens(news):
        if token in opening:
            return True
    # Romanized / Korean names from the headline (e.g. Lee Soo-man).
    for token in re.findall(r"[A-Z][a-z]+(?:-[A-Z][a-z]+)?", news.get("title", "")):
        low = token.lower()
        if len(low) >= 4 and low not in TREND_HOOK_STOPWORDS and low in opening:
            return True
    return False


def fetch_trend_news(count):
    """Return K-culture news seeds, or nothing at all.

    The first version searched the whole web for "K-Pop OR K-Drama OR BTS",
    which returns site fronts and dictionary entries rather than stories, and
    those seeds became the posts about a used-car dealer, the letter K and
    nasal congestion. The news index answers with articles, and the guard drops
    whatever still arrives off-topic. Returning an empty list is a valid
    outcome: no seed is better than a seed about the wrong subject.
    """
    day = datetime.utcnow().timetuple().tm_yday
    queries = [TREND_QUERIES[(day + i) % len(TREND_QUERIES)] for i in range(3)]

    for attempt, query in enumerate(queries):
        if attempt:
            time.sleep(TREND_BACKOFF_SECONDS)
        print(f"Searching K-culture news for {query!r}...")
        try:
            results = list(DDGS().news(query, max_results=max(count * 4, 8)))
        except Exception as e:
            print(f"  search unavailable ({e}); trying another query.")
            continue

        seeds = []
        for r in results:
            item = {
                "title": (r.get("title") or "").strip(),
                "snippet": (r.get("body") or r.get("excerpt") or "").strip(),
                "link": (r.get("url") or r.get("href") or "").strip(),
            }
            ok, why = trend_seed_ok(item)
            if not ok:
                print(f"  dropped ({why}): {item['title'][:60]}")
                continue
            seeds.append(item)
            if len(seeds) >= count:
                break

        if seeds:
            return seeds
        print("  no on-topic story in this batch.")

    print("No usable K-culture news today. Writing nothing rather than guessing.")
    return []


def generate_keywords(library_content, count, existing_titles):
    print(f"Extracting {count} long-tail speaking queries...")
    prompt = f"""You are an SEO strategist for SULSUL, a Korean speaking app.
From the textbook below, produce {count} English long-tail search queries that a K-drama fan or first-time Korea traveller would actually type into Google or ask ChatGPT.

Rules:
- 4-9 words each, natural question or task phrasing.
- Must be answerable with speaking practice, not grammar theory.
- Prefer situation queries ("what to say at a Korean convenience store") over topic nouns ("Korean particles").
- Exclude anything close to these already-published posts: {existing_titles or '(none)'}
- Spread across: cafe/food, transport, shopping, hotel, emergencies, small talk, K-drama phrases, politeness levels.

Output: a numbered list only, no commentary.

[TEXTBOOK]
{library_slice(library_content, max_chars=10000)}
"""
    keywords_text = api_call_with_retry(
        [{"role": "user", "content": prompt}], temperature=0.4
    )
    keywords_list = []
    for line in keywords_text.split("\n"):
        if ". " in line:
            keywords_list.append(line.split(". ", 1)[1].strip().strip('"'))
    return keywords_list[:count]


def generate_blog_post(keyword_data, library_content, voice_content, mode, existing_posts):
    iso_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    if mode == "trend":
        topic_text = f"{keyword_data.get('title', '')} {keyword_data.get('snippet', '')}"
    else:
        topic_text = str(keyword_data)
    cover = pick_cover(topic_text)
    existing_block = existing_posts_block(existing_posts)
    voice = (
        voice_content[:6000]
        if voice_content
        else "(no voice samples — use warm, direct, second-person Seoul-friend tone)"
    )

    if mode == "trend":
        news = keyword_data
        seed = news["title"] + " " + news.get("snippet", "")
        lib = library_slice(library_content, seed_text=seed)
        outlet = domain_of(news.get("link", ""))
        topic = f"""[MODE] trend-hook
[NEWS HOOK] {news['title']}
[NEWS SUMMARY] {news.get('snippet', '')}
[SOURCE URL] {news.get('link', '')}
[SOURCE OUTLET] {outlet}

Use the news ONLY as the first 2-3 sentences of the opening and as the reason this Korean matters right now. Name the outlet or a person/event from the headline in those opening sentences — a post that jumps straight to a generic cafe/travel template fails. Then derive a long-tail language query from it and write an evergreen post that is still useful a year from now.

Example derivation:
  News:  "BTS Jin carries the Olympic torch in Paris"
  Bad:   a summary of the torch relay
  Good:  "How to Congratulate Someone in Korean Like a Fan" — 축하해요 / 자랑스러워요 / 화이팅, when each is appropriate, how fans actually write it online.

Never summarise the news. You cannot outrank the outlet and this is not a news site.
"""
        print(f"[trend-hook] '{news['title']}' -> evergreen language query...")
    else:
        target_keyword = keyword_data
        lib = library_slice(library_content, seed_text=target_keyword)
        topic = f"""[MODE] evergreen
[PRIMARY QUERY] {target_keyword}
[SEARCH INTENT] informational
Write the post that fully answers this query and leaves the reader able to say the phrases.
"""
        print(f"[evergreen] '{target_keyword}'...")

    user = f"""[DATE] {iso_date}
[COVER IMAGE] {cover}

[ALLOWED INLINE IMAGES — choose THREE to FOUR, spaced between teaching sections, never the coverImage above. This list is already filtered to what fits this post; do not reach for anything outside it. The alt text shown here is exactly what will render — do not rewrite it.]
{chr(10).join(f"- {path} — {INLINE_IMAGE_ALT.get(path, 'no description')}" for path in relevant_inline_images(topic_text, cover))}

[VOICE SAMPLES — copy this tone, not this content]
{voice}

[SULSUL TEXTBOOK — the only source for Korean patterns you teach. Use phrases from here first; do not contradict it.]
{lib}

[EXISTING POSTS — do not repeat these angles; link 2-3 of them where relevant]
{existing_block}

[FORBIDDEN OVERLAP]
If your planned angle substantially overlaps an existing post above, pick a different, narrower angle and say nothing about the change.

In the frontmatter, set:
date: "{iso_date}"
updated: "{iso_date}"
coverImage: "{cover}"
ogImage.url: "{cover}"

{topic}
"""

    # Also remind model to replace placeholders if it copies the schema literally
    system = SYSTEM_PROMPT.replace("ISO_DATE_PLACEHOLDER", iso_date).replace(
        "COVER_IMAGE_PLACEHOLDER", cover
    )

    raw = api_call_with_retry(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.5,
    )
    draft = fix_exchange_linebreaks(fix_exchange_headings(fix_inline_image_alt(fix_inline_image_paths(fix_romanization(
        enforce_frontmatter(strip_code_fences(raw), cover, iso_date)
    )))))
    return revise_to_pass(
        draft, system, user, cover, iso_date, existing_posts,
        trend_seed=keyword_data if mode == "trend" else None,
    )


def enforce_frontmatter(text, cover, iso_date):
    """The model is asked for these values but only the code knows them for
    certain, and a single wrong character fails the publish gate."""
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    if len(parts) < 3:
        return text
    fm, body = parts[1], parts[2]

    def set_field(block, key, value):
        pattern = rf"(?m)^{key}:.*$"
        if re.search(pattern, block):
            return re.sub(pattern, f'{key}: "{value}"', block, count=1)
        return block.rstrip("\n") + f'\n{key}: "{value}"\n'

    fm = set_field(fm, "coverImage", cover)
    fm = set_field(fm, "date", iso_date)
    fm = set_field(fm, "updated", iso_date)

    if re.search(r"(?m)^ogImage:", fm):
        fm = re.sub(r'(?m)^(\s+)url:.*$', rf'\g<1>url: "{cover}"', fm, count=1)
    else:
        fm = fm.rstrip("\n") + f'\nogImage:\n  url: "{cover}"\n'

    return f"---{fm}---{body}"


ROMAN_PAIR = re.compile(
    r"(\*\*)([^*\n]*[가-힣][^*\n]*)(\*\*)(\s*(?:—|-|–)\s*)(\*)([^*\n]+)(\*)"
)


def fix_romanization(text):
    """GPT writes plausible but wrong romanization (예 as "yae", 있나요 as
    "it-na-yo"). Wrong pronunciation is worse than a thin post, so the code
    computes it and overwrites whatever the model guessed."""
    def sub(m):
        korean = spell_numbers(m.group(2))
        return (
            m.group(1) + m.group(2) + m.group(3) + m.group(4)
            + m.group(5) + rr(korean).strip() + m.group(7)
        )

    return ROMAN_PAIR.sub(sub, text)


EXCHANGE_LINE = re.compile(r"^\s*(You|Them):")
EXCHANGE_LINE_WITH_HEADING = re.compile(r"^\s*#{1,6}\s*(You|Them):")


def fix_exchange_headings(text):
    """The model sometimes writes the You:/Them: exchange as '### You:' /
    '### Them:' instead of plain text — it is not asked to, but the ##-heavy
    structure around it seems to invite it. That silently breaks the
    both-sides-exchange gate (the line no longer starts with 'Them:') AND
    inflates the FAQ question count (every exchange line counts as an H3),
    so revisions kept failing on both counts without the model ever being
    told the real cause. Stripped here instead of relying on the prompt."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if EXCHANGE_LINE_WITH_HEADING.match(line):
            lines[i] = re.sub(r"^\s*#{1,6}\s*", "", line)
    return "\n".join(lines)


def fix_exchange_linebreaks(text):
    """Markdown collapses a plain newline into a space, so a You:/Them:/You:
    exchange typed as three consecutive lines renders as one run-on sentence
    unless each line ends with a hard break (two trailing spaces). The model
    does not reliably add that whitespace, so the code enforces it instead
    of trusting the draft's exact formatting."""
    lines = text.split("\n")
    for i in range(len(lines) - 1):
        if EXCHANGE_LINE.match(lines[i]) and EXCHANGE_LINE.match(lines[i + 1]):
            lines[i] = lines[i].rstrip() + "  "
    return "\n".join(lines)


ASSET_PATH = re.compile(r"^(?:public/)?assets/blog/")


def fix_inline_image_paths(text):
    """The model occasionally drops the leading '/' from an image path
    ('assets/blog/...' instead of '/assets/blog/...'). That fails the
    allowed-path check every time, but 'invalid inline image' does not tell
    the model *why* it is invalid, so revisions burned rounds swapping to a
    different image instead of just fixing the slash. Normalized here so a
    real path never gets rejected over one missing character."""
    def sub(m):
        alt, path = m.group(1), m.group(2)
        if ASSET_PATH.match(path):
            path = "/" + path.lstrip("/")
        return f"![{alt}]({path})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", sub, text)


def fix_inline_image_alt(text):
    """Force the human-verified caption for every known image path, replacing
    whatever the model imagined. See INLINE_IMAGE_ALT for why."""
    def sub(m):
        alt, path = m.group(1), m.group(2)
        canonical = INLINE_IMAGE_ALT.get(path.strip())
        return f"![{canonical}]({path})" if canonical else m.group(0)

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", sub, text)


def body_word_count(text):
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    body = parts[2] if len(parts) >= 3 else text
    return len(re.findall(r"\b[\w']+\b", body))


def fix_instructions(reasons):
    """Turn gate failures into edits the model can actually act on."""
    steps = []
    for r in reasons:
        if r.startswith("public-copy rule"):
            rule = r.split("[", 1)[1].split("]", 1)[0]
            snippet = r.split(": ", 1)[1]
            if rule == "price":
                steps.append(
                    f'- Delete "{snippet}". Never put a price in a post. If cost comes '
                    "up at all, say SULSUL costs less than one hour with a private "
                    "tutor and link to https://sulsul.app."
                )
            elif rule == "denial":
                steps.append(
                    f'- Delete "{snippet}". Never deny wrongdoing on SULSUL\'s behalf. '
                    "Describe what SULSUL does instead."
                )
            elif rule == "competitor":
                steps.append(
                    f'- Remove the mention of "{snippet}". Describe what SULSUL does '
                    "without naming another product."
                )
            else:
                steps.append(
                    f'- Remove "{snippet}". It reads as an internal note or a claim '
                    "SULSUL cannot support, not as a sentence for a reader."
                )
        elif r.startswith("too short"):
            have = int(re.search(r"(\d+)", r).group(1))
            need = MIN_WORDS - have
            steps.append(
                f"- BODY WORD COUNT: {have} words now; minimum is {MIN_WORDS}. "
                f"Add at least {need} new words (aim for {need + 150} to be safe) as "
                "NEW situations, staff replies, and learner mistakes — never by repeating "
                "a phrase you already taught or inflating existing sentences."
            )
        elif r.startswith("too long"):
            steps.append(f"- Cut the post down to {MAX_WORDS} words or fewer.")
        elif r.startswith("only") and "distinct" in r:
            have = int(re.search(r"(\d+)", r).group(1))
            steps.append(
                f"- The post teaches only {have} different Korean phrases and needs at "
                f"least {MIN_DISTINCT_PHRASES}. Add {MIN_DISTINCT_PHRASES - have + 2} NEW "
                "phrases for situations the post does not cover yet, each with "
                "romanization, natural English, literal meaning and when to use it."
            )
        elif r.startswith("phrase repeated"):
            phrase = r.split(": ", 1)[1]
            steps.append(
                f'- "{phrase}" appears too many times. Keep it in at most two places '
                "and replace the others with different phrases that fit those spots."
            )
        elif "H2 sections" in r:
            have = int(re.search(r"(\d+)", r).group(1))
            teach_max = MAX_H2 - 2
            steps.append(
                f'- The post has {have} "##" headings but the maximum is {MAX_H2} total '
                f"(including FAQ and CTA). Merge teaching sections until at most "
                f'{teach_max} "##" remain before FAQ. Put the markdown table and numbered '
                'steps INSIDE a teaching section — never as their own "##". Keep FAQ and '
                "CTA as the last two headings."
            )
        elif r.startswith("trend hook missing"):
            headline = r.split(": ", 1)[1] if ": " in r else "the news seed"
            steps.append(
                f'- Rewrite the opening 2-3 sentences to reference this news: "{headline}". '
                "Name the outlet or a person/event from the headline, then derive the title "
                "from that story. Do not jump to a generic cafe/travel template."
            )
        elif "both-sides exchanges" in r:
            have = int(re.search(r"(\d+)", r).group(1))
            steps.append(
                f"- The post has {have} both-sides exchanges and needs at least "
                f"{MIN_EXCHANGES}. Add them to your strongest sections, each written as "
                "three lines — You: / Them: / You: — with the Korean, the "
                "romanization and the English on each line. Keep the ones already there."
            )
        elif r == "missing markdown table":
            steps.append(
                "- Add ONE markdown table with a header row, a |---|---| separator row "
                f"and up to {MAX_TABLE_ROWS} data rows mapping situation to phrase. "
                f"At most {MAX_TABLE_COLS} columns — no romanization column."
            )
        elif r.startswith("too many tables"):
            steps.append(
                "- Merge everything into exactly ONE table and remove the extra table(s)."
            )
        elif r.startswith("table has") and "columns" in r:
            steps.append(
                f"- Cut the table down to at most {MAX_TABLE_COLS} columns (e.g. "
                "situation -> phrase, or Korean -> English meaning). Move anything from "
                "the removed column into the surrounding paragraph instead."
            )
        elif r.startswith("table has") and "rows" in r:
            steps.append(
                f"- Cut the table down to at most {MAX_TABLE_ROWS} rows. Keep only the "
                "most useful situations; drop the rest rather than lengthening the table."
            )
        elif r == "FAQ section present":
            steps.append(
                '- Delete the entire "## Frequently Asked Questions" section and '
                "every ### under it. Put any unique fact into a teaching section "
                "instead — FAQ just repeats the body."
            )
        elif r == "CTA is H3 and merges into the FAQ":
            steps.append('- Change the CTA heading from "###" to "##".')
        elif r.startswith("non-question H3"):
            steps.append(
                '- Remove leftover "###" headings. Teaching content uses "##" only; '
                "there is no FAQ."
            )
        elif r.startswith("banned phrase"):
            steps.append(f'- Remove this wording entirely: "{r.split(": ", 1)[1]}".')
        elif r == "body contains H1":
            steps.append('- Remove the "# " heading; the site renders the title.')
        elif r.startswith("title too long"):
            steps.append("- Shorten the title to 60 characters or fewer.")
        elif r.startswith("too many sulsul.app"):
            steps.append("- Link to sulsul.app once, in the CTA only.")
        elif r == "missing sulsul.app CTA":
            steps.append("- Add the CTA block with the sulsul.app link.")
        elif r.startswith("inline image count"):
            steps.append(
                f"- Use {MIN_INLINE_IMAGES}-{MAX_INLINE_IMAGES} Markdown images total, "
                "spaced through the teaching sections rather than clustered together. "
                "Choose only from the allowed inline-image list in the brief, never the "
                "same image twice, use a specific descriptive alt text, and keep images "
                "out of the CTA."
            )
        elif r.startswith("invalid inline image"):
            steps.append(
                "- Replace the unapproved image path with one from the allowed "
                "inline-image list in the brief."
            )
        elif r == "duplicate inline image":
            steps.append("- Use a different image in each spot, never the same file twice.")
        elif r == "inline image repeats the cover image":
            steps.append(
                "- Replace whichever inline image matches the frontmatter coverImage "
                "with a different one from the allowed list. The cover already shows "
                "that photo once at the top of the page."
            )
        elif r == "empty inline image alt text":
            steps.append(
                "- Give both inline images descriptive English alt text naming the "
                "specific Korean-speaking situation."
            )
        elif r.startswith("unsupported percentage"):
            steps.append(
                "- Remove the exact percentage. Do not invent a discount, survey, "
                "success rate, or other numeric claim."
            )
        elif r.startswith("unsupported culture claim"):
            steps.append(
                "- Rewrite the blanket cultural claim as a narrow, situational fact. "
                "Do not claim something is common in Korea or tell readers to always "
                "ask for a discount."
            )
        elif r.startswith("missing romanization near"):
            phrase = r.split(": ", 1)[1]
            steps.append(
                f'- "{phrase}" has no *italic Revised Romanization* within the same '
                "sentence. Add it right after the bold Korean, every time a phrase "
                "first appears — opening paragraph, blockquote, exchanges, table "
                "cells, and FAQ answers included. A reader who cannot read Hangul "
                "must be able to say every bold Korean phrase out loud."
            )
        elif r.startswith("bracket placeholder in Korean phrase"):
            steps.append(
                "- Replace the [Destination]-style bracket placeholder with one "
                "concrete, real example (an actual place name) so the whole phrase "
                "can carry real romanization. A fill-in-the-blank template cannot "
                "be pronounced; a specific example can."
            )
        elif r == "generic Visit Korea homepage used as a source":
            steps.append(
                "- Remove the generic Visit Korea homepage source. A homepage does not "
                "support the article's specific claims."
            )
    return steps


def revise_to_pass(
    draft, system, user, cover, iso_date, existing_posts, trend_seed=None, rounds=4
):
    """One-shot generation lands short and repetitive no matter how the brief is
    worded, so feed the gate's own findings back instead of discarding the draft."""
    for attempt in range(1, rounds + 1):
        reasons = validate_post(draft, existing_posts, trend_seed=trend_seed)
        if not reasons:
            return draft
        steps = fix_instructions(reasons)
        if not steps:
            return draft

        print(f"  revision {attempt}: " + "; ".join(reasons))
        revision = (
            "Your draft failed the publish gate. Fix exactly these problems:\n\n"
            + "\n".join(steps)
            + "\n\nKeep everything that already works: the frontmatter, the title, the "
            "both-sides exchanges, the numbered steps, the FAQ and the CTA. Merging two "
            "thin ## sections into one IS allowed. Never delete a both-sides exchange or "
            "FAQ item to satisfy word count, and never solve a problem by repeating a "
            "phrase you have already taught.\n\n"
            'Output ONLY the finished markdown file, starting with "---" on line 1.'
        )

        raw = api_call_with_retry(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
                {"role": "assistant", "content": draft},
                {"role": "user", "content": revision},
            ],
            temperature=0.5,
        )
        candidate = fix_exchange_linebreaks(fix_exchange_headings(fix_inline_image_alt(fix_inline_image_paths(fix_romanization(
            enforce_frontmatter(strip_code_fences(raw), cover, iso_date)
        )))))
        if len(validate_post(candidate, existing_posts, trend_seed=trend_seed)) <= len(reasons):
            draft = candidate

    return draft


KOREAN_BOLD = re.compile(r"\*\*([^*\n]*[가-힣][^*\n]*)\*\*")
ROMANIZATION_NEARBY = re.compile(r"\*[A-Za-z][^*\n]*\*")


def missing_romanization(body):
    """2026-08-03: the CEO caught three rounds of Korean phrases with no
    romanization anywhere nearby (the opening paragraph, the blockquote, an
    exchange) before this was ever a machine check — a human had to read the
    live page to find it. A reader who cannot read Hangul yet cannot say a
    bold Korean phrase unless *italic romanization* sits right next to it,
    so every first mention of a phrase is checked here, not just hoped for
    in the prompt. Short particles (-요, -이요?) are exempt: they are endings
    explained in prose, not standalone phrases a reader looks up on their own.
    """
    seen_phrases = set()
    missing = []
    for m in KOREAN_BOLD.finditer(body):
        phrase = m.group(1).strip()
        if phrase in seen_phrases:
            continue
        if len(re.sub(r"[^가-힣]", "", phrase)) <= 2:
            continue
        if "[" in phrase or "]" in phrase:
            # A fill-in-the-blank template ("[Destination]으로 가주세요") cannot be
            # romanized as written — the model should not have written one, but
            # a check that keeps demanding romanization for an English
            # placeholder just loops forever instead of catching the real bug.
            continue
        window = body[m.end():m.end() + 80]
        if not ROMANIZATION_NEARBY.search(window):
            missing.append(phrase)
        seen_phrases.add(phrase)
    return missing


def table_blocks(text):
    """Return each markdown table as its list of raw lines (header, separator,
    data rows), so the gate can check column/row counts, not just presence."""
    blocks = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        sep = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if (
            "|" in lines[i]
            and sep
            and set(sep) <= set("|-: ")
            and "-" in sep
        ):
            rows = [lines[i]]
            j = i + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                rows.append(lines[j])
                j += 1
            blocks.append(rows)
            i = j
            continue
        i += 1
    return blocks


def validate_post(text, existing_posts, trend_seed=None):
    reasons = []
    lower = text.lower()

    for phrase in BANNED_PHRASES:
        if phrase in lower:
            reasons.append(f"banned phrase: {phrase}")

    # Same gate the site build runs, so a post cannot pass here and break there.
    for _line_no, rule_id, snippet, _why in scan_public_copy(text, "_posts/draft.md"):
        reasons.append(f"public-copy rule [{rule_id}]: {snippet}")

    if not text.lstrip().startswith("---"):
        reasons.append("missing frontmatter")

    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.M)
    body = parts[2] if len(parts) >= 3 else text
    fm = parts[1] if len(parts) >= 3 else ""

    if re.search(r"(?m)^#\s+\S", body):
        reasons.append("body contains H1")

    if re.search(r'(?mi)^coverImage:\s*["\']?\s*["\']?\s*$', text):
        reasons.append("empty coverImage")

    words = re.findall(r"\b[\w']+\b", body)
    if len(words) < MIN_WORDS:
        reasons.append(f"too short: {len(words)} words")
    if len(words) > MAX_WORDS:
        reasons.append(f"too long: {len(words)} words")

    inline_images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", body)
    if len(inline_images) < MIN_INLINE_IMAGES or len(inline_images) > MAX_INLINE_IMAGES:
        reasons.append(
            f"inline image count: {len(inline_images)} "
            f"(need {MIN_INLINE_IMAGES}-{MAX_INLINE_IMAGES})"
        )
    else:
        paths = [path.strip() for _alt, path in inline_images]
        for path in paths:
            if path not in INLINE_IMAGE_PATHS:
                reasons.append(f"invalid inline image: {path}")
                break
        if len(set(paths)) != len(paths):
            reasons.append("duplicate inline image")
        cover_m = re.search(r'(?mi)^coverImage:\s*["\']?([^"\'\n]+)["\']?\s*$', fm)
        if cover_m and cover_m.group(1).strip() in paths:
            reasons.append("inline image repeats the cover image")
        if any(not alt.strip() for alt, _path in inline_images):
            reasons.append("empty inline image alt text")

    percentage = re.search(r"\b\d{1,3}\s*%", body)
    if percentage:
        reasons.append(f"unsupported percentage: {percentage.group(0)}")

    culture_claim = re.search(
        r"\b(?:bargaining|asking for discounts?) is common in korea\b"
        r"|\balways (?:ask|use) [^.]{0,40}(?:discount|lower price)",
        body,
        re.I,
    )
    if culture_claim:
        reasons.append(f"unsupported culture claim: {culture_claim.group(0)[:70]}")

    if re.search(
        r'(?mi)^\s*-\s*title:\s*["\']?Visit Korea["\']?\s*$', fm
    ) and re.search(
        r'(?mi)^\s*url:\s*["\']?https://english\.visitkorea\.or\.kr/?["\']?\s*$',
        fm,
    ):
        reasons.append("generic Visit Korea homepage used as a source")

    missing_roman = missing_romanization(body)
    if missing_roman:
        reasons.append(f"missing romanization near: {missing_roman[0][:40]}")

    # A markdown link is also "**[text](url)**" — only flag a bracket that sits
    # inside Korean text, never one immediately followed by "(", which means
    # it is a link target rather than a fill-in-the-blank placeholder.
    for m in re.finditer(r"\*\*([^*\n]*\[[A-Za-z][^\]]*\][^*\n]*)\*\*(?!\()", body):
        if re.search(r"[가-힣]", m.group(1)) and "](" not in m.group(1):
            reasons.append(f"bracket placeholder in Korean phrase: {m.group(0)[:40]}")
            break

    if "## frequently asked questions" in lower:
        reasons.append("FAQ section present")

    # Any leftover ### is almost always a leftover FAQ item — teaching posts
    # use ## only (plus You:/Them: plain lines).
    if re.search(r"(?m)^###\s+", body):
        reasons.append("non-question H3 leftover — posts no longer use FAQ ###")

    tables = table_blocks(body)
    if not tables:
        reasons.append("missing markdown table")
    elif len(tables) > 1:
        reasons.append(f"too many tables: {len(tables)} (need exactly 1)")
    else:
        header_cols = [c for c in tables[0][0].split("|") if c.strip()]
        if len(header_cols) > MAX_TABLE_COLS:
            reasons.append(f"table has {len(header_cols)} columns; max is {MAX_TABLE_COLS}")
        data_rows = tables[0][2:]
        if len(data_rows) > MAX_TABLE_ROWS:
            reasons.append(f"table has {len(data_rows)} rows; max is {MAX_TABLE_ROWS}")

    h2_count = len(re.findall(r"(?m)^##\s+", body))
    if h2_count > MAX_H2:
        reasons.append(f"{h2_count} H2 sections; padded with one-line sections")

    # The reply side is the whole differentiator, and revisions quietly drop it
    # when nothing checks for it.
    exchanges = len(re.findall(r"(?m)^\s*Them:", body))
    if exchanges < MIN_EXCHANGES:
        reasons.append(f"only {exchanges} both-sides exchanges")

    if re.search(r"(?mi)^###\s+Say it out loud", body):
        reasons.append("CTA is H3 and merges into the FAQ")

    # Thin posts and good ones repeat a phrase 4-7 times alike; teaching a phrase
    # then using it in an exchange, a table row and an FAQ answer is normal. What
    # actually separates them is how many different phrases the post teaches.
    phrases = Counter(
        m.group(0).strip()
        for m in re.finditer(r"[가-힣][가-힣 ]{3,20}[가-힣]", body)
    )
    if len(phrases) < MIN_DISTINCT_PHRASES:
        reasons.append(f"only {len(phrases)} distinct Korean phrases")
    for phrase, hits in phrases.items():
        if hits > MAX_PHRASE_REPEATS:
            reasons.append(f"phrase repeated {hits}x: {phrase}")
            break

    cta_count = len(re.findall(r"https://sulsul\.app", text))
    if cta_count < 1:
        reasons.append("missing sulsul.app CTA")
    if cta_count > 3:
        reasons.append(f"too many sulsul.app links: {cta_count}")

    title_m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, re.M)
    title = title_m.group(1) if title_m else ""
    if title.lower().startswith("the ultimate guide"):
        reasons.append("generic ultimate-guide title")
    if len(title) > 70:
        reasons.append(f"title too long: {len(title)} chars")

    for p in existing_posts:
        if title_similarity(title, p["title"]) >= 0.85:
            reasons.append(f"cannibalizes existing: {p['slug']}")
            break

    if trend_seed and not opening_references_news(body, trend_seed):
        headline = trend_seed.get("title", "news seed")[:80]
        reasons.append(f"trend hook missing: opening ignores news ({headline})")

    return reasons


def save_post(text, existing_posts, out_dir=None, trend_seed=None):
    out_dir = out_dir or BLOG_POSTS_DIR
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(REJECTED_DIR, exist_ok=True)

    reasons = validate_post(text, existing_posts, trend_seed=trend_seed)
    slug = extract_frontmatter_slug(text)
    filepath = os.path.join(out_dir, f"{slug}.md")
    if os.path.exists(filepath):
        slug = f"{slug}-{datetime.utcnow().strftime('%H%M%S')}"
        filepath = os.path.join(out_dir, f"{slug}.md")

    title = extract_title(text)

    if reasons:
        reject_path = os.path.join(REJECTED_DIR, f"{slug}.md")
        with open(reject_path, "w", encoding="utf-8") as f:
            f.write("<!-- REJECTED: " + " | ".join(reasons) + " -->\n")
            f.write(text)
        print(f"Rejected ({'; '.join(reasons)}) -> {reject_path}")
        return {"slug": slug, "title": title, "kept": False, "reasons": reasons}

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Published: {filepath}")
    return {"slug": slug, "title": title, "kept": True, "reasons": []}


def write_run_summary(mode, results):
    """Record what the gate did, so the pass rate is visible without opening
    every log. GitHub renders this at the top of the run page."""
    kept = [r for r in results if r["kept"]]
    lines = [
        f"### SULSUL blog — {mode} run",
        "",
        f"Passed the gate: **{len(kept)} of {len(results)}**",
        "",
        "| Draft | Result |",
        "|---|---|",
    ]
    for r in results:
        verdict = "kept" if r["kept"] else "rejected — " + "; ".join(r["reasons"][:3])
        lines.append(f"| {r['title'][:70]} | {verdict} |")
    if not results:
        lines.append("| (no draft attempted) | nothing on topic to write about |")

    summary = "\n".join(lines) + "\n\n"
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(summary)
    print("\n" + summary)


def main():
    parser = argparse.ArgumentParser(description="SULSUL Blog Content Engine v2")
    parser.add_argument("--mode", choices=["textbook", "trend"], default="textbook")
    parser.add_argument("--count", type=int, default=3, help="Posts to generate (default 3)")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Write to _preview/ instead of _posts/ and ignore the per-run cap. "
        "For reading drafts before deciding anything; nothing here can be published.",
    )
    args = parser.parse_args()

    if args.preview:
        out_dir = PREVIEW_DIR
        print(f"Preview run: drafts go to {os.path.relpath(PREVIEW_DIR, ROOT)}/, not to the blog.")
    else:
        out_dir = BLOG_POSTS_DIR
        cap = MAX_PER_RUN[args.mode]
        if args.count > cap:
            print(f"Requested {args.count} posts; capping at {cap} for {args.mode} mode.")
            args.count = cap

    print(f"SULSUL Blog Engine v2 — mode={args.mode}, count={args.count}, model={MODEL}\n")

    library_content = read_markdown_files(LIBRARY_DIR)
    voice_content = read_markdown_files(VOICE_DIR)
    # A preview draft still counts as written, so later drafts do not repeat it.
    existing = list_existing_posts([BLOG_POSTS_DIR, PREVIEW_DIR] if args.preview else None)

    if not library_content:
        print(f"Warning: no textbook files in {LIBRARY_DIR}")
    if not voice_content:
        print(f"Warning: no voice files in {VOICE_DIR}")

    if args.mode == "trend":
        items = fetch_trend_news(args.count)
    else:
        titles = "; ".join(p["title"] for p in existing)
        items = generate_keywords(library_content, args.count, titles)

    if not items:
        print("Nothing to write about this run.")
        write_run_summary(args.mode, [])
        return

    print("\nQueue:")
    for i, item in enumerate(items, 1):
        label = item["title"] if args.mode == "trend" else item
        print(f"  {i}. {label}")
    print()

    results = []
    for item in items:
        label = item["title"] if args.mode == "trend" else str(item)
        try:
            post = generate_blog_post(
                item, library_content, voice_content, args.mode, existing
            )
            saved = save_post(
                post,
                existing,
                out_dir,
                trend_seed=item if args.mode == "trend" else None,
            )
            results.append(saved)
            if saved["kept"]:
                existing.append({"slug": saved["slug"], "title": saved["title"]})
        except Exception as e:
            print(f"Failed on item: {e}")
            results.append(
                {"slug": "", "title": label[:70], "kept": False, "reasons": [str(e)[:80]]}
            )

    write_run_summary(args.mode, results)
    print("Rejected drafts (if any) are in _rejected/")


if __name__ == "__main__":
    main()
