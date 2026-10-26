# Desktop plan stress review

26 October 2026 · Verdict: **REVISE the implementation contracts; retain the product direction and cumulative release ladder.**

The Electron/React presentation direction and small-first-release approach remain reasonable. The plan is not yet a complete engineering specification. Two R1 architecture contracts need resolution, and later releases have concrete integration and acceptance gaps. This review did not implement the app, modify its backend, alter the original plan/preview, connect accounts, launch UI, inspect a screen/clipboard, start a scheduler, or touch live memory.

## Results at a glance

| Evidence | Actual result | What it establishes |
|---|---|---|
| Actual preview inline JavaScript, executed with a minimal fake DOM | **366 reachable states; 7,620 transitions. BFS and DFS agree.** | Finite navigation/tab/release state exploration. Not browser rendering or native interaction. |
| Preview targeted checks | **4 pass; 7 fail** | Executed phase/IME checks plus source-backed CSS/control observations. Not a real-browser accessibility pass. |
| Deliberately permissive abstract action model | 1,376 states; 5,632 transitions; all four tested safety properties have counterexamples | The model checker detects intentionally missing authorization, verification and replay guards. This is not the existing backend. |
| Proposed guarded abstract action model | 240 states; 875 transitions; no checked invariant violation | The proposed guards satisfy those properties within the stated model assumptions. |
| Deliberately permissive / guarded chat models | 30 states/86 transitions and 10 states/22 transitions; three counterexamples in the former, none in the latter | Checks scoped delivery, terminal cancellation and duplicate final output in a finite abstraction. |
| Event-order permutations | **288 orderings against each variant**; permissive 116 violations, guarded zero | Abstract reorderings, not real concurrent threads or provider requests. |
| Existing Python `wire()` boundary function | **9 checks pass** | Nested values around 2^53 and INT64 boundaries retain the existing conversion behaviour. Future TypeScript contracts still need qualification. |
| Existing task-read projection, extracted method with fake session | `needsAction` remains unchanged; `etag` and `updated` are not retained | Concrete normalization/versioning integration gap before building a canonical local/provider work-item layer. No authentication, app or real HTTP request was involved. |
| Timezone arithmetic | Nonexistent spring time, ambiguous autumn time and date-only task shift reproduced | Boundary examples using installed IANA timezone data. No scheduled job was run. |
| Combinatorial design matrix | **3,840 designed scenarios; 24 selected scenarios cover all 239 two-factor pairs** | Test designs only. All rows remain **Not run**. Pairwise coverage does not establish higher-order fault coverage. |
| Manual source/design review | **36 findings: 2 P0, 18 P1, 16 P2; 72 proposed supplemental cases** | Specific contract, user-flow, integration and coverage amendments. These counts are not 36 observed production bugs. |

Do not add unlike rows as a single app test count. Raw evidence: [preview-results.json](preview-results.json), [model-results.json](model-results.json). Scripts are included and input source hashes are recorded.

## The two pre-R1 decisions

### F01: define the canonical chat session and authority

The plan promises genuine Hermes replies but leaves `chat_start`/events as illustrative names. It does not yet define which transcript is canonical, how it maps to Hermes sessions, or exactly which profile state/tools/memory the R1 chat inherits.

Failure path: create a new conversation in one space → attach to an existing Hermes profile/session → unrelated history, tools or implicit memory enter the reply. A good-looking new chat window does not prevent this.

**Closure:** specify the chat request/event/persistence contract, canonical transcript and session mapping, tool-closed R1 binding, provider/model policy, and explicit R2-only scoped memory flow. Choose the actual supported host only after its extension paths pass these boundaries. [R1 contract addendum](R1-CONTRACT-ADDENDUM.md).

### F02: define one authenticated runtime owner and its lifecycle

The existing code supplies a runtime lock and in-memory credentials; the future UI still needs an authenticated discovery/attach/start protocol. A port, stale PID or remembered filesystem path is insufficient.

Failure path: two app launches race → they start or attach to different data roots → conversations split. Alternatively, Quit shuts down a shared Hermes process that the app does not own.

**Closure:** stable app-data identity, instance/API/schema handshake, secure credential handoff, single-owner arbitration, lifecycle leases and owned-versus-shared shutdown. A second window is another view, not another embedded database owner. Do not silently adopt a new empty runtime to hide an unavailable one.

P0 here means a decision that blocks freezing the R1 implementation contract, not an emergency vulnerability in a shipped app.

