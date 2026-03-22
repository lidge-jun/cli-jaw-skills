---
name: data-scraper-agent
description: Build a fully automated AI-powered data collection agent for any public source — job boards, prices, news, GitHub, sports, anything. Scrapes on a schedule, enriches data with a free LLM (Gemini Flash), stores results in Notion/Sheets/Supabase, and learns from user feedback. Runs 100% free on GitHub Actions. Use when the user wants to monitor, collect, or track any public data automatically.
---

# Data Scraper Agent

Build a production-ready, AI-powered data collection agent for any public data source.
Runs on a schedule, enriches results with a free LLM, stores to a database, and improves over time.

**Stack: Python · Gemini Flash (free) · GitHub Actions (free) · Notion / Sheets / Supabase**

## When to Activate

- User wants to scrape or monitor any public website or API
- User says "build a bot that checks...", "monitor X for me", "collect data from..."
- User wants to track jobs, prices, news, repos, sports scores, events, listings
- User asks how to automate data collection without paying for hosting
- User wants an agent that gets smarter over time based on their decisions

## Core Concepts

### The Three Layers

Every data scraper agent has three layers:

```
COLLECT → ENRICH → STORE
  │           │        │
Scraper    AI (LLM)  Database
runs on    scores/   Notion /
schedule   summarises Sheets /
           & classifies Supabase
```

### Free Stack

| Layer | Tool | Why |
|---|---|---|
| **Scraping** | `requests` + `BeautifulSoup` | No cost, covers 80% of public sites |
| **JS-rendered sites** | `playwright` (free) | When HTML scraping fails |
| **AI enrichment** | Gemini Flash via REST API | 500 req/day, 1M tokens/day — free |
| **Storage** | Notion API | Free tier, great UI for review |
| **Schedule** | GitHub Actions cron | Free for public repos |
| **Learning** | JSON feedback file in repo | Zero infra, persists in git |

### AI Model Fallback Chain

Build agents to auto-fallback across Gemini models on quota exhaustion:

```
gemini-2.0-flash-lite (30 RPM) →
gemini-2.0-flash (15 RPM) →
gemini-2.5-flash (10 RPM) →
gemini-flash-lite-latest (fallback)
```

### Batch API Calls for Efficiency

Use batching to stay within free tier limits:

```python
# Inefficient: 33 API calls for 33 items
for item in items:
    result = call_ai(item)  # hits rate limit

# Efficient: 7 API calls for 33 items (batch size 5)
for batch in chunks(items, size=5):
    results = call_ai(batch)  # stays within free tier
```

---

## Workflow

### Step 1: Understand the Goal

Ask the user:

1. **What to collect:** "What data source? URL / API / RSS / public endpoint?"
2. **What to extract:** "What fields matter? Title, price, URL, date, score?"
3. **How to store:** "Where should results go? Notion, Google Sheets, Supabase, or local file?"
4. **How to enrich:** "Do you want AI to score, summarise, classify, or match each item?"
5. **Frequency:** "How often should it run? Every hour, daily, weekly?"

Common examples to prompt:
- Job boards → score relevance to resume
- Product prices → alert on drops
- GitHub repos → summarise new releases
- News feeds → classify by topic + sentiment
- Sports results → extract stats to tracker
- Events calendar → filter by interest

---

### Step 2: Design the Agent Architecture

Generate this directory structure for the user:

```
my-agent/
├── config.yaml              # User customises this (keywords, filters, preferences)
├── profile/
│   └── context.md           # User context the AI uses (resume, interests, criteria)
├── scraper/
│   ├── __init__.py
│   ├── main.py              # Orchestrator: scrape → enrich → store
│   ├── filters.py           # Rule-based pre-filter (fast, before AI)
│   └── sources/
│       ├── __init__.py
│       └── source_name.py   # One file per data source
├── ai/
│   ├── __init__.py
│   ├── client.py            # Gemini REST client with model fallback
│   ├── pipeline.py          # Batch AI analysis
│   ├── jd_fetcher.py        # Fetch full content from URLs (optional)
│   └── memory.py            # Learn from user feedback
├── storage/
│   ├── __init__.py
│   └── notion_sync.py       # Or sheets_sync.py / supabase_sync.py
├── data/
│   └── feedback.json        # User decision history (auto-updated)
├── .env.example
├── setup.py                 # One-time DB/schema creation
├── enrich_existing.py       # Backfill AI scores on old rows
├── requirements.txt
└── .github/
    └── workflows/
        └── scraper.yml      # GitHub Actions schedule
```

---

### Steps 3-8: Implementation Templates

Full Python implementation templates for all agent components:

- **Step 3:** Build the Scraper Source
- **Step 4:** Build the Gemini AI Client
- **Step 5:** Build the AI Pipeline (Batch)
- **Step 6:** Build the Feedback Learning System
- **Step 7:** Build Storage (Notion example)
- **Step 8:** Orchestrate in main.py

See [references/code-templates.md](references/code-templates.md) for complete code with:
- Scraper source template with REST API, HTML, and RSS patterns
- Gemini AI client with model fallback and rate limiting
- Batch AI pipeline with config-driven analysis
- Feedback learning system with positive/negative classification
- Notion storage sync with duplicate detection
- Main.py orchestrator tying all components together

For common scraping patterns (REST API, HTML parsing, RSS feeds, pagination, JS-rendered pages), see [references/scraping-patterns.md](references/scraping-patterns.md).

