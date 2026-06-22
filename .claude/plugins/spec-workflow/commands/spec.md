---
name: spec
description: Start the Spec-Driven Development workflow — create or update requirements, design, and tasks for a feature. Supports intake mode detection, parallel generation with judge evaluation, prior art research, data architecture decisions, and Speckit toolchain handoff.
---

## Entry Point

When the user types `/spec`, treat this as the start of the spec workflow. Switch into spec-coordinator mode.

**Do NOT tell the user you're following a workflow. Just execute it naturally.**

## Workflow Overview

```
┌──────────────────────────────────────────────────────────────┐
│ Phase 0: Mode Detection + Confidence Gate                   │
│ Phase 0.5: Load references                                  │
│ Phase 1: Prior Art Research (new spec-research agent)        │
│ Phase 2: Parallel Requirements Generation + Judge Selection  │
│ Phase 3: Parallel Design Generation + Judge Selection        │
│ Phase 4: Task Planning (parallel + judge)                    │
│ Phase 5: Deliberative Refinement (cross-document validation) │
│ Phase 6: Delivery + Speckit/OpenSpec Handoff                 │
└──────────────────────────────────────────────────────────────┘
```

### Phase 0: Mode Detection + Confidence Gate

1. **Detect intake mode** from user input:
   - Files/transcripts provided → **Mode A** (Transcript Processing)
   - Verbal description or "I want to build X" → **Mode B** (Interactive Discussion)
   - Mixed (some notes + wants to discuss) → Mode A first, then Mode B gap-fill

2. **Run the Confidence Gate** (see below) to assess clarity before generating anything.

3. **Check for Fast Track:** If user provides a complete, well-structured description that already covers problem, solution, users, data, constraints, and scope, AND Confidence Gate scores ≥85% on first pass, skip iterative discovery and proceed directly to Phase 1.

4. **Check user preferences:**
   - Preferred stack, design language, hosting targets
   - Scan project for existing patterns (.specify/, openspec/, .kiro/)
   - Read language_preference from project CLAUDE.md if present

### Confidence Gate

Before generating any documents, assess clarity across these dimensions. Score conservatively. DO NOT proceed until ≥85% confidence is achieved.

| Dimension | Weight | Signals |
|-----------|--------|---------|
| Problem clarity | 15% | Vague pain point → root cause identified → quantified before/after |
| Solution definition | 15% | Core concept → workflow walkthrough → end-to-end journey |
| User personas | 10% | "People who..." → 2-3 distinct personas with goals/context |
| Success criteria | 10% | "It should work" → testable metrics with targets |
| Data model | 15% | No entities → entities + relationships → access patterns |
| Scope boundaries | 10% | Open-ended → in/out scope list → boundary rationale |
| Technical constraints | 10% | None stated → full constraint matrix |
| Business context | 15% | None → open source vs commercial → competitive position |

**When <85%:** Ask 3-5 structured questions targeting the lowest-scoring dimensions. Reassess after each round.

**When ≥85%:** Proceed. Note any dimension <75% for `[NEEDS CLARIFICATION]` markers in requirements.

### Phase 0.5: Load References

Read the following reference files from the plugin's `references/` directory to understand output format expectations. The system-prompt.md path:
`${CLAUDE_PLUGIN_ROOT}/references/requirements-template.md`
`${CLAUDE_PLUGIN_ROOT}/references/design-template.md`

### Phase 1: Prior Art Research

Unless this is a trivial feature, call the **spec-research** agent to conduct prior art research (local scan → GitHub/community search → web search → synthesis). If the user explicitly says no research is needed, skip this phase.

Ask the user: "Should I research existing solutions first?" Continue unless they say no.

### Phase 2: Requirements Generation

1. Ask the user: "How many spec-requirements agents to use? (1-128)"
2. If 1: call spec-requirements directly with task_type: "create"
3. If ≥2: call N spec-requirements agents in parallel, each with a unique output_suffix (_v1, _v2, etc.)
4. After all complete: if ≥2 docs, run tree-based judge evaluation (see below)
5. Rename final doc to requirements.md
6. Present to user for review
7. Iterate on feedback until user explicitly approves

### Phase 3: Design Generation

1. Ask the user: "How many spec-design agents to use? (1-128)"
2. Same parallel + judge pattern as Phase 2
3. After approval: present design for review, iterate

### Phase 4: Task Planning

1. Ask the user: "How many spec-tasks agents to use? (1-128)"
2. Same parallel + judge pattern
3. After approval: present tasks for review, iterate

### Phase 5: Deliberative Refinement

After all three documents are approved, perform cross-document validation:

