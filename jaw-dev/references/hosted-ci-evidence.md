# Hosted CI evidence (DEV-CI-EVIDENCE-01)

Zero failing checks is not proof that the expected tests ran. Before saying CI
passed, record the PR head, the checked SHA, workflow event, run ID, attempt,
and required jobs; then verify that each required job executed and concluded
successfully. Inspect an aggregate's dependencies, not only its headline.

Five failure shapes need different diagnoses:

1. Required jobs never started; a failure-filtered rollup can be empty when
   only lightweight checks ran. Investigate approval gates or workflow filters.
2. An aggregate failed because a dependency was cancelled or skipped although
   completed test legs passed. Missing completion evidence is not a test failure.
3. `gh run rerun --failed` exited zero but regenerated no missing jobs. Its
   exit records accepted request, not resulting coverage.
4. `gh run view --exit-status` exited zero while the run was pending or cancelled.
   Check status and conclusion separately.
5. A run at the same SHA came from another event, such as manual dispatch.
   Confirm the event and ref expected by the repository's required checks.

For GitHub repositories, use read-only queries before any rerun or approval:

```sh
gh pr view <PR> -R <REPO> --json headRefOid,statusCheckRollup
gh api --paginate 'repos/<REPO>/commits/<HEAD_SHA>/check-runs?per_page=100'
gh run list -R <REPO> --commit <HEAD_SHA> --json databaseId,event,headSha,status,conclusion,workflowName
gh run view <RUN> -R <REPO> --json event,headSha,attempt,status,conclusion,jobs
```

Compare returned jobs with the workflow's expected graph and correlate merge-ref
checks if applicable. An empty check-run list does not establish the reason.
Distinguish absent, approval-blocked, skipped, cancelled, pending, and failed.
Rerun acceptance is not success; a full rerun is justified only after inspection
shows a partial rerun cannot restore the missing evidence.

If a completed job's log is unavailable through `gh run view --job <JOB> --log`
while its parent workflow is still running, inspect that job directly:

```sh
gh api 'repos/<REPO>/actions/jobs/<JOB>' --jq '{id,run_id,head_sha,status,conclusion}'
gh api 'repos/<REPO>/actions/jobs/<JOB>/logs'
```

Read command status, stderr, and returned content before calling logs unavailable.
If the raw response is rejected for escape sequences, some CLI versions support
`--allow-escape-sequences`; verify installed help first. It relaxes terminal
protection, so read the result through a non-executing text reader. Retain run,
attempt, and job IDs across reruns; older logs may have expired.
