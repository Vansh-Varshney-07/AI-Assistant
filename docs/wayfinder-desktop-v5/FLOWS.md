# Proposed interaction and authority flows

These are static planning diagrams. They do not run agents, authorize resources or assert implemented endpoints. See C01–C23 and U01–U12 for failure details.

## Source assembly and app ownership

```mermaid
flowchart TD
  A[Freeze GitHub commit and reviewed local file hashes] --> B[Merge source allowlist in isolated branch]
  B --> C[Validate package, contracts and prior regressions]
  C --> D[Start local bundled renderer]
  D --> E[Main verifies selected stable data root and compatibility]
  E --> F{Owned instance or securely paired service?}
  F -->|Yes| G[Verify descriptor, generation and component health]
  F -->|No| H[Recovery screen; no alternate empty store]
  G --> I[Service inclusion and resource authority checks]
  I --> J[Enable only qualified named intents]
```

The original checkout is never reset/copied live. A failed attach is not permission to steal a lock or trust a listening port. A source import does not migrate a runtime.

## Ordinary chat, not automatic memory

```mermaid
flowchart TD
  A[User composes in Home or Chat] --> B[Main persists pending command identity]
  B --> C[Service validates namespace, scope, profile and budget]
  C --> D[Atomically accept input and run identity]
  D --> E[Durably reserve dispatch]
  E --> F[Existing isolated Hermes invocation]
  F --> G{Stop, completion or failure wins service race}
  G -->|Completion| H[Commit final transcript and terminal snapshot]
  G -->|Stop| I[Fence late publication; retain honest cost uncertainty]
  G -->|Crash or failure| J[Interrupted or failed; observe original attempt]
  H --> K[Route by immutable space and conversation IDs]
  J --> L[Explicit new bounded read attempt if eligible]
```

Remember is a separate reviewed operation. A connection retry observes the original request; it does not submit a new ID. No W35/echo/fixture fallback exists for ordinary chat.

## Exact memory or optional connector review

```mermaid
flowchart TD
  A[User form or worker proposal] --> B[Service validates exact scoped plan]
  B --> C[Persist digest, versions, expiry and preconditions]
  C --> D[Renderer shows preview and requests review]
  D --> E[Main reloads service record and opens trusted bounded confirmation]
  E -->|Reject or cancel| F[No new effect admission]
  E -->|Approve| G[Final service rechecks authority, monotonic lifetime and uncertainty lock]
  G -->|Changed, revoked or expired| H[Refuse; review new proposal]
  G -->|Valid| I[Durable admission and exact provider operation]
  I --> J[Independent receipt and attribution inspection]
  J -->|Verified| K[Verified historical outcome]
  J -->|Unconfirmed| L[Unknown outcome and stable family lock]
  L --> M[Fresh read-only reconciliation of original effect]
  M -->|Attributed| K
  M -->|Unresolved| L
```

A new title, request ID, UI window or connection generation cannot bypass the family lock. The upstream in-memory token alone is never the final application approval.

## Selected evidence and forget barrier

```mermaid
flowchart TD
  A[Trusted picker and disclosure decision] --> B[Current file identity, grant, hash and bounds]
  B --> C[Existing scoped extraction and bounded evidence]
  C --> D[Permitted model/context use]
  D --> E[Revalidate freshness and epoch before delivery]
  F[User requests Forget] --> G[Persist privacy barrier and bump context epoch]
  G --> H[Block dependent pending results and old conversation inference]
  H --> I[Purge declared active copies through existing APIs]
  I -->|All acknowledged| J[Verified local purge receipt and fresh conversation]
  I -->|Partial or failed| K[Privacy-blocked scope and pending cleanup]
  G --> L[Keep minimal deletion ledger for backup lifetime]
  M[Restore older backup in isolated root] --> N{Latest ledger verified and applied?}
  N -->|Yes| O[Explicit compatible activation]
  N -->|No| P[Quarantine; no normal recall]
```

Retraction, chat deletion and artifact clearing remain separate. Old history, provider disclosure and independent backups are not silently declared erased.

## Google reads and independent local tasks

```mermaid
flowchart TD
  A[Human account consent when app flow is ready] --> B[Verify stable account, scopes and connection generation]
  B --> C[Review exact read resource and disclosure policy]
  C --> D[Issue fresh scoped grant]
  D --> E[Fixed bounded provider read]
  E --> F{Account, grant and generation still valid?}
  F -->|No| G[Withhold late result; show account recovery]
  F -->|Yes| H[Preserve raw state, versions, dates, coverage and observed time]
  H --> I[Read-only provider projection]
  I --> J[Explicit one-time Copy to local draft]
  J --> K[Versioned local WorkItem in app storage]
  K --> L[Local edits affect only the local item]
```

An empty/partial/error response does not become a complete day. Copy is not sync, and consent is not an external-write approval.

## Linear workflow and standing daily read

```mermaid
flowchart TD
  A[Review pinned linear template and resource intentions] --> B{Manual run or qualified occurrence?}
  B -->|Manual| C[One-run scoped authority]
  B -->|Occurrence| D[Existing Hermes authenticated callback]
  D --> E[Check fixed-zone instant, revision, epoch, lateness and no overlap]
  E -->|Invalid or missed| F[Record skip or denial; no catch-up]
  E -->|Valid| G[Unique durable occurrence admission under standing authority]
  C --> H[Reserve root work, model and time budgets]
  G --> H
  H --> I[Fresh short-lived source grants]
  I --> J[Selected existing read step]
  J --> K{Required typed evidence current and permitted?}
  K -->|No| L[Partial or blocked run; synthesis withheld]
  K -->|Yes| M[Next declared step or bounded synthesis]
  M --> N[Persist timeline, provenance and terminal state]
  O[Quit or revoke] --> P[Persist app admission-stop fence]
  P --> Q[No new children or callbacks; cancel owned queued work]
```

The adapter does not create another cron executor. Main and quick chat share one runtime and request/draft authority; neither can extend a workflow budget.
