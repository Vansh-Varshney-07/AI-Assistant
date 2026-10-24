# Wayfinder personal AI app

A configurable personal assistant whose main agent coordinates bounded work using approved knowledge, capabilities and procedures.

## Language

**Main app**:
The primary interface for conversations, connections, workflows, memory, skills, approvals and preferences.
_Avoid_: animal companion, memory engine

**Quick-chat window**:
A small persistent view for conversations and quick tasks in the same application.
_Avoid_: separate assistant, desktop observer

**Orchestrator**:
The main agent responsible for context selection, planning, coordination and result review.
_Avoid_: permanent agent fleet

**Worker**:
A bounded reasoning assignment with selected context, capabilities and an expected result.
_Avoid_: connector, tool

**Memory space**:
An independent pool of retained knowledge for an authorized purpose.
_Avoid_: owner credential, physical tier

**Context packet**:
The selected knowledge, evidence and constraints supplied for a worker assignment.
_Avoid_: shared memory copy

**Plugin**:
A reviewed integration package that exposes a set of capabilities.
_Avoid_: agent, universal account access

**Connection**:
An authorized binding between a configured plugin and a particular account or resource.
_Avoid_: approval for every operation

**Tool operation**:
One specific capability offered by a plugin or approved local resource.
_Avoid_: workflow, skill

**Skill**:
A reviewed reusable procedure for a class of work.
_Avoid_: factual memory, permission grant

**Workflow template**:
A reusable versioned arrangement of steps, inputs, dependencies and review points.
_Avoid_: completed job

**Workflow run**:
One execution attempt with its own progress, outcomes and recorded effects.
_Avoid_: template, conversation

**Action proposal**:
A concrete operation and intended effect presented before application.
_Avoid_: completed action

**Standing grant**:
A revocable permission for explicitly bounded repeated operations.
_Avoid_: unrestricted autonomy

**Source evidence**:
Original material supporting a claim, answer or action proposal.
_Avoid_: user instruction, model confidence
