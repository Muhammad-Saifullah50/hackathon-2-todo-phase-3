---
id: "0002"
title: "auth-clarification-session"
date: 2025-12-19
stage: spec
feature: "004-user-auth-better-auth"
context: feature
---

# PROMPT

$PROMPT_TEXT

# RESPONSE

I conducted a clarification session to resolve ambiguities in the User Authentication specification. 
Five key questions were addressed:
1. **JWT Expiration**: Set to 7 days.
2. **JWT Claims**: Explicit `iss` ("todo-auth") and `aud` ("todo-api") claims defined and validated.
3. **Frontend Token Attachment**: Use an Axios request interceptor in `lib/api.ts`.
4. **Missing Secret Behavior**: Application will fail immediately with a clear error message.
5. **Display Name Uniqueness**: Duplicates allowed; email remains the unique identifier.

The specification was incrementally updated with these decisions in the `Clarifications`, `Functional Requirements`, and `Key Entities` sections.