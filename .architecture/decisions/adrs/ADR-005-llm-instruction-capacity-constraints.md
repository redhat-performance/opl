# ADR-005: LLM Instruction Capacity Constraints

## Status

Accepted

## Context

Through analysis of HumanLayer's research-backed article "Writing a Good CLAUDE.md" (December 2024), we discovered critical limitations in LLM instruction-following capacity that directly impact the effectiveness of our framework's AI assistant documentation.

**Key Research Findings:**
- Frontier LLMs reliably follow approximately 150-200 discrete instructions
- Claude Code's system prompt already contains ~50 instructions
- This leaves only 100-150 instructions for project-specific guidance
- LLM performance degrades when instruction density exceeds optimal capacity

**Current State:**
- Our CLAUDE.md file contains 572 lines of documentation
- Estimated ~100 discrete instructions in current CLAUDE.md
- At or exceeding optimal instruction capacity
- Includes significant content that is rarely relevant (setup procedures, update procedures)
- No awareness of or accounting for instruction capacity constraints

**Problem Statement:**
Without understanding and respecting LLM instruction capacity constraints, we risk:
1. Degraded AI assistant performance due to cognitive overload
2. Important instructions being ignored or deprioritized
3. Inefficient use of our limited instruction budget
4. Documentation that actively harms rather than helps AI assistant effectiveness

**Claude Code Behavior:**
Claude Code injects a system reminder stating context "may or may not be relevant to tasks" and actively filters out non-universally-applicable instructions. This explains why task-specific procedures (like setup instructions) may not be reliably followed even when present in CLAUDE.md.

## Decision Drivers

* **Performance Impact**: Exceeding instruction capacity degrades AI assistant effectiveness across all workflows
* **Research-Backed**: HumanLayer findings supported by empirical evidence and industry consensus
* **Framework Scope**: As a framework for AI-assisted architecture, we must model best practices
* **User Experience**: Poor instruction density directly impacts user's experience with framework
* **Maintenance Burden**: Understanding constraints enables better documentation decisions
* **Competitive Advantage**: Optimized AI assistant onboarding differentiates our framework

## Decision

We formally recognize and adopt LLM instruction capacity constraints as a foundational principle for all AI assistant documentation in the AI Software Architect framework.

**Core Principle:**
All documentation intended for AI assistant consumption (CLAUDE.md, AGENTS.md, .architecture/agent_docs/) must respect the ~150-200 instruction capacity limit, accounting for the ~50 instructions already used by Claude Code's system prompt.

**Specific Constraints:**
1. **CLAUDE.md Target**: < 30 discrete instructions (budget for 100-line file)
2. **Total AI Documentation**: < 100 instructions across all files loaded in a single context
3. **Instruction Definition**: A discrete instruction is any directive that requires the AI to take action, make a decision, or follow a specific procedure
4. **Universal Applicability**: Only instructions that are relevant to ≥80% of interactions should be in CLAUDE.md

**Architectural Components Affected:**
* CLAUDE.md (primary impact)
* AGENTS.md (secondary review needed)
* Future .architecture/agent_docs/ structure (guided by this constraint)
* Documentation templates and guidelines

**Interface Changes:**
* No code interface changes
* Documentation structure changes (see ADR-006 for implementation)
* Quality standards for documentation contributions

## Consequences

### Positive

* **Improved AI Performance**: Staying within instruction capacity ensures reliable instruction following
* **Better Prioritization**: Forces us to identify truly essential vs. nice-to-have documentation
* **Clearer Documentation**: Constraint drives clarity and conciseness
* **Measurable Quality**: Provides quantitative metric for documentation quality
* **Future-Proof**: Principle applies to all current and future LLMs
* **Competitive Advantage**: Optimized AI assistant effectiveness differentiates our framework
* **Educational Value**: Users learn best practices they can apply to their own projects

### Negative

* **Content Limitations**: Cannot include everything we might want in CLAUDE.md
* **Harder Documentation**: Writing concise, high-value content requires more effort
* **Measurement Overhead**: Need to count and evaluate instructions
* **Potential User Confusion**: Users might expect comprehensive documentation in one place
* **Migration Effort**: Existing documentation must be refactored

### Neutral

* **Different Structure Required**: Drives need for progressive disclosure pattern (ADR-006)
* **Documentation Becomes Multi-File**: Single CLAUDE.md splits into main file + supporting docs
* **Ongoing Maintenance**: Requires periodic review of instruction counts
* **Documentation Process Changes**: Review processes must include instruction counting

## Implementation

**Phase 1: Establish Measurement Standards (Immediate)**
* Define what constitutes a "discrete instruction"
* Create instruction counting methodology
* Document examples of instruction types
* Add instruction count targets to documentation guidelines

**Phase 2: Audit Current Documentation (Week 1)**
* Count instructions in current CLAUDE.md
* Categorize by: always-relevant, frequently-relevant, rarely-relevant, task-specific
* Identify which instructions are most critical
* Identify which instructions have low ROI given their instruction cost

**Phase 3: Refactor to Meet Constraints (Week 1-2)**
* Implement progressive disclosure pattern (ADR-006)
* Reduce CLAUDE.md to < 30 instructions
* Move task-specific content to .architecture/agent_docs/
* Validate instruction counts in refactored structure

**Phase 4: Establish Ongoing Governance (Week 2+)**
* Add instruction count checks to documentation review process
* Create quarterly review process for instruction relevance
* Monitor user feedback on documentation effectiveness
* Iterate based on real-world usage patterns

## Alternatives Considered

### Alternative 1: Ignore Instruction Capacity Constraints