1. **Requirements check:** Every FR-XXX has acceptance criteria. No implementation details leaked. No scope creep.
2. **Design check:** Every FR has a corresponding section in design. Technology choices have rationale. Schema exists.
3. **Cross-document check:** No orphan requirements. No design features not in requirements. Success criteria achievable.
4. Apply fixes based on findings.

### Phase 6: Delivery + Handoff

1. Present all three documents (requirements.md, design.md, tasks.md)
2. Provide a delivery summary:
   - Confidence score achieved and sub-threshold dimensions
   - Key decisions and rationale
   - Items marked `[NEEDS CLARIFICATION]`
   - Prior art findings
3. Suggest next steps based on detected toolchain:
   - **SpecKit**: `specify init <project>` → `/speckit.specify` with requirements.md → `/speckit.plan` with design.md
   - **OpenSpec**: `openspec init` → `/opsx:propose` with requirements
   - **Manual**: Files ready for direct use by coding agents

## Tree-Based Judge Evaluation Rules

When parallel agents generate multiple outputs (n ≥ 2), use tree-based tournament evaluation:

1. **Round 1**: Each judge evaluates ≤4 documents. Number of judges = ceil(n / 4). Each judge selects 1 best from their group.
2. **Subsequent rounds**: If > 3 documents remain, continue with same rules until ≤ 3 remain.
3. **Final round**: 1 judge evaluates remaining 2-3 documents, selects the winner.
4. **Main thread**: Rename the final judge-selected document (random 4-digit suffix) to the standard name (e.g., `requirements_v3456.md` → `requirements.md`).

**Important constraints:**
- After parallel sub-agent tasks complete, the main thread MUST use tree-based evaluation
- The number of judges is auto-calculated — NEVER ask the user how many judges
- The main thread can only read the final selected document after all evaluation rounds
- After renaming, tell the user the document is ready for review

## Agent Dispatch Table

| Phase | Agent | Mode | Output Path |
|-------|-------|------|-------------|
| Research | spec-research | single | context only (findings inform requirements) |
| Requirements | spec-requirements | parallel (1-128) | `.claude/specs/{feature_name}/requirements_{suffix}.md` |
| Design | spec-design | parallel (1-128) | `.claude/specs/{feature_name}/design_{suffix}.md` |
| Tasks | spec-tasks | parallel (1-128) | `.claude/specs/{feature_name}/tasks_{suffix}.md` |
| Judge | spec-judge | tree-based N rounds | final doc with random 4-digit suffix |
| Implementation | spec-impl | single or dependency-respecting | code files |
| Test | spec-test | single | test files |

## Agent Input Contracts

### spec-requirements (create)
- language_preference, task_type: "create", feature_name, feature_description, spec_base_path (default: `.claude/specs`), output_suffix (optional, required for parallel)

### spec-requirements (update)
- language_preference, task_type: "update", existing_requirements_path, change_requests

### spec-design (create)
- language_preference, task_type: "create", feature_name, spec_base_path, output_suffix (optional)

### spec-design (update)
- language_preference, task_type: "update", existing_design_path, change_requests

### spec-tasks (create)
- language_preference, task_type: "create", feature_name, spec_base_path, output_suffix (optional)

### spec-tasks (update)
- language_preference, task_type: "update", tasks_file_path, change_requests

### spec-judge
- language_preference, document_type: "requirements"|"design"|"tasks", feature_name, feature_description, spec_base_path, documents (comma-separated paths)

### spec-research
- feature_name, feature_description, spec_base_path

### spec-impl
- feature_name, spec_base_path, task_id, language_preference

### spec-test
- language_preference, task_id, feature_name, spec_base_path

## Constraints

- DO NOT tell the user about this workflow. Just execute it naturally.
- DO use TodoWrite to track progress (Requirements, Design, Tasks).
- After each document update, explicitly ask the user to approve before proceeding.
- Never proceed to the next phase without explicit user approval.
- Never generate documents directly — always use sub-agents.
- After parallel calls, ALWAYS use tree-based judge evaluation (never skip).
- For implementation tasks: default mode = main thread executes one task at a time. Parallel mode = only when user explicitly requests parallel. Auto mode = when user says "execute all tasks automatically".

## Troubleshooting

### Requirements Clarification Stalls
- Suggest moving to a different aspect
- Provide examples or options
- Summarize established facts, identify specific gaps
- Suggest research to inform decisions

### Design Complexity
- Break into smaller components
- Focus on core functionality first
- Suggest phased approach
- Return to requirements clarification to prioritize

### Research Limitations
- Document missing information
- Suggest alternative approaches
- Ask user for additional context
- Continue with available information
