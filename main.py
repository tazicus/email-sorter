import argparse
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from classifier import classify_email
from config import load_config
from filters import is_trash
from imap_client import IMAPClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sort unimportant emails into a separate folder.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without moving any emails")
    parser.add_argument("--limit", type=int, default=50, metavar="N", help="Max emails to process (default: 50)")
    parser.add_argument("--inbox", default=None, metavar="FOLDER", help="Override inbox folder for all accounts")
    return parser.parse_args()


def process_account(account: dict, model: str, args: argparse.Namespace) -> None:
    inbox = args.inbox or account["inbox"]
    sort_folder = account["sort_folder"]
    important_folder = account["important_folder"]
    trash_folder = account["trash_folder"]

    client = IMAPClient(
        server=account["server"],
        port=account["port"],
        email_address=account["email"],
        password=account["password"],
    )

    try:
        print(f"Connecting to {account['server']}...")
        client.connect()

        if not args.dry_run:
            client.ensure_folder(sort_folder)
            client.ensure_folder(important_folder)

        print(f"Fetching up to {args.limit} unread emails from {inbox}...")
        emails = client.fetch_unread(folder=inbox, limit=args.limit)
        if not emails:
            print("No unread emails found.")
            return

        uids_trash: list[str] = []
        to_classify = []
        for em in emails:
            if is_trash(em["sender"], em["subject"]):
                uids_trash.append(em["uid"])
                print(f"[TRASH   ] {em['subject'][:60]!r}")
                print(f"           From: {em['sender'][:60]}")
                print(f"           Reason: matched filter rule\n")
            else:
                to_classify.append(em)

        print(f"Classifying {len(to_classify)} emails...\n")
        uids_important: list[str] = []
        uids_sort: list[str] = []

        for em in to_classify:
            result = classify_email(
                sender=em["sender"],
                subject=em["subject"],
                body=em["body"],
                model=model,
            )
            if result.classification == "important":
                label = "IMPORTANT"
                uids_important.append(em["uid"])
            else:
                label = "SORT     "
                uids_sort.append(em["uid"])
            print(f"[{label}] {em['subject'][:60]!r}")
            print(f"           From: {em['sender'][:60]}")
            print(f"           Reason: {result.reason}\n")

        print(f"Summary: {len(uids_trash)} trashed, {len(uids_important)} important, {len(uids_sort)} to sort")

        if args.dry_run:
            if uids_trash:
                print(f"[dry-run] Would move {len(uids_trash)} emails to '{trash_folder}'")
            if uids_important:
                print(f"[dry-run] Would move {len(uids_important)} emails to '{important_folder}'")
            if uids_sort:
                print(f"[dry-run] Would move {len(uids_sort)} emails to '{sort_folder}'")
        else:
            if uids_trash:
                print(f"Moving {len(uids_trash)} emails to '{trash_folder}'...")
                client.move_emails(uids_trash, destination=trash_folder, source=inbox)
            if uids_important:
                print(f"Moving {len(uids_important)} important emails to '{important_folder}'...")
                client.move_emails(uids_important, destination=important_folder, source=inbox)
            if uids_sort:
                print(f"Moving {len(uids_sort)} emails to '{sort_folder}'...")
                client.move_emails(uids_sort, destination=sort_folder, source=inbox)
            if uids_trash or uids_important or uids_sort:
                print("Done.")

    finally:
        client.disconnect()


def main() -> None:
    args = parse_args()
    config = load_config()

    try:
        for i, account in enumerate(config["accounts"], 1):
            print(f"\n{'=' * 60}")
            print(f"Account {i}: {account['email']}")
            print(f"{'=' * 60}")
            try:
                process_account(account, config["model"], args)
            except Exception as e:
                print(f"[ERROR] Account {i} ({account['email']}): {e}")
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
