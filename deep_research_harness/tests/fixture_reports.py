"""Shared fixture report builder for journeys and unit tests.

Fixture-only helper: scenarios wrap their asserted sentences as the body so
journeys keep proving plumbing while the report stays realistic (heading,
Sources section, structure floor). The real structure contract is owned by the
engine validator, never by this template. stdlib-only so the offline unit lane
can import it.
"""

from __future__ import annotations


def fixture_report(body: str) -> str:
    return (
        "## 结论\n\n"
        f"{body}\n\n"
        "## 依据摘要\n\n"
        "Fixture 脚本正文按 final_report 准入契约组织：至少一个 Markdown 标题、"
        "一个 Sources 类来源节、以及足够的最小长度；本段落既是契约说明也是长度"
        "的一部分。旅程断言所需原文片段完整保留于正文，供各旅程逐一核验。\n\n"
        "## Sources\n\n"
        "- https://fixture.example/source-a\n"
        "- https://fixture.example/source-b\n"
        "- https://fixture.example/source-c\n"
    )
