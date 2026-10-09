---
name: issue-to-change
description: Prepare a confirmed issue conclusion and submit it to the downstream OpenSpec process for handling; record the destination on the card and close the card when its backlog conditions are met.
whenToUse: A confirmed issue conclusion needs downstream handling. The receiving process and the user decide whether a change opens; this method only prepares and submits the request.
---

# Request downstream handling

**Input:** the scoped issue, its confirmed conclusion and supporting evidence. For work that
will be done, include its scope, alternatives and acceptance criteria. Resolve uncertain
choices through [requirements confirmation](requirements-elicitation.md) before treating them
as decisions.

**Output:** a submitted processing request with a traceable destination (an opened OpenSpec
change whose proposal cites this card), or an explicit gap preventing submission.

Backlog and the OpenSpec process are two successive parts. Backlog clarifies the problem and
prepares the conclusion; this method requests the next part to handle it. The proposal stops
at the admission boundary — **规范语义的改动由人拍板** (root AGENTS.md invariant 1); the user
rules on whether the change proceeds to apply. Submitting the request does not mean a change
is approved, implemented or complete.

## 1. Prepare the materials

Use the [backlog closure criteria](../README.md) (four-way table). State the applicable
conclusion:

- **Do it:** the observable problem, intended result, scope and exclusions, chosen approach,
  actual alternatives and their costs, and executable acceptance criteria. If completion
  cannot be judged, return to [acceptance design](validation-design.md).
- **Do it later:** why it is deferred, the condition for reconsidering it, and where that
  condition can be observed. A qualifying condition may add one row to
  [triggers.md](../triggers.md) under its admit bar. Leave future design unresolved when it is
  unnecessary for this decision.
- **Do not do it:** why, and the scope in which that reason applies.
- **An existing conclusion already answers it:** link the existing decision (settled card,
  spec, trigger row) and explain which question it settles. If no further processing is
  needed, the card can close under the backlog rules without a downstream request.

Separate confirmed facts from recommendations. A human choice that is still pending keeps the
dependent conclusion open (`状态: 等人拍板`); record the exact question and next step.

## 2. Submit a processing request

Run the downstream entry (`openspec-propose` skill / `openspec new change`) and produce the
planning artifacts; the proposal's Change Focus and adjacent contracts must cite this card.
The artifacts stop at the admission boundary and wait for the user — do not start
implementation in the same move.

Record on the card: the change name, the submission date, and what handling was requested
(the `## 落地关联` section owns this). Update the card's status line: the graduation ticket is
punched only per the charter's residency rules — `毕业门: 已过 → <change>` together with the
card leaving the active zone, never as an unfulfilled declaration. This makes the handoff
reconstructable without relying on the conversation alone.

Backlog does not open a change as proof of submission, decide whether one is needed beyond the
user's ruling, or prescribe downstream format and lifecycle. Merely drafting the request on
the card is preparation, not submission. If delivery could not happen, report the gap and do
not claim it was submitted.

**Done:** the request has been submitted to the downstream entry and its destination is
recorded. Waiting for downstream processing is separate from an unresolved backlog question.
Submission itself grants no implementation authority.

## 3. Close the issue when its conditions are met

Apply the [backlog closure rules](../README.md): this repo's timing — the card closes when its
conclusions have been absorbed or landed by the change (the CLS ledger then records the real
destination), not upon submission. Preserve the discussion, add the conclusion and destination,
move the card into `_archived/_settled_issues/` per the three-README ritual, repair relative
links, and update the active and settled lists.

**Finish:** another reader can tell what backlog concluded, why, where downstream handling was
requested, and whether the card is closed or exactly what still prevents closure. The
OpenSpec process owns all subsequent decisions about the change and delivery.
