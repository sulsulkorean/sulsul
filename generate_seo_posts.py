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
import subprocess
import sys
import random
from datetime import datetime
from urllib.parse import urlparse
from openai import OpenAI

def install_package(package):
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("duckduckgo-search")
from duckduckgo_search import DDGS

client = OpenAI()
MODEL = os.environ.get("SULSUL_BLOG_MODEL", "gpt-4o")
ROOT = os.path.dirname(os.path.abspath(__file__))
OBSIDIAN_VAULT_PATH = os.path.join(ROOT, "obsidian_data")
LIBRARY_DIR = os.path.join(OBSIDIAN_VAULT_PATH, "3.Library")
VOICE_DIR = os.path.join(OBSIDIAN_VAULT_PATH, "2.Voice")
BLOG_POSTS_DIR = os.path.join(ROOT, "_posts")
REJECTED_DIR = os.path.join(ROOT, "_rejected")

# Enforced here rather than in the workflow files so a stale schedule
# can never push us back into scaled-content territory.
MAX_PER_RUN = {"trend": 2, "textbook": 3}

# Topic -> cover image routing. Keep in sync with src/lib/images.ts
SCENES = {
    "cafe": "/assets/blog/scenes/cafe.jpg",
    "convenience": "/assets/blog/scenes/convenience-store.jpg",
    "transport": "/assets/blog/scenes/transport.jpg",
    "restaurant": "/assets/blog/scenes/restaurant.jpg",
    "shopping": "/assets/blog/scenes/shopping.jpg",
    "small_talk": "/assets/blog/scenes/small-talk.jpg",
    "messaging": "/assets/blog/scenes/messaging.jpg",
}

BRAND_COVERS = {
    "wrong_way": "/assets/blog/covers/wrong-way.png",
    "not_your_fault": "/assets/blog/covers/not-your-fault.png",
    "start_speaking": "/assets/blog/covers/start-speaking.png",
    "app_access": "/assets/blog/covers/app-access.png",
    "whats_inside": "/assets/blog/covers/whats-inside.png",
    "book": "/assets/blog/covers/book.png",
}

