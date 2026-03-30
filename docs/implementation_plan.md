# Architecture: Adaptive Language-Practice Session

## Overview

Three Lambdas, three routes, no Lambda-to-Lambda calls. Each request is fully self-contained — evaluation and feedback are inline with the request that needs them.

---

## Lambdas

### `POST /session` → `create_session.py`

Creates a session and generates all exercises in one step.

**Request:**
```json
{ "prompt": "10 sentences to practice German accusative case", "level": "B1", "feedback_mode": "end", "lang": "en" }
```

**What it does:**
- Sends the user's free-text prompt to Claude, which returns structured exercise JSON including `topic`, `category`, `language`, and an `exercises` array
- Validates the response schema before writing to DynamoDB
- Persists a SESSION metadata item and one item per exercise
- Returns `session_id` + first exercise (question only, no expected answer)

**Claude's response shape:**
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

**Inputs validated:** `prompt` (required, ≤500 chars), `level` (A1–C2), `feedback_mode` (`each`|`end`), `lang` (`en`|`uk`). `user_id` is read from the Cognito JWT claim — never from the request body.

---

### `POST /session/{id}/answer` → `submit_answer.py`

The core practice loop.

**Request:**
```json
{ "exercise_id": "01", "answer": "Ich sehe den Mann." }
```

**What it does:**
- Fetches all session items in one DynamoDB query
- Evaluates the answer with Claude (returns `{"is_correct": true|false}`)
- If `feedback_mode=each` and the answer is wrong, generates a one-sentence correction
- Saves `user_answer` and `is_correct` to the exercise item
- Returns `next_exercise` (the next unanswered exercise) or `null` when the session is complete
- On session complete: marks `status=complete`, returns `mistakes` list, and (if `feedback_mode=end`) generates a summary feedback paragraph

**Response:**
```json
{
  "is_correct": true,
  "feedback": "...",         // present when feedback is triggered
  "next_exercise": { "id": "02", "question": "..." }  // null when session complete
}
```

When `next_exercise` is `null`, also returns:
```json
{ "mistakes": [ { "exercise_id": "01", "question": "...", "expected_answer": "...", "user_answer": "..." } ] }
```

**Inputs validated:** `answer` (required, ≤300 chars). Ownership check: rejects with 403 if the JWT `sub` doesn't match the session's `user_id`.

---

### `POST /session/{id}/retry` → `retry_session.py`

Generates a targeted retry set from the user's mistakes.

**Request:**
```json
{ "mistakes": [ { "question": "...", "expected_answer": "...", "user_answer": "..." } ] }
```

**What it does:**
- Sends the mistakes list to Claude, which generates a new exercise set addressing those specific gaps
- Creates a new SESSION item in DynamoDB with `parent_session_id` pointing to the original session
- Inherits `level`, `feedback_mode`, `lang`, `user_id` from the parent session
- Returns a new `session_id` + first exercise

---

## What this deliberately avoids

- **No `getNextExerciseLambda`** — the next exercise is returned inline with the answer response
- **No `evaluateAnswersLambda`** — evaluation is part of `submit_answer`
- **No separate prompt-parsing Lambda** — Claude handles topic/category/language extraction as part of exercise generation
- **No Lambda-to-Lambda invocation** — each request is fully self-contained

---

## API Gateway

All routes protected by a Cognito JWT authorizer. `payload_format_version = "2.0"` on all Lambda integrations so JWT claims are available at `requestContext.authorizer.jwt.claims`.

| Method | Route | Lambda |
|--------|-------|--------|
| POST | `/session` | `create_session` |
| POST | `/session/{id}/answer` | `submit_answer` |
| POST | `/session/{id}/retry` | `retry_session` |

---

## Frontend flow

1. User signs in via Cognito auth UI
2. User selects level (A1–C2) and feedback mode from pill selectors, then types a free-text prompt → `POST /session` → first exercise displayed
3. User submits answer → `POST /session/{id}/answer` → feedback (if triggered) + next exercise
4. Session complete → mistakes summary shown, "Retry mistakes?" prompt
5. User accepts retry → `POST /session/{id}/retry` → new exercise set begins

---

## DynamoDB

See [dynamodb_schema.md](dynamodb_schema.md) for the full schema.

One table, two item types. Composite key: `session_id` (PK) + `question_id` (SK). The `question_id` value `"SESSION"` identifies the metadata item; `"01"`, `"02"`, ... identify exercises. A `by-user` GSI on `user_id` supports listing sessions per user.
