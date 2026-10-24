# WAYFINDER — Master Build Plan

### A Personal AI Operating System with Dynamic Agents, Persistent Memory, Reusable Skills, and Controlled Execution

**Core vision:** Build a personal AI assistant that understands natural-language requests, remembers relevant context, dynamically creates workflows, selects the right tools, delegates bounded tasks to specialized workers, and asks for permission before applying changes.

Wayfinder should not be a chatbot with a collection of integrations, nor a fixed system of seven large agents. It should be a **dynamic workflow orchestration platform** in which tools, skills, and agent workers are reusable building blocks.

The system will combine your existing **Iron Web memory architecture** with **Hermes Agent, NemoClaw, and OpenShell**, plus a custom orchestration layer and a desktop companion.

The objective is to build incrementally, reuse working components, and avoid rebuilding the memory system or creating unnecessary agents.

---

# 1. Product Scope

Wayfinder will provide seven major capability areas, but these will be implemented as collections of reusable tools and skills rather than seven permanently running agents.

| Capability                         | What Wayfinder should do                                                                                            | Initial integrations                              |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **Personal assistant**             | Conversational interaction, context retrieval, remembering preferences, and answering questions about previous work | Hermes + Iron Web                                 |
| **Work assistant**                 | Extract commitments, summarize work-related messages, and identify deadlines                                        | Supported email APIs + WhatsApp Business Platform |
| **Fitness assistant**              | Retrieve activity data, identify weekly trends, and produce a fitness summary                                       | Supported fitness and health APIs                 |
| **Task and schedule manager**      | Manage tasks, notes, reminders, and calendar schedules                                                              | Notion + Google Calendar                          |
| **Browser and research assistant** | Search the web, retrieve pages, compare evidence, and summarize findings                                            | Tavily                                            |
| **Developer assistant**            | Inspect repositories, issues, pull requests, and code; prepare changes for review                                   | GitHub                                            |
| **Desktop companion**              | Floating animal interface, global hotkey, selected-screen context, and memory visibility                            | Desktop application + controlled screen capture   |

These capabilities can cooperate in a single workflow.

For example, a request to organize the upcoming week might combine calendar retrieval, college-task analysis, GitHub issue inspection, and fitness summarization. The planner decides which steps are needed; it does not automatically activate every capability for every request.

Integration availability will depend on API permissions, account access, and platform limitations.

---

# 2. The Complete System Architecture

```text
                         WAYFINDER
                  Personal AI Operating System
                               │
                ┌──────────────┴──────────────┐
                │                             │
          DESKTOP COMPANION              OTHER INTERFACES
          Animal Popup + Chat            Future Web / Mobile
                │                             │
                └──────────────┬──────────────┘
                               │
                     REQUEST INTAKE LAYER
                               │
                     INTENT / CONTEXT ANALYSIS
                               │
                      WORKFLOW PLANNER
                  Goal → Steps → Dependencies
                               │
                    WORKFLOW VALIDATION
                               │
              ┌────────────────┴────────────────┐
              │                                 │
        IRON WEB GATEWAY                  TOOL REGISTRY
        Orchestrator only                 Metadata Search
        Relevant memories                 Semantic Matching
        Provenance                        Skills Discovery
        Temporal validity                 Permission Filtering
              │                                 │
              └────────────────┬────────────────┘
                               │
                     ORCHESTRATOR / SUPERVISOR
                  Context Assembly + Coordination
                               │
                    DYNAMIC WORKFLOW ENGINE
                               │
                ┌──────────────┼──────────────┐
                │              │              │
           WORKER A        WORKER B        WORKER C
           Research        Scheduling      Analysis
                │              │              │
           Reusable        Reusable        Reusable
           Skills          Skills          Skills
                │              │              │
           Approved        Approved        Approved
           Read Tools      Read Tools      Read Tools
                └──────────────┼──────────────┘
                               │
                      RESULT VALIDATION
                               │
                     ACTION / RISK CHECK
                               │
                       APPROVAL GATE
                               │
                     APPROVED EXECUTION
                               │
                 HERMES + CONTROLLED RUNTIME
                               │
                 OPEN SHELL SECURITY BOUNDARY
                               │
                  CONNECTED SERVICES / TOOLS
                               │
                RESULTS + AUDIT + MEMORY REVIEW
                               │
                       WAYFINDER UI
```

