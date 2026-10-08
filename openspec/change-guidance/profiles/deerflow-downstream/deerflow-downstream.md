# DeerFlow Downstream Profile

> authority: guidance only; public upstream contracts and local owners define behavior
> trigger: changing a DeerFlow public-interface dependency, gitlink, or compatibility boundary

Enable only for a downstream product that leverages DeerFlow public APIs. Name the
public interface and compatibility question. Ordinary downstream work neither
modifies nor source-browses upstream. Gitlink metadata proves revision/worktree scope
only; it does not prove runtime compatibility or approve a pointer change.

## Pinning Discipline

Every behavioral claim about upstream must carry a pinned citation (release tag or
commit) and the method it was verified with; prose equations between the gitlink
and an upstream release are forbidden — state the ancestry relation and verify it
(`git merge-base --is-ancestor`) instead. Upstream documentation is a snapshot of
its release by default: when a claim rests on docs, verify against source at the
pinned revision before relying on it (the application corpus records concrete
divergences). When the gitlink advances (re-pin), re-review every standing upstream
claim against the new revision — the retained corpus under
`_backlog/_reference/deerflow-application-corpus/` keeps the re-review triggers
for its own conclusions.