## Reproducible preview defects

These are failures in the design preview itself. It is correctly labelled synthetic and does not call a backend, so they do not demonstrate unauthorized real actions.

| Finding | Reproduction | Observed result | Proposed correction |
|---|---|---|---|
| F27 | Select R1 and inspect Plan/Review; select R2 Chat | R1 still shows Google-plan/task-approval content; R2 uses a Google request before R3 | Gate examples, inspector content and action surfaces from the same manifest as navigation. |
| F28 | Inspect the layout below its 760px breakpoint | Sidebar is hidden; no drawer opener exists | Accessible open/close navigation with focus restore. Actual viewport tests still needed. |
| F29 | Toggle inspector at wide desktop width | JavaScript toggles a class used only by a narrow media rule; desktop inspector has no hide path | One real visibility state with wide-grid and narrow-sheet rules. |
| F30 | Enter while `isComposing=true` | Submit handler intercepts IME confirmation | Composition-aware keyboard handling. |
| F26 | Follow the composer focus CSS cascade | `outline:none!important` defeats its declared focus-visible outline | Clear visible focus or an equivalent focus-within treatment, then real keyboard/high-contrast verification. |

F27 accounts for three failed assertions; the other four account for one each. The preview checks also confirm that R1 navigation is correctly restricted, downgrading from an unavailable destination returns to Chat, preview send is inert, and the page declares no backend connections.

## DFS counterexamples and what must prevent them

These paths are generated by deliberately permissive comparison models. They demonstrate why the specified guard is necessary; they are not claims that today's `ActionGate` accepts these paths. Existing exact-action checks and non-replay behaviour should be reused.

```text
Selected account changes -> approve original account-A proposal -> dispatch
  Required: immutable target/account binding and final authorization check.

Approve -> dispatch -> provider applies -> receive acknowledgement
  Required: independent verification before declaring the effect verified.

Approve -> dispatch -> acknowledgement lost -> ordinary retry -> dispatch
  Required: unknown result stays non-replayable; reconcile instead.

Submit -> cancellation confirmed -> late completion arrives
  Required: terminal state and event-sequence fencing.

Submit -> final arrives -> duplicate final arrives
  Required: one final publication per attempt and canonical event identity.

Visible space changes -> space-A request/result -> active-view append
  Required: route by the original run/conversation/space, not current selection.
```

The action model bounds one reviewed action, two selectable accounts, at most two dispatches and two effects. It assumes each provider dispatch applies at most one effect and treats independent verification as an authorized oracle. It does **not** prove provider-side exactly-once behaviour, SDK retry safety, resource identity, reconciliation-grant enforcement, persistence atomicity, OS isolation, fairness or eventual completion. Those have separate implementation tests. Expiry is modelled as monotone; real wall-clock rollback needs an additional admission/expiry rule.

## Important integration gaps

### Earlier than the release outline makes obvious

