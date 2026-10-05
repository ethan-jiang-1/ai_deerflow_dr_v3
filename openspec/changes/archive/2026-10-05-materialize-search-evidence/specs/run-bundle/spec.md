# Spec Delta

## ADDED Requirements

### Requirement: Search and fetch results are materialized readably

Every `web_search` and `web_fetch` tool result observed by the run engine SHALL be
materialized as a readable JSON file under `diagnostics/searches/` — named by
generation, per-run sequence, and tool name, and carrying the tool arguments
(the query or URL), the full result content, and a recording timestamp. Files
SHALL be deduplicated by tool-call id across the chunk and values-snapshot event
sources; a tool result without a paired observed call SHALL not be materialized.
This materialization SHALL NOT place anything into `evidence/`: the admission
contract is untouched, and these files are process diagnostics — the readable
projection of data the checkpoint already holds, not accepted evidence. A bundle
whose runs predate the materializer MAY legally lack the directory.

#### Scenario: A scripted search turn materializes its result

- **WHEN** a run's scripted model emits a `web_search` tool call with a query and
  the tool result flows back through the real agent loop
- **THEN** `diagnostics/searches/` contains a JSON file carrying the query in its
  arguments and the full result content, named with the generation and tool name

#### Scenario: Duplicate event sources do not double-write

- **WHEN** the same tool result is observed both as a message chunk and inside a
  values snapshot
- **THEN** exactly one file is materialized for that tool-call id

#### Scenario: Non-search tools are not materialized

- **WHEN** a run uses a tool whose name is not `web_search` or `web_fetch`
- **THEN** no search-log file is written for it
