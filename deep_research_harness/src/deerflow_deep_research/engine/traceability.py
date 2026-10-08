"""Source traceability: report URLs versus the run's own search corpus.

Pure stdlib. A report's http(s) URLs are "traceable" when each appears
verbatim in the concatenated tool-output corpus of the same run
(``diagnostics/searches/`` records). This proves **record support**, never
that a record is true — the naming is 可追溯性, not 真实性.

Known boundary (deliberate, evidence-recorded): no URL-decoding, scheme
stripping, or variant normalization — a fetch result truncated by the tool
may fail to pair; admission-blocking use of this metric was rejected on
that evidence (see archive 2026-10-08 register-source-traceability-machine).

@impl RUA-002"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable

_URL_RE = re.compile(r"https?://[^\s)\]}>\"']+")
_TRAILING_PUNCT = "),.;'\""


@dataclass(frozen=True)
class SourceTraceReport:
    """Every distinct URL in the report and which side of the verdict it fell."""

    urls: tuple[str, ...]
    traceable: tuple[str, ...]
    untraceable: tuple[str, ...]


def _normalize(url: str) -> str:
    return url.rstrip(_TRAILING_PUNCT)


def search_corpus_text(records: Iterable[tuple[str, dict]]) -> str:
    """Assemble the corpus from materialized record payloads: the tool's raw
    output plus its arguments (arguments are JSON-dumped so any URL passed to
    web_fetch can also support a citation)."""
    parts: list[str] = []
    for content, arguments in records:
        parts.append(content)
        parts.append(json.dumps(arguments, ensure_ascii=False))
    return "\n".join(parts)


def trace_source_urls(report_text: str, corpus: str) -> SourceTraceReport:
    """Render the per-URL verdict. An empty corpus renders every URL
    untraceable — the metric cannot pass on empty input."""
    urls = tuple(dict.fromkeys(_normalize(u) for u in _URL_RE.findall(report_text)))
    traceable = tuple(u for u in urls if u and u in corpus)
    untraceable = tuple(u for u in urls if u not in traceable)
    return SourceTraceReport(urls=urls, traceable=traceable, untraceable=untraceable)
