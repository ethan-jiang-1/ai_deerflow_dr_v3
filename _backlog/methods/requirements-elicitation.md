---
name: requirements-elicitation
description: Clarify a vague request or an incomplete issue card through interview-style sharpening applied to this repo. Use for uncertain requirements, overloaded terms, or a problem too large for one sitting.
whenToUse: User-directed requirements deliberation; settle the scope and questions, record answers on the issue card, and ask the human when judgment lacks confidence. Not implementation or scheduling.
---

# Clarify requirements

**Input:** the user's request or named card and authorized deliberation scope.
**Output:** an issue card (`状态: 推敲中`) with confirmed answers, evidence links and a
judgment-ready or blocked state.

## Confirm uncertain requirements with the user

**If you lack confidence in a requirements interpretation, trade-off or recommendation, ask
the human before settling it.** Present what is confirmed, what is uncertain, its impact, the
evidence and the specific confirmation needed. Offer a recommendation only when supported;
otherwise say you cannot yet recommend. Keep the item unresolved and pause dependent
judgments, not independent work.

Facts are the agent's job: inspect accessible code, docs or experiments. If evidence remains
missing or contradictory, ask whether to investigate further, change direction or accept an
explicit assumption. Confirmation of an assumption is not proof of a fact. Business goals,
taste, acceptable risk and authority boundaries require human judgment — in this repo the
non-negotiables live in the root `AGENTS.md` (REVIEW 节制). Silence is not approval; explicit
"按建议执行" is confirmation.

## 1. Establish scope and a card

Read the [charter](../README.md), the [issues contract](../issues/README.md) and relevant
existing decisions: sweep [`_archived/_settled_issues/`](../_archived/_settled_issues/README.md)
by domain concept, and scan [triggers.md](../triggers.md) (supersede-check — an overturned
ruling may already answer this). Record the trigger, user-visible outcome and completion
condition in the existing or new `YYYY-MM-DD-<slug>.md` card; add its roster row. Separate
facts, assumptions and unanswered questions.

For a raw external bug/feature report, verify it first via the raw-request entry of
[requirements-probes](requirements-probes.md) before treating it as aligned requirements.

**Done:** one card owns the named deliberation and its current unknowns. A partial card is valid.

## 2. Interview and sharpen vocabulary

Use the `grilling` skill (plus `domain-modeling` when terms are overloaded): supply the card,
constraints, existing vocabulary and decisions. Follow its round protocol; pending lookups
block only dependent questions. Capture answers, attribution, alternatives and costs in the
card as they settle, not at the end. Record only alternatives actually considered; a fixed
constraint need not generate fake candidates.

Vocabulary owners in this repo are [`CONTEXT-MAP.md`](../../CONTEXT-MAP.md) and the
per-layer `CONTEXT.md` files — tentative terms and choices stay on the card; update current
owners only for authorized, effective facts. Do not create parallel glossary directories.

**Done or waiting:** confirmed requirements and new unknowns are on the card. An empty ready
frontier with pending facts/answers is waiting, not a completed interview. For evidence gaps,
read [requirements-probes](requirements-probes.md); return its results to the dependent
question.

## 3. Split only genuinely oversized ideas

For a destination too foggy or large for one sitting, do not chart a tracker: split the card
into named decision sections (destination, resolved decisions, precise questions,
not-yet-specified, out of scope) or open child cards that cite the parent. These are judgment
dependencies, not an execution queue. Separate questions requiring the user's judgment from
fact-finding the agent can do. Work one human-decision branch per session; independent
research can proceed in parallel. Stay within the user's named scope.

**Finish:** confirmed understanding or an honest blocker with next step/trigger is recorded.
When the conclusion is ready to be organized, read
[requirements-synthesis](requirements-synthesis.md). This method neither schedules work nor
authorizes implementation; a card status never grants authority.