### The architecture has four distinct planes

**1. Intelligence plane:** Hermes, planning, reasoning, worker assignment, and result synthesis.

**2. Memory plane:** Iron Web, accessed through a controlled gateway by the orchestrator.

**3. Capability plane:** Tool registry, skill registry, APIs, connectors, and atomic operations.

**4. Control plane:** Permissions, approval, execution policies, audit logs, and OpenShell sandbox restrictions.

NemoClaw supports the deployment and integration of compatible agent environments. It is not a replacement for the workflow engine, memory engine, or authorization logic that we build for Wayfinder.

---

# 3. Technology Responsibilities

We need a clear division of responsibility so that components do not overlap unnecessarily.

| Component                      | Responsibility                             | What we must implement                                                              |
| ------------------------------ | ------------------------------------------ | ----------------------------------------------------------------------------------- |
| **Iron Web**                   | Persistent AI memory                       | Reuse the existing architecture and expose a controlled memory gateway              |
| **Hermes Agent**               | Agent runtime and reasoning                | Configure the orchestrator and bounded worker runs                                  |
| **NemoClaw**                   | Agent deployment and integration framework | Use the supported deployment path where appropriate                                 |
| **OpenShell**                  | Controlled execution environment           | Apply filesystem, network, and process restrictions                                 |
| **Wayfinder Workflow Engine**  | Task execution lifecycle                   | Build planning, dependencies, pauses, retries, cancellation, and resumability       |
| **Tool Registry**              | Atomic action discovery                    | Define metadata, input/output schemas, permissions, and tool matching               |
| **Skill Registry**             | Reusable procedures                        | Store, version, discover, and invoke skills                                         |
| **Policy and Approval Engine** | Authorization                              | Validate proposed operations and enforce approval before protected actions          |
| **Desktop UI**                 | User interaction                           | Implement the floating animal, global hotkey, chat, approvals, and memory dashboard |

**Important:** We should not assume every desired function is already built into Hermes or NemoClaw. The exact APIs and supported integrations must be verified against the versions we choose.