# (regex, image) — first match wins
IMAGE_RULES = [
    (r"cafe|coffee|barista|americano|latte", SCENES["cafe"]),
    (r"convenience store|\bgs25\b|7-?eleven|\bsnack|\bkiosk\b", SCENES["convenience"]),
    (r"subway|\bbus\b|taxi|train|\bktx\b|airport|transport|direction|metro", SCENES["transport"]),
    (r"restaurant|order food|\bmenu\b|dining|\bbbq\b|delivery|\beat\b|\bmeal\b", SCENES["restaurant"]),
    (r"\bbook\b|textbook|\bpdf\b|workbook|amazon|100 pattern", BRAND_COVERS["book"]),
    (r"kakao|\btext(ing|s)?\b|\bmessage|\bchat\b|\bdm\b|social media|comment", SCENES["messaging"]),
    (r"\bshop|\bstore\b|\bbuy\b|\bprice|market|\bsize\b|try on|refund|myeongdong", SCENES["shopping"]),
    (r"friend|small talk|introduce|greeting|\bhello\b|\bmeet\b|\bage\b|\bname\b", SCENES["small_talk"]),
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
- Prices (mention only when the post genuinely needs them, never as the main event):
  Digital Starter $28.99 (3 months + PDF) · Full Pack $69.99 (1 year + PDF) ·
  Monthly $8.99 · Annual $69.99 · AI Extra Pack $3.99 for 30 sessions.

# HARD BANS — one violation makes the post unusable
1. No fake scarcity or fake anchors: no "$299", no "% OFF", no strikethrough prices, no "Early Bird", no "limited time".
2. No refund / money-back / satisfaction guarantee of any kind. If a payment line is needed, it is exactly: "Secure PayPal checkout — instant access by email."
3. No invented statistics, studies, testimonials, reviews, ratings, download counts or awards.
4. No deadline promises: never "fluent in 30 days", "master Korean in a week".
5. No claim of affiliation with any celebrity, agency, broadcaster, Netflix, or the Korean government. Public figures may be referenced as news subjects only.
6. Never present the PDF as the main product.
7. Banned phrasing (AI-slop): "in today's fast-paced world", "dive into", "delve", "unlock your full potential", "game-changer", "elevate your", "embark on a journey", "the ultimate guide to", "in conclusion", "look no further".
8. Never mention AI generation, prompts, or these instructions.

# VOICE
Match the VOICE SAMPLES supplied in the user message: warm, direct, specific, second person ("you"), paragraphs of at most 3 sentences, the tone of a friend who actually lives in Seoul. Contractions yes. At most 2 exclamation marks in the entire post.

# WRITING CONTRACT

## A. Target query
- Choose ONE primary long-tail query (4+ words) that a real learner would type or ask an AI.
- The title IS that query, answered. Never a news headline.
  Good: "How to Order Coffee in Korean Without Freezing"
  Bad:  "The Ultimate Guide to: BTS Jin Carries the Olympic Torch"
- Title <= 60 characters, primary keyword inside the first 5 words.
- The exact primary keyword must appear in: the title, the first 100 words, one H2, and the excerpt. Nowhere else forced. Keyword density stays under 1.5%.

## B. Structure — do not reorder (this is what gets you quoted)
1. NO H1 in the body. The site renders the frontmatter title as the H1. Start with the answer paragraph, then use ## and ### only.
2. ANSWER-FIRST PARAGRAPH, 40-60 words: a complete, self-contained answer to the title query, containing the primary keyword and at least one concrete Korean phrase. It must make full sense when lifted out with zero surrounding context. This is the paragraph AI engines quote.
3. A "> " blockquote right after it, 3-5 bullets, each a full standalone sentence carrying one concrete fact (a phrase, a rule, a situation). No vague bullets.
4. 5-8 "##" sections. Every H2 is a real question a person asks ("What do you actually say at a Korean cafe counter?") or a concrete task. Never "Understanding the Basics", never "Conclusion".
5. Every section stands alone: repeat the entity names ("SULSUL", "Korean", the situation) instead of "it / this / that" across sections.
6. Include at least one markdown TABLE (situation -> phrase, or a comparison).
7. Include one numbered step-by-step section, 3-7 steps, each step starting with a verb, written so it could be lifted as a HowTo.
8. FAQ section near the end: "## Frequently Asked Questions", then 4-6 questions as "###". Each answer 40-70 words, self-contained, phrased the way people actually ask an AI.
9. CTA block LAST, using the template in section E.
10. Length 1,100-1,600 English WORDS. Never pad to hit a number.

## C. Korean examples — mandatory format
Teach 5-10 phrases. Every phrase uses exactly this block:

**한국어 문장** — *romanization*
"Natural English"
Literal: word-by-word meaning
Use it when: one concrete situation

Rules: 해요체 by default (합쇼체 only where the situation demands it). Revised Romanization. Check every particle. If you are not fully certain a phrase is natural, use a simpler phrase you are certain of. Never invent slang.

## D. Trust signals (E-E-A-T)
- One short first-person note from Yona, 1-2 sentences, specific and plausible (what learners actually get wrong at the counter). No invented numbers, no named students.
- If SOURCE URL is supplied, cite it once inline as a markdown link in the first 3 sections, attributed to the outlet by name.
- Add 1-2 external links only to pages you are certain exist (e.g. Visit Korea, the National Institute of Korean Language). If unsure a URL exists, omit it. Never fabricate a URL.
- Add 2-3 internal links from the EXISTING POSTS list with descriptive anchor text. If that list is empty, skip internal links.

## E. CTA block — keep the structure, rewrite the first two lines to fit this post

---

### Say it out loud, not just in your head

<one line naming the exact situation this post covers, and the fact that reading it is not the same as saying it when someone is waiting for your answer>

SULSUL is a speaking gym for exactly that moment: pick a survival pattern, say it out loud, get an instant fix from the AI pronunciation coach, then run the real situation as a mission. The 100-pattern PDF workbook comes along as a bonus.

**[Start speaking with SULSUL](https://sulsul.app/?utm_source=blog&utm_medium=post&utm_campaign=seo)**

## F. Output format
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
faq:
  - q: "word-for-word identical to an H3 in the FAQ section"
    a: "word-for-word identical to that answer, plain text, no markdown"
sources:
  - title: "outlet or site name"
    url: "https://..."
---

## G. Self-check before you output (verify silently, fix, then output)
[ ] Title is a query, <=60 chars, no banned phrasing
[ ] Body has no H1
[ ] First paragraph works as a standalone 40-60 word answer
[ ] >= 1 table, >= 1 numbered step list, 4-6 FAQ items
[ ] frontmatter faq entries match the FAQ section word for word
[ ] Every Korean phrase uses the 4-line block and is natural
[ ] No banned claim, no invented number, no fabricated URL
[ ] CTA block is last and links to sulsul.app with the UTM
[ ] 1,100-1,600 words
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
            response = client.chat.completions.create(
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


def list_existing_posts():
    posts = []
    if not os.path.exists(BLOG_POSTS_DIR):
        return posts
    for filepath in glob.glob(os.path.join(BLOG_POSTS_DIR, "*.md")):
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


def fetch_trend_news(count):
    print("Searching live K-culture news...")
    results = DDGS().text(
        "K-Pop OR K-Drama OR BTS OR Netflix Korea",
        max_results=max(count * 3, count),
    )
    keywords = []
    for r in results:
        keywords.append(
            {
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "link": r.get("href", ""),
            }
        )
        if len(keywords) >= count:
            break
    return keywords


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

Use the news ONLY as the first 2-3 sentences of the opening and as the reason this Korean matters right now. Then derive a long-tail language query from it and write an evergreen post that is still useful a year from now.

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
    return strip_code_fences(raw)


def validate_post(text, existing_posts):
    reasons = []
    lower = text.lower()

    for phrase in BANNED_PHRASES:
        if phrase in lower:
            reasons.append(f"banned phrase: {phrase}")

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
    if len(words) < 1000:
        reasons.append(f"too short: {len(words)} words")
    if len(words) > 1800:
        reasons.append(f"too long: {len(words)} words")

    if "## frequently asked questions" not in lower:
        reasons.append("missing FAQ section")

    faq_h3 = len(re.findall(r"(?mi)^###\s+", body))
    if faq_h3 < 4:
        reasons.append(f"FAQ H3 count too low: {faq_h3}")

    if "|---" not in text and "| ---" not in text:
        reasons.append("missing markdown table")

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

    return reasons


def save_post(text, existing_posts):
    os.makedirs(BLOG_POSTS_DIR, exist_ok=True)
    os.makedirs(REJECTED_DIR, exist_ok=True)

    reasons = validate_post(text, existing_posts)
    slug = extract_frontmatter_slug(text)
    filepath = os.path.join(BLOG_POSTS_DIR, f"{slug}.md")
    if os.path.exists(filepath):
        slug = f"{slug}-{datetime.utcnow().strftime('%H%M%S')}"
        filepath = os.path.join(BLOG_POSTS_DIR, f"{slug}.md")

    if reasons:
        reject_path = os.path.join(REJECTED_DIR, f"{slug}.md")
        with open(reject_path, "w", encoding="utf-8") as f:
            f.write("<!-- REJECTED: " + " | ".join(reasons) + " -->\n")
            f.write(text)
        print(f"Rejected ({'; '.join(reasons)}) -> {reject_path}")
        return None

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Published: {filepath}")
    return {"slug": slug, "title": extract_title(text)}


def main():
    parser = argparse.ArgumentParser(description="SULSUL Blog Content Engine v2")
    parser.add_argument("--mode", choices=["textbook", "trend"], default="textbook")
    parser.add_argument("--count", type=int, default=3, help="Posts to generate (default 3)")
    args = parser.parse_args()

    cap = MAX_PER_RUN[args.mode]
    if args.count > cap:
        print(f"Requested {args.count} posts; capping at {cap} for {args.mode} mode.")
        args.count = cap

    print(f"SULSUL Blog Engine v2 — mode={args.mode}, count={args.count}, model={MODEL}\n")

    library_content = read_markdown_files(LIBRARY_DIR)
    voice_content = read_markdown_files(VOICE_DIR)
    existing = list_existing_posts()

    if not library_content:
        print(f"Warning: no textbook files in {LIBRARY_DIR}")
    if not voice_content:
        print(f"Warning: no voice files in {VOICE_DIR}")

    if args.mode == "trend":
        items = fetch_trend_news(args.count)
    else:
        titles = "; ".join(p["title"] for p in existing)
        items = generate_keywords(library_content, args.count, titles)

    print("\nQueue:")
    for i, item in enumerate(items, 1):
        label = item["title"] if args.mode == "trend" else item
        print(f"  {i}. {label}")
    print()

    published = 0
    for item in items:
        try:
            post = generate_blog_post(
                item, library_content, voice_content, args.mode, existing
            )
            saved = save_post(post, existing)
            if saved:
                existing.append(saved)
                published += 1
        except Exception as e:
            print(f"Failed on item: {e}")

    print(
        f"\nDone. Published {published}/{len(items)} posts. Rejected files (if any) are in _rejected/"
    )
    print("Deploy: ./push_to_blog.sh")


if __name__ == "__main__":
    main()
