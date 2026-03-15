# DynamoDB Schema

Table name: `{project_name}-{environment}-table-language-learning`
Billing: `PAY_PER_REQUEST`
TTL attribute: `ttl` (Unix timestamp, auto-delete after session retention period)

## Key structure

| Key | Attribute | Type |
|-----|-----------|------|
| PK  | `session_id` | String |
| SK  | `question_id` | String |

## Item types

One table, two item types — distinguished by the `question_id` value.

### Session metadata item

`question_id = "SESSION"`

| Attribute | Type | Description |
|-----------|------|-------------|
| `session_id` | S | Unique session identifier (PK) |
| `question_id` | S | Always `"SESSION"` for this item type |
| `topic` | S | Exercise topic (e.g. "German accusative case") |
| `category` | S | Grammar category (e.g. "grammar") |
| `language` | S | Target language (e.g. "German") |
| `level` | S | Learner level passed to Claude (A1–C2) |
| `feedback_mode` | S | When to generate feedback: `each` (after every answer) or `end` (at session end) |
| `status` | S | Session state: `active` \| `complete` |
| `parent_session_id` | S | Set on retry sessions; references the original session (optional) |
| `ttl` | N | Unix timestamp for auto-deletion |

### Exercise item

`question_id = "01"`, `"02"`, ... (zero-padded, assigned at session creation)

| Attribute | Type | Description |
|-----------|------|-------------|
| `session_id` | S | Session this exercise belongs to (PK) |
| `question_id` | S | Exercise index, e.g. `"01"` (SK) |
| `question` | S | The exercise prompt shown to the user |
| `expected_answer` | S | Correct answer (used for evaluation) |
| `user_answer` | S | User's submitted answer (set on answer submission) |
| `is_correct` | BOOL | Whether the answer was marked correct (set on answer submission) |
| `feedback` | S | Textual feedback from Claude (set when feedback is triggered) |
