import email
import imaplib
import ssl
from email.header import decode_header as _decode_header


def _decode_header_field(value: str | bytes | None) -> str:
    if value is None:
        return ""
    parts = _decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def _extract_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
        return ""
    payload = msg.get_payload(decode=True)
    if payload is None:
        return str(msg.get_payload())
    charset = msg.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


class IMAPClient:
    def __init__(self, server: str, port: int, email_address: str, password: str):
        self.server = server
        self.port = port
        self.email_address = email_address
        self.password = password
        self._conn: imaplib.IMAP4_SSL | None = None

    def connect(self) -> None:
        context = ssl.create_default_context()
        self._conn = imaplib.IMAP4_SSL(self.server, self.port, ssl_context=context)
        self._conn.login(self.email_address, self.password)

    def disconnect(self) -> None:
        if self._conn:
            try:
                self._conn.logout()
            except Exception:
                pass
            self._conn = None

    def ensure_folder(self, folder: str) -> None:
        status, folders = self._conn.list()
        existing = [f.decode() if isinstance(f, bytes) else f for f in (folders or [])]
        # Each LIST entry looks like: (\flags) "sep" folder_name
        # Extract the folder name as the last whitespace-delimited token (strip quotes)
        folder_names = {entry.rsplit(" ", 1)[-1].strip('"') for entry in existing if entry}
        if folder not in folder_names:
            status, data = self._conn.create(folder)
            if status != "OK":
                raise RuntimeError(f"Failed to create folder '{folder}': {data}")

    def fetch_unread(self, folder: str = "INBOX", limit: int = 50) -> list[dict]:
        self._conn.select(folder, readonly=True)
        status, data = self._conn.uid("SEARCH", None, "ALL")
        if status != "OK" or not data or not data[0]:
            return []
        uids = data[0].split()
        uids = uids[-limit:]  # most recent N
        results = []
        for uid in uids:
            status, msg_data = self._conn.uid("FETCH", uid, "(RFC822)")
            if status != "OK" or not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            results.append(
                {
                    "uid": uid.decode() if isinstance(uid, bytes) else uid,
                    "subject": _decode_header_field(msg.get("Subject")),
                    "sender": _decode_header_field(msg.get("From")),
                    "recipient": _decode_header_field(msg.get("To")),
                    "body": _extract_body(msg),
                }
            )
        return results

    def move_emails(self, uids: list[str], destination: str, source: str = "INBOX") -> None:
        if not uids:
            return
        self._conn.select(source)
        uid_set = ",".join(uids)
        self._conn.uid("COPY", uid_set, destination)
        self._conn.uid("STORE", uid_set, "+FLAGS", r"(\Deleted)")
        self._conn.expunge()