---

### Step 9: GitHub Actions Workflow

```yaml
# .github/workflows/scraper.yml
name: Data Scraper Agent

on:
  schedule:
    - cron: "0 */3 * * *"  # every 3 hours — adjust to your needs
  workflow_dispatch:        # allow manual trigger

permissions:
  contents: write   # required for the feedback-history commit step

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - run: pip install -r requirements.txt

      # Uncomment if Playwright is enabled in requirements.txt
      # - name: Install Playwright browsers
      #   run: python -m playwright install chromium --with-deps

      - name: Run agent
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python -m scraper.main

      - name: Commit feedback history
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/feedback.json || true
          git diff --cached --quiet || git commit -m "chore: update feedback history"
          git push
```

---

### Step 10: config.yaml Template

```yaml
# Customise this file — no code changes needed

# What to collect (pre-filter before AI)
filters:
  required_keywords: []      # item must contain at least one
  blocked_keywords: []       # item must not contain any

# Your priorities — AI uses these for scoring
priorities:
  - "example priority 1"
  - "example priority 2"

# Storage
storage:
  provider: "notion"         # notion | sheets | supabase | sqlite

# Feedback learning
feedback:
  positive_statuses: ["Saved", "Applied", "Interested"]
  negative_statuses: ["Skip", "Rejected", "Not relevant"]

# AI settings
ai:
  enabled: true
  model: "gemini-2.5-flash"
  min_score: 0               # filter out items below this score
  rate_limit_seconds: 7      # seconds between API calls
  batch_size: 5              # items per API call
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Breaks | Fix |
|---|---|---|
| One API call per item | Hits rate limits fast | Batch items (5 per call) |
| Parsing JS-heavy sites with BeautifulSoup | Returns empty HTML | Use Playwright for dynamic content |
| Ignoring user feedback | Agent never learns | Log positive/negative decisions to `data/feedback.json` |
| Hardcoding API keys in code | Security risk, fails in CI | Use environment variables + GitHub Secrets |
| Re-scraping old items | Wastes API quota | Store item IDs, check before processing |
| Running scraper locally on your laptop | Forgets to run when offline | Use GitHub Actions cron |
| Blocking scrapers with real user agents | Gets detected as bot | Use custom, honest User-Agent string |
| Skipping error handling in scrapers | One failed source crashes everything | Wrap each source in try/except |

---

## Free Tier Limits Reference

| Service | Limit | Strategy |
|---|---|---|
| **Gemini Flash API** | 500 req/day, 1M tokens/day | Batch 5 items per call, rate limit 7s |
| **GitHub Actions** | 2,000 min/month (public repos) | Typical run: 2-5 min → 400+ runs/month |
| **Notion API** | 3 req/sec (rate limit) | Add 0.5s sleep between writes |
| **Google Sheets API** | 60 req/min (user), 300 req/min (project) | Batch updates into single append call |
| **Supabase Free** | 500MB storage, 2GB bandwidth | Fine for text data agents |

---

## Requirements Template

```txt
# requirements.txt
requests>=2.32.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
pyyaml>=6.0
python-dotenv>=1.0.0

# For Notion
notion-client>=2.2.0

# For Google Sheets
# google-auth>=2.28.0
# google-auth-oauthlib>=1.2.0
# google-auth-httplib2>=0.2.0
# google-api-python-client>=2.118.0

# For Supabase
# supabase>=2.4.0

# For JS-rendered pages
# playwright>=1.41.0
```

---

## Quality Checklist

Before deploying your agent:

- [ ] Scraper returns consistent schema (name, url, date_found minimum)
- [ ] Pre-filters (keywords) work and reduce API load
- [ ] AI batching enabled (batch_size ≥ 3)
- [ ] Model fallback chain configured in `ai/client.py`
- [ ] Storage sync handles duplicates (check by URL or unique ID)
- [ ] Feedback system logs positive/negative decisions
- [ ] Config file has user priorities and keywords filled in
- [ ] Profile context.md describes user background for AI scoring
- [ ] GitHub Actions secrets set (GEMINI_API_KEY, storage tokens)
- [ ] Cron schedule matches user needs (hourly / daily / weekly)
- [ ] Test run completes without errors: `python -m scraper.main`
- [ ] GitHub Actions workflow commits feedback.json back to repo
- [ ] Rate limits respected (7s between Gemini calls, 0.5s for Notion)
- [ ] Error handling in place for API failures and network issues

---

## Real-World Examples

```
"Build me an agent that monitors Hacker News for AI startup funding news"
"Scrape product prices from 3 e-commerce sites and alert when they drop"
"Track new GitHub repos tagged with 'llm' or 'agents' — summarise each one"
"Collect Chief of Staff job listings from LinkedIn and Cutshort into Notion"
"Monitor a subreddit for posts mentioning my company — classify sentiment"
"Scrape new academic papers from arXiv on a topic I care about daily"
"Track sports fixture results and keep a running table in Google Sheets"
"Build a real estate listing watcher — alert on new properties under ₹1 Cr"
```

---

## Reference Implementation

A complete working agent built with this exact architecture would scrape 4+ sources,
batch Gemini calls, learn from Applied/Rejected decisions stored in Notion, and run
100% free on GitHub Actions. Follow Steps 1–10 above to build your own.
