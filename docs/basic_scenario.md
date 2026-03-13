# User Story: Adaptive Language-Practice Session (No User Accounts)

## Story

**As a learner,**
I want to ask the system for X exercises on a free-text topic,
so that I can practice items one by one, get textual feedback from Claude Sonnet at configurable intervals, and — if I want — re-run a targeted practice set focused on items I got wrong.

## Acceptance Criteria

1. **Exercise generation** — User submits a free-text prompt (e.g. *"Get 10 sentences to train topic 'German accusative case'"*). The system generates X items via Claude Sonnet and stores them under a new session ID.

2. **One-by-one practice** — The system presents items individually, persists each user answer, and marks each answer as correct or incorrect using Claude Sonnet evaluation.

3. **Textual feedback** — Feedback is text-only (no numeric scores). Feedback frequency is configurable per session via a `feedback_every_n` parameter.

4. **Retry mistakes** — After all X items are completed, the system prompts the user to "retry mistakes". If accepted, the list of incorrectly answered items and the user's answers is sent to Claude Sonnet, which generates a new targeted exercise set designed to address those specific mistakes.

5. **Session persistence & cleanup** — Sessions are stored for a configurable retention period and then auto-deleted (currently implemented via DynamoDB TTL).
