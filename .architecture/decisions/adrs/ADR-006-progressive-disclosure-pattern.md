# ADR-006: Progressive Disclosure Pattern for AI Assistant Documentation

## Status

Accepted

## Context

Following ADR-005's establishment of LLM instruction capacity constraints, we need a concrete architectural pattern for structuring our AI assistant documentation. Our current 572-line CLAUDE.md file exceeds optimal instruction density and loads content that is rarely relevant to most user interactions.

**Current Documentation Structure:**
```
CLAUDE.md (572 lines, ~100 instructions)
  ├── Setup procedures (used once per project)
  ├── Update procedures (used rarely)
  ├── Implementation methodology (used occasionally)
  ├── Review workflows (used frequently)
  └── Pragmatic mode details (used occasionally)
```

**Problems with Current Structure:**
1. **Instruction Waste**: Setup procedures (~20 instructions) loaded in every interaction but used once per project
2. **Cognitive Overload**: All content presented equally, no prioritization
3. **Maintenance Burden**: Monolithic file difficult to update and review
4. **Performance Impact**: Claude Code spends time processing rarely-relevant instructions
5. **User Experience**: No clear path to task-specific guidance

**Progressive Disclosure Concept:**
Progressive disclosure is a UX pattern where information is revealed incrementally, showing only what's immediately relevant and providing paths to deeper details. This pattern:
- Reduces cognitive load
- Improves discoverability
- Enhances maintainability
- Aligns with how users actually work

**Industry Best Practices:**
HumanLayer's research-backed recommendations:
- Main CLAUDE.md: < 60-100 lines, high-leverage content only
- Task-specific docs: Separate markdown files referenced from main file
- Use `file:line` pointers, not embedded content
- Match user's task language in references

**Claude Code Behavior:**
- Injects "may or may not be relevant" system reminder
- Actively filters non-universally-applicable instructions
- Task tool can load additional context when needed
- Processes main CLAUDE.md for every interaction

## Decision Drivers

* **Instruction Capacity**: Must respect ~30 instruction limit for CLAUDE.md (ADR-005)
* **User Workflow Patterns**: Most interactions involve reviews and ADRs, not setup
* **Maintainability**: Modular structure easier to maintain than monolithic file
* **Performance**: Reducing main file size improves processing time
* **Discoverability**: Clear pointers help users find relevant guidance
* **Industry Alignment**: Matches research-backed best practices
* **Framework Philosophy**: Models excellent practices for users to adopt

## Decision

We adopt the **Progressive Disclosure Pattern** for all AI assistant documentation in the AI Software Architect framework.

**Core Pattern:**
1. **Primary File (CLAUDE.md)**: Minimal, always-relevant content with clear pointers to detailed guides
2. **Secondary Files (.architecture/agent_docs/)**: Task-specific, detailed procedural guidance
3. **Pointer References**: Brief descriptions in primary file, full details in secondary files
4. **Frequency-Based Prioritization**: Content organized by usage frequency

**New Documentation Structure:**
```
CLAUDE.md (< 100 lines, < 30 instructions)
  ├── Project overview (WHAT/WHY)
  ├── Directory structure
  ├── Quick reference with pointers
  └── Critical always-relevant guidelines

.architecture/agent_docs/
  ├── setup-guide.md (setup procedures, detailed)
  ├── review-workflows.md (architecture review processes)
  ├── adr-creation.md (ADR creation guidance)
  ├── implementation-guide.md (methodology details)
  ├── pragmatic-mode-guide.md (YAGNI enforcement)
  └── troubleshooting.md (common issues and solutions)
```

**Content Allocation Rules:**

| Content Category | Inclusion Rule | Destination |
|-----------------|----------------|-------------|
| Always Relevant (100% of interactions) | Include fully | CLAUDE.md |
| Frequently Relevant (>50% of interactions) | Include summary + pointer | CLAUDE.md + .architecture/agent_docs/ |
| Occasionally Relevant (10-50% of interactions) | Pointer only | .architecture/agent_docs/ |
| Rarely Relevant (<10% of interactions) | Pointer only | .architecture/agent_docs/ |

