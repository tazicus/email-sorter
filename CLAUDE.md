# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Email sorter: connects to an IMAP mailbox, classifies unread emails as "important" or "not_important" using Claude AI, and moves unimportant ones to a configurable folder (default: `Sorted`).

## Environment Setup

```bash
python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

copy .env.example .env
# Fill in IMAP_SERVER, EMAIL_ADDRESS, EMAIL_PASSWORD, ANTHROPIC_API_KEY
```

## Common Commands

```bash
# Preview what would be moved without touching anything
python main.py --dry-run

# Process up to 100 emails
python main.py --limit 100

# Use a non-default inbox folder
python main.py --inbox "Work"

# Run tests
python -m pytest

# Lint / format
ruff check .
black .
```

## Architecture

Five modules, each with a single responsibility:

| File | Role |
|---|---|
| `config.py` | Loads `.env` via `python-dotenv`; validates required vars; returns a plain `dict` |
| `imap_client.py` | `IMAPClient` — SSL IMAP connection, fetch unread emails, move by UID |
| `classifier.py` | Calls Claude API; returns `EmailClassification(classification, reason)` |
| `main.py` | CLI entry point — orchestrates fetch → classify → move |

### Key design decisions

- **UID-based IMAP ops** (`uid("SEARCH")`, `uid("FETCH")`, `uid("COPY")`, `uid("STORE")`) — avoids sequence number drift when expunging during batch deletes.
- **Batch move strategy** — classify all emails first, collect UIDs, then a single `move_emails()` call + single `expunge`. Never moves mid-loop.
- **Prompt caching** — system prompt in `classifier.py` carries `cache_control: {type: "ephemeral"}`. Cached across all calls in a session (significant cost savings at volume).
- **Structured output** — `output_config.format` with explicit JSON schema enforces `classification` enum + `reason` string. Parsed with `pydantic`.
- **Model** — defaults to `claude-haiku-4-5` (cost-effective for classification); override via `MODEL` env var.

### Data flow

```
.env → config.py → main.py
                     │
                     ├─ imap_client.py  →  IMAP server (fetch unread)
                     ├─ classifier.py   →  Claude API  (classify each)
                     └─ imap_client.py  →  IMAP server (move batch)
```

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `IMAP_SERVER` | yes | — | Hostname, e.g. `imap.gmail.com` |
| `IMAP_PORT` | no | `993` | SSL port |
| `EMAIL_ADDRESS` | yes | — | Login address |
| `EMAIL_PASSWORD` | yes | — | Password or app-specific password |
| `ANTHROPIC_API_KEY` | yes | — | Claude API key |
| `SORT_FOLDER` | no | `Sorted` | Destination folder for unimportant mail |
| `INBOX_FOLDER` | no | `INBOX` | Source folder to read from |
| `MODEL` | no | `claude-haiku-4-5` | Any Claude model ID |