**Description:** Continue with current approach, assuming LLMs can handle arbitrary instruction density.

**Pros:**
* No changes required
* Can include comprehensive documentation in one place
* Simpler mental model for users

**Cons:**
* Ignores research findings
* Degraded AI assistant performance
* Framework fails to model best practices
* User experience suffers
* Competitive disadvantage

**Decision:** Rejected. The research is clear and the performance impact is real.

### Alternative 2: Rely Purely on Task Tool Context Loading

**Description:** Minimal CLAUDE.md, rely entirely on Claude Code's Task tool to load relevant context when needed.

**Pros:**
* Extreme clarity on what's always-loaded
* Maximum instruction capacity available for task-specific context
* Forces modular documentation

**Cons:**
* Extra step for every task (launching Task tool)
* Potential performance overhead
* Less immediate access to common workflows
* May frustrate users with repeated context loading

**Decision:** Rejected as too extreme. Balanced approach with ~30 instructions in CLAUDE.md and progressive disclosure is more user-friendly.

### Alternative 3: Separate CLAUDE.md Per Workflow

**Description:** Multiple CLAUDE-*.md files (CLAUDE-setup.md, CLAUDE-review.md, etc.), user activates relevant one.

**Pros:**
* Clear separation of concerns
* Each workflow gets full instruction budget
* Easy to add new workflows

**Cons:**
* Requires manual activation
* User confusion about which file to use
* Doesn't align with how Claude Code loads context
* More complex mental model

**Decision:** Rejected. Doesn't align with Claude Code's context loading behavior. Progressive disclosure (ADR-006) achieves similar benefits more naturally.

## Pragmatic Enforcer Analysis

**Reviewer**: Pragmatic Enforcer
**Mode**: Balanced

**Overall Decision Complexity Assessment**:
This decision addresses a current, concrete problem (AI assistant performance degradation) with research-backed evidence. It adds no implementation complexity but rather constrains documentation to be simpler. This is an appropriate application of external research to improve system effectiveness.

**Decision Challenge**:

**Proposed Decision**: "Formally recognize and adopt LLM instruction capacity constraints (~150-200 instructions) as a foundational principle for all AI assistant documentation"

**Necessity Assessment**: 8/10
- **Current need**: We currently exceed optimal instruction density (572 lines, ~100 instructions)
- **Future need**: Will remain critical as framework grows and users add content
- **Cost of waiting**: Continued degraded AI assistant performance, poor user experience
- **Evidence of need**: Research-backed findings, industry consensus, explains current issues

**Complexity Assessment**: 2/10
- **Added complexity**: Minimal - adds a constraint, doesn't add features
- **Maintenance burden**: Low - periodic counting and review
- **Learning curve**: Low - straightforward principle to understand
- **Dependencies introduced**: None - constrains existing practices

**Alternative Analysis**:
The alternatives were adequately considered:
- "Do nothing" (Alternative 1) properly rejected based on evidence
- "Extreme minimal" (Alternative 2) appropriately rejected as over-optimization
- "Multiple files" (Alternative 3) appropriately rejected for UX concerns

The selected approach is the middle ground: establish the principle and apply it reasonably.

**Simpler Alternative Proposal**:
The selected approach IS the simpler alternative. Alternative approaches were either:
- Ignoring the problem (simpler but wrong)
- Over-engineering the solution (more complex)

This decision adds a constraint that drives simplicity rather than adding complexity.

**Recommendation**: ✅ Approve decision

**Justification**:
This decision is exemplary pragmatic engineering:
1. **Evidence-based**: Grounded in research, not speculation
2. **Addresses current problem**: We exceed instruction capacity now
3. **Drives simplicity**: Constraint forces clearer, more concise documentation
4. **Low complexity cost**: No implementation complexity, only documentation discipline
5. **High value**: Directly improves AI assistant effectiveness (core framework value)

This is exactly the kind of decision pragmatic mode supports: solving a real, current problem with a simple constraint that improves quality.

**Pragmatic Score**:
- **Necessity**: 8/10
- **Complexity**: 2/10
- **Ratio**: 0.25 (Well under target of <1.5)

**Overall Assessment**:
This represents appropriate engineering for a current need. The constraint drives simplicity and quality without adding system complexity. Strong approval from pragmatic perspective.

## Validation

**Acceptance Criteria:**
- [x] Research findings documented
- [x] Instruction capacity limits defined
- [x] Impact on current documentation assessed
- [x] CLAUDE.md refactored to meet constraints (572 → 126 lines, ~14 instructions)
- [x] .architecture/agent_docs/ structure implemented (workflows.md, reference.md, README.md)
- [x] Instruction counting methodology defined (instruction-counting-methodology.md)
- [x] Documentation guidelines updated (documentation-guidelines.md)
- [x] Quarterly review process established (quarterly-review-process.md)

**Testing Approach:**
* Manual instruction counting in CLAUDE.md
* User feedback on AI assistant effectiveness before/after refactoring
* Monitor task completion rates and user satisfaction
* A/B testing if feasible (users with old vs. new documentation structure)
* Track documentation maintenance burden over time

**Success Metrics:**
* CLAUDE.md instruction count: < 30
* CLAUDE.md line count: < 100
* User-reported AI assistant effectiveness: > 8/10
* Documentation relevance: > 80% of content used in > 80% of sessions

## References

* [HumanLayer Blog - Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
* [Architecture Review: CLAUDE.md Best Practices](./../reviews/claude-md-best-practices-humanlayer-article.md)
* [ADR-006: Progressive Disclosure Pattern](./ADR-006-progressive-disclosure-pattern.md)
* Research on LLM instruction-following capacity (referenced in HumanLayer article)
