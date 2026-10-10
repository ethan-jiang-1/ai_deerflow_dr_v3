# Deep Research Product

The Deep Research Product helps people obtain research outcomes. This glossary carries
the stable product vocabulary; runtime facts stay with their owning code and specs.

## Language

**Deep Research Product**:
The downstream product that turns a research question into a useful research outcome
with evidence, scope and assumptions, and material uncertainty visible to the person
receiving it.
_Avoid_: the DeerFlow platform, the host agent itself

**Run Bundle**:
The independently deletable durable record of one research run — its state, evidence,
content, and event journal. Deleting a Bundle never makes the Harness stop working and
never recreates the run.
_Avoid_: a cache entry, a log directory, harness-internal state

**Harness**:
The stable execution and control environment that creates, drives, and disposes of
runs. It owns no durable run state and holds no registry that can authorize or recover
a run.
_Avoid_: the research agent, the model, the pipeline

**Gate**:
Two senses, kept distinct by context: the admission gate machine (`engine/gate.py`,
renders pass/blocked for a run) and a quality gate (a lane that must exit zero, e.g.
`make verify`). Writing prefers "admission gate" for the machine.
_Avoid_: using the bare word for both in one sentence

**Entry Surface**:
A user-facing or host-facing surface through which a run starts or is observed —
the closed CLI verb set plus the make lanes (owner: `entry-surface` capability).
_Avoid_: an internal module boundary

> 词汇的权威随 owning spec 落地；本文件只登记承重词，避免第二权威。
