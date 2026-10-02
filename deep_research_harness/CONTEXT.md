# Deep Research Product

The Deep Research Product helps people obtain research outcomes. (v3 skeleton — this
glossary carries the stable product vocabulary; runtime facts are not defined here and
do not exist yet.)

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

**Entry Interface**:
A user-facing or host-facing surface through which a run starts or is observed.
(v3 surfaces are pending; the vocabulary side and the operational side must stay
name-mapped in the same change that defines either.)
_Avoid_: an internal module boundary

> 词汇的权威随 owning spec 落地；本文件在骨架期只登记承重词，避免第二权威。
