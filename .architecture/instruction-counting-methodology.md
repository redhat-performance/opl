# Instruction Counting Methodology

**Version**: 1.0.0
**Created**: 2025-12-04
**Related**: [ADR-005: LLM Instruction Capacity Constraints](decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md)

## Purpose

This document defines the methodology for counting discrete instructions in AI assistant documentation (AGENTS.md, CLAUDE.md, .architecture/agent_docs/) to ensure we respect LLM instruction capacity constraints (~150-200 total instructions, with Claude Code using ~50).

## What is a "Discrete Instruction"?

A **discrete instruction** is any directive that requires the AI assistant to:
1. Take a specific action
2. Make a decision
3. Follow a particular procedure
4. Apply a rule or guideline

## Instruction Categories

### 1. Command/Directive Instructions
Direct commands telling the AI what to do.

**Examples:**
- "Create ADR for [topic]"
- "Follow TDD methodology"
- "Apply pragmatic analysis"
- "Check .architecture/config.yml"

**Count**: 1 instruction per distinct command

### 2. Conditional Logic Instructions
If-then statements that guide decision-making.

**Examples:**
- "If pragmatic_mode.enabled: Apply YAGNI principles"
- "When conducting reviews: Adopt member personas"
- "If file doesn't exist: Create from template"

**Count**: 1 instruction per conditional branch that affects behavior

### 3. Process/Procedure Instructions
Multi-step procedures where each step requires action.

**Example:**
```
Setup process:
1. Analyze project structure
2. Customize templates
3. Create directories
4. Conduct initial review
```

**Count**: 1 instruction per distinct step (4 instructions in example)

### 4. Reference/Lookup Instructions
Directives to check or reference specific information.

**Examples:**
- "Reference .architecture/principles.md"
- "Check members.yml for available specialists"
- "See .architecture/agent_docs/workflows.md for details"