Official references: [Hermes Agent documentation](https://hermesagent.nousresearch.com/?utm_source=chatgpt.com), [NVIDIA NemoClaw](https://github.com/NVIDIA/NemoClaw?utm_source=chatgpt.com), and [NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell?utm_source=chatgpt.com).

---

# 4. The Atomic Capability System

This is the central design principle of Wayfinder.

We will have three building blocks: **tools, skills, and workers**.

## 4.1 Tools — one operation per capability

Tools perform specific, well-defined actions.

Examples:

| Tool                      | Purpose                               | Risk           |
| ------------------------- | ------------------------------------- | -------------- |
| `search_web`              | Search for relevant webpages          | Read           |
| `fetch_webpage`           | Retrieve a webpage                    | Read           |
| `search_memory`           | Find relevant stored memories         | Sensitive read |
| `get_calendar_events`     | Read calendar events                  | Read           |
| `create_calendar_event`   | Create a calendar event               | Write          |
| `search_notion_tasks`     | Retrieve tasks                        | Read           |
| `update_notion_task`      | Update a task                         | Write          |
| `search_github_issues`    | Find issues                           | Read           |
| `create_github_issue`     | Create an issue                       | Write          |
| `get_fitness_summary`     | Retrieve supported activity data      | Sensitive read |
| `capture_selected_screen` | Capture a user-selected screen region | Sensitive read |

A tool should not be able to silently expand its authority. A read-only GitHub tool must not also have permission to merge pull requests.

## 4.2 Skills — reusable procedures

Skills describe how to achieve a goal using available tools.

Examples:

* `weekly_planning`
* `research_and_source_comparison`
* `fitness_weekly_summary`
* `github_repository_investigation`
* `task_prioritization`
* `memory_correction`
* `calendar_conflict_resolution`
* `document_summarization`

A skill contains its procedure, required inputs, expected outputs, constraints, and suggested tools.

A skill does **not** grant permissions by itself. The policy engine independently checks the worker's authority and the requested operation.

## 4.3 Workers — bounded reasoning tasks

Workers are configured agent runs that receive:

* A specific objective.
* Relevant context.
* Selected skills.
* A limited tool allowlist.
* Explicit restrictions.
* An expected output schema.
* A timeout and resource budget where appropriate.

For example, a research worker might receive a question, relevant preferences, a source-comparison skill, and read-only web tools. It would not receive unrestricted calendar access or direct Iron Web credentials.

Workers can be created dynamically for each workflow. We do not need seven permanently running domain agents.

### The decision rule

* Use a **tool** for an atomic operation.
* Use a **skill** for a reusable procedure.
* Use a **worker** when a step requires independent reasoning or adaptation.
* Use the **orchestrator** for memory access, coordination, and final decisions.

This minimizes unnecessary model calls and makes the system easier to test.

---

# 5. The Workflow Planning and Execution Engine

Every user request should become a validated workflow rather than an informal sequence of agent messages.

## 5.1 Request lifecycle

1. **Intake:** Understand the user's goal and constraints.
2. **Context retrieval:** Retrieve only the memories relevant to the task.
3. **Planning:** Generate steps, dependencies, and expected results.
4. **Capability discovery:** Find suitable tools and skills.
5. **Policy validation:** Reject unavailable, unauthorized, or inappropriate operations.
6. **Worker assignment:** Assign bounded tasks to suitable workers.
7. **Execution:** Run authorized read operations and independent tasks in parallel where possible.
8. **Validation:** Check results, evidence, completeness, and constraints.
9. **Approval:** Present proposed changes for review.
10. **Application:** Execute approved changes.
11. **Audit:** Record what happened.
12. **Memory review:** Decide whether the outcome should update persistent memory.

The workflow engine should persist its execution state so an interrupted task can resume without repeating every completed step.

## 5.2 Example: planning the user's week

User prompt:

> Plan my week around college work, fitness goals, and pending GitHub issues. Suggest a balanced schedule, but don't change anything without asking me.

The planner creates the following workflow:

| Step | Operation                       | Dependencies | Permission         |
| ---- | ------------------------------- | ------------ | ------------------ |
| 1    | Retrieve relevant preferences   | None         | Memory gateway     |
| 2    | Read calendar events            | None         | Read               |
| 3    | Retrieve pending college tasks  | None         | Read               |
| 4    | Retrieve GitHub issues          | None         | Read               |
| 5    | Retrieve available fitness data | None         | Read               |
| 6    | Consolidate findings            | Steps 1–5    | Internal reasoning |
| 7    | Draft the weekly schedule       | Step 6       | Prepare            |
| 8    | Check conflicts and constraints | Step 7       | Prepare            |
| 9    | Present proposed changes        | Step 8       | Approval required  |
| 10   | Apply approved changes          | Step 9       | Write              |

Steps 2–5 may run in parallel. If a connector is unavailable, the planner should report the missing data rather than inventing it.

The workflow must distinguish between **preparing an action and applying an action**.

---

# 6. Tool Discovery and Metadata Matching

Your vector-based tool discovery concept will become a core subsystem.

Every tool should have structured metadata similar to this:

```yaml
name: create_calendar_event
description: Create a calendar event after authorization
capabilities:
  - calendar
  - scheduling
operation: write

input_schema:
  title: string
  start_time: datetime
  end_time: datetime
  timezone: string

output_schema:
  event_id: string
  status: string

data_scope:
  - calendar

allowed_worker_types:
  - scheduling

risk_level: write
requires_approval: true

network_policy:
  - approved_calendar_api

memory_access: none
```

This is an illustrative configuration, not an existing tool definition.

### Discovery pipeline

1. The planner describes what each workflow step needs.
2. Semantic retrieval identifies candidate tools from their metadata.
3. Exact schema validation checks whether the candidate can satisfy the task.
4. The policy engine filters candidates based on the current workflow and worker.
5. The orchestrator assigns a permitted tool.
6. The executor validates arguments and invokes it.
7. The result is validated against the declared output schema.

**Vector similarity is for discovery, not authorization.**

The system must never execute an arbitrary tool name simply because an LLM generated it or the vector search returned a close match.

For the first version, SQLite plus a vector index may be sufficient. We should not introduce a separate infrastructure service until the number of tools or measured performance justifies it.

---

# 7. Iron Web: Persistent Memory and Context Isolation

Iron Web remains the central memory system. We should reuse its existing architecture rather than rebuild it inside Hermes.

Your key requirement is:

> The orchestrator can access persistent memory. Workers receive only task-relevant context and cannot directly browse or modify the full memory store.

## 7.1 Memory flow

```text
User Request
     │
     ▼
Orchestrator
     │
     ▼
Iron Web Memory Gateway
     │
     ├── Retrieve relevant memories
     ├── Check temporal validity
     ├── Retrieve provenance
     ├── Resolve corrections / superseded facts
     └── Apply access and sensitivity filters
     │
     ▼
Task-Specific Context Package
     │
     ▼
Bounded Worker
     │
     ▼
Worker Result
     │
     ▼
Orchestrator Reviews Result
     │
     ▼
Optional Memory Update
```

## 7.2 Memory rules

* Workers do not receive direct Iron Web credentials.
* The memory gateway returns only the information needed for a task.
* Sensitive memories are filtered before context is shared.
* Workers return proposed observations or corrections; they do not directly update persistent memory.
* The orchestrator decides whether a result should be stored.
* Memory updates preserve provenance, temporal validity, and correction history.
* Temporary workflow data is not automatically promoted into long-term memory.
* Memory retrieval and memory modification are separate operations.

We should also prevent indirect access. A worker must not be able to reach the underlying memory database through an unrestricted network connection or filesystem path.

## 7.3 What must be tested

1. Store a memory and retrieve it in a later conversation.
2. Restart the application and verify persistence.
3. Correct a memory and ensure the obsolete value is not incorrectly reused.
4. Verify provenance for a retrieved fact.
5. Confirm that unrelated or sensitive memories are not forwarded to a worker.
6. Verify that a worker cannot directly access the full memory system.
7. Inspect the memory dashboard to see what was stored and why.

These tests are particularly important because Iron Web is a key differentiator of the project.

---

# 8. Approval, Permissions, and Security

Approval must be a system-level enforcement mechanism, not merely a conversational instruction.

## 8.1 Four operation classes

| Class          | Examples                                                              | Default behavior                                      |
| -------------- | --------------------------------------------------------------------- | ----------------------------------------------------- |
| **Read**       | Search webpages, retrieve calendar events, inspect GitHub issues      | Execute if authorized                                 |
| **Prepare**    | Draft emails, propose schedules, generate code patches                | Prepare without applying                              |
| **Write**      | Create events, update tasks, create issues, send messages             | Require approval                                      |
| **Restricted** | Delete files, change credentials, perform broad filesystem operations | Additional safeguards; some actions remain prohibited |

For the first version, use a conservative rule: all external writes require explicit approval. We can later introduce narrowly scoped exceptions for low-risk operations if you want them.

## 8.2 Approval workflow

```text
Worker proposes action
         │
         ▼
Validate action and target
         │
         ▼
Check permissions and policy
         │
         ▼
Display exact proposed change
         │
         ▼
User approves / edits / rejects
         │
         ▼
Revalidate approved action
         │
         ▼
Execute through permitted tool
         │
         ▼
Record result
```

Approval should be bound to the exact operation and its parameters. If the target or material details change, the system must request approval again.

A plan approval must not automatically authorize every future action the worker might invent.

The interface should provide:

* **Approve**
* **Review individually**
* **Edit**
* **Reject**
* **Cancel workflow**

For destructive operations, the system may require stronger confirmation or simply refuse the action.

## 8.3 Security responsibilities

**Wayfinder's policy engine**

* Decides which operations a workflow and worker may request.
* Enforces approval requirements.
* Checks tool parameters and data scope.

**OpenShell**

* Restricts execution environments and applicable filesystem/network access.
* Helps prevent unauthorized access outside the permitted workspace.
* Provides a controlled environment for supported agent workloads.

**NemoClaw**

* Helps manage the supported agent deployment and integration configuration.

**Iron Web gateway**

* Restricts memory operations and controls context exposure.

These controls are complementary. A sandbox alone cannot determine whether an action is appropriate, and an approval button alone cannot guarantee that an agent is technically unable to bypass restrictions.

---

# 9. Desktop Companion: The Animal Popup

The animal companion is Wayfinder's user interface, not a separate agent.

## 9.1 First version

The desktop companion should provide:

* A small floating animal icon.
* A global hotkey to open and close the assistant.
* A chat interface.
* A selected-screen or region-capture action.
* Pending approval notifications.
* A workflow-progress panel.
* A memory dashboard.
* Controls to pause, cancel, and inspect workflows.

The UI should reveal what Wayfinder is doing rather than making the system feel like a black box.

## 9.2 Desktop understanding

For the initial release, use user-triggered screen capture. The user selects a region or requests a screenshot, and Wayfinder receives that specific image as task context.

Later, we can add opt-in desktop indexing and broader contextual awareness. That requires:

* Explicitly selected folders and applications.
* Sensitive-data exclusions.
* Visible capture and indexing status.
* Pause and disable controls.
* Inspection and deletion of stored desktop context.
* Restrictions on which workers can access captured data.

We should not begin with silent, continuous recording of the entire desktop. It creates unnecessary privacy and security risks and is not required to validate the core architecture.

## 9.3 UI design principle

The interface should make four things immediately visible:

1. **What did I ask?**
2. **What is Wayfinder planning to do?**
3. **What data and tools will it use?**
4. **What will happen if I approve?**

That is more important in the first release than elaborate animations or a complex animal-character system.

---

# 10. Reusable Skills and Tool Lifecycle

Skills and tools should be independently maintainable so new capabilities can be added without redesigning the orchestrator.

Each skill should have:

* A unique identifier and version.
* A description and intended use.
* Required inputs and expected outputs.
* Procedure or instructions.
* Suggested tools.
* Constraints and failure handling.
* Compatibility requirements.
* Tests and validation criteria.

Each tool should have a separately maintained contract defining its schema, permissions, network requirements, and execution behavior.

### Example

A `weekly_planning` skill might use:

1. Calendar-reading tools.
2. Task-retrieval tools.
3. Optional fitness-summary tools.
4. A scheduling-analysis worker.
5. A conflict-checking procedure.
6. Calendar-writing tools, available only after approval.

The same skill can work with different calendar providers as long as the tool contracts remain compatible.

We should version skills, test them before activation, and avoid letting an agent silently rewrite its own permissions or grant itself additional tools.

---

# 11. Integration Roadmap

Integrations should be added in a deliberate order. Each one introduces authentication, permissions, data handling, and failure cases.

| Integration           | Initial scope                                             | Later capabilities                                                    |
| --------------------- | --------------------------------------------------------- | --------------------------------------------------------------------- |
| **Tavily**            | Search the web                                            | Multi-source research and evidence synthesis                          |
| **Google Calendar**   | Read events and availability                              | Approved event creation, updates and reminders                        |
| **GitHub**            | Read repositories, issues and pull requests               | Approved issue creation, branch operations and proposed code changes  |
| **Notion**            | Read tasks and notes                                      | Approved task updates and page creation                               |
| **Email**             | Read supported messages and extract commitments           | Draft replies, with sending behind approval                           |
| **WhatsApp Business** | Use supported business messaging APIs and authorized data | Business-message summarization and approved responses where permitted |
| **Fitness APIs**      | Retrieve activity and weekly metrics                      | Personalized summaries and trend analysis                             |
| **Desktop context**   | User-selected screenshot or screen region                 | Opt-in desktop indexing with strict privacy controls                  |

### Integration rules

1. Start with read-only permissions.
2. Request only the OAuth scopes required by the feature.
3. Store credentials using an appropriate secure mechanism.
4. Keep credentials out of worker prompts and logs.
5. Route writes through the approval and policy layers.
6. Validate results against expected schemas.
7. Handle expired credentials, rate limits, and unavailable services gracefully.

For email and messaging, we should distinguish between personal and business accounts and use the officially supported APIs. We should not assume that an integration can access arbitrary WhatsApp conversations.

---

# 12. Implementation Phases and Milestones

The build should progress from a functioning core to a complete desktop assistant.

## Phase 0 — Repository Audit and Environment Validation

**Objective:** Determine what already works before writing new infrastructure.

Tasks:

* Inspect the Iron Web repository and its current architecture.
* Identify working memory APIs, storage components, configuration, and tests.
* Determine what remains of the previous web UI and integrations.
* Verify how Hermes can invoke custom tools and receive task-specific context.
* Check NemoClaw and OpenShell compatibility with Windows 11 + WSL2.
* Select a supported execution and deployment path.
* Record missing components and integration boundaries.

**Deliverable:** A verified component map, a reuse-versus-rebuild list, and an implementation checklist.

**Completion condition:** We know exactly how Wayfinder will call Iron Web and what needs to be built around it.

## Phase 1 — Validate Iron Web Memory

**Objective:** Prove that the existing memory architecture works independently of Wayfinder.

Tasks:

* Create a minimal test interface.
* Test memory storage and retrieval.
* Test persistence across restarts.
* Test corrections, temporal validity, and provenance.
* Inspect what is displayed in the memory dashboard.
* Test retrieval quality and latency with representative prompts.
* Verify that memory access can be restricted to a gateway.

**Deliverable:** A repeatable memory test suite and a verified memory interface.

**Completion condition:** We can demonstrate what was stored, why it was retrieved, and how corrections are handled.

## Phase 2 — Build the Wayfinder Core

**Objective:** Create the first working end-to-end assistant.

Tasks:

* Connect a chat interface to the Hermes runtime.
* Implement request intake and structured task representation.
* Build the orchestrator.
* Add the Iron Web memory gateway.
* Implement bounded worker configuration.
* Create a simple workflow state model.

**Deliverable:** A working assistant that can retrieve relevant memories, answer a request, and maintain task context.

**Completion condition:** A request travels through intake → memory retrieval → reasoning → response without requiring manual intervention between stages.

## Phase 3 — Tool and Skill Registries

**Objective:** Make capabilities dynamically discoverable and reusable.

Tasks:

* Define tool metadata and schemas.
* Implement semantic candidate retrieval.
* Add strict permission filtering.
* Define skill metadata and versioning.
* Validate tool inputs and outputs.
* Implement worker-specific tool allowlists.
* Add tests for invalid tool selection and unauthorized operations.

**Deliverable:** A registry that can discover appropriate tools and skills for a task.

**Completion condition:** Wayfinder selects from registered capabilities rather than executing arbitrary tool names generated by an LLM.

## Phase 4 — Workflow Planner and Executor

**Objective:** Convert natural-language requests into executable workflows.

Tasks:

* Convert requests into structured goals and constraints.
* Generate workflow steps and dependencies.
* Validate plans before execution.
* Support sequential and parallel tasks.
* Assign workers dynamically.
* Add retries, timeouts, cancellation, and error handling.
* Persist workflow state and support resumability.
* Validate worker results before they reach later stages.

**Deliverable:** A workflow engine that coordinates tools and workers.

**Completion condition:** Wayfinder can plan and complete a multi-step read-only task while showing progress and handling failures.

## Phase 5 — Approval and Security

**Objective:** Ensure that actions remain under user control.

Tasks:

* Classify tools by risk and operation type.
* Add the approval interface.
* Bind approvals to exact action parameters.
* Revalidate actions before execution.
* Enforce worker permissions and data scopes.
* Add audit records.
* Test rejection, cancellation, and changed-action scenarios.
* Configure OpenShell restrictions where supported.

**Deliverable:** A controlled execution system with auditable approvals.

**Completion condition:** No protected write operation executes without valid authorization.

## Phase 6 — First Real Integrations

**Objective:** Demonstrate useful workflows against real services.

Start with:

1. Tavily web search.
2. Google Calendar read access.
3. GitHub read access.

Then add:
4. Notion task retrieval.
5. Fitness data retrieval.
6. Email and supported WhatsApp Business integrations.

**Deliverable:** Real workflows that combine data from multiple sources.

**Completion condition:** Wayfinder can retrieve information from connected services, combine the results, and propose changes without applying them prematurely.

## Phase 7 — Desktop Companion

**Objective:** Make Wayfinder usable during normal desktop work.

Tasks:

* Build the floating animal popup.
* Implement the global hotkey.
* Connect the UI to the workflow engine.
* Display current plans and task progress.
* Implement selected-screen capture.
* Show approval requests and execution results.
* Build the memory inspection interface.
* Add pause, cancellation, and privacy controls.

**Deliverable:** A usable desktop companion.

**Completion condition:** The user can invoke Wayfinder from the desktop, inspect a plan, approve an action, and see the outcome.

## Phase 8 — Advanced Features and Hardening

**Objective:** Expand functionality without compromising reliability.

Tasks:

* Add reusable skills for common workflows.
* Add more integrations.
* Improve memory retrieval and latency.
* Test long-running and interrupted workflows.
* Add desktop indexing only if required.
* Test security boundaries and failure recovery.
* Package and document the application.
* Prepare a demonstration using real, reproducible scenarios.

**Deliverable:** A stable, extensible personal AI system.

**Completion condition:** The application has repeatable end-to-end tests, documented permissions, and demonstrable security controls.

---

# 13. Recommended Technical Structure

We should keep the initial codebase modular without introducing unnecessary microservices.

An initial structure could look like this:

```text
wayfinder/
│
├── app/
│   ├── main.py
│   ├── config.py
│   └── lifecycle.py
│
├── desktop/
│   ├── popup.py
│   ├── hotkey.py
│   ├── chat_view.py
│   ├── approval_view.py
│   └── memory_view.py
│
├── orchestrator/
│   ├── intake.py
│   ├── planner.py
│   ├── supervisor.py
│   ├── worker_factory.py
│   ├── context_builder.py
│   └── result_validator.py
│
├── workflows/
│   ├── models.py
│   ├── executor.py
│   ├── dependency_manager.py
│   ├── state_store.py
│   └── recovery.py
│
├── memory/
│   ├── gateway.py
│   ├── context_filter.py
│   └── update_review.py
│
├── registry/
│   ├── tools.py
│   ├── skills.py
│   ├── metadata.py
│   └── semantic_search.py
│
├── policies/
│   ├── authorization.py
│   ├── risk_classifier.py
│   ├── approval.py
│   └── execution_rules.py
│
├── execution/
│   ├── tool_executor.py
│   ├── hermes_adapter.py
│   └── openshell_adapter.py
│
├── integrations/
│   ├── tavily/
│   ├── google_calendar/
│   ├── github/
│   ├── notion/
│   ├── email/
│   ├── whatsapp_business/
│   └── fitness/
│
├── skills/
│   ├── research/
│   ├── weekly_planning/
│   └── summarization/
│
├── audit/
│   └── event_log.py
│
└── tests/
    ├── test_memory_gateway.py
    ├── test_tool_registry.py
    ├── test_workflows.py
    ├── test_approval.py
    └── test_permissions.py
```

This is the **target logical structure**, not a requirement to create every file immediately. We should adapt it to the existing Iron Web repository and the actual APIs exposed by Hermes.

Initially, keep the application in one repository and use clear module boundaries. Split components into separate services only when deployment, isolation, or measured performance requires it.

---

# 14. Essential Non-Functional Requirements

Wayfinder should be judged not only by what it can do but also by how reliably and safely it does it.

| Requirement          | Acceptance criterion                                                      |
| -------------------- | ------------------------------------------------------------------------- |
| Memory isolation     | Workers cannot directly access the complete memory store                  |
| Context relevance    | Workers receive only task-relevant context                                |
| Tool security        | Unregistered and unauthorized tools are rejected                          |
| Approval enforcement | Protected writes cannot execute without valid approval                    |
| Workflow reliability | Failed or interrupted workflows can be inspected and recovered            |
| Auditability         | Each action has a traceable workflow and execution record                 |
| Memory integrity     | Corrections and superseded memories are handled correctly                 |
| Privacy              | Users can inspect and control stored context                              |
| Extensibility        | New tools and skills can be registered without rewriting the orchestrator |
| Resource efficiency  | Unnecessary worker creation and model calls are avoided                   |
| Observability        | Users can see the plan, selected tools, worker progress, and results      |

We should test these requirements as we build, not postpone all security and reliability work until the final phase.

## 15. The First End-to-End Demonstration

Our first meaningful demonstration should be a deliberately small version of the final product.

### User prompt

> Research the best options for organizing my upcoming week, remember my preference for evening workouts, inspect my available calendar slots, and propose a schedule. Do not make changes without asking me.

### Expected behavior

1. The intake stage identifies the goal and constraints.
2. The orchestrator retrieves the relevant preference from Iron Web.
3. The planner creates a workflow.
4. The registry discovers the necessary read-only tools and skills.
5. The workflow engine executes the permitted steps.
6. A worker analyzes the results.
7. The orchestrator validates the proposed schedule.
8. The UI displays the schedule and any proposed calendar changes.
9. The user approves, edits, or rejects the changes.
10. Only approved operations execute.
11. The application records the outcome and considers whether a memory update is appropriate.

This single demonstration tests the central architecture without requiring every integration or agent to be finished.

---

# 16. How We Will Measure Progress

We should not measure progress by the number of agents, tools, or integrations we have created.

Instead, track these milestones:

* **Memory:** Can Wayfinder retrieve the right memory, preserve provenance, and handle corrections?
* **Planning:** Does the generated workflow contain the necessary steps and dependencies?
* **Discovery:** Does the system choose appropriate registered tools without bypassing permissions?
* **Execution:** Can workflows complete, recover from failures, and resume after approval?
* **Safety:** Are unauthorized operations rejected even if a worker requests them?
* **Efficiency:** How many model calls and tool calls does a workflow require, and how long does it take?
* **Usability:** Can the user understand what the assistant is doing and control the outcome?
* **Extensibility:** Can a new capability be added through a tool or skill without redesigning the core?

These measurements will help us identify whether the system's real bottleneck is planning, memory retrieval, tool selection, external APIs, or model latency.

---

# 17. Final Architecture Decisions

I recommend treating the following as the foundational design decisions for Wayfinder.

| Decision             | Direction                                                                              |
| -------------------- | -------------------------------------------------------------------------------------- |
| Agent organization   | Dynamic workers, not seven fixed domain agents                                         |
| Atomic operations    | Individual tools with explicit schemas                                                 |
| Reusability          | Versioned skills independent of individual workers                                     |
| Planning             | Structured workflows with explicit dependencies                                        |
| Memory               | Existing Iron Web architecture                                                         |
| Memory access        | Orchestrator-only, mediated through a gateway                                          |
| Tool discovery       | Metadata retrieval plus semantic matching and strict authorization                     |
| Execution            | Hermes runtime, integrated with the workflow engine                                    |
| Deployment           | NemoClaw where compatible with the chosen agent environment                            |
| Isolation            | OpenShell where supported, combined with application-level policies                    |
| Approval             | Centralized gate for protected operations                                              |
| Interface            | Floating animal companion with chat, approvals, workflow status, and memory inspection |
| Initial integrations | Tavily, Google Calendar, and GitHub read access                                        |
| Initial priority     | Validate the architecture before expanding the feature set                             |

## 18. What We Should Do First

**Do not start by creating the desktop UI, installing every integration, or writing a new memory engine.**

Our first task is to inspect the current Iron Web codebase and establish the boundary between its existing memory functionality and the new Wayfinder components.

We need to identify:

1. The working memory entry points and API.
2. How memories are stored, retrieved, corrected, and inspected.
3. Which existing integrations and UI components remain usable.
4. How Hermes can invoke the memory gateway and execute bounded worker tasks.
5. Which NemoClaw/OpenShell deployment options are actually compatible with your environment.

Once we have that information, we can create a concrete implementation checklist mapped to the actual files and functions in the repository.

**The guiding principle:** Build the smallest working version of the complete architecture first. Then expand it by adding tools, skills, workers, and integrations—not by repeatedly redesigning the core.