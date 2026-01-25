# Tutorial 09: Events — Runtime Timeline, Tool Calls, and State Tracking

## 0) What an Event is (and why you should care)

An **Event** is the runtime’s basic unit of communication: a single record that represents something that happened during an agent run (user input, agent output, tool calls/results, state/artifact updates, control signals, or errors). Events also build on the LLM response structure and add ADK-specific metadata and `actions`.

Why Events matter:
1) They give you the **complete chronological history** of a run (the best way to debug and understand behavior).
2) They carry **state and artifact changes** via `actions` so the session can be updated consistently.
3) They enable **control flow** across agents and tools (handoff/transfer, escalation, end-of-run signals).
4) They power **session history** because the SessionService stores them in `session.events`.

> Note (Python naming): in ADK Python you’ll commonly see snake_case like `invocation_id`, `state_delta`, `artifact_delta`, `transfer_to_agent`, `skip_summarization`.

---

## 1) Conceptual structure (how to “see” an Event)

At a high level, every event is: **metadata + content + actions + runtime details**.

### A) Metadata (who/when/which run)
Identifies who created the event and when/where it happened:
- `author`: who produced the event (`"user"` or an agent name)
- `id`: unique id for the event
- `timestamp`: time created
- `invocationId` / `invocation_id`: groups events belonging to the same user-request → final-response cycle
- `branch`: a hierarchy path when runtime forks execution (useful in multi-agent / branching flows)

### B) Content (the payload: text / tool call / tool result / other)
The actual payload of the event—what was said or exchanged:
- `content.parts[]` is the primary place to look
- `parts` is a **list**: iterate through parts to collect text, tool calls, and tool responses
- parts may contain:
  - `text`
  - `functionCall`
  - `functionResponse`
  - other content types (code execution results, media, etc.)

### C) Actions (side effects + control signals)
Side effects and control signals the runtime should apply next:
- `actions` can contain:
  - state changes (`stateDelta` / `state_delta`)
  - artifact updates (`artifactDelta` / `artifact_delta`)
  - control flow signals (`transferToAgent` / `transfer_to_agent`, `escalate`)
  - summarization behavior (`skipSummarization` / `skip_summarization`)
  - other runtime-directed signals

---

## 2) How to identify the “type” of an event

When you’re reading an event stream, quickly classify the event before extracting details:

### Step 1 — Check the author
- `author == "user"` → user input event
- `author == "<AgentName>"` → produced by that agent (LLM output, tool calls, tool results, or control signals)

### Step 2 — Check the payload: content and parts
Look at `content` and `content.parts[]` (remember: `parts` is a list).

Then classify the event using these fast checks:

#### A) Tool call request
- If you see `content.parts[].functionCall`, it’s a tool request event.

#### B) Tool result
- If you see `content.parts[].functionResponse`, it’s a tool result event.

#### C) Text message (streaming vs complete)
- If you see `content.parts[].text`:
  - `partial == true` → streaming chunk
  - `partial == false` → complete text message

#### D) State/artifact update only
- If `content == null` and `actions.stateDelta` and/or `actions.artifactDelta` exists → state/artifact update event.

#### E) Control signal or other
- If none of the above match, it may be a control signal or a non-textual payload.

---

## 3) Extracting key information (the 3 things you do most)

### A) Text content
Goal: read “what was said”.

Where to look:
- `content.parts[].text`

Practical approach:
- first ensure `content` exists
- then ensure `parts[]` exists and is non-empty
- then iterate parts and collect `.text` across parts that contain it

---

### B) Function (tool) call details
Goal: identify “which tool was requested, with what arguments”.

Where to look:
- `content.parts[].functionCall`
  - `functionCall.name`
  - `functionCall.args`
  - `functionCall.id` (correlation key)
  - `functionCall.partialArgs[]` (streamed args fragments, if present)
  - `functionCall.willContinue` (tool call continues / streaming)

Helper method: `event.get_function_calls()` → list of tool calls in this event

---

### C) Function (tool) response details
Goal: read “what the tool returned” and connect it back to the call.

Where to look:
- `content.parts[].functionResponse`
  - `functionResponse.name`
  - `functionResponse.response`
  - `functionResponse.id` (correlates with the call)
  - `functionResponse.scheduling` (delivery behavior)
  - `functionResponse.willContinue` (streaming tool output)

Helper method: `event.get_function_responses()` → list of tool results in this event

Correlation rule:
- Match `functionCall.id` ↔ `functionResponse.id`

---

### D) Identifiers you’ll use constantly
- `id`: unique per event instance
- `invocationId` / `invocation_id`: groups all events belonging to the same run (trace/log correlation)

---

## 4) Detecting actions and side effects (how to read `actions`)

The `actions` object signals changes that occurred (or should occur). Always check it exists before reading fields.

### A) State changes
Where to look:
- `actions.stateDelta` / `actions.state_delta`

What it means:
- key/value pairs that were modified in session state during the step producing this event

### B) Artifact changes
Where to look:
- `actions.artifactDelta` / `actions.artifact_delta`

What it means:
- indicates which artifacts were saved/updated and how the artifact state changed

### C) Control flow signals
Where to look:
- `actions.transferToAgent` / `actions.transfer_to_agent` → pass control to another agent
- `actions.escalate` → escalate / terminate a loop or signal higher-level handling
- `actions.skipSummarization` / `actions.skip_summarization` → tool result should not be summarized by the LLM

---

## 5) Determining “final” responses (what should be shown as the answer)

Use `event.is_final_response()` to identify events suitable for display as the complete output for a turn. This filters out intermediate steps like tool calls, partial streaming chunks, and internal updates.


