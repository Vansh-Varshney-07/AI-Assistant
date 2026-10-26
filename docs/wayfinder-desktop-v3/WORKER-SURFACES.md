# Workers belong behind product features

The UI is a client, not a new agent. A logical role does not need a permanent process or a permanent tab. One task may use one role or several; expose the names and evidence actually used in the run inspector.

## IDs established by the supplied ownership brief

| Roles | User-facing surfaces | Earliest planned exposure |
|---|---|---|
| W01 orchestrator | Chat; task/run progress | R1 |
| W02 context retrieval; W38 memory queries | Memory evidence and source inspector; access through trusted orchestrator gateway | R2 |
| W04 capability discovery | Connections and availability; mostly backstage in earlier releases | R2/R3; advanced inspection R6 |
| W05 workflow coordination | Run timeline and workflow step list | Basic R1; editable workflows R4 |
| W17 reminder-related role, as identified in the ownership examples | Scheduler and due-task views | R5 |
| W25 coding-related role, as identified in the ownership examples | Projects, repository evidence and reviewed changes | R7 |
| W26 activity analysis | Later fitness area; currently deferred by the user | Later optional release |
| W32 message-action role, as identified in the ownership examples | Communication draft review and supported exact sends | R7 |
| W33 Desktop Context Analyst | Explicitly attached image analysis; user-selected input only | Optional after R2 and its own qualification |
| W34 File Discovery Worker; W35 Local File Analyst | File picker, attachments, document results and citations | R2 |
| W36 Desktop Action Planner; W37 Desktop Action Worker | Proposed desktop action review and actual verified outcomes | R7 optional; current native execution remains unqualified |
| W41 conflict integration; W42 maintenance integration | Memory conflicts, corrections, retractions and dry-run/review controls | R2 narrow operations; later expansion separately qualified |
| W44 recovery | Resume observation, interrupted status and reconciliation | Basic R1; richer R4/R7 |
| W45 security findings, as identified in the ownership examples | Advisory findings in run/change inspector; cannot grant permission | R4/R7 |
| W46 audit | Reviews, receipts and activity history | R2; expanded R4/R7 |
| W47 evaluation infrastructure | Artifact checks and run diagnostics | R4; advanced R6 |

The ownership brief also references **W03, W06–W16, W18–W24, W27–W31, W39, W40 and W43** without supplying a complete numbered name-to-contract catalogue in the inspected project files. These IDs remain in the product coverage inventory, not invented role definitions. Their already named capability families below have user-facing homes. Reconcile the IDs against actual worker configurations before enabling them; no new prompts or replacement roles are authorized by this mapping.

## Named roles already present in the repository registry

The current inspected registry has 29 named entries. These are metadata, not 29 independently qualified production workers. It also contains overlapping general and specialist roles. Resolve aliases/bindings through one registry integration path rather than duplicating execution.

| Existing registry names | Product home |
|---|---|
| Orchestrator | Chat and run coordination |
| Email Analyst; Message Analyst | Briefs and source inspection; Gmail first, other message providers only when selected/qualified |
| Calendar Analyst; Schedule Optimizer; General Task & Schedule Worker | Today, Tasks, Scheduler and exact calendar-change review |
| Task Manager; Commitment Tracker | Proposed work items, due dates and task sources |
| Contact Lookup Worker; Meeting Preparation Worker | Meeting/recipient context when a separately permitted connector exists |
| Document Analyst; Local File Analyst; File Discovery Worker | Attachments and grounded document answers |
| Data Analyst | Selected-data results and artifacts |
| Web Researcher; Source Verifier; General Research & Verification Worker | Cited chat answers and research workflows |
| Response Drafter; Communication Reviewer; Message Action Worker; General Communication Worker | Draft → review → supported approved send, never automatic dispatch from source text |
| Repository Analyst; Error Investigator | Projects, diagnostics and reviewed coding workflows |
| Memory Query Worker | Orchestrator-only memory integration and evidence inspector |
| General Knowledge Worker | Notes/knowledge context through supported connectors |
| Desktop Context Analyst; Desktop Action Planner; Desktop Action Worker; General Desktop Execution Worker | Explicitly enabled desktop support; no inferred background access |

## Agent configuration UX

A role details screen should show: purpose; tested binding/version; model preset; permitted input kinds; effective allowed tools; required connections; scope/budget limits; last synthetic qualification; dependent workflows; and disable/revoke controls. Credentials and hidden reasoning are absent. Ordinary settings cannot broaden a server policy.

Use separate states: **Planned → Configured → Tested → Available**, plus **Disabled**, **Unavailable** and **Needs review**. Availability is contextual: a tested role can still lack an account or current task grant. Skills and Atlas discovery never mint authorization. A status badge must derive from actual evidence, not merely registry `verified` text.
