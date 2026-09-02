# Git Remote & Repository Safety Guardrail

## Activation
Always On

## Directives
1. **Explicit Remote & Target Confirmation**:
   - Before executing any `git push` (especially to `main` or `master`), verify `git remote -v`.
   - If the task involves a migration, architectural rewrite, or a new project spun off from an existing codebase, **always ask the user** whether changes belong to the original repository or if a new remote repository should be created/targeted.
2. **No Autonomous Push to Upstream**:
   - Never push code to upstream or production branches without explicit user confirmation of the target URL and branch.
3. **Rollback & Remote Switching Support**:
   - When asked to fork, duplicate, or switch repositories, immediately update the remote (`git remote set-url origin <new-url>`) before making any push.
