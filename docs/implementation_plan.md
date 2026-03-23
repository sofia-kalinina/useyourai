# Implementation Plan: Adaptive Language-Practice Session

## Architecture: 3 Lambdas, 3 Routes

### `POST /session`
Creates a session and generates all exercises in one step.

- Receives: `{ prompt, level, feedback_mode, lang }`
- Calls Claude with the user's free-text prompt, asks for structured JSON:
  ```json
  {
    "topic": "German accusative case",
    "category": "grammar",
    "language": "German",
    "exercises": [
      { "id": "01", "question": "...", "expected_answer": "..." }
    ]
  }
  ```
- Persists session metadata + all exercises to DynamoDB
- Returns: `session_id` + first exercise

**Note:** Topic/category/language extraction happens here — Claude parses the free-text prompt and returns structured metadata stored on the session record. No separate parsing Lambda needed.

---

### `POST /session/{id}/answer`
The core practice loop.

- Receives: `{ exercise_id, answer }`
- Saves the answer, marks it correct/incorrect (Claude evaluation)
- Feedback fires after each answer (`feedback_mode=each`) or at end of session only (`feedback_mode=end`)
- Returns:
  ```json
  {
    "is_correct": true,
    "feedback": "...",      // only present when evaluation triggered
    "next_exercise": {...}  // null when session is complete
  }
  ```
- When `next_exercise` is null, also returns `mistakes: [...]` (list of incorrectly answered exercises + user answers)

---

### `POST /session/{id}/retry`
Generates a targeted retry set based on mistakes.

- Receives: `{ mistakes: [...] }` (exercises + user's wrong answers)
- Calls Claude asking for a new exercise set specifically designed to fix those mistakes
- Creates a child session in DynamoDB (linked to parent via `parent_session_id`)
- Returns: `session_id` + first exercise of retry set

---

## DynamoDB Schema

One table, two item types (composite key: `session_id` PK + `question_id` SK):

| question_id | Item type | Key fields |
|---|---|---|
| `SESSION` | Session metadata | `topic`, `category`, `language`, `level`, `feedback_mode`, `lang`, `user_id`, `status`, `ttl`, `parent_session_id` |
| `01`, `02`, ... | Exercise | `question`, `expected_answer`, `user_answer`, `is_correct`, `feedback` |

---

## API Gateway Routes

| Method | Route | Lambda |
|---|---|---|
| POST | `/session` | `createSessionLambda` |
| POST | `/session/{id}/answer` | `submitAnswerLambda` |
| POST | `/session/{id}/retry` | `retrySessionLambda` |

---

## Frontend Flow

1. User selects level (A1–C2) and feedback mode ("after each answer" / "at the end") from UI pill selectors
2. User types free-text prompt → `POST /session` → display first exercise
3. User submits answer → `POST /session/{id}/answer` → display feedback (if triggered) + next exercise
4. Session complete → show mistakes summary + feedback, "Retry mistakes?" prompt shown
5. User accepts retry → `POST /session/{id}/retry` → new exercise set begins

---

## What this deliberately avoids
- No `getNextExerciseLambda` — next exercise is returned inline with the answer response
- No `evaluateAnswersLambda` — evaluation is part of answer submission
- No separate "parse user prompt" Lambda — Claude handles parsing as part of exercise generation
- No Lambda-to-Lambda invocation — each request is fully self-contained

---

## Sprint Plan

### Sprint 1 — Foundation ✅
1. ✅ Fix DynamoDB table name mismatch (Lambda code + IAM policy)
2. ✅ Implement DynamoDB schema (session + exercise item types)
3. ✅ Implement `createSessionLambda` (`POST /session`)
4. ✅ Update API Gateway routes

### Sprint 2 — Core Loop
5. ✅ Implement `submitAnswerLambda` (`POST /session/{id}/answer`) with inline evaluation
6. ✅ Update frontend to call `POST /session` and display first exercise
7. Integration test: full practice cycle end-to-end

### Sprint 3 — Retry & Hardening
8. ✅ Implement `retrySessionLambda` (`POST /session/{id}/retry`)
9. ✅ Secure API Gateway — Cognito JWT authorizer on all routes (issue #99); `payload_format_version = "2.0"` on integrations
10. ✅ Add prod environment — Terraform config + manual deploy workflow; base workspace owns shared IAM role and ACM certs
11. CloudWatch structured logging across all Lambdas — issue #37
12. ✅ Harden Lambdas against prompt injection (XML tag wrapping, length caps, schema validation) — issue #67
13. ✅ Add level selector + feedback mode UI controls — issue #65
14. ✅ Replace `feedback_every_n` with `level` + `feedback_mode` params — issue #66
15. ✅ Add Cognito auth UI (sign-up, sign-in, confirm, forgot password, silent token refresh) — issue #95
16. ✅ Harden CloudFront (security headers, S3 public access block, config.js no-cache) — issue #106
17. ✅ Refactor deploy workflows into shared reusable workflow with fail-fast on empty TFC outputs
