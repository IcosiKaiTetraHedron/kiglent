"""Plain text decoder."""
from __future__ import annotations

from typing import TYPE_CHECKING

import kiglent

if TYPE_CHECKING:
    from kiglent.resource import Location
    from kiglent.text import UnformattedDocument


class PlainTextDecoder(kiglent.text.DocumentDecoder):  # noqa: D101
    def decode(self, text: str, location: Location | None=None) -> UnformattedDocument:  # noqa: ARG002
        document = kiglent.text.document.UnformattedDocument()
        document.insert_text(0, text)
        return document
