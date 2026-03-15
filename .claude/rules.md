# Workflow Rules

- **Confirm before push/PR:** When autonomously implementing work, always pause before `git push` or `gh pr create`. Show a summary of commits and changed files, then wait for explicit confirmation. Not required when the user explicitly invokes `/pr`.

- **UI changes require local review before commit:** Any change to `ui/` must be run locally (`cd ui && npm start`) and reviewed by the user before staging, committing, or pushing. After making UI changes, stop and ask the user to test locally and confirm they approve before proceeding.