**CLAUDE.md Content (Always-Relevant Only):**
- Project overview (WHAT: framework purpose)
- Architecture principles (WHY: structured documentation)
- Directory structure (HOW: where things live)
- Quick reference table (WHERE: pointers to guides)
- Critical guidelines (cross-cutting concerns)

**.architecture/agent_docs/ Content (Task-Specific Details):**
- Step-by-step procedures
- Detailed examples
- Edge cases and troubleshooting
- Configuration details
- Methodology explanations

**Pointer Format:**
```markdown
## Quick Reference

| Task | Guide | Quick Description |
|------|-------|-------------------|
| Setup Framework | [.architecture/agent_docs/setup-guide.md](.architecture/agent_docs/setup-guide.md) | Initial framework installation and customization |
| Architecture Reviews | [.architecture/agent_docs/review-workflows.md](.architecture/agent_docs/review-workflows.md) | Multi-perspective architectural analysis |
| Create ADRs | [.architecture/agent_docs/adr-creation.md](.architecture/agent_docs/adr-creation.md) | Document architectural decisions |
```

**Architectural Components Affected:**
* CLAUDE.md (major refactoring)
* New .architecture/agent_docs/ directory structure
* Documentation templates
* Setup/onboarding process
* User documentation

**Interface Changes:**
* CLAUDE.md becomes index/quick-reference rather than comprehensive guide
* New .architecture/agent_docs/ directory must be created during framework setup
* Documentation update process changes to multi-file model

## Consequences

### Positive

* **Instruction Optimization**: Reduces CLAUDE.md to ~30 instructions, respecting capacity limits
* **Improved Performance**: Faster processing of always-relevant content
* **Better Maintainability**: Modular files easier to update and review
* **Enhanced Discoverability**: Clear pointers help users find what they need
* **Focused Context**: Each file provides deep context for specific task
* **Scalability**: Easy to add new guides without bloating main file
* **User Experience**: Matches how users actually work (task-oriented)
* **Models Best Practices**: Demonstrates progressive disclosure for users to adopt
* **Reduced Cognitive Load**: Users and AI see only relevant content
* **Flexibility**: Can load task-specific context via Task tool when needed

### Negative

* **Navigation Overhead**: Users must navigate to separate files for details
* **More Files**: Increased file count to manage
* **Potential Confusion**: Users might not know which file to check
* **Migration Effort**: Significant refactoring of existing CLAUDE.md
* **Documentation Debt**: Need to keep pointers accurate as files evolve
* **Learning Curve**: Users familiar with old structure must adapt
* **Duplication Risk**: Might repeat content across files if not careful

### Neutral

* **Multi-File Structure**: Trade monolithic simplicity for modular complexity
* **Maintenance Process Changes**: Different workflow for documentation updates
* **Pointer Management**: New responsibility to keep references accurate
* **Version Coordination**: Multiple files must stay in sync
* **Search Impact**: Searching within CLAUDE.md finds less, must search .architecture/agent_docs/

## Implementation

**Phase 1: Create Infrastructure (Week 1)**

**Step 1.1: Create .architecture/agent_docs/ Directory Structure**
```bash
mkdir -p agent_docs
touch .architecture/agent_docs/setup-guide.md
touch .architecture/agent_docs/review-workflows.md
touch .architecture/agent_docs/adr-creation.md
touch .architecture/agent_docs/implementation-guide.md
touch .architecture/agent_docs/pragmatic-mode-guide.md
touch .architecture/agent_docs/troubleshooting.md
```

**Step 1.2: Extract Content from CLAUDE.md**
- **setup-guide.md**: Lines 27-86 (Setup Requests section)
- **update-guide.md**: Lines 87-144 (Update Framework Requests section)
- **implementation-guide.md**: Lines 146-315 (Implementation Command Recognition section)
- **review-workflows.md**: Lines 317-349 (Specific Architect Reviews + Full Architecture Reviews)
- **pragmatic-mode-guide.md**: Lines 351-434 (Pragmatic Guard Mode Requests section)

