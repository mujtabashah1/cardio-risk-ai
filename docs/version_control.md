# Version-control workflow

Target: https://github.com/mujtabashah1/cardio-risk-ai, branch main. The project had no .git directory or ancestor history when inspected on 2026-10-04. A new main repository was initialized after the website passed automated and actual Chrome verification. No existing history was removed or rewritten.

Git 2.56.0.windows.1 and GitHub CLI 2.102.0 were installed as workspace-local tools from official GitHub release ZIPs. Their downloads matched the published SHA-256 asset digests. They live outside the project, in ../.runtime/, and are not part of the repository. Standard Git/GitHub CLI installations may be used instead.

The frozen 182,048-byte model is small enough for ordinary Git. Its hash is unchanged. Training source, API, frontend, tests, scripts, dictionary, metadata and reviewed aggregate/synthetic reports are staged. Respondent-level raw/clean/split files, source IDs, review records, model candidates, arrays/caches and credentials are ignored. Manual QA notes/exports stay local to prevent later personal notes from being accidentally pushed.

Before every push:

```powershell
git status --short
python scripts/review_git_privacy.py
git diff --cached --stat
```

Run relevant automated tests and browser checks before staging. The privacy utility reviews staged blobs and prints file/line locations rather than credential values. Keyword references in validation/security tests must be reviewed separately; a keyword match alone is not evidence of a live credential. Do not push if a real credential or respondent record is found. Check any existing remote history before the first push; never force-push.

Authentication was initially absent. Starting browser login was blocked by automatic approval review because the account/login authority was supplied in an attachment. Explicit chat authorization is pending. No login, repository creation or push has succeeded at this point. Once authorized, authenticate using `gh auth login --hostname github.com --git-protocol https --web` as mujtabashah1. Never supply a GitHub password to the agent. The authenticated remote and account must be verified before pushing; repository creation, if required, should default to private visibility.

This development milestone creates no v1.0.0 release tag and does not publish or deploy the local website. Current status and commit are reported at completion.
