# Headless memory API

The API binds to localhost. Every POST requires `Authorization: Bearer <private credential>` and `Content-Type: application/json`. Authenticated credentials select the tenant, actor and role; request bodies cannot choose them.

| Endpoint | Purpose |
| --- | --- |
| `POST /v1/events` | Save a source event and durable receipt |
| `POST /v1/events/status` | Read processing status using `eid` |
| `POST /v1/events/retry` | Retry a failed receipt |
| `POST /v1/events/withdraw` | Withdraw an unresolved event |
| `POST /v1/events/forget` | Remove retained evidence and redact its text |
| `POST /v1/identity` | Read the authenticated principal |
| `POST /v1/history` | Read source events and receipt states |
| `POST /v1/recall`, `/v1/recall-path` | Read claims with supporting evidence and relationships |
| `POST /v1/search` | Search reconciled memory candidates |
| `POST /v1/context` | Compile hot context, cards and supporting evidence |
| `POST /v1/context/validate` | Revalidate a `context_token` before using generated work |
| `POST /v1/work`, `/v1/work/list` | Register/list work and its claim dependencies |
| `POST /v1/work/claim`, `/v1/work/complete` | Acquire and complete work using an execution lease |
| `POST /v1/handoff` | Read current requirements and review reasons |
| `POST /v1/notifications`, `/v1/notifications/ack` | Read/acknowledge agent notifications |

Example confirmed event, submitted with the user's credential:

```json
{
  "event_id": "requirements-1",
  "subject": "User",
  "text": "Current requirements: Jaipur, December 1-5, budget 60000 INR.",
  "confirmed": true,
  "scope": {"trip_id": "task-1"},
  "claims": [
    {"subject": "User", "predicate": "destination", "value": "Jaipur", "scope": {"trip_id": "task-1"}},
    {"subject": "User", "predicate": "dates", "value": "2026-12-01 to 2026-12-05", "scope": {"trip_id": "task-1"}},
    {"subject": "User", "predicate": "budget", "value": 60000, "kind": "rule", "scope": {"trip_id": "task-1"}},
    {"subject": "User", "predicate": "currency", "value": "INR", "scope": {"trip_id": "task-1"}}
  ]
}
```

Poll `/v1/events/status` with `{"eid":"requirements-1"}` until ready. A receipt acknowledges saved input; it does not establish that semantic processing succeeded.

Request `/v1/context` with the planner/reviewer credential:

```json
{"subject":"User","scope":{"trip_id":"task-1"},"task_type":"itinerary","query":"Prepare current requirements."}
```

The result contains `agent_text`, `traveller_text`, `cards`, `evidence_text`, `prompt`, `claim_ids`, token accounting and a `context_token`. Readiness requires all mandatory fields to be supported. After generating work, send the proof to `/v1/context/validate` with `{"context_token":"<returned proof>"}` and handle invalidation before proceeding.

HTTP 409 signals pending memory or a state conflict. HTTP 401/403 signals authentication/permission failure. Missing or disputed requirements are represented explicitly; callers must inspect readiness and receipt state.
