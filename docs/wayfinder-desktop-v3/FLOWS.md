# Draft flows

Planning diagrams. All new desktop releases, adapters and interfaces shown here are proposals, not current release evidence. [Return to the plan](PLAN.md).

## Presentation architecture

```mermaid
flowchart TD
    UI[React conversation and management views]
    IPC[Typed preload bridge]
    MAIN[Electron main broker]
    API[Existing authenticated Python service]
    CHAT[Guarded chat and run facade]
    H[Installed Hermes runtime]
    MEM[Iron Web context gateway]
    DB[(Existing graph and vector memory)]
    STATE[(SQLite application state)]
    GATE[Policy and exact approval gate]
    EXT[Scoped file and account adapters]
    UI --> IPC --> MAIN --> API
    API --> CHAT --> H
    API --> MEM --> DB
    API --> STATE
    API --> GATE --> EXT
    EXT -->|Evidence and receipts| API
    H -->|Validated output and events| API
    API -->|Scoped snapshots and events| MAIN
    MAIN -->|Sanitized view data| UI
    S[Existing OpenShell managed boundary] -. restricts .-> H
```

The renderer never receives database access, a bearer token, a generic shell API or a generic authenticated HTTP proxy. Keep existing Origin rejection. An SDK-based Hermes Desktop host must demonstrate equivalent control before adoption.

## R1: first user conversation

```mermaid
flowchart LR
    A[Launch installed app] --> B{Runtime available?}
    B -->|No| C[Explain unavailable component and recovery]
    B -->|Yes| D[Open or create conversation]
    D --> E[Type and submit]
    E --> F[Bind one request and run ID]
    F --> G[Run actual Hermes inference]
    G --> H{Actual outcome}
    H -->|Complete| I[Persist and show answer]
    H -->|Cancelled| J[Show stopped or stopping state]
    H -->|Failed| K[Show failure and safe next step]
    I --> L[Reopen same conversation after restart]
```

If cancellation cannot yet stop the upstream inference, show that distinction and suppress publication of a supposedly active answer. A renderer reconnect observes the same run rather than resubmitting it.

## R2 onward: evidence and exact change review

```mermaid
flowchart TD
    Q[User request] --> SC[Bind authenticated scope]
    SC --> CTX[Retrieve permitted memory and selected evidence]
    CTX --> P[Reason or prepare a bounded plan]
    P --> W{Protected change?}
    W -->|No| V[Validate sources and present answer]
    W -->|Yes| PRE[Show exact target payload and expiry]
    PRE --> D{User decision}
    D -->|Reject| NO[Record rejected - no effect]
    D -->|Revise| PRE
    D -->|Approve once| CHECK[Revalidate digest scope and preconditions]
    CHECK --> EX[Execute supported operation]
    EX --> O{Independently verified?}
    O -->|Yes| DONE[Show receipt and applied change]
    O -->|Uncertain| UNKNOWN[Result needs checking]
    UNKNOWN --> REC[Read-only reconciliation]
    REC -->|Verified| DONE
    REC -->|Unconfirmed| UNKNOWN
```

Revising produces a fresh proposal/digest and invalidates the old approval. Reconciliation does not silently retry a write. Model output cannot take the approval branch.

## R4/R5: workflow and recurring occurrence

```mermaid
flowchart LR
    A[Choose template or draft steps] --> B[Validate bindings inputs dependencies budgets]
    B --> C[Review and save version]
    C --> D{Run mode}
    D -->|Manual| R[Create scoped run]
    D -->|Recurring| S[Review timezone resources standing grant and missed-run policy]
    S --> H[Existing Hermes scheduling adapter]
    H --> OCC[Durable occurrence identity]
    OCC --> CHECK[Check version grant and prior outcome]
    CHECK --> R
    R --> EXEC[Existing execution and qualified delegation]
    EXEC --> V[Validate each step and evidence]
    V --> END[Show result partial failure or uncertainty]
    PAUSE[Pause schedule] -. prevents future dispatch .-> H
```

Pausing future occurrences does not undo a dispatched effect. An edited template does not inherit the old scheduled authorization. Sleeping/offline behaviour is defined per schedule; UI timers do not own recurring execution.

## Release evolution

```mermaid
flowchart LR
    R1[R1 Real chat] --> R2[R2 Memory and files]
    R2 --> R3[R3 Google and tasks]
    R3 --> R4[R4 Workflows]
    R4 --> R5[R5 Scheduler and quick access]
    R5 --> R6[R6 Skills and agent controls]
    R6 --> R7[R7 Reviewed advanced actions]
```

Every arrow means: add complete functionality, refine observed friction, migrate data safely and rerun earlier acceptance cases.
