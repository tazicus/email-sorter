"""List all folders on every configured account."""
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
    })
    i += 1

for acc in accounts:
    print(f"\nAccount {acc['index']}: {acc['email']}")
    print("-" * 50)
    try:
        ctx = ssl.create_default_context()
        conn = imaplib.IMAP4_SSL(acc["server"], acc["port"], ssl_context=ctx)
        conn.login(acc["email"], acc["password"])
        status, folders = conn.list()
        for f in folders:
            print(f.decode() if isinstance(f, bytes) else f)
        conn.logout()
    except Exception as e:
        print(f"Error: {e}")
