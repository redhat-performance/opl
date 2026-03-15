# Documentation Guidelines

**Version**: 1.0.0
**Created**: 2025-12-04
**Related**: [ADR-005](decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md), [ADR-006](decisions/adrs/ADR-006-progressive-disclosure-pattern.md)

## Purpose

This document defines guidelines for contributing to AI Software Architect framework documentation, with emphasis on respecting LLM instruction capacity constraints while maintaining clarity and usefulness.

## Core Principles

### 1. Instruction Capacity First

**The Constraint**: LLMs reliably follow ~150-200 instructions total. Claude Code uses ~50, leaving 100-150 for project documentation.

**What This Means**:
- Every instruction counts—make each one valuable
- Prioritize always-relevant over occasionally-relevant content
- Use progressive disclosure for task-specific details

### 2. Progressive Disclosure

**The Pattern**: Show what's immediately relevant, provide paths to deeper details.

**Implementation**:
- **AGENTS.md**: Cross-platform overview, always-relevant workflows (~150 instructions)
- **CLAUDE.md**: Claude Code-specific features and enhancements (~14 instructions)
- **.architecture/agent_docs/**: Detailed task-specific procedures (loaded as needed)

### 3. Clarity Over Cleverness

Write for understanding, not impressiveness:
- Use simple, direct language
- One concept per paragraph
- Examples when helpful, not for decoration
- Clear headings that match user mental models

## Document Structure

### AGENTS.md (Cross-Platform Core)

**Target**: < 500 lines, < 150 instructions
**Current**: 418 lines, ~120 instructions ✅

**Include**:
- Project overview (WHAT/WHY)
- Directory structure
- Core workflows (reviews, ADRs, implementation)
- Architectural principles
- Framework configuration
- Quick reference with pointers to agent_docs/

**Exclude**:
- Setup procedures (→ agent_docs/workflows.md)
- Detailed methodology (→ agent_docs/reference.md)
- Troubleshooting (→ agent_docs/reference.md)
- Assistant-specific features (→ CLAUDE.md, etc.)

### CLAUDE.md (Claude Code Enhancements)

**Target**: < 100 lines, < 30 instructions
**Current**: 126 lines, ~14 instructions ✅

**Include**:
- Claude Code-specific features (Skills, MCP)
- Natural language request patterns
- Quick reference table
- Critical Claude-specific guidelines

**Exclude**:
- Cross-platform content (→ AGENTS.md)
- Detailed procedures (→ agent_docs/)
- Setup instructions (→ agent_docs/workflows.md)

### .architecture/agent_docs/ (Detailed Procedures)

**Target**: No line limits—loaded progressively as needed
**Current**: 1,058 lines total ✅

**Structure**:
- **README.md**: Navigation guide, quick lookup
- **workflows.md**: Step-by-step procedures (setup, reviews, ADRs, implementation)
- **reference.md**: Advanced topics (pragmatic mode, troubleshooting, recalibration)

**Include**:
- Detailed step-by-step procedures
- Configuration examples
- Edge cases and troubleshooting
- Methodology details
- Task-specific guidance

**Exclude**:
- Always-relevant content (→ AGENTS.md)
- Redundant explanations

## Content Allocation Rules

Use this decision tree when adding documentation:

```
Is this relevant to >80% of user interactions?
├─ YES → Consider for AGENTS.md (check instruction budget)
└─ NO → Is this Claude Code-specific?
    ├─ YES → Consider for CLAUDE.md (check instruction budget)
    └─ NO → Add to .architecture/agent_docs/
```

**Frequency-Based Prioritization**:

| Frequency | Destination | Example |
|-----------|-------------|---------|
| Always (100%) | AGENTS.md | Core workflows, directory structure |
| Often (50-80%) | AGENTS.md summary + agent_docs/ | Architecture reviews, ADR creation |
| Sometimes (10-50%) | agent_docs/ only | Pragmatic mode configuration |
| Rarely (<10%) | agent_docs/ only | Setup procedures, troubleshooting |

## Instruction Counting

**What Counts as an Instruction**:
- Commands/directives: "Create ADR for [topic]"
- Conditional logic: "If pragmatic_mode.enabled: Apply YAGNI"
- Process steps: "1. Analyze 2. Customize 3. Create"
- Actionable references: "Check .architecture/config.yml"
- Guidelines/constraints: "Keep CLAUDE.md < 100 lines"

**What Doesn't Count**:
- Informational text: "The framework provides..."
- Examples (unless they ARE the instruction)
- Human-only references: "For more info, see..."
- Headings and structure
- Clarifications of existing instructions

**Detailed methodology**: [instruction-counting-methodology.md](instruction-counting-methodology.md)

## Writing Guidelines

### For Instructions

**Do**:
- Be specific: "Check `.architecture/config.yml`" not "Check config"
- Be actionable: "Create ADR for [topic]" not "ADRs can be created"
- Be conditional when appropriate: "When user requests X: Do Y"

**Don't**:
- Repeat yourself—one instruction per directive
- Write instructions as informational text
- Assume context—be explicit about what to do

### For Explanations

**Do**:
- Explain WHY, not just WHAT
- Use examples to clarify
- Link to related documentation
- Write for both humans and AI assistants

**Don't**:
- Write long paragraphs—break into digestible chunks
- Duplicate content across files
- Assume prior knowledge—provide context

### For Examples

**Do**:
- Show realistic use cases
- Include command patterns users will actually type
- Demonstrate correct format (YAML, markdown, etc.)

**Don't**:
- Overdo it—one good example beats five mediocre ones
- Make examples complicated
- Let examples become stale—keep them updated

## Review Process

### Before Submitting Documentation Changes

**Checklist**:
- [ ] Correct file? (AGENTS.md vs CLAUDE.md vs agent_docs/)
- [ ] Instruction budget? (Count if adding to AGENTS.md or CLAUDE.md)
- [ ] Clear and actionable?
- [ ] No duplication?
- [ ] Links work?
- [ ] Examples current?
- [ ] Follows style guidelines?

### Documentation Review Standards

**Reviewers should verify**:
1. **Instruction Capacity**: Changes don't exceed budgets
2. **Progressive Disclosure**: Right content in right place
3. **Clarity**: Clear, concise, actionable
4. **Accuracy**: Information is current and correct
5. **Links**: All internal references work
6. **Consistency**: Follows existing patterns and style

**Tools**:
- Manual instruction counting (see [instruction-counting-methodology.md](instruction-counting-methodology.md))
- Link validation (check all .md references)
- Line count verification (`wc -l`)

## Common Scenarios

### Adding New Workflow

**Question**: "Where does documentation for a new workflow go?"

**Answer**:
1. **Always-relevant workflow** (used >80% of time):
   - Add brief description to AGENTS.md § Core Workflows
   - Add detailed procedure to agent_docs/workflows.md
   - Add to quick reference table in AGENTS.md
   - Check instruction budget in AGENTS.md

2. **Occasionally-relevant workflow** (used 10-80% of time):
   - Add only to agent_docs/workflows.md
   - Add pointer in AGENTS.md quick reference table

3. **Rarely-used workflow** (<10% of time):
   - Add only to agent_docs/workflows.md
   - Optional: Add to agent_docs/README.md navigation

### Updating Existing Documentation

**Question**: "How do I update documentation without breaking instruction budgets?"

**Answer**:
1. Identify which file needs updating
2. If AGENTS.md or CLAUDE.md:
   - Count current instructions before change
   - Count instructions after change
   - Verify still under budget (<150 for AGENTS.md, <30 for CLAUDE.md)
   - If over budget: Move detail to agent_docs/, keep summary/pointer
3. If agent_docs/:
   - Update freely (no instruction limit)
   - Ensure references from main files still accurate

### Adding Claude Code Feature

**Question**: "Where do I document a new Claude Code-specific feature?"

**Answer**:
1. **Feature overview**: Add to CLAUDE.md § Claude Code-Specific Features
2. **Usage details**: Add to agent_docs/workflows.md or reference.md
3. **Configuration**: Update .architecture/config.yml if needed
4. **Check budget**: Ensure CLAUDE.md stays < 30 instructions

### Moving Content Between Files

**Question**: "When should I move content from AGENTS.md to agent_docs/?"

**Triggers**:
- AGENTS.md approaching 150 instruction limit
- Content used <50% of time
- Detailed procedures bloating main file
- Content better suited for progressive disclosure

**Process**:
1. Identify content to move
2. Create detailed version in agent_docs/
3. Replace in AGENTS.md with brief summary + pointer
4. Update quick reference table
5. Verify links work

## Version Control

### When to Update Version Numbers

**Framework version** (in config.yml):
- Major: Breaking changes to structure or interfaces
- Minor: New features, significant improvements
- Patch: Bug fixes, clarifications

**Documentation version** (in individual files):
- Update when significant changes made
- Include date and change summary
- Reference related ADRs

### Changelog

**Track in**:
- ADRs for architectural decisions
- Git commit messages for incremental changes
- Version information sections in key files

## Maintenance

### Quarterly Review Checklist

Perform every quarter (or after major framework changes):

- [ ] Re-count instructions in AGENTS.md and CLAUDE.md
- [ ] Verify against targets (<150 and <30 respectively)
- [ ] Check for instruction bloat or redundancy
- [ ] Validate all internal links
- [ ] Review usage patterns (which agent_docs/ sections accessed most?)
- [ ] Collect user feedback on findability
- [ ] Update stale examples
- [ ] Refactor if needed

**Schedule**: March 1, June 1, September 1, December 1

**Process**: See [quarterly-review-process.md](quarterly-review-process.md)

## Questions?

**Not finding what you need?**
- Check existing documentation patterns in the repo
- Review [ADR-005](decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md) for rationale
- Review [ADR-006](decisions/adrs/ADR-006-progressive-disclosure-pattern.md) for structure
- See [instruction-counting-methodology.md](instruction-counting-methodology.md) for counting details

**Still unclear?**
- Open an issue on GitHub
- Propose documentation improvements via PR
- Ask in discussions

## References

- [ADR-005: LLM Instruction Capacity Constraints](decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md)
- [ADR-006: Progressive Disclosure Pattern](decisions/adrs/ADR-006-progressive-disclosure-pattern.md)
- [Instruction Counting Methodology](instruction-counting-methodology.md)
- [HumanLayer Blog - Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
