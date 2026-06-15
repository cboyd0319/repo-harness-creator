# Clean State Checklist

Use this before ending a non-trivial session.

## Required Checks

- [ ] Startup path still works, or the breakage is recorded with risk.
- [ ] Verification path ran, or the skipped command and reason are recorded.
- [ ] `feature_list.json` reflects actual feature state when feature status or
  major durable product evidence changed. No item is `passing` without
  evidence.
- [ ] `current-state.md` records the current objective, verified state,
  blockers, touched surfaces, and next step when those facts materially
  changed.
- [ ] `docs/harness/evidence/evidence-log.md` records meaningful verification
  evidence when it must be preserved. Do not log every focused test rerun.
- [ ] No temporary debug files, stale generated reports, or undocumented partial
  work are left behind.

## Next Session

The next session should be able to read `AGENTS.md`, `feature_list.json`, and
`current-state.md`, then continue without reconstructing state from chat
history.
