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

Authentication was initially absent. On 2026-10-04, the user requested a retry after signing in and explicitly approved the GitHub CLI OAuth permissions. Browser device authorization completed, and CLI account verification confirmed **mujtabashah1**, active HTTPS access, with credentials in the Windows keyring. No credential values are recorded here. The requested repository was absent; after explicit user approval it was created as **private**, with no pre-existing remote branch/history. Authenticated repository inspection confirmed the correct owner, name and visibility.

Later on 2026-10-04, the user explicitly requested making that existing repository public. GitHub CLI changed its visibility and authenticated inspection confirmed PUBLIC. The React milestone follows the same staged-blob privacy review and normal main-branch push workflow. Only source, the frozen model and reviewed documentation/aggregate/synthetic evidence are published.

This development milestone creates no v1.0.0 release tag and does not publish or deploy the local website. Current status and commit are reported at completion.

The local website milestone and follow-up clone safeguards are committed on **main**, using the owner handle and GitHub noreply address as repository-local commit identity (no private email was requested). Origin is configured to the requested URL. Working tree and staged privacy review were checked. A fresh local clone passed 68 Python tests with one optional local-data audit skipped, and preserved the frozen artifact/supporting integrity hashes. All 69 Python tests passed in the original workspace where the excluded local audit inputs exist. Push normally with `git push -u origin main`; never force push. Completion verification compares the local HEAD with remote main and inspects the remote tree for required source and prohibited respondent/credential files. The final commit SHA and push result are reported at completion.
