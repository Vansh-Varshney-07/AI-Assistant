# Open decision frontier

## Available now

- [Choose the main-app and quick-window state contract](issues/01-app-quick-state.md)
- [Choose Iron Web authority and memory-release invariants](issues/02-memory-authority.md)
- [Choose the plugin configuration and capability contract](issues/03-plugins-capabilities.md)

## Waiting on prerequisites

- [Choose task approvals, egress and standing grants](issues/04-approval-egress.md)
- [Choose runtime profiles and worker enforcement](issues/05-runtime-workers.md)
- [Choose workflow editing, validation and recovery semantics](issues/06-workflow-contract.md)
- [Choose Tavily-first research and model routing policy](issues/07-tavily-model-routing.md)
- [Choose skill governance and workflow-template reuse](issues/08-skill-reuse.md)
- [Choose background availability and scheduled-run ownership](issues/09-background-lifecycle.md)
- [Choose starter daily-life operations and expansion gates](issues/10-starter-adapters.md)
- [Choose measurable memory and integrated MVP release gates](issues/11-release-evidence.md)

## Dependencies

```mermaid
flowchart TD
    T1["Choose the main-app and quick-window state contract"]
    T2["Choose Iron Web authority and memory-release invariants"]
    T3["Choose the plugin configuration and capability contract"]
    T4["Choose task approvals, egress and standing grants"]
    T5["Choose runtime profiles and worker enforcement"]
    T6["Choose workflow editing, validation and recovery semantics"]
    T7["Choose Tavily-first research and model routing policy"]
    T8["Choose skill governance and workflow-template reuse"]
    T9["Choose background availability and scheduled-run ownership"]
    T10["Choose starter daily-life operations and expansion gates"]
    T11["Choose measurable memory and integrated MVP release gates"]
    T1 --> T4
    T2 --> T4
    T3 --> T4
    T2 --> T5
    T3 --> T5
    T4 --> T5
    T2 --> T6
    T3 --> T6
    T4 --> T6
    T2 --> T7
    T3 --> T7
    T4 --> T7
    T3 --> T8
    T4 --> T8
    T6 --> T8
    T1 --> T9
    T4 --> T9
    T6 --> T9
    T3 --> T10
    T4 --> T10
    T5 --> T10
    T6 --> T10
    T1 --> T11
    T2 --> T11
    T3 --> T11
    T4 --> T11
    T5 --> T11
    T6 --> T11
    T7 --> T11
    T8 --> T11
    T9 --> T11
    T10 --> T11
```

Claim one available ticket before work. Human-facing references use ticket names; tracker numbers are only dependency mechanics. All design tickets remain open.
