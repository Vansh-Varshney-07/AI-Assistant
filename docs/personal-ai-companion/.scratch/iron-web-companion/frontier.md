# Decision frontier

This view lists open decision tickets. The map indexes resolved research and standing user requirements; it does not duplicate open ticket bodies.

## Available now

- [Choose the orchestrator-only memory contract](issues/04-memory-contract.md)
- [Choose tool discovery and capability enforcement](issues/05-tool-routing.md)

## Waiting on prerequisites

- [Choose interactive approvals and recurring grants](issues/06-approvals-recurring.md)
- [Choose retention, deletion and outbound data controls](issues/07-data-control.md)
- [Choose the work-item model and sync ownership](issues/08-task-sync.md)
- [Choose the general fitness adapter contract](issues/09-fitness-sdk.md)
- [Choose the animal companion and remembering-chat interaction](issues/10-animal-chat-ux.md)
- [Choose reusable skill review and versioning](issues/11-skills-governance.md)
- [Choose the web research and interactive browser boundary](issues/12-web-vs-browser.md)
- [Choose GitHub capabilities and repository boundaries](issues/13-github-capabilities.md)
- [Confirm WhatsApp Business eligibility and local delivery path](issues/14-whatsapp-onboarding.md)
- [Choose the first complete workflow and build boundary](issues/15-first-slice.md)
- [Choose release evidence and failure-recovery gates](issues/16-release-gates.md)

## Dependency view

```mermaid
flowchart TD
    T1["Establish Hermes isolation and extension boundaries"]
    T2["Establish productivity connector feasibility"]
    T3["Establish fitness, web and desktop feasibility"]
    T4["Choose the orchestrator-only memory contract"]
    T5["Choose tool discovery and capability enforcement"]
    T6["Choose interactive approvals and recurring grants"]
    T7["Choose retention, deletion and outbound data controls"]
    T8["Choose the work-item model and sync ownership"]
    T9["Choose the general fitness adapter contract"]
    T10["Choose the animal companion and remembering-chat interaction"]
    T11["Choose reusable skill review and versioning"]
    T12["Choose the web research and interactive browser boundary"]
    T13["Choose GitHub capabilities and repository boundaries"]
    T14["Confirm WhatsApp Business eligibility and local delivery path"]
    T15["Choose the first complete workflow and build boundary"]
    T16["Choose release evidence and failure-recovery gates"]
    T1 --> T4
    T1 --> T5
    T4 --> T6
    T5 --> T6
    T4 --> T7
    T2 --> T8
    T6 --> T8
    T7 --> T8
    T3 --> T9
    T7 --> T9
    T4 --> T10
    T6 --> T10
    T7 --> T10
    T1 --> T11
    T5 --> T11
    T6 --> T11
    T3 --> T12
    T5 --> T12
    T6 --> T12
    T2 --> T13
    T5 --> T13
    T6 --> T13
    T7 --> T13
    T2 --> T14
    T5 --> T14
    T6 --> T14
    T7 --> T14
    T4 --> T15
    T5 --> T15
    T6 --> T15
    T7 --> T15
    T4 --> T16
    T5 --> T16
    T6 --> T16
    T7 --> T16
    T8 --> T16
    T9 --> T16
    T11 --> T16
    T12 --> T16
    T13 --> T16
    T15 --> T16
    style T1 fill:#e5f4e9,stroke:#378250
    style T2 fill:#e5f4e9,stroke:#378250
    style T3 fill:#e5f4e9,stroke:#378250
```

Metadata uses local tracker numbers for dependency mechanics; human references use ticket names. Claim one frontier ticket before work. No implementation is authorized by being on this list.
