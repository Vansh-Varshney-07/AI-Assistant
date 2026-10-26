# Revised flows

All diagrams are proposed integration paths. A passed offline model does not qualify an installed adapter. Contract references resolve in [CONTRACTS.md](CONTRACTS.md).

## Runtime and request admission

```mermaid
flowchart TD
    A[Open Wayfinder] --> B[Stable data-root identity]
    B --> C{Existing owner?}
    C -->|Yes| D[Authenticated compatible attach]
    C -->|No| E[Existing lock plus owned secure bootstrap]
    D --> F{Identity / API / schema / health valid?}
    E --> F
    F -->|No| G[Recovery view: no replacement database or bypass]
    F -->|Yes| H[Trusted host persists request ID and admission namespace]
    H --> I[Service validates identity / scope / policy / limits]
    I --> J[Atomic input plus run commit]
    J --> K[Durable dispatch reservation]
    K --> L[Bounded tool-closed Hermes call]
    L --> M[Scoped sequenced events and canonical terminal commit]
    M --> N[Snapshot or subscribe in any permitted view]
    N -->|Reconnect| N
```

## Cancellation and uncertainty are separate

```mermaid
stateDiagram-v2
    [*] --> queued: accepted
    queued --> reserved: budget and authority
    queued --> cancelled: service accepts stop
    reserved --> running: local dispatch admitted
    reserved --> interrupted: restart or unknown dispatch
    running --> stop_requested: user stop or deadline
    running --> completed: final committed first
    running --> failed: known failure
    running --> interrupted: crash / lost observation
    stop_requested --> cancelled: service fences delivery
    stop_requested --> completed: completion won prior race
    cancelled --> [*]
    completed --> [*]
    failed --> [*]
    interrupted --> [*]
```

Cancellation fences delivery/admission; it does not prove an upstream abort or absence of external effects. The latter has a distinct machine:

```mermaid
flowchart LR
    P[Exact proposal] --> R[Trusted compare-and-set review]
    R --> V[Final account / version / scope / expiry validation]
    V --> D[Durable reservation and one local dispatch]
    D --> A[Acknowledged]
    D --> U[Uncertain]
    A --> Q[Authorized read-only verification]
    U --> Q
    Q -->|Attributed independent evidence| OK[Verified]
    Q -->|Missing access or weak evidence| U
    U --> X[No ordinary retry; duplicate-risk lock remains]
```

## Forget without derived-context resurrection

```mermaid
flowchart TD
    A[Explicit scoped forget] --> B[Durable privacy barrier and context epoch]
    B --> C[Withhold stale pending results and proposals]
    B --> D[Old affected chats view-only for inference]
    B --> E[Existing memory APIs purge active sources and projections]
    E --> F{All declared copies verified?}
    F -->|No| G[Pending purge; affected memory unavailable]
    F -->|Yes| H[Receipt with exact deletion scope and backup limits]
    H --> I[New chat, fresh permitted evidence only]
    J[Old backup] --> K[Isolated restore plus latest deletion ledger]
    K -->|Ledger missing| L[Refuse activation / quarantine]
    K -->|Verified and applied| I
```

## Workflow and daily schedule

```mermaid
flowchart TD
    T[Versioned linear read template] --> M[Manual run authorization]
    T --> S[Reviewed daily fixed-zone standing authorization]
    S --> H[Qualified Hermes scheduler adapter]
    H --> O{Fresh revision / intended UTC occurrence / active app epoch?}
    O -->|No| SK[Blocked or skipped record]
    O -->|Yes| AD[Unique occurrence admission]
    M --> G[Fresh narrow run and step grants]
    AD --> G
    G --> C[Calendar read]
    C --> K[Tasks read]
    K --> F{Typed / permitted / current / within budget?}
    F -->|No| P[Partial or blocked; no synthesis fallback]
    F -->|Yes| B[Scoped model brief]
    B --> R[Canonical result and source observation times]
    R --> UI[Main / quick view observe same run]
```

The adapter reuses the installed scheduler; this diagram does not introduce a second clock loop. Core workflows cannot contain writes. Same-day schedule edits default effective next local day; sleep/missed times skip without a burst.

## Cumulative delivery

```mermaid
flowchart LR
    G[Compatibility and contract spike] --> R1[1 Real chat]
    R1 --> R2[2 Memory and documents]
    R2 --> R3[3 Provider reads and local tasks]
    R3 --> R4[4 Linear read workflows]
    R4 --> R5[5 Daily schedule and quick access]
    R5 --> R6[6 Skills and roles]
    R6 --> R7[7 Repository review]
    R7 -. separate qualification .-> OPT[Optional exact effects / selected images / native]
```

Every arrow requires prior applicable acceptance plus shared-boundary regression. Deferred research/notes/fitness are not implied by any box.
