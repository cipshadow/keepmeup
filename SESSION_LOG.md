# keepmeup Session Log

### 2026-08-30 — Published as a public repo

**Goal:** Cip wanted keepmeup added to his portfolio site, which meant making the repo public first.

**What we did:**
- **Scanned all 8 commits before touching visibility.** No credentials, tokens, or keys anywhere — but the repo tracked 32 of Cip's personal `.claude/commands/*.md` files, swept in by an unrelated 2026-08-03 cross-repo sync. They name his private repos (`fin-advice`, `health`, `therapy`, `Eterauto`, `AEOnow`) and one describes scanning his email for passport/visa/financial documents. Cip chose to purge them from history rather than publish as-is.
- Rewrote history with `git filter-branch --index-filter` to remove all of `.claude/` (including `settings.json`, whose `SessionStart` hook auto-installs a plugin — not something to ship in a repo strangers clone), then deleted `refs/original`, expired the reflog, and gc'd. 8 commits → 5.
- **Force-pushing the rewrite was not sufficient.** After `git push --force`, the orphaned pre-rewrite commit was still fetchable from GitHub by SHA — verified live by fetching it and reading `email-scan.md` straight out of the remote. GitHub keeps unreferenced objects until it garbage-collects, which isn't user-triggerable. Deleted the repo and recreated it instead; confirmed the old SHA now returns `not our ref` on fetch and HTTP 422 via the API.
- While making the docs public-ready, found and fixed four real bugs, not just cosmetic cleanup:
  - `install.sh` was rewriting the tracked `com.local.keepmeup.plist` **in place** with `sed` — that's how an absolute `/Users/cip` path had ended up committed, and every future clone would go dirty on install. Replaced with a `__HOME__` placeholder expanded only into the LaunchAgent destination.
  - `setup_autostart.sh` copied the plist verbatim with no substitution — would have installed a broken LaunchAgent pointing at a placeholder path.
  - `verify.sh` checked for a repo-level `venv/` that no longer exists (the venv moved inside the `.app` bundle when it became self-contained) — it failed even on a correct install.
  - README's Quick Start said to `open KeepMeUp.app` directly, but the bundle is gitignored and only exists after `install.sh` builds it — never worked on a fresh clone.
- Rewrote README to a real clone-and-run flow, trimmed SETUP_GUIDE.md down to the verification checklist it uniquely offers (install/usage now live only in the README, not duplicated), added `LICENSE` (MIT).
- **Second history rewrite**, later in the session, per Cip's explicit ask: stripped the remaining `/Users/cip` occurrences (README, SETUP_GUIDE, the plist, the built launcher script) down to `~`, and deleted/recreated the repo again to actually clear the old objects — same lesson as above, applied a second time.

**Key decisions & trade-offs:**
- **Delete-and-recreate over any GitHub-support GC request**, both times history was rewritten. **Why:** immediate and independently verifiable (fetch the old SHA, expect failure) versus asking support to run GC on an unknown timeline — the repo had zero stars/forks/issues/releases, so nothing valuable was lost by starting the identity over.
- **MIT license, unprompted choice.** Cip asked for "a license" without naming one; matched fokuskeeper's existing choice for consistency across the portfolio rather than asking.

**Pending:**
- GitHub's license detector hadn't indexed the new `LICENSE` file yet as of publish time — cosmetic, resolves on its own.

**Files involved:**
- `README.md`, `SETUP_GUIDE.md` — rewritten for a public audience
- `install.sh`, `setup_autostart.sh`, `verify.sh` — path-handling bugs fixed
- `com.local.keepmeup.plist` — `__HOME__` placeholder
- `LICENSE` — new, MIT
- `.claude/` — removed entirely, from history as well as HEAD

**Learned:**
- **A tracked file a script edits in place is a liability the moment the repo might go public** — `install.sh`'s `sed -i` on the checked-in plist is what put a personal path into the commit history in the first place, days or weeks before anyone thought about publishing. Prefer a placeholder template plus an install-time substitution that writes to the *destination*, never back onto the tracked source.
- **Force-push does not remove anything from GitHub — confirmed twice this session, not once.** The only way to be sure orphaned objects are gone is delete-and-recreate, then verify the old SHA is unreachable both via `git fetch <sha>` and the REST API.

**How to continue:** Nothing blocking. The repo is public, clean, and linked from `cipblujdea.com`'s Projects folder as a "Mac app".
