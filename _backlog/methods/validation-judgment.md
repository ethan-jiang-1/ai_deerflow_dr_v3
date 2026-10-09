---
name: validation-judgment
description: Judge a claimed completion against its acceptance criteria, item by item, recording pass, fail, evidence-insufficient or awaiting-human — without weakening criteria to match reality.
whenToUse: Work was claimed done and needs acceptance judgment against previously written criteria. Not for writing new criteria.
---

# Judge acceptance results

**Input:** the acceptance criteria and the claimed delivery (change tasks, receipts, test
   runs).
**Output:** a per-item verdict that lands in the record owning the work — the change's
Delivery Record / closeout evidence, or the issue card when no change is involved.

1. **Judge per item, not per vibe.** For each criterion: **pass** (evidence cited), **fail**
   (the gap named), **evidence-insufficient** (what check is missing), or **awaiting-human**
   (the named judgment only a human can make). A delivered implementation with an unmet
   criterion is a fail, not a partial pass.
2. **Do not move the goalposts.** If the implementation cannot meet the standard, record the
   actual difference; changing the criterion to match the implementation is forbidden (the
   proving discipline lives in the charter and test-evidence policy). If the criterion itself
   was wrong, that is a new decision — write it on the card and get the ruling.
3. **Check the red, not just the green.** A guard counts only if its negative control was seen
   red; a receipt counts only if it is newer than the last change to what it covers.
4. **Load skills only when a step needs them:** `code-review` for standards/spec review,
   `diagnosing-bugs` for failure diagnosis. Their outputs feed the verdicts; they do not
   replace the criteria.

**Finish:** every criterion has one of the four verdicts with its evidence pointer, and the
owning record carries the result. Awaiting-human items state exactly who must decide what.
