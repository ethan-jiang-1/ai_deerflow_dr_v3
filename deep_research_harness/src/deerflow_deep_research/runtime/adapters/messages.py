"""Reading one field off a framework message.

The framework hands messages as dicts in some paths and as objects in others, so
both the stream adapter and the watch projection need the same two-case read. It
lives here (the framework-boundary package) rather than in either consumer.

@impl DEW-001"""

from __future__ import annotations


def message_field(message: object, name: str, default=None):  # noqa: ANN001 — dict/object adapter
    """The named field, whether the message is a mapping or an object."""
    if isinstance(message, dict):
        return message.get(name, default)
    return getattr(message, name, default)
