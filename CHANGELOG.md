# Changelog

All changes to this project are recorded here.

---

## 2026-05-27

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
