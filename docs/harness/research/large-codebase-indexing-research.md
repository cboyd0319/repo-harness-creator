# Large Codebase Analysis And Indexing Research

Reviewed: 2026-06-15 UTC.

Status: repo-local research.

Implementation note: the first standard-library structural index slice is
implemented as `harnessforge index --target . --json`. Large repos can raise
the file scan limit with `--max-files`; bounded component inventories now
report truncation instead of silently hiding omitted boundaries.

This note responds to the current product risk: HarnessForge must understand
large existing repositories much better before it can generate or improve a
high-quality harness for them.

## Conclusion

No single open source indexer should become a default HarnessForge dependency.
The better shape is a tiered, local, target-contained indexing strategy:

1. Always build a cheap structural repo index with the Python standard library.
2. Detect optional project-owned or installed index artifacts when present.
3. Offer adapters for heavier symbol, code-search, and code-intelligence tools
   only when explicitly enabled.
4. Generate compact, cited repo maps for harness design, not private code
   summaries or embeddings.
5. Record confidence, source path, freshness, ignored/generated/vendor status,
   and unknowns for every inferred component boundary.

The first product slice is a read-only `harnessforge index --target . --json`
command that emits a deterministic structural index. It does not run language
servers, build systems, networked search services, or embedding models by
default.

## Source Review

| Source | What It Does Well | Limit For HarnessForge | Useful Pattern |
| --- | --- | --- | --- |
| Sourcegraph Zoekt | Fast trigram code search and local command-based indexing. It recommends ctags as a symbol-ranking signal. | Search is not repo understanding by itself. It needs an external Go tool and an index lifecycle. | Optional text index adapter; fast local search over huge trees. |
| Sourcebot | Self-hosted code search and navigation aimed at humans and agents, with cited answers over code search/navigation. | Service deployment, auth, and multi-repo sync are too heavy for default generation. | Agent-facing answers should cite exact files and snippets. |
| Livegrep and Hound | Fast regex/trigram search over large source repositories. | Mostly text search, not semantic harness design. Requires a running service for normal use. | Simple search indexes are valuable but should be optional. |
| OpenGrok | Source search plus cross-reference navigation over source trees and VCS history. | Java service and index management are too heavy for default target repos. | Cross-reference navigation matters for large legacy codebases. |
| Universal Ctags | Widely adopted symbol/tag index for many languages. | Tag output is shallow and language support varies. Requires external installation. | Optional symbol extractor and ranking signal. |
| Tree-sitter | Incremental parsing and concrete syntax trees for many languages. | ASTs alone do not resolve cross-file meaning or build semantics. Python bindings and grammars would add dependencies. | Best candidate for optional structural parsing and repo-map extraction. |
| ast-grep | Tree-sitter based structural search, lint, and rewrite. | Good for patterns, not a full repository model. External binary/dependency. | Optional structural-query adapter for finding framework and architecture signals. |
| Aider repo map | Uses tree-sitter definitions/references to build compact codebase maps for AI context. | AI context selection is task-dependent and not the same as harness generation. | Rank important symbols and emit small cited repo maps instead of broad summaries. |
| SCIP and LSIF | Language-agnostic code intelligence index formats for definitions and references. SCIP supersedes LSIF in current Sourcegraph docs. | Good indexes depend on language-specific generators and build setup. | Detect or import existing code-intelligence artifacts when present. |
| Kythe | Language-agnostic graph of source facts and cross-references, often build-instrumented. | Build instrumentation is too heavy and language support varies by project. | Build-aware facts are higher confidence than text-only inference. |
| Glean | Fact database for source code with symbols, relationships, calls, hierarchies, and flexible queries. | Heavy service and schema ecosystem, not defaultable in arbitrary repos. | Store normalized source facts separately from generated prose. |
| CodeQL | Query code as data for semantic security analysis. | Not a default open source dependency for HarnessForge and focused on security analysis. | Treat deep semantic databases as optional project-owned evidence. |
| Semgrep | Fast multi-language static analysis with rule-based semantic matching. | Rules find patterns, not full project architecture. Some ecosystem features are commercial. | Detect repo-owned Semgrep configs as review and verification signals. |

Primary source links:

- Sourcegraph Zoekt: https://github.com/sourcegraph/zoekt
- Sourcebot: https://github.com/sourcebot-dev/sourcebot
- Livegrep: https://github.com/livegrep/livegrep
- Hound: https://github.com/hound-search/hound
- OpenGrok: https://github.com/oracle/opengrok
- Universal Ctags: https://github.com/universal-ctags/ctags
- Tree-sitter: https://github.com/tree-sitter/tree-sitter
- ast-grep: https://github.com/ast-grep/ast-grep
- Aider repo map: https://aider.chat/2023/10/22/repomap.html
- SCIP: https://scip-code.org/
- Sourcegraph SCIP Java indexer: https://sourcegraph.github.io/scip-java/
- Sourcegraph SCIP Python indexer: https://github.com/sourcegraph/scip-python
- Microsoft LSIF specification: https://microsoft.github.io/language-server-protocol/specifications/lsif/0.4.0/specification/
- Kythe: https://kythe.io/
- Kythe generated-code indexing: https://kythe.io/docs/schema/indexing-generated-code.html
- Glean: https://github.com/facebookincubator/Glean
- Meta Glean article: https://engineering.fb.com/2024/12/19/developer-tools/glean-open-source-code-indexing/
- GitHub Stack Graphs: https://github.com/github/stack-graphs
- GitHub Stack Graphs article: https://github.blog/open-source/introducing-stack-graphs/
- CodeQL: https://codeql.github.com/
- Semgrep: https://github.com/semgrep/semgrep

## Product Direction

### Phase 1: Built-In Structural Index

Implemented a read-only `harnessforge index --target . --json` command with no
new runtime dependencies. Use `--max-files <N>` for deeper scans of large
repositories. It reports:

- repo size, file count, ignored/generated/vendor/test/doc/source splits;
- detected components and confidence;
- detected source-of-truth docs, instruction files, and workflow surfaces;
- package/build/test manifests and their owning directories;
- likely generated code and vendored code;
- language distribution by file count and byte size;
- high-signal entrypoints, scripts, local actions, and CI path filters;
- missing or ambiguous boundaries that require project review.
- file-scan and component-inventory truncation limits.

The output should be a portable JSON report. It must not include local absolute
paths, secrets, private code excerpts, embeddings, or large raw file lists by
default.

### Phase 2: Optional Repo Map

Generate a compact repo map from the structural index:

- component name;
- purpose inferred from manifests and file names;
- owner/source-of-truth clues;
- verification commands;
- confidence and unknowns;
- exact target-relative source paths.

This should feed generated instructions and `--enhance-existing` addenda. It
should stay cited and compact so it improves harness quality without turning
instruction files into code summaries.

### Phase 3: Optional External Adapters

Add opt-in adapters only after Phase 1 is stable:

- ctags adapter for symbols;
- tree-sitter or ast-grep adapter for structural patterns;
- SCIP/LSIF/Kythe/Glean import when the repo already has those artifacts;
- code-search adapter for Zoekt, Sourcebot, Livegrep, Hound, or OpenGrok only
  when the user provides an existing local index or endpoint.

Adapters should report availability, version, command, input paths, output
paths, duration, and risk. They should not be required for normal `init`.

## Index Contract

Any future HarnessForge index should be:

- read-only by default;
- deterministic from the same repo state and options;
- target-contained when persisted;
- safe to delete;
- freshness tracked by file hash, manifest hash, or git commit;
- explicit about ignored, generated, vendored, and fixture code;
- explicit about confidence and unknowns;
- portable across macOS, Windows, and Linux;
- usable without network access.

## Rejected Defaults

- No networked indexing service by default.
- No committed embeddings or private code summaries.
- No mandatory language-server startup during `init`, `inspect`, `audit`, or
  `sync --check`.
- No automatic benchmark or semantic score claims from an index.
- No generated harness text that includes large code excerpts.
- No machine-local absolute paths in index reports or generated files.

## Open Questions

- Should the first index command be `harnessforge index` or folded into
  `harnessforge inspect --index`?
- Should a persisted index live under `.harnessforge/` and be ignored by
  default, or should HarnessForge only write explicit `--json-report` files?
- How should the index handle huge monorepos where a full file walk is cheap
  but language-specific parsing is expensive?
- Which confidence model is useful enough without pretending to be exact?
