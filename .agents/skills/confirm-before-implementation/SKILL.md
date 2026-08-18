---
name: confirm-before-implementation
description: Enforces confirming with the user before writing or modifying code when asked questions, suggestions, ideas, or recommendations.
---

# Confirm Before Implementation Skill

## Overview
This skill strictly regulates code modifications when responding to user questions, requests for advice, code reviews, suggestions, or conceptual discussions.

## Core Rule
**DO NOT make code modifications immediately when answering questions or providing suggestions.**
Always present your analysis, explanation, proposal, or recommended plan first, and ask for explicit user confirmation before writing or editing files.

## Workflow Instructions

### 1. Analyze and Explain (No File Editing)
When the user asks a question, requests a suggestion, or proposes a feature/change without explicitly instructing you to apply the changes immediately:
- Conduct research or inspect relevant code files.
- Formulate your answer, recommendation, or proposed technical design.
- Explain what changes you plan to make and why.
- You may include code snippets or diffs in your markdown response to illustrate the proposed solution.

### 2. Request Explicit User Confirmation
At the end of your response, ask the user clearly:
> *"Would you like me to proceed with implementing these changes?"*

### 3. Implementation (Only After Approval)
- Do NOT call file editing tools (`write_to_file`, `replace_file_content`, `multi_replace_file_content`, etc.) to modify project source code until the user responds with explicit confirmation (e.g. "yes", "proceed", "go ahead", "approved", or similar).
- Exception: Creating or updating planning artifacts (`implementation_plan.md`) when planning is required is allowed.

## Triggers
This skill should activate whenever user prompts contain:
- Questions ("How do I...", "Why is...", "What is the best way to...")
- Requests for suggestions ("What do you suggest...", "Can you recommend...")
- Code review / Feedback requests ("How does this look?", "Any improvements?")
- Conceptual proposals where immediate implementation was not explicitly ordered.
