import json
from typing import Literal

import anthropic
from pydantic import BaseModel


class EmailClassification(BaseModel):
    classification: Literal["important", "not_important"]
    reason: str


_SCHEMA = {
    "type": "object",
    "properties": {
        "classification": {"type": "string", "enum": ["important", "not_important"]},
        "reason": {"type": "string"},
    },
    "required": ["classification", "reason"],
    "additionalProperties": False,
}

_SYSTEM_PROMPT = """You are an email importance classifier. Classify each email as "important" or "not_important".

Important: personal messages, work requiring action, financial transactions, legal/official documents, security alerts.
Not important: marketing, newsletters, promotions, social media notifications, automated digests."""

_client = anthropic.Anthropic()


def classify_email(sender: str, subject: str, body: str, model: str = "claude-haiku-4-5") -> EmailClassification:
    response = _client.messages.create(
        model=model,
        max_tokens=128,
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"From: {sender}\nSubject: {subject}\n\nBody:\n{body[:500]}",
            }
        ],
        output_config={"format": {"type": "json_schema", "schema": _SCHEMA}},
    )
    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)
    return EmailClassification(**data)
