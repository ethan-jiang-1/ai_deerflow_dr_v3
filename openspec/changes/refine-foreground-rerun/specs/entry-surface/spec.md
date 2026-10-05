# Spec Delta

## MODIFIED Requirements

### Requirement: Six verbs mirror the state machine and observation layers

The CLI SHALL expose exactly `create`, `status`, `watch`, `cancel`, `refine`, and
`inspect`; each SHALL delegate to the owning runtime action and SHALL add no second
state authority. `create` SHALL start a bundle (configuration selected explicitly,
`fixture` by default) and drive the run engine in the foreground with the live human
view; `status` SHALL report state, journal summary, and owner-PID liveness; `watch`
SHALL render the journal projection until the run reaches a terminal state, then exit;
`cancel` SHALL record the cancellation request; `refine` SHALL require non-empty
direction text, enter the next generation, and then drive the run engine in the
foreground over that generation's direction document — continuing the bundle's
declared composition ladder (no fresh ladder choice; an unwired composition SHALL
fail loudly naming it) — ending at a typed terminal state with the same terminal
output and environment-remedy behavior as `create`; `inspect` SHALL render the journal
timeline, the admitted evidence, the assembly snapshot, and the checkpoint thread
summary when the framework is available. Any other command SHALL be rejected loudly
naming the legal set.

#### Scenario: Every verb delegates and unknown verbs fail

- **WHEN** each of the six verbs runs against a fixture bundle, and an unknown verb is
  requested
- **THEN** each verb produces the substrate's declared behavior, and the unknown verb
  fails naming the legal command set

#### Scenario: Refined generation runs to an honest terminal

- **WHEN** `refine` runs on a terminal fixture bundle with direction text
- **THEN** the next generation is created, the run engine is driven in the foreground
  over the direction document, and the command exits after printing a typed terminal
  state for that generation
