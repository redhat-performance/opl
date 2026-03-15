# ADR-007: Tool Permission Restrictions for Claude Skills

## Status

Accepted

## Context

Our Claude Skills currently have implicit unlimited access to all available tools (Read, Write, Edit, Bash, Glob, Grep, etc.). When a skill is activated, it can use any tool without restriction. This creates a security concern where the blast radius of a skill malfunction or misuse is unnecessarily large.

The [First Principles Deep Dive to Claude Agent Skills](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) blog post by Lee Han Chung documents best practices for Claude Code skills, including the `allowed-tools` frontmatter field that restricts skill capabilities to only necessary tools.

Our architecture review (`.architecture/comparisons/claude-skills-deep-dive-comparison.md`) identified this as a **critical security gap** that all team members agreed should be addressed immediately.

**Current State:**
- 7 skills with no tool restrictions
- Implicit full access to Read, Write, Edit, Bash, Glob, Grep, etc.
- No principle of least privilege applied

**Problem Statement:**
Without tool permission restrictions, a skill that only needs to read files (like `list-members`) has the same capabilities as a skill that needs to modify the entire project structure (like `setup-architect`). This violates security best practices and creates unnecessary risk.

## Decision Drivers

* **Security**: Principle of least privilege - skills should only have access to tools they actually need
* **Blast Radius Limitation**: Reduce potential damage from skill malfunction or unexpected behavior
* **Explicit Intent**: Make tool requirements clear in skill frontmatter
* **Industry Best Practice**: Align with Claude Code's documented patterns
* **Low Implementation Cost**: 2-hour effort to add frontmatter to 7 skills
* **No Structural Changes**: Can be implemented without refactoring skill logic

## Decision

**We will add explicit `allowed-tools` restrictions to all Claude Skills via YAML frontmatter.**

Each skill will declare only the tools it requires using the `allowed-tools` field. Claude Code will enforce these restrictions during skill execution.

**Architectural Components Affected:**
* All 7 Claude Skills in `.claude/skills/`
* Skill YAML frontmatter structure
* Common patterns documentation (`_patterns.md`)

**Interface Changes:**
* Add `allowed-tools` field to skill YAML frontmatter
* No changes to skill logic or process workflows
* No changes to skill invocation patterns

**Tool Permission Assignments:**

```yaml
# list-members - Read only
allowed-tools: Read

# architecture-status - Read and search
allowed-tools: Read,Glob,Grep

# create-adr - Read, write, basic bash commands
allowed-tools: Read,Write,Bash(ls:*,grep:*)

# specialist-review - Read, write, search
allowed-tools: Read,Write,Glob,Grep

# architecture-review - Read, write, search, git commands
allowed-tools: Read,Write,Glob,Grep,Bash(git:*)

# pragmatic-guard - Read and edit only
allowed-tools: Read,Edit

# setup-architect - Full access (installation requires broad permissions)
allowed-tools: Read,Write,Edit,Glob,Grep,Bash
```

**Wildcard Scoping:**
- Use `Bash(git:*)` to allow only git commands
- Use `Bash(ls:*,grep:*)` to allow specific command families
- Full `Bash` access only for skills requiring broad system access

## Consequences

### Positive

* **Improved Security**: Each skill limited to minimum necessary permissions
* **Clear Capability Documentation**: Tool requirements explicit in frontmatter
* **Reduced Blast Radius**: Skill malfunction can't use tools it wasn't designed to need
* **Alignment with Best Practices**: Follows Claude Code's documented patterns
* **Future-Proof**: Pattern scales as we add more skills
* **No Logic Changes**: Existing skill workflows unchanged

### Negative

* **Maintenance Overhead**: Must update `allowed-tools` if skill needs change
* **Permission Debugging**: May need to adjust if we discover missing tools during execution
* **Initial Audit**: Requires reviewing each skill to determine actual tool usage

### Neutral

* **Documentation Update**: Need to document pattern in `_patterns.md`
* **No Performance Impact**: Permission checks handled by Claude Code
* **Backward Compatible**: Claude Code supports both restricted and unrestricted skills

## Implementation

**Phase 1: Add Restrictions to All Skills (Week 1)**

1. Audit each skill's SKILL.md to identify actual tool usage
2. Add `allowed-tools` line to YAML frontmatter for all 7 skills
3. Test each skill to ensure all necessary tools are included
4. Document pattern in `.claude/skills/_patterns.md`

**Specific Changes:**

`.claude/skills/list-members/SKILL.md`:
```yaml
---
name: list-members
description: [existing description]
allowed-tools: Read
---
```

`.claude/skills/architecture-status/SKILL.md`:
```yaml
---
name: architecture-status
description: [existing description]
allowed-tools: Read,Glob,Grep
---
```

`.claude/skills/create-adr/SKILL.md`:
```yaml
---
name: create-adr
description: [existing description]
allowed-tools: Read,Write,Bash(ls:*,grep:*)
---
```

`.claude/skills/specialist-review/SKILL.md`:
```yaml
---
name: specialist-review
description: [existing description]
allowed-tools: Read,Write,Glob,Grep
---
```

