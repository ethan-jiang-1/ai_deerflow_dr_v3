---
name: validation-design
description: Turn confirmed requirements into observable acceptance criteria before implementation, using this repo's evidence lanes and human judgment boundaries.
whenToUse: Confirmed requirements need executable acceptance criteria before an approach is finalized and handed off. Deferral, rejection and links to existing conclusions need no implementation matrix.
---

# Design acceptance before implementation

**Input:** a scoped issue card with confirmed behavior, constraints, alternatives, failure or
recovery paths, and explicit Out of Scope. Before proceeding, read
[requirements-elicitation](requirements-elicitation.md)'s user-confirmation rules.

The purpose is to make the plan **clear to build and possible to accept**. Do not invent
acceptance criteria for an uncertain product choice: expose the uncertainty and ask the human.
Technical evidence selection can be agent-led when the behavior is already confirmed.

## 1. Partition the behavior

Classify every behavior that matters to the user with this repo's seam vocabulary (root
change-guidance, Change Focus): **deterministic-guardrail** (parsing, state, business rules,
gates — repeatable code behavior), **cognitive-program** (extraction, generation, judgment,
dialogue — model-dependent output), **wiring** (harness slots, registration, data flow,
assembly), or **human-decision** (taste, business value, risk). Do not use one end-to-end demo
as proof for all classes. A plan may have no cognitive surface; do not create an eval just
because this is an agent product.

## 2. Write acceptance criteria on the card

Keep criteria in `## 验收标准` on the same issue. For a small scope a short list is enough; when
behaviors need separate checks, use one table row per load-bearing behavior. `## 关闭条件`
refers to the criteria without repeating them. Each criterion names:

| Field | What to record |
|---|---|
| Behavior | User-observable result and the requirement it traces to |
| Seam class | deterministic-guardrail / cognitive-program / wiring / human-decision |
| Input/state | Preconditions, representative input and relevant complementary state |
| Pass/fail signal | Observable assertion, expected value source, and the failure signal |
| Negative/recovery | Failure, refusal, uncertainty, or recovery path; test the complement of conditional claims |
| Evidence owner | Existing repo owner, command or artifact path, and what it can/cannot prove |
| Human judgment | Only where taste, business value, risk, compliance or authority cannot be mechanically decided |

Use the repo's evidence lanes to choose the owner and command:
[testing-and-evaluation](../../../deep_research_harness/docs/testing-and-evaluation.md) (车道表
与各 lane 的"不证明什么"列) and
[test-evidence-policy](../../../openspec/governance/test-evidence-policy.md). Preserve source
links, versions, artifact commits and attribution for load-bearing evidence. A command
finishing, a keyword being present, one happy-path example, or a passing demo is not by itself
a pass condition.

## 3. Keep the criteria executable and honest

- Deterministic behavior normally becomes a behavioral test at an existing seam. Borrow TDD's
  red-before-green and independent expected values (`tdd` skill); use this repo's established
  interface owners rather than turning every technical seam into a new human approval.
- Cognitive surfaces need a bounded eval case and, for load-bearing claims, a real-model
  observation (真实梯，显式 opt-in). Automatic eval is regression evidence, not a substitute for
  a human judgment about tone, taste, business value or risk.
- Wiring needs the existing composition or smoke evidence; do not prebuild a new harness here.
- For conditional claims, include both the triggering and complementary state. If proposing a
  new guard, prove its negative fixture before counting the guard as evidence (新守卫必须能变红).

**Done:** every load-bearing requirement has a seam class, observable pass/fail signal,
negative or complementary case, evidence owner, and an explicitly named human judgment or an
explicit "none". These criteria describe how downstream work will be judged; designing them
does not require the work to have been implemented. Hand them off via
[issue-to-change](issue-to-change.md).
