# Workflow Rules

- **Confirm before push/PR:** When autonomously implementing work, always pause before `git push` or `gh pr create`. Show a summary of commits and changed files, then wait for explicit confirmation. Not required when the user explicitly invokes `/pr`.

- **UI changes require build check and visual review before commit:** Any change to `ui/` must be verified before staging, committing, or pushing:
  1. Run `cd ui && npm run build` to confirm there are no compilation errors.
  2. Start the dev server with `cd ui && npm start` (run in background) so the user can open the browser and review visually.
  3. Ask the user to confirm the UI looks correct before proceeding to commit.
