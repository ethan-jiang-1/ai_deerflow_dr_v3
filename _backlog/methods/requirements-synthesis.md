---
name: requirements-synthesis
description: Organize confirmed requirements and evidence, compare approaches, and record a supported conclusion and closure criteria on the issue card.
whenToUse: An issue has enough information to compare approaches or prepare a conclusion. Not implementation or scheduling.
---

# Organize the approach and conclusion

**Input:** the scoped card, confirmed answers and terms, evidence, prototype findings,
alternatives, constraints and unresolved questions. Follow the [user-confirmation
rules](requirements-elicitation.md). A missing fact or uncertain choice remains explicit.

## 1. Organize confirmed requirements

Synthesize the answers already obtained into the card's `## 方案与取舍`. Cover the user's
workflow, intended result, relevant failure and recovery cases, scope and exclusions. For
model-facing work include authority per action, correction, and behavior when the model is
wrong, uncertain, refuses or hallucinates. Retain alternatives actually considered, their
costs and supporting evidence.

Use `codebase-design` only when module interfaces or test seams need analysis. Verify existing
capabilities and prefer established seams. If a new requirements gap appears, return to that
specific question rather than restarting the entire discussion.

**Done:** another session can reconstruct the intended result, scope and reasons from the card
without the conversation. For a do-it conclusion, prepare [acceptance
criteria](validation-design.md) now, before comparing implementation steps. Deferral, rejection
and an existing conclusion do not require hypothetical implementation criteria.

## 2. Compare approaches and steps where needed

Compare genuine candidates against the confirmed requirements, costs and evidence. Prefer
behavior and contract descriptions over brittle line-by-line implementation recipes. Keep
source paths and assertion targets where they make a fact or acceptance criterion checkable.

For work needing multiple independently verifiable steps, keep candidate steps on the current
card (they become the change's tasks at handoff), not in new ticket files or an execution
queue. Each names the result delivered, acceptance criteria and real prerequisites. A small
problem needs no invented breakdown.

Present unresolved choices with evidence and a recommendation when supported; set the card to
`状态: 等人拍板` while a human choice blocks. Human approval of a breakdown confirms that
choice; it does not grant implementation authority beyond the user's actual request.

## 3. Record the conclusion and prepare the handoff

Use the [backlog closure criteria](../README.md) (four-way table). Answer whether to do it,
when, in what order and what is excluded, only to the detail needed for the conclusion. Record
one of:

- **Do it:** confirmed result, scope, approach, reasons and executable acceptance criteria.
- **Do it later:** reason, observable reconsideration condition and its location; a qualifying
  condition goes to [triggers.md](../triggers.md) per its admit bar, the sentence itself stays
  on this card.
- **Do not do it:** reason and applicable scope.
- **An existing conclusion answers it:** destination link and the question it settles.

If facts or user confirmation still block the conclusion, keep the issue active and name the
exact gap and next step. A card status never grants authority.

Use [the handoff method](issue-to-change.md) to request downstream handling when needed.
Backlog prepares and submits the materials; the OpenSpec flow decides whether a change opens
and how it is implemented. Submission is not change creation or downstream completion.

Persist the confirmed answers, evidence and unresolved questions before a session boundary. On
resume, reread the card and linked artifacts; ask the user only where reconstruction leaves a
dependent choice uncertain.

**Finish:** the card has a supported conclusion ready for handoff, or a concrete unresolved
question. The card's closure follows the backlog rules, independently of downstream completion.
