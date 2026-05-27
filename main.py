import argparse
import sys

from classifier import classify_email
from config import load_config
from imap_client import IMAPClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sort unimportant emails into a separate folder.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without moving any emails")
    parser.add_argument("--limit", type=int, default=50, metavar="N", help="Max emails to process (default: 50)")
    parser.add_argument("--inbox", default=None, metavar="FOLDER", help="Override inbox folder name")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()

    inbox = args.inbox or config["INBOX_FOLDER"]
    sort_folder = config["SORT_FOLDER"]
    model = config["MODEL"]

    client = IMAPClient(
        server=config["IMAP_SERVER"],
        port=config["IMAP_PORT"],
        email_address=config["EMAIL_ADDRESS"],
        password=config["EMAIL_PASSWORD"],
    )

    try:
        print(f"Connecting to {config['IMAP_SERVER']}...")
        client.connect()

        if not args.dry_run:
            client.ensure_folder(sort_folder)

        print(f"Fetching up to {args.limit} unread emails from {inbox}...")
        emails = client.fetch_unread(folder=inbox, limit=args.limit)
        if not emails:
            print("No unread emails found.")
            return

        print(f"Classifying {len(emails)} emails...\n")
        uids_to_sort: list[str] = []
        kept = 0

        for em in emails:
            result = classify_email(
                sender=em["sender"],
                subject=em["subject"],
                body=em["body"],
                model=model,
            )
            label = "KEEP  " if result.classification == "important" else "SORT  "
            print(f"[{label}] {em['subject'][:60]!r}")
            print(f"         From: {em['sender'][:60]}")
            print(f"         Reason: {result.reason}\n")

            if result.classification == "not_important":
                uids_to_sort.append(em["uid"])
            else:
                kept += 1

        print(f"Summary: {kept} kept, {len(uids_to_sort)} to sort")

        if uids_to_sort:
            if args.dry_run:
                print(f"[dry-run] Would move {len(uids_to_sort)} emails to '{sort_folder}'")
            else:
                print(f"Moving {len(uids_to_sort)} emails to '{sort_folder}'...")
                client.move_emails(uids_to_sort, destination=sort_folder, source=inbox)
                print("Done.")

    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(1)
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