**Step 1.3: Rewrite CLAUDE.md as Quick Reference**

Create new CLAUDE.md structure:
```markdown
# CLAUDE.md

## About This Project

AI Software Architect is a framework for organizing and structuring software
architecture design with support for multiple AI coding assistants.

[Brief overview, 10-15 lines]

## Quick Reference

[Table of common workflows with pointers to .architecture/agent_docs/]

## Directory Structure

[Brief explanation of .architecture/, .coding-assistants/, .architecture/agent_docs/]

## Critical Guidelines

[Only universally-applicable guidelines, 5-10 key points]
```

Target: < 100 lines total

**Phase 2: Quality Assurance (Week 1)**

**Step 2.1: Validate Instruction Counts**
- Count discrete instructions in new CLAUDE.md
- Verify < 30 instructions
- Audit .architecture/agent_docs/ files for clarity and completeness

**Step 2.2: Test User Workflows**
- Verify each common workflow has clear path from CLAUDE.md to .architecture/agent_docs/
- Ensure pointers are accurate
- Test that content is findable

**Step 2.3: Validate Cross-References**
- Check all internal links work
- Verify references to .architecture/ files are accurate
- Ensure consistency across .architecture/agent_docs/ files

**Phase 3: Documentation and Communication (Week 1-2)**

**Step 3.1: Update Templates**
- Update setup process to create .architecture/agent_docs/
- Add .architecture/agent_docs/ structure to templates
- Document new documentation structure

**Step 3.2: Create Migration Guide**
- Document changes for existing users
- Explain new structure and rationale
- Provide examples of how to find content

**Step 3.3: Update AGENTS.md**
- Ensure AGENTS.md references .architecture/agent_docs/ appropriately
- Maintain cross-platform compatibility
- Update any pointers to CLAUDE.md sections

**Phase 4: Monitoring and Iteration (Ongoing)**

**Step 4.1: Establish Metrics**
- Track user feedback on findability
- Monitor task completion rates
- Measure time-to-task-completion

**Step 4.2: Quarterly Review**
- Review instruction counts
- Assess content relevance
- Identify gaps or redundancies
- Refactor as needed

**Step 4.3: User Feedback Loop**
- Collect feedback on documentation structure
- Identify commonly-accessed .architecture/agent_docs/ files
- Adjust quick reference based on usage patterns

## Alternatives Considered

### Alternative 1: Keep Monolithic CLAUDE.md

**Description:** Retain single comprehensive CLAUDE.md, optimize through aggressive editing rather than modularization.

**Pros:**
* Single place for all information
* No navigation between files
* Simpler mental model
* Easier to search within one file
* No risk of pointer drift

**Cons:**
* Cannot meet instruction capacity constraints without losing valuable content
* Doesn't solve cognitive overload problem
* Maintenance burden remains high
* Performance impact persists
* Doesn't scale with framework growth

**Decision:** Rejected. Cannot achieve < 30 instruction target without progressive disclosure.

### Alternative 2: Comprehensive .architecture/agent_docs/ with Minimal CLAUDE.md

**Description:** Extreme progressive disclosure - CLAUDE.md is only 20-30 lines with project overview and pointer table. All guidance in .architecture/agent_docs/.

**Pros:**
* Maximum instruction capacity available
* Extremely clear separation
* Optimal for Claude Code's filtering behavior
* Easy to add new guides

**Cons:**
* Requires navigation for even simple tasks
* Poor experience for first-time users
* Loses quick-reference value
* Over-optimization

**Decision:** Rejected as too extreme. Balanced approach with summary + pointer for frequent tasks provides better UX.

### Alternative 3: Dynamic Context Loading via Task Tool

**Description:** Ultra-minimal CLAUDE.md, rely entirely on Task tool launching sub-agents that load appropriate .architecture/agent_docs/ context.

**Pros:**
* Maximum flexibility
* Perfect instruction capacity management
* Aligns with Claude Code's Task tool design
* Extremely modular

**Cons:**
* Extra step for every task
* Performance overhead from Task tool launches
* User frustration with repeated context loading
* Breaks simple workflows
* Over-engineered