**Count**: 1 instruction per unique reference (but NOT if it's just a pointer for humans)

### 5. Guideline/Constraint Instructions
Rules that constrain or guide behavior.

**Examples:**
- "Keep CLAUDE.md < 100 lines"
- "Only universally-applicable instructions in main file"
- "Never compromise security-critical features"
- "Respect instruction capacity limits"

**Count**: 1 instruction per distinct guideline

## What DOES NOT Count as an Instruction

### 1. Informational Content
Descriptive text that doesn't direct behavior.

**Examples:**
- "The framework provides architecture documentation"
- "Version 1.2.0 was released in 2025"
- "This file contains cross-platform instructions"

**Count**: 0 instructions

### 2. Examples
Illustrations that don't create new requirements.

**Examples:**
- "Example: 'Ask Security Specialist to review auth'"
- Code snippets showing configuration format
- Sample output or templates

**Count**: 0 instructions (unless the example IS the instruction)

### 3. Human-Only References
Pointers intended for human readers, not AI behavior.

**Examples:**
- "For more information, see..."
- "Additional resources:"
- "Repository: https://github.com/..."

**Count**: 0 instructions

### 4. Headings and Organization
Structural elements that don't direct action.

**Examples:**
- "## Core Workflows"
- "### Setup Procedures"
- Table of contents

**Count**: 0 instructions

### 5. Redundant/Clarifying Statements
Restatements of instructions already counted.

**Example:**
```
"Create ADR for [topic]"
"In other words, document architectural decisions as ADRs"
```

**Count**: 1 instruction (not 2), second is clarification

## Counting Methodology

### Step 1: Identify Instruction Candidates

Read through the document and mark:
- [ ] Commands (do X)
- [ ] Conditionals (if X, then Y)
- [ ] Procedures (step 1, step 2, ...)
- [ ] References requiring action (check X, read Y)
- [ ] Guidelines constraining behavior (must X, never Y)

### Step 2: Filter Out Non-Instructions

Remove:
- [ ] Pure information
- [ ] Examples (unless they ARE the instruction)
- [ ] Human-only references
- [ ] Structural elements
- [ ] Redundant clarifications

### Step 3: Count Distinct Instructions

For each remaining item:
1. Is it a unique directive?
2. Does it require distinct AI behavior?
3. Is it not redundant with another instruction?

If yes to all three: Count it.

### Step 4: Calculate Totals

Sum up instructions by category:
- Commands/Directives: X
- Conditionals: Y
- Procedures: Z
- References: A
- Guidelines: B
- **Total**: X + Y + Z + A + B

## Target Metrics

Based on ADR-005:

| Document | Target Lines | Target Instructions | Current | Status |
|----------|--------------|---------------------|---------|--------|
| **CLAUDE.md** | < 100 | < 30 | 126 lines, ~14 instr | ✅ Instructions met, lines close |
| **AGENTS.md** | < 500 | < 150 | 418 lines, ~120 instr | ✅ Both met |
| **.architecture/agent_docs/** | No limit | Loaded as needed | 1,058 lines | ✅ Progressive disclosure |
| **Total Budget** | - | < 200 (accounting for Claude Code's ~50) | ~134 | ✅ Well under |

## Example: Counting Instructions in CLAUDE.md

**Document Section:**
```markdown
## Claude Code-Specific Features

### 1. Claude Skills Integration

Claude Code users can access framework operations as reusable skills:

**Available Skills:**
- `setup-architect`: Set up framework in a new project
- `architecture-review`: Conduct multi-perspective reviews
- `create-adr`: Create Architectural Decision Records

**See [AGENTS.md](AGENTS.md#installation-options) for installation instructions.**
```

**Instruction Count:**
- "Claude Code users can access framework operations as reusable skills" → **0** (informational)
- List of available skills → **0** (informational list, not directives)
- "See [AGENTS.md]..." → **0** (human-only reference pointer)

**Total**: 0 instructions in this section (purely informational)

**Alternative Phrasing (With Instructions):**
```markdown
**When user requests setup:** Use `setup-architect` skill
**When user requests review:** Use `architecture-review` skill
**When user requests ADR:** Use `create-adr` skill
```

**Instruction Count**: 3 instructions (conditional directives)

## Practical Application

### When Writing Documentation

**Ask yourself:**
1. Does this tell the AI what to do? → Instruction
2. Does this explain context/background? → Not an instruction
3. Does this provide an example? → Not an instruction (usually)
4. Does this constrain AI behavior? → Instruction

### When Reviewing Documentation

**Check:**
- [ ] Instruction count in acceptable range
- [ ] All counted items actually direct AI behavior
- [ ] No redundant instructions
- [ ] Informational content not miscounted as instructions
- [ ] Progressive disclosure used for task-specific details

### When Refactoring Documentation

**Strategies to reduce instruction count:**
1. **Extract to .architecture/agent_docs/**: Move task-specific procedures
2. **Combine similar**: Merge related instructions
3. **Make informational**: Convert directives to descriptive text where appropriate
4. **Use config files**: Move settings to `.architecture/config.yml`
5. **Reference vs. repeat**: Point to existing instructions rather than duplicate

## Edge Cases

### Case 1: Command Patterns

**Text:**
```
"Start architecture review for version X.Y.Z"
"Start architecture review for [feature name]"
```

**Count**: 1 instruction (both are examples of the same command pattern)

### Case 2: "See X" References

**Text:**
```
"See [.architecture/agent_docs/workflows.md](.architecture/agent_docs/workflows.md) for detailed procedures"
```

**Question**: Is this an instruction?
**Answer**: No, if it's a pointer for humans. Yes, if it directs AI to read and apply that content.

**Context matters**: In CLAUDE.md quick reference → No (human pointer). In procedural steps → Yes (AI directive).

### Case 3: Nested Procedures

**Text:**
```
Setup process:
1. Analyze project
   - Check package files
   - Identify frameworks
2. Create templates
```

**Count**: 4 instructions (Analyze, Check, Identify, Create)

### Case 4: Implicit Instructions

**Text:**
```
"The framework follows TDD methodology"
```

**Question**: Is this an instruction to follow TDD?
**Answer**: No, unless context makes it a directive. "The framework follows..." is informational. "Follow TDD methodology" is an instruction.

## Quarterly Review Process

Every quarter (or after major documentation changes):

1. **Re-count instructions** in CLAUDE.md, AGENTS.md
2. **Check against targets** (< 30 and < 150 respectively)
3. **Identify instruction bloat** (unnecessary or redundant)
4. **Refactor if needed** (move to .architecture/agent_docs/, combine, remove)
5. **Document changes** (update this methodology if counting approach evolves)
6. **Validate with users** (are instructions being followed correctly?)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-04 | Initial methodology based on ADR-005 implementation |

## References

- [ADR-005: LLM Instruction Capacity Constraints](decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md)
- [ADR-006: Progressive Disclosure Pattern](decisions/adrs/ADR-006-progressive-disclosure-pattern.md)
- [HumanLayer Blog - Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- Research on LLM instruction-following capacity (~150-200 instructions)
