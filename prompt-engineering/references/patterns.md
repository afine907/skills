# Prompt Engineering Patterns Reference

## Few-Shot Prompting

Provide examples of input-output pairs to guide the model.

```
Classify the sentiment of each review.

Review: "The food was amazing and the service was excellent!"
Sentiment: Positive

Review: "Terrible experience. Long wait and cold food."
Sentiment: Negative

Review: "It was okay, nothing special but nothing bad either."
Sentiment: Neutral

Review: "I loved the ambiance but the portions were too small."
Sentiment:
```

**When to use:** Classification, formatting tasks, style matching, translation.

**Tips:** Use 3-5 examples, include edge cases, keep format consistent, order from simple to complex.

---

## Chain-of-Thought (CoT)

Ask the model to show its reasoning step by step.

```
Solve this step by step.

A store sells apples for $2 each. On Tuesday, they sold 15 apples
in the morning and 23 in the afternoon. They also sold 8 oranges
at $3 each. What was the total revenue from apples?

Think through this step by step:
```

**Variants:**

### Zero-shot CoT
Simply add "Let's think step by step" or "Explain your reasoning" to any prompt.

### Manual CoT
Provide explicit reasoning steps in the prompt.

```
Q: Roger has 5 tennis balls. He buys 2 cans of 3 tennis balls each.
   How many does he have now?

A: Roger starts with 5 balls. 2 cans of 3 balls = 6 balls.
   5 + 6 = 11. The answer is 11.
```

### Auto-CoT
Generate reasoning chains automatically for a set of diverse questions, then include them as few-shot examples.

**When to use:** Math, logic, multi-step reasoning, debugging, complex analysis.

---

## System Prompt Framing

Set the model's role, constraints, and behavior at the system level.

```
You are a senior Python developer with 15 years of experience.
You write clean, well-documented code following PEP 8.
When reviewing code, you:
1. Check for correctness first
2. Look for performance issues
3. Suggest readability improvements
4. Note security concerns

You always explain WHY something should change, not just WHAT to change.
```

**Key elements:**
- Role definition
- Expertise level
- Behavioral rules
- Output format expectations
- Constraints and boundaries

---

## Structured Output Prompting

Request specific output formats.

```
Analyze this function and return your findings as JSON:

function calculateDiscount(price, customerType) {
  // ...
}

Return in this format:
{
  "correctness": { "score": 1-10, "issues": [] },
  "performance": { "score": 1-10, "issues": [] },
  "readability": { "score": 1-10, "issues": [] },
  "suggestions": []
}
```

**When to use:** API integrations, automated pipelines, data extraction, evaluation tasks.

---

## Self-Consistency

Generate multiple reasoning paths and take the majority answer.

```
Solve this problem using 3 different approaches.
For each approach, show your work independently.
Then compare your answers and give the most likely correct one.
```

**When to use:** High-stakes decisions, ambiguous problems, verification.

---

## ReAct (Reason + Act)

Interleave reasoning with tool use or action steps.

```
Thought: I need to find the stock price of AAPL.
Action: search("AAPL stock price")
Observation: AAPL is at $178.72
Thought: P/E ratio = 178.72 / 6.42 = 27.8
Answer: The P/E ratio for AAPL is approximately 27.8.
```

**When to use:** Multi-step research, tool-using agents, troubleshooting.

---

## Tree of Thought (ToT)

Explore multiple branches of reasoning, evaluate them, and select the best.

```
Problem: Design a database schema for a social media app.

Branch A (relational): Strong consistency, complex joins, proven at scale.
Branch B (document): Flexible schema, fast reads, eventual consistency.
Branch C (hybrid): Best of both, more operational complexity.

Selected: Branch C -- social apps are read-heavy with some
consistency requirements (auth, payments) best served by relational.
```

**When to use:** Architecture decisions, complex problem-solving, design exploration.

---

## Decomposition

Break complex tasks into smaller, manageable subtasks.

```
Task: Build a user registration system.

Subtasks:
1. Design API contract (request/response schemas)
2. Implement input validation
3. Add password hashing
4. Create database write logic
5. Handle duplicate email detection
6. Write integration tests

For each: implementation plan, key decisions, dependencies.
```

**When to use:** Large tasks, project planning, complex implementations.

---

## Pattern Selection Guide

| Task | Best Pattern(s) |
|---|---|
| Classification | Few-shot, structured output |
| Math / Logic | CoT, self-consistency |
| Code generation | System prompt framing, decomposition |
| Research / Analysis | ReAct, ToT |
| Creative writing | Few-shot (style examples) |
| Debugging | CoT, ReAct |
| Architecture decisions | ToT, decomposition |
| Automated pipelines | Structured output |
| Complex projects | Decomposition, meta-prompting |
