import os
from dotenv import load_dotenv


def load_config() -> dict:
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Missing required environment variable: ANTHROPIC_API_KEY")

    # Shared folder defaults — used when an account has no account-specific override
    shared_sort_folder = os.getenv("SORT_FOLDER", "Sorted")
    shared_important_folder = os.getenv("IMPORTANT_FOLDER", "Important")
    shared_inbox_folder = os.getenv("INBOX_FOLDER", "INBOX")

    accounts = []
    i = 1
    while True:
        server = os.getenv(f"IMAP_SERVER_{i}")
        if not server:
            break
        email = os.getenv(f"EMAIL_ADDRESS_{i}")
        password = os.getenv(f"EMAIL_PASSWORD_{i}")
        missing = [name for name, val in {
            f"EMAIL_ADDRESS_{i}": email,
            f"EMAIL_PASSWORD_{i}": password,
        }.items() if not val]
        if missing:
            raise SystemExit(f"Account {i} is missing: {', '.join(missing)}")
        accounts.append({
            "server": server,
            "port": int(os.getenv(f"IMAP_PORT_{i}", "993")),
            "email": email,
            "password": password,
            "sort_folder": os.getenv(f"SORT_FOLDER_{i}") or shared_sort_folder,
            "important_folder": os.getenv(f"IMPORTANT_FOLDER_{i}") or shared_important_folder,
            "inbox": os.getenv(f"INBOX_FOLDER_{i}") or shared_inbox_folder,
        })
        i += 1

    if not accounts:
        raise SystemExit(
            "No accounts configured. Add IMAP_SERVER_1, EMAIL_ADDRESS_1, "
            "EMAIL_PASSWORD_1 to .env"
        )

    return {
        "api_key": api_key,
        "model": os.getenv("MODEL", "claude-haiku-4-5"),
        "accounts": accounts,
    }
