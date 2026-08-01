# SULSUL Korean Blog

Programmatic SEO + GEO content engine for [sulsul.app](https://sulsul.app).

## Positioning

Speak Korean in Seoul — not just study it.
Speaking gym first. PDF workbook as a bonus.
Prices: Starter $28.99 / Full Pack $69.99 / Monthly $8.99 / Annual $69.99 / AI Pack $3.99.
No fake % OFF anchors. No money-back guarantee claims.

## Stack

- Next.js (App Router) + Markdown posts in `_posts/`
- `generate_seo_posts.py` — Content Engine v2 (SEO + GEO prompt, brand bans, publish gate)
- GitHub Actions: trend (2/day) + textbook (3/weekday)
- Vercel deploy on push to `main`

## Local

```bash
npm install
npm run dev
```

Generate posts (needs `OPENAI_API_KEY`):

```bash
python3 generate_seo_posts.py --mode textbook --count 3
python3 generate_seo_posts.py --mode trend --count 2
./push_to_blog.sh
```

## Env

| Variable | Where | Purpose |
|----------|-------|---------|
| `OPENAI_API_KEY` / `OPENAI` secret | GitHub Actions | Generation |
| `SULSUL_BLOG_MODEL` | optional | Default `gpt-4o` |
| `NEXT_PUBLIC_SITE_URL` | Vercel | Canonical domain (default `https://blog.sulsul.app`) |

## Key routes

- `/` — blog index
- `/posts/[slug]` — article + JSON-LD (BlogPosting, FAQPage, Breadcrumb)
- `/what-is-sulsul` — canonical brand entity page
- `/sitemap.xml`, `/robots.txt`, `/feed.xml`
- `/llms.txt`, `/llms-full.txt` — LLM agent cards

## Quality gate

Posts that fail banned-phrase, H1, FAQ, table, length, CTA, or cannibalization checks land in `_rejected/` and are **not** published to `_posts/`.
