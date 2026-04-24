#!/usr/bin/env python3
"""
generate_post.py

Generates a new SEO-optimized affiliate blog post using Claude AI.
Reads the next topic from topics.txt and saves the post to content/posts/.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key_here
    python generate_post.py
"""

import os
import json
import re
import sys
from datetime import date
from pathlib import Path

import anthropic

# ── Configuration ─────────────────────────────────────────────────────────────

TOPICS_FILE = Path(__file__).parent / "topics.txt"
POSTS_DIR   = Path(__file__).parent / "content" / "posts"
MODEL       = "claude-haiku-4-5-20251001"

AMAZON_ASSOCIATE_ID = "gymjar-20"

SYSTEM_PROMPT = """\
You are an expert content writer for a fitness and gym equipment affiliate blog.
You write in a helpful, honest, and conversion-focused style.
Your articles are thorough, specific, and genuinely useful to readers.
You include real product names, realistic price ranges, and balanced assessments.
You understand fitness culture, gym terminology, and what serious athletes and casual gym-goers need."""


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_next_topic() -> str:
    """Pop and return the first topic from topics.txt."""
    if not TOPICS_FILE.exists():
        sys.exit("Error: topics.txt not found.")

    lines = [l.strip() for l in TOPICS_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]

    if not lines:
        sys.exit("Error: topics.txt is empty. Add more topics!")

    topic = lines[0]
    TOPICS_FILE.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")
    return topic


def generate_post(topic: str) -> dict:
    """Call Claude to generate a blog post and return parsed JSON."""
    client = anthropic.Anthropic()

    user_prompt = f"""Write a comprehensive, SEO-optimized affiliate blog post.

Topic: {topic}

Return ONLY a valid JSON object — no markdown code fences, no extra text — with these exact fields:

{{
  "title": "SEO title (50-60 chars, include year if evergreen)",
  "slug": "url-friendly-slug-with-hyphens",
  "description": "Compelling meta description (150-160 chars)",
  "tags": ["tag1", "tag2", "tag3"],
  "excerpt": "2-3 sentence excerpt summarising the article",
  "content": "Full article in markdown (1200-1800 words)",
  "image_url": "https://images.unsplash.com/photo-xxxxx?w=1200&q=80"
}}

Requirements for the content field:
- Start with an engaging 2-paragraph introduction (no H2 heading yet)
- Include 4-6 H2 product sections, each covering: name, key specs, who it suits, typical price
- Insert this exact affiliate link wherever natural: [Check Price on Amazon](https://amazon.com?tag={AMAZON_ASSOCIATE_ID})
- End with a "## Final Verdict" H2 giving a clear overall recommendation
- Use real product names (Rogue, Bowflex, Garmin, Whoop, Nike, Lululemon, Theragun, etc.)
- Keep tone motivational, practical, and genuine — not salesy
- Target both beginner gym-goers and experienced athletes where relevant
- Escape all quotes and newlines properly so the JSON is valid

Image URL Instructions:
- Find ONE relevant fitness/gym/workout image from Unsplash
- Search Unsplash for images matching the topic (e.g., "best dumbbells" → weight training images)
- Use direct download URL format: https://images.unsplash.com/photo-[ID]?w=1200&q=80
- If no good thematic match found, set image_url to null
- Do NOT invent URLs — only use valid Unsplash image URLs you're confident about
"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)


def save_post(post: dict) -> Path:
    """Write the post as a Hugo-formatted markdown file."""
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    today    = date.today().isoformat()
    slug     = post["slug"]
    filename = f"{today}-{slug}.md"
    filepath = POSTS_DIR / filename

    tags_yaml = "\n".join(f'  - "{tag}"' for tag in post.get("tags", []))

    # Extract image URL if present and not null
    image_url = post.get("image_url") or ""
    image_yaml = f'image: "{image_url}"\n' if image_url else ""

    front_matter = f"""---
title: "{post['title']}"
date: {today}
description: "{post['description']}"
slug: "{slug}"
tags:
{tags_yaml}
excerpt: "{post['excerpt']}"
{image_yaml}draft: false
---

"""

    filepath.write_text(front_matter + post["content"], encoding="utf-8")
    return filepath


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    topic = get_next_topic()
    print(f"Generating post: {topic}")

    post     = generate_post(topic)
    filepath = save_post(post)

    remaining = [l for l in TOPICS_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"Saved → {filepath.name}")
    print(f"Title  : {post['title']}")
    print(f"Topics remaining: {len(remaining)}")


if __name__ == "__main__":
    main()