- **Schema evolution starts with R1**, not R7. Older app writers must refuse unsupported newer data; migration interruption and rollback need a contract before the first schema changes.
- **R1 event transport is new work.** The existing bridge returns a final marked response; the existing API client has a finite request timeout. Long model work needs asynchronous accepted-run observation, not one long blocking frontend request or fake token replay.
- **Rich output is a trust boundary from R1.** Sanitized Markdown is mentioned, but active HTML, tracking images, source resolution, model-supplied deep links and IPC sender checks need explicit negative cases. [Electron's security guidance](https://www.electronjs.org/docs/latest/tutorial/security) supports these boundary checks.
- **A local file grant is not automatically remote-disclosure permission.** Model/provider selection and sensitive attachment disclosure must follow a defined policy.
- **Memory correctness needs real retrieval evaluation.** Existing deterministic fixtures and isolated storage checks do not establish neural retrieval quality or protection against stale transcript reuse. The inherited memory-quality contract remains relevant.

### Google and task details

- The task read adapter projects to `TaskItem`; that presentation representation is not yet a provider-write/version/conflict contract. A synthetic call through the actual extracted method shows `needsAction` is passed through, although the generic model comments describe pending/completed; provider `etag`/`updated` are omitted. Raw status is not intrinsically invalid, but consumers must not assume canonical pending semantics. Preserve or explicitly resolve provider versions before writes/sync. Local completion, remote completion, deletion and refresh have to agree.
- Google Tasks records the **date** component of `due`; the time portion is discarded. A timed reminder cannot be promised by passing a timestamp through that field. Generic timestamp conversion can also shift the displayed date west of UTC. [Google Tasks resource reference](https://developers.google.com/tasks/reference/rest/v1/tasks).
- Google OAuth refresh tokens for applicable external apps in **Testing** can expire after seven days, and tokens can be revoked for other reasons. Re-consent and account switching are normal lifecycle paths, not exceptional afterthoughts. [Google OAuth token-expiration reference](https://developers.google.com/identity/protocols/oauth2#expiration).
- Disabling a connector, disconnecting an account, removing local credentials and revoking provider consent need distinguishable meanings. Pending proposals and in-flight delivery must not silently move to a newly selected account.

### Workflows and scheduler

- Present context tickets last about two minutes and Google read grants about five minutes in memory. A template cannot save these opaque IDs and expect them to work after restart or tomorrow. A standing schedule authorization must issue fresh narrow occurrence/task grants through the authoritative service.
- Cross-step outputs need explicit types, version pinning and freshness rules. Different provider reads are not an atomic cross-provider snapshot; show observation times and preserve uncertainty.
- Budgets must cover all descendants, and foreground chat needs a queue policy. A cost field cannot act as an enforceable budget if provider usage is unavailable.
- R5 needs explicit DST gap/fold, fixed-versus-device timezone, overlap, clock-change and missed-occurrence rules. The computed boundary examples reproduce why these distinctions matter.
- Existing Hermes cron must dispatch through the same trusted gate. UI Quit, backend unavailability or policy failure cannot produce an unrestricted background fallback. Qualify this integration before promising recurring execution; do not build a replacement scheduler to conceal a mismatch.

### Coverage and packaging

- The worker map includes web research and knowledge/notes roles, but the release ladder does not assign them a concrete qualified slice. Name an optional delivery slice or explicitly defer it.
- The 47 planned IDs and 29 named metadata entries remain unreconciled. This was already declared open; it is not evidence that all planned workers are configured.
- The inspected Windows PATH Node is **22.19.0**. The current upstream Hermes Desktop source manifest inspected for this design declares **Node >=26**. That mismatch affects a source-build route; a prebuilt SDK extension does not necessarily require the source build toolchain. Pin the chosen route and compatibility matrix before building, without upgrading the active runtime by assumption. [Upstream manifest](https://github.com/NousResearch/hermes-agent/blob/main/apps/desktop/package.json).
- Read-only R3a and optional W37 need explicit required/optional/justified-N/A acceptance metadata. Otherwise an intentionally unavailable optional operation can block an otherwise useful release, or be falsely marked passed.

## Closure order

1. **Before freezing R1:** close F01/F02; adopt the chat/runtime/event/security/migration contracts in the addendum; resolve the host compatibility gate; pin the R1 feature manifest.
2. **Before accepting R1:** close its P1 cases and preview/accessibility inconsistencies. Run actual packaged Windows lifecycle, keyboard and IPC tests. Static/mock-DOM checks do not substitute.
3. **Before R2:** close memory context/deletion/disclosure/source/freshness and real retrieval-quality cases.
4. **Before R3:** close Google lifecycle, task date/sync and operation-specific write contracts. A clearly read-only variant can progress without pretending write qualification passed.
5. **Before R4/R5:** close workflow types/versioning/budgets and standing-grant/occurrence/lifecycle semantics. No ad-hoc scheduler fallback.
6. **Before R6/R7:** reconcile worker IDs, qualify capability/version changes and each supported advanced effect; W37 remains separately optional and unqualified.

Detailed records: [36 findings](FINDINGS.md), [findings CSV](FINDINGS.csv), [72 supplemental cases](SUPPLEMENTAL-CASES.csv), [coverage and DFS journeys](COVERAGE.md).

## Scope limits

There is no implemented Electron app to load-test yet. No production latency, memory pressure, real CSS rendering, screen-reader behaviour, provider writes, WSL lifecycle, native driver or database crash recovery was exercised here. The 3,840 rows are designed future scenarios, not 3,840 passing tests. Every such scenario and all original 42 release cases remain **Not run**.

BFS/DFS are exhaustive for the finite graphs actually defined, not for every possible string, network interleaving, backend implementation or future plugin. Cycles admit infinitely many traces. Coverage claims are therefore stated as finite reachable states/transitions and enumerated model event orders, with assumptions and missing implementation evidence visible.
