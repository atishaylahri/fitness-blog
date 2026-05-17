# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Hugo static site ("Gym Stack") publishing AI-generated fitness/gym affiliate posts to GitHub Pages at https://atishaylahri.github.io/fitness-blog/. Posts are written by Claude via `generate_post.py` and committed by a weekly GitHub Actions cron.

## Commands

- Local preview: `hugo server -D` (Hugo extended v0.124.0 to match CI)
- Production build: `hugo --minify` (outputs to `./public`)
- Generate one post locally: `pip install anthropic && export ANTHROPIC_API_KEY=... && python generate_post.py`
- Trigger weekly generation manually: GitHub Actions → "Generate Weekly Post" → Run workflow

## Architecture

Two loosely coupled pipelines drive the site:

1. **Content generation** (`generate_post.py` + `topics.txt`): Pops the first line of `topics.txt`, calls Claude (model `claude-haiku-4-5-20251001`) with a strict JSON-output prompt, and writes a Hugo-formatted markdown file to `content/posts/YYYY-MM-DD-<slug>.md`. The prompt requires an Amazon affiliate link with associate tag `gymjar-20` injected into the body, plus an Unsplash `image_url`. `topics.txt` is treated as a queue — the script rewrites it in place after consuming the first line, so edits to ordering directly control what publishes next.

2. **Build/deploy** (`.github/workflows/`): `weekly-post.yml` runs Sundays 09:00 UTC, runs `generate_post.py`, and commits new posts under the `Gym Stack Bot` identity. Its completion triggers `deploy.yml` (`workflow_run`), which builds with Hugo and publishes to GitHub Pages. A push to `main` also triggers `deploy.yml` directly, so manually edited posts deploy without re-running generation.

Site config lives in `hugo.toml` (title, menus, `markup.goldmark.renderer.unsafe = true` to allow raw HTML in generated markdown). Layouts in `layouts/_default/` (`baseof.html`, `list.html`, `single.html`) and `layouts/partials/` are the only theme — there is no external Hugo theme dependency. Static assets in `static/css/`.

## Notes for editing

- When changing the post front matter shape, update `save_post()` in `generate_post.py` **and** the layout templates in `layouts/` together — they share an implicit contract (`title`, `date`, `description`, `slug`, `tags`, `excerpt`, `image`, `draft`).
- The affiliate tag `gymjar-20` and Amazon link format are hardcoded in the generation prompt; changing affiliate IDs means editing the `user_prompt` string in `generate_post.py`.
- Bumping the Hugo version requires editing `hugo-version` in `.github/workflows/deploy.yml`.
