# Iron Web companion

A personal assistant in which a main agent coordinates specialist work while the user controls retained knowledge and real-world actions.

## Language

**Orchestrator**:
The main agent responsible for interpreting requests, selecting relevant memories, coordinating workers and proposing actions to the user.
_Avoid_: main memory agent, manager tool

**Worker**:
A specialist agent carrying out a bounded assignment using the context and capabilities granted for that assignment.
_Avoid_: Gmail tool, connector agent

**Connector**:
A connection to an external application or a local resource, such as a mailbox, calendar or notes folder.
_Avoid_: agent, skill

**Tool operation**:
A specific available action on a connector, such as searching messages or creating a calendar event.
_Avoid_: skill, permission

**Memory space**:
An independent pool of retained knowledge for a chosen purpose, such as a personal project or an isolated experiment.
_Avoid_: user identity, physical memory tier

**Context packet**:
A selected, task-relevant view of knowledge and constraints supplied to a worker.
_Avoid_: full memory copy, permanent worker memory

**Workflow**:
A coordinated job consisting of related assignments and proposed actions toward a user goal.
_Avoid_: memory record, calendar event

**Proposed action**:
A concrete change or external operation prepared for review before execution.
_Avoid_: completed action, approved action

**Approval**:
The user's permission for a defined operation with specified limits and effects.
_Avoid_: confidence score, model agreement

**Standing approval**:
A revocable permission for recurring operations within explicitly agreed limits.
_Avoid_: permanent permission, unrestricted autonomy

**Reusable skill**:
A reviewed procedure for accomplishing a recurring class of work.
_Avoid_: personal fact, raw conversation history

**Work item**:
An obligation, follow-up or scheduled activity the user wants to track.
_Avoid_: worker assignment, tool call

**Source evidence**:
The original material supporting a remembered claim, extracted obligation or proposed action.
_Avoid_: trusted instruction, model certainty

**Animal companion**:
The desktop interface through which the user chats, reviews actions, receives reminders and inspects assistant activity.
_Avoid_: desktop recorder, unrestricted observer
