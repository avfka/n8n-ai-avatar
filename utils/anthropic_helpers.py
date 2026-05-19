"""
Helpers for building valid Anthropic API message payloads.

The Anthropic API returns:
  400 cache_control cannot be set for empty text blocks

if any content block has both an empty `text` field and a `cache_control` key.
sanitize_messages() strips cache_control from those blocks before the request
is sent so the call never hits that validation error.
"""

from __future__ import annotations
from typing import Any


def sanitize_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a copy of *messages* safe to send to the Anthropic API.

    Removes ``cache_control`` from text blocks whose ``text`` value is empty
    (``""`` or ``None``), which would otherwise produce a 400 error.
    """
    result = []
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            new_blocks = []
            for block in content:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "text"
                    and not block.get("text")
                    and "cache_control" in block
                ):
                    block = {k: v for k, v in block.items() if k != "cache_control"}
                new_blocks.append(block)
            message = {**message, "content": new_blocks}
        result.append(message)
    return result
