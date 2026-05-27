"""Quick IMAP connection test for all configured accounts."""
import imaplib
import os
import ssl

from dotenv import load_dotenv

load_dotenv()

accounts = []
i = 1
while True:
    server = os.getenv(f"IMAP_SERVER_{i}")
    if not server:
        break
    accounts.append({
        "index": i,
        "server": server,
        "port": int(os.getenv(f"IMAP_PORT_{i}", "993")),
        "email": os.getenv(f"EMAIL_ADDRESS_{i}", ""),
        "password": os.getenv(f"EMAIL_PASSWORD_{i}", ""),
        "inbox": os.getenv(f"INBOX_FOLDER_{i}", "INBOX"),
    })
    i += 1

if not accounts:
    print("No accounts found. Check that .env has IMAP_SERVER_1, IMAP_SERVER_2, etc.")
    raise SystemExit(1)

for acc in accounts:
    label = f"Account {acc['index']} ({acc['email']})"
    missing = [k for k in ("email", "password") if not acc[k]]
    if missing:
        idx = acc["index"]
        missing_vars = ", ".join(f"EMAIL_{m.upper()}_{idx}" for m in missing)
        print(f"[SKIP]  {label} - missing: {missing_vars}")
        continue
    try:
        ctx = ssl.create_default_context()
        conn = imaplib.IMAP4_SSL(acc["server"], acc["port"], ssl_context=ctx)
        conn.login(acc["email"], acc["password"])
        status, data = conn.select(acc["inbox"], readonly=True)
        status2, uids = conn.uid("SEARCH", None, "UNSEEN")
        unread = len(data[0].split()) if status == "OK" and data[0] else 0
        conn.logout()
        print(f"[OK]    {label} — connected to {acc['server']}, {unread} unread in {acc['inbox']}")
    except imaplib.IMAP4.error as e:
        print(f"[FAIL]  {label} — IMAP error: {e}")
    except OSError as e:
        print(f"[FAIL]  {label} — network error: {e}")
