# Changelog

All changes to this project are recorded here.

---

## v0.0.2 — 2026-05-27

### Fixed
- `imap_client.py` — fixed `ensure_folder` to parse full folder names from IMAP LIST response correctly; raises error if `CREATE` fails instead of silently continuing
- `imap_client.py` — fetch scope changed from `UNSEEN` to `ALL` so both read and unread messages are processed
- `classifier.py` — lazy-init Anthropic client so `load_dotenv()` runs before the client is created
- `main.py` — force UTF-8 stdout to handle emoji in email subjects

### Changed
- Both classifications now trigger a move: important → `IMPORTANT_FOLDER`, unimportant → `SORT_FOLDER`
- `.env` / `.env.example` — folder names updated to use full `INBOX.` namespace prefix (`INBOX.aisorted`, `INBOX.ai-important`); renamed `important` → `ai-important` to avoid IMAP reserved name conflict

---

## v0.0.1 — 2026-05-27

### Added
- `.env` created from `.env.example` with multi-account structure (numbered suffixes `_1`, `_2`)
- `.env.example` updated to match multi-account structure
- `ANTHROPIC_API_KEY` and `MODEL` moved to a shared section at the top of both env files
- `EMAIL_ADDRESS_1` pre-filled with `tazicus@gmail.com`

### Added
- `test_connections.py` — standalone script to test IMAP login for all numbered accounts in `.env`
- `SETUP_INSTRUCTIONS.md` — step-by-step guide: install Python, create venv, fix Account 2 in `.env`, run connection test

### Changed
- `config.py` — rewritten to load multi-account structure; returns `{ api_key, model, accounts: [...] }` instead of flat single-account dict
- `main.py` — added `process_account()` helper; `main()` now loops over all accounts, printing a header per account

## 2026-05-27 (continued)

### Changed
- `.env` — `SORT_FOLDER`, `IMPORTANT_FOLDER`, `INBOX_FOLDER` moved to shared section as defaults; account-level `SORT_FOLDER_1` etc. removed (now optional overrides)
- `config.py` — folder variables now use fallback chain: account-specific (`SORT_FOLDER_1`) → shared (`SORT_FOLDER`) → hardcoded default; `important_folder` added to each account config
- `main.py` — both classifications now trigger a move: important emails → `IMPORTANT_FOLDER`, unimportant → `SORT_FOLDER`; inbox is fully cleared of unread emails each run
- `imap_client.py` — fetch scope changed from `UNSEEN` to `ALL` so both read and unread messages are processed
- `imap_client.py` — fixed `ensure_folder` to parse full folder names from IMAP LIST response correctly; now raises an error if `CREATE` fails instead of silently continuing
- `.env` / `.env.example` — folder names updated to use full `INBOX.` namespace prefix required by these servers (`INBOX.aisorted`, `INBOX.ai-important`); `important` renamed to `ai-important` to avoid IMAP reserved name conflict
