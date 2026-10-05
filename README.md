# Save Kew Riverside deployment

## Forwarding to the Primary School domain

Ordinary HTML on `savekewriverside.org` forwards in the browser directly to the
matching `savekewriversideprimaryschool.org` page, preserving query and fragment.
The workflow first performs all existing exact-source and public-asset checks,
then checks out the manifest's exact tested source commit and runs its reviewed
legacy artifact transformer. Only that generated public directory is uploaded.
`public/` remains the exact promoted source output and must not be hand-edited.

Browser replace navigation preserves Back. Saved-letter and pending-return
recovery stays at the old origin, retaining its original Formspree endpoint.
No-script/manual fallback, downloads, JSON boards and the school visit handoff
remain available. Forwarding/recovery pages omit analytics initialization.
This is a browser redirect, not an HTTP 301; no DNS change is required.


This repository serves `savekewriverside.org`. The authoritative source is
[ystoneman/kew-riverside-website](https://github.com/ystoneman/kew-riverside-website).
Edit and test the website there. This repository contains a promoted copy of its
public assets; it is not a second place to edit website content.

The original repository continues to serve
`https://ystoneman.github.io/kew-riverside-website/`. After the user-authorized
30 September cutover, ordinary HTML forwards in the browser to the matching
new-domain page. Complete manual/no-script fallback, old-origin Letters/Sent
recovery, public downloads/JSON and the school visit handoff remain available.
**Never attach the new custom
domain to the original repository.** Only this deployment repository may have
`savekewriverside.org` configured in its Pages settings.

## Contents and deployment gate

- `public/`: exact files produced by the source repository's public allowlist
  validator. This is the only directory uploaded to GitHub Pages.
- `promotion.json`: source repository, full commit, included base-main commit,
  candidate branch, workflow event/run,
  passing check names, validator digest, and every public file's SHA256 digest.
  This metadata remains outside the published directory.
- `scripts/`: promotion and verification tools, using Python's standard library.

An empty scaffold cannot deploy. The workflow fails unless a populated manifest
matches the complete public file set and all asset digests. It rechecks the source
workflow through GitHub's public read API: validation and all five browser
projects must have passed for the recorded commit. It then fetches that exact
source commit read-only, reruns its allowlist validator, and compares the freshly
staged asset digests and validator digest with the promoted files. Editing both
an asset and its local manifest therefore cannot substitute untested bytes.
Pages deployment uses this
repository's own short-lived GitHub Actions token and OIDC permissions. There is
no cross-repository write token or credential to maintain.

## Promote a tested source release

1. Update `codex/new-domain-candidate` from current authoritative `main`, preserving
   the candidate's new-domain form endpoint, analytics host gate and URLs. Record
   the full `main` SHA included in the candidate. During the overlap, `main`
   retains the original site's configuration and **cannot be promoted directly**.
2. Complete the source repository's required reviews and run
   `.github/workflows/pages.yml` with `workflow_dispatch` on the candidate branch.
   Validation and all browser projects must succeed; its `deploy` job must be
   skipped so the old website is not published from this branch. Get the exact
   candidate SHA and successful run ID from GitHub Actions. Local results alone
   are insufficient.
3. Use a separate, clean source checkout at exactly that candidate SHA. Keep private intake
   and unrelated work outside it. Do not discard changes from another checkout.
4. From this repository, run:

   ```sh
   python3 scripts/promote.py --source /absolute/path/to/clean/source-checkout \
     --commit FULL_CANDIDATE_SHA --base-main FULL_INCLUDED_MAIN_SHA \
     --run-id SUCCESSFUL_CANDIDATE_RUN_ID
   python3 scripts/verify.py --check-source-run
   ```

   Promotion and CI reject a stale base-main SHA. They also verify through GitHub
   that this base is actually an ancestor of the tested candidate. If main
   advanced during preparation, update and retest the candidate first.
5. Review the diff. Stage `public/` and `promotion.json` together by name and
   inspect the staged diff before committing. Run the deployment guard tests:

   ```sh
   python3 -m unittest discover -s scripts -p 'test_*.py' -v
   git add public promotion.json
   git diff --cached --check
   git diff --cached --stat
   ```

6. Open a pull request here, wait for the verification workflow, then merge.
   The `main` workflow uploads only `public/` and deploys to this repository's
   GitHub Pages environment. A successful deployment still needs live checks.

Promotion runs the original committed `check_site.py --stage` command. That
validator selects the public files and rejects private data/unexpected files.
The source checkout must stay clean and at the same SHA throughout promotion.
Never hand-copy the entire source tree or manually edit a promoted asset.
If a recorded source workflow is rerun, promote its completed successful attempt
again so the manifest evidence matches. Public API errors fail verification;
retry after restoring API access rather than weakening the gate.

## Domain activation and verification

Configure GitHub Pages with Actions as its source in this deployment repository.
Set the custom domain here, provision a valid HTTPS certificate, and enable
Enforce HTTPS. Keep the original site's URL working throughout.

Before directing visitors to the new address, check HTTPS, styles and scripts,
mobile navigation, key journeys, local links and downloads, form provider domain
settings, and analytics consent on the actual custom domain. Do not submit real
test forms or analytics events. Provider configuration and browser verification
are release gates outside this byte-verification workflow.

Do not enable a redirect from the original site until the new address has passed
those checks and the user has approved the cutover. A custom domain on the
original repository would immediately redirect it and is not part of this design.

## Source-to-two-sites synchronization and recovery

The person publishing a source update owns completion of both site releases.
After every original-site publication, update the new-domain candidate from
that published main revision, preserve and review the target-specific settings,
run its checks, and promote it here. Record the included main SHA and verify both
public sites before marking the release complete. Track any temporary mismatch
in the release notes with an owner and next action. Prioritize corrections,
withdrawn material and privacy/removal requests; do not leave removed material
available on the second site while waiting for a routine content release.

The original repository retains the complete source and public recovery pages.
If the canonical new site fails after forwarding is live, restore the original
artifact's ordinary allowlist upload through a reviewed current-main workflow
change (omit the legacy transform). Run its required checks and verify the old
URL before calling recovery complete. Do not move or reset either custom-domain
setting. Prepare any new-domain recovery candidate from current main, preserving
current corrections and privacy removals, and rerun checks before promoting.
There is deliberately no stale-source bypass: blindly reverting an old promoted
commit could restore material that has since been removed.

For each later source release, repeat the candidate and promotion process above.
This manual sync is intentional: a source commit does not silently change the
custom-domain deployment. Record and verify any provider or
URL changes during the release; asset digests alone do not prove them correct.