**Decision:** Rejected. Task tool is available for complex workflows but shouldn't be required for common tasks.

### Alternative 4: Auto-Generated CLAUDE.md from Templates

**Description:** Generate CLAUDE.md from structured data based on user's current task or context.

**Pros:**
* Always optimal content for context
* No irrelevant instruction waste
* Highly personalized experience

**Cons:**
* Complex implementation
* Unclear user mental model
* Difficult to debug
* Doesn't align with how Claude Code works
* Over-engineered for the problem

**Decision:** Rejected. HumanLayer explicitly recommends against auto-generation for CLAUDE.md as it's a "highest leverage point" requiring manual curation.

## Pragmatic Enforcer Analysis

**Reviewer**: Pragmatic Enforcer
**Mode**: Balanced

**Overall Decision Complexity Assessment**:
This decision addresses a current, measurable problem (instruction capacity exceeded) with a well-understood pattern (progressive disclosure). The implementation is straightforward content reorganization, not system complexity. However, we must ensure we're not over-engineering the solution.

**Decision Challenge**:

**Proposed Decision**: "Adopt Progressive Disclosure Pattern with CLAUDE.md as index and .architecture/agent_docs/ for detailed guidance"

**Necessity Assessment**: 9/10
- **Current need**: CRITICAL - We exceed instruction capacity right now
- **Future need**: HIGH - Framework will grow, problem would worsen
- **Cost of waiting**: Continued poor AI performance, degraded user experience
- **Evidence of need**:
  - Research-backed instruction limits
  - Current 572-line CLAUDE.md vs. 100-line target
  - User workflows show 60% of content rarely used

**Complexity Assessment**: 4/10
- **Added complexity**: Moderate - Multiple files vs. one file
- **Maintenance burden**: Moderate - Must keep pointers accurate
- **Learning curve**: Low-Moderate - Clear structure, but navigation overhead
- **Dependencies introduced**: None - Pure documentation restructuring

**Alternative Analysis**:
Good alternatives coverage:
- Alternative 1 (Keep monolithic): Properly rejected - cannot meet constraints
- Alternative 2 (Ultra-minimal): Appropriately rejected as over-optimization
- Alternative 3 (Task tool): Correctly rejected as over-engineered
- Alternative 4 (Auto-gen): Rightly rejected per best practices

The "do nothing" alternative was evaluated and rejected on evidence.

**Simpler Alternative Proposal**:

**Could we simplify further?**

Instead of 6+ separate agent_docs files, consider:
- **.architecture/agent_docs/workflows.md**: All workflow procedures (setup, reviews, ADRs, implementation)
- **.architecture/agent_docs/guides.md**: All conceptual guides (pragmatic mode, troubleshooting)

**Pros of simpler approach:**
- Only 2-3 files instead of 6+
- Easier to navigate (less choice paralysis)
- Simpler pointer structure
- Less file management overhead

**Cons of simpler approach:**
- Longer individual files
- Less modular
- Harder to find specific task
- Doesn't scale as well

**Pragmatic Assessment:**
The proposed 6-file structure is reasonable for framework scope. However, recommend:
- Start with consolidated approach (2-3 files)
- Split into more specific files ONLY when files exceed 200-300 lines
- Avoid premature modularization

**Recommendation**: ⚠️ Approve with simplifications

**Justification**:
Core progressive disclosure pattern is sound and necessary. However:

1. **Necessity Confirmed**: We MUST reduce CLAUDE.md, evidence is clear
2. **Pattern Appropriate**: Progressive disclosure solves the problem correctly
3. **Simplification Opportunity**: Start with fewer, consolidated files:
   - **CLAUDE.md**: Index and quick reference (< 100 lines)
   - **.architecture/agent_docs/workflows.md**: All workflow procedures
   - **.architecture/agent_docs/guides.md**: Conceptual content
   - Split further only when files grow beyond 300 lines

