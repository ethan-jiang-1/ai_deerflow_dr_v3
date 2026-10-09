---
name: validation-evidence
description: Pick the minimal evidence lane that can actually check a stated acceptance criterion, using this repo's lane table and evidence owners.
whenToUse: Acceptance criteria exist and the question is which existing command or asset can check them. Not for inventing new harnesses.
---

# Choose evidence

**Input:** an acceptance criterion (from a card's `## 验收标准` or a change's Evidence seam)
and its seam class.
**Output:** the chosen lane, the exact command or asset, and an honest statement of what it
proves and does not prove.

This method owns no evidence of its own; the owners are
[testing-and-evaluation](../../deep_research_harness/docs/testing-and-evaluation.md)（车道
表 + 各 lane 的"不证明什么"列）and
[test-evidence-policy](../../openspec/governance/test-evidence-policy.md). Rules:

1. **Start at the cheapest lane that can fail.** Offline unit/contract mirror → assembly
   smoke → real-ladder observation (explicit opt-in) → cold-start release. One lane passing
   does not certify the next.
2. **Match the lane to the seam class.** deterministic-guardrail → unit/contract tests at the
   owning seam; cognitive-program → bounded eval or real-ladder observation, with its limits
   stated; wiring → composition/smoke evidence; human-decision → a named human verdict, never
   a synthetic proxy.
3. **Exit codes are read directly.** Pipes swallow real results — run the command, check the
   exit code, record it as the runner (回执纪律：命令/退出码/revision，新于最后一次改动).
4. **New guards must be able to go red.** If the check is new, seed a negative fixture and see
   it fail before counting it as evidence.
5. **What this machine cannot verify is labeled UNVERIFIED** — say so instead of borrowing
   plausibility.

**Finish:** the criterion has a lane, a command, and a recorded "proves / does not prove"
statement. If no existing lane can check it, that is a real gap — record it rather than
pretending a nearby green check covers it.
