---
name: requirements-probes
description: Resolve an issue card's evidence gaps with research or a prototype; verify incoming raw reports. Return findings to the consuming card rather than creating a parallel workflow.
whenToUse: A requirements question cannot be settled by the current interview alone, or an incoming report needs verification before deliberation. Not production implementation or approval.
---

# Probe an unknown

**Input:** a scoped issue card, the exact unknown, and the judgment it blocks. Before
proceeding, read the [user-confirmation rules](requirements-elicitation.md). Read the chosen
skill and use only the missing functional step.

## 1. Pick by the unknown

| Unknown | Skill and input | Result that must return |
|---|---|---|
| External fact | `research`: small decidable question, version and primary sources | Cited answer, counterevidence and limits, not merely a report |
| Knowledge held by another person | Draft a sendable question list (recipient, facts/decisions needed back) — a human sends it | Attributed replies feeding the card |
| Logic/state feel or UI shape | `prototype`: one design question, logic or UI branch, candidates and shared inputs | Runnable artifact, observed behavior and a separately confirmed human verdict |

**Raw-request entry, not a fourth probe:** for an incoming external bug/feature report, supply
the original report, existing implementation, related rejections and verification steps;
return a verified claim or a structured "confirmed / still needed" request and a disposition
recommendation. Search by domain concept and reproduce the claim where possible; use existing
card/bug homes, not tracker labels or a new rejection directory.

For question lists, settle the send rather than asking the requester to invent the recipient's
knowledge. Send early, order by importance, assume one reply. Replies are new evidence, not an
automatic decision. Already-aligned requirements need no second verification; a ready brief is
not permission to build.

**Done:** the probe has a bounded question, input, destination and a stated way to judge its
result.

## 2. Run without stalling independent questions

Delegate independent primary-source research in the background; continue the card's ready
questions. Verify each load-bearing finding against its source and baseline when it returns.
Treat source limits and contradictory evidence as unresolved rather than smoothing them away.

For a prototype, hand the bounded question to an isolated session/directory or branch. Compare
candidates on the same inputs and let the stakeholder react to the runnable result. If the
interpretation or verdict is uncertain, ask the human. Preserve the prototype with a commit
pointer; production keeps only an authorized validated change, not the demo. No production
integration here.

For model-facing requirements, evidence may test extraction, failure mechanisms or harness
capabilities. The human still confirms acceptable behavior, autonomy and risk; successful
operation of a sample does not establish reliability, adoption or business value.

**Done or waiting:** distinguish observed result, human verdict and unresolved assumptions.
Missing recipient input or human confirmation blocks its dependent judgment, not unrelated
fact-finding.

## 3. Return evidence to its consumer

Keep short findings in the card's known/unresolved sections. This repo has no card-migration
research directory by ruling (see the charter's 刻意不借 register): evidence lives on the card;
material with long-lived external-analysis value goes to
[`_research/`](../_research/README.md) per its own contract. Link the evidence once; record
which question it settles, source/version or artifact commit, limitations, attribution and what
becomes answerable next.

**Finish:** the consuming card has updated evidence and unresolved items. Return to the
affected question in [requirements-elicitation](requirements-elicitation.md), or proceed to
[requirements-synthesis](requirements-synthesis.md) only when that judgment is ready. A report
or prototype alone does not settle a requirement or authorize implementation.