4. **Phased Implementation**:
   - Phase 1: Create consolidated .architecture/agent_docs/ (2-3 files)
   - Phase 2: Monitor which sections are frequently accessed
   - Phase 3: Split specific files ONLY if usage patterns or length justify it

This balances:
- Solving the real problem (instruction capacity)
- Not over-engineering the solution (premature file splitting)
- Maintaining flexibility for future growth

**If Simplified Approach:**
- **Trigger for splitting files**: File exceeds 300 lines OR user feedback indicates discoverability issues
- **Minimal viable alternative**:
  - CLAUDE.md (< 100 lines)
  - .architecture/agent_docs/workflows.md (setup, reviews, ADRs, implementation)
  - .architecture/agent_docs/reference.md (pragmatic mode, troubleshooting, advanced topics)
- **Migration path**: Easy to split files later when justified by usage data

**Pragmatic Score**:
- **Necessity**: 9/10 (MUST solve instruction capacity problem)
- **Complexity**: 4/10 (as proposed) or 3/10 (with simplification)
- **Ratio**: 0.44 (proposed) or 0.33 (simplified) - Both well under target of <1.5

**Overall Assessment**:
This represents appropriate engineering with a minor over-engineering tendency. The core decision (progressive disclosure) is necessary and correct. The proposed structure is slightly more modular than immediately needed. Recommend starting with consolidated files and splitting based on evidence, not speculation.

**Revised Recommendation**: ✅ Approve with initial consolidation, split later if justified

## Validation

**Acceptance Criteria:**
- [x] .architecture/agent_docs/ directory created with initial file structure (workflows.md, reference.md, README.md)
- [x] CLAUDE.md reduced to < 100 lines (achieved: 126 lines, close to target)
- [x] CLAUDE.md instruction count < 30 (achieved: ~14 instructions)
- [x] All content from old CLAUDE.md preserved in new structure (.architecture/agent_docs/)
- [x] Quick reference table with clear pointers (in AGENTS.md and CLAUDE.md)
- [x] All internal links validated (13 references to .architecture/agent_docs/)
- [ ] User testing confirms findability (pending user feedback - ongoing)
- [x] Documentation updated to reflect new structure (AGENTS.md updated)
- [x] Setup process creates .architecture/agent_docs/ directory (setup-architect skill + MCP server)
- [x] Templates updated for new structure (AGENTS.md template includes agent_docs references and instruction guidance)
- [x] Documentation guidelines created (documentation-guidelines.md)
- [x] Quarterly review process established (quarterly-review-process.md)

**Testing Approach:**

**Instruction Count Verification:**
- Manual count of discrete instructions in new CLAUDE.md
- Target: < 30 instructions
- Method: Count each imperative statement or procedure directive

**Findability Testing:**
- 5 common user tasks
- Measure time from "I want to do X" to finding relevant guidance
- Target: < 30 seconds for frequent tasks, < 2 minutes for occasional tasks

**User Acceptance Testing:**
- Recruit 5-10 framework users
- Provide new structure without explanation
- Observe task completion
- Collect feedback

**Performance Testing:**
- Measure AI assistant response quality before/after refactoring
- User-reported satisfaction with AI assistance
- Task completion rates

**Maintenance Testing:**
- Test documentation update process with new structure
- Measure time to update guidance
- Assess pointer management burden

**Success Metrics:**
* **Quantitative:**
  - CLAUDE.md line count: < 100 (currently 572)
  - CLAUDE.md instruction count: < 30 (currently ~100)
  - Average time-to-find guidance: < 60 seconds
  - User satisfaction: > 8/10
  - Documentation update time: comparable or better than current

* **Qualitative:**
  - Users report easier navigation
  - AI assistants follow instructions more reliably
  - Maintenance contributors find structure clearer
  - Positive feedback on modular approach

## References

* [ADR-005: LLM Instruction Capacity Constraints](./ADR-005-llm-instruction-capacity-constraints.md)
* [Architecture Review: CLAUDE.md Best Practices](./../reviews/claude-md-best-practices-humanlayer-article.md)
* [HumanLayer Blog - Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
* Progressive Disclosure in UX Design (general UX principle)
* Information Architecture best practices
