# Evaluator Rubric

Use this after non-trivial agent work or before accepting a large change.

Score each category from 0 to 2.

| Category | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Correctness | Target behavior is missing or contradicted | Partially works with known gaps | Matches requested behavior |
| Verification | No relevant check ran | Some checks ran but coverage or evidence is incomplete | Required checks ran with evidence |
| Scope Discipline | Hidden assumptions, unrelated behavior, drive-by refactors, or style churn | Mostly scoped with minor drift | Stayed within the selected objective and surfaced assumptions |
| Reliability | Fails restart, repeat run, or common platform path | Works in one path with stated risk | Survives restart and expected platform paths |
| Maintainability | Over-abstracted, speculative, dependency-heavy, or hard to understand | Understandable but needs cleanup | Fits project patterns, avoids unnecessary abstractions, and reduces confusion |
| Handoff Readiness | Next session must infer state | Handoff exists but has gaps | State, blockers, files, and next step are clear |

For cross-component or user-visible changes, verification should include the
highest relevant evidence layer: static checks, runtime/startup checks, and
system or user-flow checks. A passing unit test alone is not enough when the
changed behavior depends on component interaction.

Scope and maintainability review should flag speculative features,
unrequested configurability, new dependencies, broad rewrites, or cleanup that
does not trace to the current objective. Intentional simplifications should
record the known ceiling and upgrade path.

## Verdict

- Accept: total score is 10 or higher and no category is 0.
- Revise: score is 7 to 9, or one category is 0 with a clear fix.
- Block: score is below 7, verification is absent, or correctness is unproven.

## Follow-Up

Record any rubric weakness here when human judgment and the rubric disagree.
Update this file before using the same evaluation again.

## Agent Review Signal

Agent-assisted review should prioritize high-signal defects: correctness,
security, race or data integrity, migration risk, scalability, test integrity,
and architectural fit. Avoid promoting style noise or speculative cleanup into
blocking feedback unless it changes maintainability or user-visible behavior.

## Benchmark And Effectiveness Claims

Do not present structural audit scores, smoke tests, or synthetic benchmarks as
proof of production agent effectiveness. Any benchmark or effectiveness claim
must record the task set or corpus, command, environment, input selection or
seed, scope limits, and known failure modes. Label smoke, synthetic, and
experimental results explicitly.