`.claude/skills/architecture-review/SKILL.md`:
```yaml
---
name: architecture-review
description: [existing description]
allowed-tools: Read,Write,Glob,Grep,Bash(git:*)
---
```

`.claude/skills/pragmatic-guard/SKILL.md`:
```yaml
---
name: pragmatic-guard
description: [existing description]
allowed-tools: Read,Edit
---
```

`.claude/skills/setup-architect/SKILL.md`:
```yaml
---
name: setup-architect
description: [existing description]
allowed-tools: Read,Write,Edit,Glob,Grep,Bash
---
```

**Phase 2: Documentation and Patterns (Week 1)**

1. Add "Tool Permission Pattern" to `.claude/skills/_patterns.md`
2. Document principle of least privilege
3. Provide examples of appropriate tool assignments
4. Create troubleshooting guide for permission errors

## Alternatives Considered

### Alternative 1: Maintain Status Quo (No Restrictions)

**Pros:**
* No implementation effort
* No risk of permission errors
* No maintenance overhead

**Cons:**
* Significant security gap remains
* Violates principle of least privilege
* Diverges from industry best practices
* Unnecessary blast radius for skill failures

**Verdict:** Rejected - security concerns outweigh convenience

### Alternative 2: Defer Until We Have More Skills

**Pros:**
* Avoid premature work
* Can assess patterns with larger skill library

**Cons:**
* Security gap persists
* Habit of unrestricted skills becomes established
* Harder to retrofit later
* No cost to implementing now

**Verdict:** Rejected - 2-hour implementation cost doesn't justify deferral

### Alternative 3: Apply Only to High-Risk Skills

**Pros:**
* Reduced initial effort
* Focus on skills with write/bash access

**Cons:**
* Inconsistent approach
* Still leaves some skills unrestricted
* Doesn't establish pattern for future skills
* Only saves 30 minutes vs. full implementation

**Verdict:** Rejected - consistency and completeness preferred

## Pragmatic Enforcer Analysis

**Reviewer**: Pragmatic Enforcer
**Mode**: Balanced

**Overall Decision Complexity Assessment**:
This decision is appropriately simple. Adding a single line of YAML frontmatter to existing skills requires minimal complexity while delivering significant security value. No structural refactoring, no new abstractions, no additional dependencies.

**Decision Challenge**:

**Proposed Decision**: "Add explicit `allowed-tools` restrictions to all Claude Skills via YAML frontmatter"

**Necessity Assessment**: 9/10
- **Current need**: Security gap exists today; all skills have unlimited access
- **Future need**: Will remain necessary as we add more skills
- **Cost of waiting**: Low immediate risk but establishes poor precedent
- **Evidence of need**: Industry best practice (documented in blog), unanimous architect agreement, security principle of least privilege

**Complexity Assessment**: 2/10
- **Added complexity**: Single YAML field per skill - trivial complexity
- **Maintenance burden**: Must update if skill needs change (rare)
- **Learning curve**: Simple concept, well-documented
- **Dependencies introduced**: None - Claude Code already supports this

**Alternative Analysis**:
All alternatives considered are either "do nothing" (rejected for security) or "do less" (partial implementation). No simpler approach exists that still addresses the security concern.

**Simpler Alternative Proposal**:
None. This is already the minimal solution. Adding one line of frontmatter is the simplest possible approach to tool restriction.

**Recommendation**: ✅ **Approve decision**

**Justification**:
Rare case where complexity ratio is extremely favorable (0.22). High necessity due to security concerns, trivial complexity. No simpler alternative exists. This is exactly the kind of lightweight, high-value change that pragmatic engineering endorses.

**Pragmatic Score**:
- **Necessity**: 9/10
- **Complexity**: 2/10
- **Ratio**: 0.22 *(Target: <1.5 for balanced mode - well under threshold)*

**Overall Assessment**:
**Appropriate engineering**. This is not premature optimization or speculative complexity. It's a straightforward security improvement with minimal cost and clear value. Implement immediately.

## Validation

**Acceptance Criteria:**
- [x] All 7 skills have `allowed-tools` frontmatter field
- [x] Each skill declares only tools it actually uses
- [x] Wildcard scoping used for `Bash` where appropriate
- [x] Pattern documented in `_patterns.md`
- [ ] All skills tested and confirmed working with restrictions
- [ ] No permission errors during normal skill execution

**Testing Approach:**
1. Invoke each skill with typical use cases
2. Verify skill can perform all necessary operations
3. Confirm no permission errors occur
4. Test edge cases (large reviews, complex ADRs, etc.)
5. Validate wildcard scoping works correctly (e.g., `Bash(git:*)` allows git commands)

## References

* [Claude Skills Deep Dive Comparison](../../comparisons/claude-skills-deep-dive-comparison.md)
* [Claude Skills Deep Dive Takeaways](../../comparisons/claude-skills-takeaways.md)
* [First Principles Deep Dive to Claude Agent Skills](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) (External)
* [ADR-006: Progressive Disclosure Documentation Pattern](./ADR-006-progressive-disclosure-documentation.md)

---

**Decision Date**: 2025-12-04
**Approved By**: Systems Architect, Security Specialist, AI Engineer, Maintainability Expert, Pragmatic Enforcer (Unanimous)
**Implementation Target**: Week of 2025-12-04
