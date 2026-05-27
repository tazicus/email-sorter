import os
from dotenv import load_dotenv


def load_config() -> dict:
    load_dotenv()
    required = ["IMAP_SERVER", "EMAIL_ADDRESS", "EMAIL_PASSWORD", "ANTHROPIC_API_KEY"]
    config = {}
    missing = []
    for key in required:
        value = os.getenv(key)
        if not value:
            missing.append(key)
        else:
            config[key] = value
    if missing:
        raise SystemExit(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in the values."
        )
    config["IMAP_PORT"] = int(os.getenv("IMAP_PORT", "993"))
    config["SORT_FOLDER"] = os.getenv("SORT_FOLDER", "Sorted")
    config["INBOX_FOLDER"] = os.getenv("INBOX_FOLDER", "INBOX")
    config["MODEL"] = os.getenv("MODEL", "claude-haiku-4-5")
    return config
