# ADR-003: Adoption of Agents.md Standard

## Status

Accepted

**Implementation Date**: 2025-11-20
**Completed Phases**: Phase 1-3 (Immediate implementation)
**Deferred Phases**: Phase 4 (Awaiting trigger conditions)

## Context

The AI Software Architect framework currently provides AI assistant integration through:
- **CLAUDE.md** - Claude Code-specific instructions stored in project root
- **.coding-assistants/** directory - Assistant-specific configurations for Claude, Cursor, Copilot, etc.
- **.architecture/** directory - Architecture documentation, decisions, and reviews

This approach works well for Claude Code users but presents challenges:

1. **Limited Cross-Platform Discoverability**: Each AI assistant must be explicitly configured. Non-Claude users face friction adopting the framework.

2. **No Industry Standard Alignment**: While CLAUDE.md is Claude-specific, there's no universal entry point that all AI assistants recognize.

3. **Documentation Fragmentation**: Setup and usage instructions are duplicated across multiple assistant-specific files.

4. **Scaling Challenges**: Each new AI assistant requires custom integration work and documentation.

### The Agents.md Standard

[Agents.md](https://agents.md/) is an emerging industry standard (20,000+ projects) that provides:

- **Predictable Location**: A dedicated file that AI agents automatically look for
- **Cross-Platform Compatibility**: Works with OpenAI Codex, Google Jules, Cursor, VS Code AI, Claude, and others
- **Clear Separation**: Distinguishes human documentation (README.md) from agent instructions (AGENTS.md)
- **Monorepo Support**: Nested AGENTS.md files for subprojects with tailored instructions
- **Standard Format**: Markdown with common sections (setup, build, test, conventions, security)

### Gap Analysis

**Current State:**
- Framework supports multiple AI assistants conceptually
- Each assistant needs custom configuration
- No universal entry point

**Desired State:**
- Any AI assistant can discover and use the framework
- Clear separation between cross-platform and assistant-specific features
- Reduced adoption friction

### Architectural Alignment

This decision aligns with our principle of **Domain-Centric Design**: Our domain is "collaborative software architecture with AI assistants." Adopting a standard that makes architecture practices accessible to any AI assistant directly serves this domain.

## Decision Drivers

* **Broader Adoption**: Make framework accessible to all AI assistants, not just Claude Code
* **Industry Standards**: Align with established patterns used by 20,000+ projects
* **Reduced Friction**: Lower barrier to entry for projects using different AI tools
* **Future-Proofing**: Ready for new AI assistants without framework changes
* **Clear Boundaries**: Separate cross-platform features from assistant-specific capabilities
* **Maintainability**: Single source of truth for cross-platform instructions
* **Architectural Principle**: "Pragmatic Simplicity" - use existing standards rather than custom solutions

## Decision

We will adopt the **Agents.md standard** as a complementary layer to our existing assistant integration, not as a replacement.

**Implementation Approach:**

```
Project Root
├── AGENTS.md              (New: Cross-platform agent instructions)
├── CLAUDE.md              (Existing: Claude-specific enhancements)
├── README.md              (Existing: Human-focused documentation)
├── .architecture/         (Existing: Architecture artifacts)
└── .coding-assistants/    (Existing: Assistant-specific configs)
```

**Content Distribution Strategy:**

| Topic | AGENTS.md | CLAUDE.md | .architecture/ |
|-------|-----------|-----------|----------------|
| Framework overview | ✅ Brief (2-3 sentences) | ✅ Detailed | ❌ |
| Setup process | ✅ Generic | ✅ Claude-specific | ❌ |
| Architecture reviews | ✅ How to request | ✅ Claude Skills | ✅ Templates |
| ADR creation | ✅ Basic process | ✅ MCP tools | ✅ Templates |
| Members & roles | ❌ Link only | ❌ Link only | ✅ Full content |
| Principles | ❌ Link only | ❌ Link only | ✅ Full content |
| Pragmatic mode | ✅ How to enable | ✅ Detailed behavior | ✅ Configuration |

**AGENTS.md Structure (Minimal Implementation):**

```markdown
# AI Software Architect Framework

Brief overview (2-3 sentences)

## Setup

Generic setup instructions that work for any AI assistant

## Core Workflows

- Requesting architecture reviews
- Creating ADRs
- Getting specialist reviews
- Enabling pragmatic mode

## Architecture Principles

Link to .architecture/principles.md

## Build & Test

Standard commands for the framework itself (if applicable)

## Assistant-Specific Features

- Claude Code: See CLAUDE.md for Skills and MCP integration
- Cursor: See .coding-assistants/cursor/README.md
- Copilot: See .coding-assistants/codex/README.md
```

**Architectural Components Affected:**

* **New**: `AGENTS.md` in project root
* **Modified**: `.architecture/templates/` - Add AGENTS.md template for project setup
* **Modified**: `CLAUDE.md` - Add header explaining relationship to AGENTS.md
* **Modified**: Setup process in CLAUDE.md - Generate AGENTS.md during project setup
* **No Change**: `.architecture/` directory structure
* **No Change**: `.coding-assistants/` directory structure

**Interface Changes:**

* AI assistants gain cross-platform entry point via AGENTS.md
* CLAUDE.md explicitly extends AGENTS.md rather than being standalone
* Setup process generates both AGENTS.md and CLAUDE.md
* Clear documentation of which file to update for different scenarios

## Consequences

### Positive

* **Broader Reach**: Framework becomes accessible to all AI assistants, not just Claude Code
* **Standards Compliance**: Aligns with industry-standard pattern (20,000+ projects)
* **Lower Adoption Friction**: Projects using Cursor, Copilot, Jules, etc. can adopt framework more easily
* **Future-Proof**: New AI assistants work immediately without framework changes
* **Clear Separation**: Distinguishes cross-platform vs. assistant-specific features
* **Better Discoverability**: AI assistants automatically look for AGENTS.md
* **Maintains Claude Advantages**: Claude-specific features (Skills, MCP) remain in CLAUDE.md
* **Minimal Overhead**: Single additional file with well-defined scope
* **Principle Alignment**: Uses existing standard rather than inventing custom solution

### Negative

* **Additional File**: One more file in project root (though standard location)
* **Maintenance Burden**: Two documentation files need updating (mitigated by clear boundaries)
* **Potential Confusion**: Developers need to know AGENTS.md vs CLAUDE.md (mitigated by clear documentation)
* **Duplication Risk**: Risk of duplicating content between files (mitigated by cross-references)
* **Implementation Effort**: Update setup process and create templates (~2-4 hours)
* **Limited Examples**: Starting with minimal AGENTS.md, may need expansion (track via deferrals)

### Neutral

* **Documentation Distribution**: Content moves from single file to two files with clear boundaries
* **Setup Process Changes**: Projects get both AGENTS.md and CLAUDE.md
* **Learning Curve**: Users of other assistants need to understand framework structure
* **Cross-References**: Files reference each other for complete picture

## Implementation

### Phase 1: Create AGENTS.md Template (Immediate)

**Deliverables:**
* Create `.architecture/templates/AGENTS.md` template
* Define content structure (~100-150 lines)
* Include placeholders for project-specific customization

**Timeline:** 1-2 hours

**Tasks:**
- [ ] Write AGENTS.md template with standard sections
- [ ] Define cross-platform setup instructions
- [ ] Document core workflows (reviews, ADRs, specialist reviews)
- [ ] Add references to assistant-specific documentation
- [ ] Include pragmatic mode activation instructions

### Phase 2: Update CLAUDE.md (Immediate)

**Deliverables:**
* Add header to CLAUDE.md explaining relationship to AGENTS.md
* Reference AGENTS.md for core concepts
* Emphasize CLAUDE.md covers Claude-specific enhancements

**Timeline:** 30 minutes

**Tasks:**
- [ ] Add header section to CLAUDE.md
- [ ] Remove content that should move to AGENTS.md
- [ ] Add cross-references to AGENTS.md where appropriate
- [ ] Update "how to use this file" guidance

### Phase 3: Update Setup Process (Immediate)

**Deliverables:**
* Modify CLAUDE.md setup instructions to generate AGENTS.md
* Customize AGENTS.md based on project analysis
* Ensure both files are created during framework setup

**Timeline:** 1 hour

**Tasks:**
- [ ] Update setup recognition in CLAUDE.md
- [ ] Add AGENTS.md generation step
- [ ] Customize AGENTS.md template based on project tech stack
- [ ] Test setup process with sample project
- [ ] Verify both files are properly created

### Phase 4: Documentation & Testing (Deferred)

**Trigger Conditions:**
- First non-Claude user attempts framework adoption
- Confusion about AGENTS.md vs CLAUDE.md content boundaries
- 3+ questions about which file to update

**Potential Tasks** (deferred):
- Create comprehensive guide explaining file relationships
- Document "which file do I update" decision tree
- Create examples for different AI assistants using AGENTS.md
- Test framework with Cursor, Copilot, Jules, etc.
- Gather feedback from multi-assistant usage

**Justification for Deferral:**
Cannot validate cross-platform functionality without actual users of other assistants. Better to wait for real usage patterns to inform documentation than to create speculative examples.

## Alternatives Considered

### Alternative 1: Continue with CLAUDE.md Only

**Description**: Maintain current approach with only CLAUDE.md, document how other assistants should adapt it.

**Pros:**
* No implementation effort required
* No additional maintenance burden
* Single file to maintain
* No risk of confusion or duplication

**Cons:**
* No alignment with industry standards
* Higher friction for non-Claude users
* Each assistant needs custom documentation
* Doesn't scale to new AI assistants
* Misses discoverability benefits

**Rejected**: Insufficient - limits framework reach and requires custom work for each assistant

### Alternative 2: Replace CLAUDE.md with AGENTS.md

**Description**: Remove CLAUDE.md entirely, put everything in AGENTS.md with sections for different assistants.

**Pros:**
* Single file to maintain
* All assistant instructions in one place
* No cross-referencing needed

**Cons:**
* Loses Claude-specific optimizations (Skills, MCP, hooks)
* File becomes very large and complex
* Mixes cross-platform with assistant-specific content
* Harder to find relevant information
* Doesn't leverage Claude's advanced capabilities

**Rejected**: Throws away Claude Code's unique strengths, creates maintenance burden

### Alternative 3: Create Assistant-Specific AGENTS.md Files

**Description**: Create AGENTS.md, AGENTS-CLAUDE.md, AGENTS-CURSOR.md, etc.

**Pros:**
* Each assistant gets tailored instructions
* Clear separation per assistant
* Can optimize for each tool

**Cons:**
* Not aligned with Agents.md standard (expects single file)
* High maintenance burden (multiple files)
* Duplication across files
* Non-standard approach confuses assistants
* Violates "single entry point" benefit

**Rejected**: Doesn't follow standard, creates excessive maintenance burden

### Alternative 4: Minimal AGENTS.md + Keep CLAUDE.md (Selected)

**Description**: Create minimal AGENTS.md for cross-platform instructions, keep CLAUDE.md for Claude-specific features.

**Pros:**
* Standards compliant (Agents.md)
* Leverages Claude's unique capabilities (CLAUDE.md)
* Clear separation of concerns
* Minimal maintenance burden
* Low implementation effort
* Future-proof for new assistants

**Cons:**
* Two files instead of one
* Need to define clear boundaries
* Risk of some duplication

**Selected**: Best balance of standards compliance, maintainability, and assistant-specific optimization

### Alternative 5: Defer Until Real Need

**Description**: Wait until non-Claude users request framework support before creating AGENTS.md.

**Pros:**
* Zero effort now
* Informed by real user needs
* May never be needed

**Cons:**
* Higher friction for potential adopters today
* Reactive rather than proactive
* Misses opportunity to align with standards early
* May slow adoption unnecessarily

**Partially Rejected**: While waiting for detailed cross-assistant documentation makes sense (deferred to Phase 4), creating basic AGENTS.md now enables adoption and aligns with standards at low cost.

## Pragmatic Enforcer Analysis

**Reviewer**: Pragmatic Enforcer
**Mode**: Balanced

**Overall Decision Complexity Assessment**:

This decision introduces a single additional file (AGENTS.md) to align with an industry standard used by 20,000+ projects. The implementation is intentionally minimal (~100-150 lines) with clear boundaries. This is solving a current problem (friction for non-Claude users) with a proven standard rather than a custom solution.

**Decision Challenge**:

**Proposed Decision**: "Adopt Agents.md standard as complementary layer to CLAUDE.md"

**Necessity Assessment**: 7/10

- **Current need (6/10)**: Framework currently works fine for Claude Code users. However, non-Claude users face friction. We support multiple assistants conceptually but lack universal entry point. Not urgent but actively limiting adoption.

- **Future need (8/10)**: AI assistant ecosystem is rapidly expanding (OpenAI Codex, Google Jules, Cursor, VS Code AI, etc.). Industry standard (20K+ projects) suggests this is becoming table stakes. Framework's value proposition is "collaborative architecture with AI assistants" - limiting to one assistant contradicts this.

- **Cost of waiting (4/10)**: Framework works today without AGENTS.md. However, every potential adopter using non-Claude assistants faces friction. Adoption grows slower. May need to answer "how do I use this with Cursor?" repeatedly. Cost is opportunity cost, not technical debt.

- **Evidence of need**: Industry standard with 20,000+ projects demonstrates clear demand. Framework explicitly supports multiple assistants (.coding-assistants/ directory exists) but lacks entry point.

**Complexity Assessment**: 3/10

- **Added complexity (3/10)**: Single additional file in project root. Well-defined boundaries via content distribution table. Cross-references keep files synchronized. Minimal duplication risk with clear separation.

- **Maintenance burden (3/10)**: One additional file to maintain. However, content boundaries are clear (cross-platform vs. Claude-specific). Cross-references prevent drift. Standard format means less decision-making about structure.

- **Learning curve (2/10)**: Developers need to understand "AGENTS.md for all assistants, CLAUDE.md for Claude features." Clear with simple explanation. Standard location (project root) is familiar. Header in CLAUDE.md explains relationship.

- **Dependencies introduced (1/10)**: No new dependencies. Using existing standard. Both files are plain markdown. No tooling required.

**Alternative Analysis**:

- Alternative 1 (CLAUDE.md only): Simpler (0 additional files) but doesn't solve non-Claude adoption friction. This is maintaining status quo, not solving problem.
- Alternative 2 (Replace CLAUDE.md): Loses Claude-specific optimizations. Not simpler, just different structure.
- Alternative 3 (Multiple AGENTS-*.md files): More complex (multiple files), violates standard.
- Alternative 5 (Defer entirely): Simpler now but misses low-cost opportunity to align with standards.

Selected alternative is genuinely simpler than alternatives 2 & 3, and actively solves problem that alternative 1 & 5 leave unsolved.

**Simpler Alternative Proposal**:

The selected approach (minimal AGENTS.md) already is the simplest approach that solves the problem:

1. **Minimal Content** (~100-150 lines vs. comprehensive documentation)
2. **Clear Boundaries** (content distribution table prevents scope creep)
3. **Deferred Documentation** (Phase 4 waits for real usage)
4. **Leverages Standard** (don't invent custom format)
5. **Preserves Existing** (CLAUDE.md remains for Claude features)

**Potential Simplification**:
Could defer entirely and create AGENTS.md only when first non-Claude user requests it. However, this has marginal benefit (saves 2-3 hours) at cost of ongoing friction and repeated explanations. Creating minimal AGENTS.md now is appropriate scope.

**Recommendation**: ✅ Approve decision with simplifications already applied

**Justification**:

This decision appropriately balances current need with future positioning:

1. **Current Need is Real**: Framework explicitly supports multiple assistants but lacks universal entry point. Non-Claude users face friction today.

2. **Solution is Standard**: Not inventing custom approach. Using industry standard with 20,000+ projects proves viability and discoverability.

3. **Implementation is Minimal**: ~2-4 hours total effort. Single additional file. Clear boundaries prevent scope creep.

4. **Complexity is Low**: 3/10 complexity score. Adding one well-defined file to project root. Standard format reduces decision-making.

5. **Appropriate Deferrals**: Phase 4 (comprehensive docs, cross-assistant testing) properly deferred until real usage demands it.

6. **Preserves Claude Advantages**: Doesn't compromise Claude Code's unique capabilities (Skills, MCP, hooks).

**Pragmatic Score**:
- **Necessity**: 7/10
- **Complexity**: 3/10
- **Ratio**: 0.43 *(Target: <1.5 for balanced mode)* ✅

**Overall Assessment**:

This is appropriate engineering for current needs. Framework's value proposition is multi-assistant support, but lacks standard entry point. Solution uses proven standard rather than custom approach. Implementation is minimal with clear boundaries. Comprehensive documentation appropriately deferred until real usage. Complexity-to-necessity ratio (0.43) well below threshold (1.5).

**Not over-engineering because:**
- Solving real current problem (non-Claude user friction)
- Using standard solution, not custom invention
- Minimal implementation (one file, ~150 lines)
- Appropriate deferrals (extensive docs wait for real usage)
- Low complexity-to-necessity ratio (0.43)

**Recommendation**: Implement Phase 1-3 immediately, defer Phase 4 until triggered by real usage.

## Validation

**Acceptance Criteria:**

**Phase 1-3 (Immediate):**
- [ ] AGENTS.md template created in `.architecture/templates/`
- [ ] Template includes all standard sections (overview, setup, workflows, references)
- [ ] Content boundaries documented in ADR (completed via table above)
- [ ] CLAUDE.md header added explaining relationship to AGENTS.md
- [ ] Setup process generates AGENTS.md during project initialization
- [ ] AGENTS.md customized based on project technology stack
- [ ] Both files maintained during framework setup
- [ ] Cross-references present in both files

**Phase 4 (Deferred):**
- [ ] Comprehensive "which file" decision tree (trigger: 3+ questions)
- [ ] Examples for Cursor, Copilot, Jules usage (trigger: first non-Claude adopter)
- [ ] Cross-assistant testing (trigger: 2+ assistants actively using framework)
- [ ] Multi-assistant usage guide (trigger: user requests)

**Testing Approach:**

**Phase 1-3:**
1. Test setup process creates both AGENTS.md and CLAUDE.md
2. Verify content boundaries match table in ADR
3. Confirm cross-references work correctly
4. Review AGENTS.md template with sample projects (various tech stacks)
5. Verify AGENTS.md contains only cross-platform instructions

**Phase 4 (when triggered):**
1. Test framework usage with multiple AI assistants
2. Gather feedback from non-Claude users
3. Identify confusion points about file boundaries
4. Validate cross-assistant workflows
5. Measure adoption friction before/after

## References

* [Agents.md Standard](https://agents.md/) - Industry standard for AI agent instructions
* [Architectural Principles](../../principles.md) - Pragmatic Simplicity, Domain-Centric Design
* [Framework Members](../../members.yml) - Architecture review team including Pragmatic Enforcer
* [ADR-002: Pragmatic Guard Mode](./ADR-002-pragmatic-guard-mode.md) - Related decision on pragmatic approach
* [CLAUDE.md](../../../CLAUDE.md) - Current Claude-specific instructions
* [.coding-assistants/](../../../.coding-assistants/) - Existing multi-assistant support

## Implementation Notes

**File Location Decisions:**
- AGENTS.md: Project root (standard location per Agents.md spec)
- Template: `.architecture/templates/AGENTS.md` (follows existing template pattern)
- No nested AGENTS.md files initially (defer until monorepo usage emerges)

**Content Boundary Rules:**

**Always in AGENTS.md:**
- Framework overview and purpose
- Generic setup instructions
- Core workflows (reviews, ADRs, specialist reviews)
- Pragmatic mode activation (cross-platform)
- Links to .architecture/ artifacts

**Always in CLAUDE.md:**
- Claude Skills installation and usage
- MCP server integration
- Claude-specific slash commands
- Hooks configuration
- Claude Code-specific request patterns

**In Both (with different detail levels):**
- Setup process (generic in AGENTS.md, Claude-optimized in CLAUDE.md)
- Architecture reviews (how to request in AGENTS.md, Skills usage in CLAUDE.md)
- ADR creation (basic process in AGENTS.md, MCP tools in CLAUDE.md)

**Migration Strategy:**

No migration needed for existing projects - they can continue using CLAUDE.md only. New projects created with updated setup process get both files. Existing projects can add AGENTS.md if they want to support multiple assistants.

**Rollout Plan:**

1. **Week 1**: Create templates and update setup process
2. **Week 1**: Test with sample project setup
3. **Week 1**: Update framework documentation
4. **Ongoing**: Monitor for Phase 4 trigger conditions
5. **As needed**: Expand AGENTS.md based on real usage patterns

---

**Decision Date**: 2025-11-20
**Implementation Date**: 2025-11-20
**Status**: Accepted - Phase 1-3 Complete
**Author**: Collaborative architectural analysis (Systems Architect, AI Engineer, Domain Expert, Maintainability Expert, Security Specialist, Pragmatic Enforcer)

## Implementation Results

**Phase 1-3 Completed**: 2025-11-20 (~1.5 hours)

**Deliverables:**
- ✅ `.architecture/templates/AGENTS.md` - 9.7 KB template with placeholders
- ✅ `CLAUDE.md` - Updated with "About This File" section and AGENTS.md references
- ✅ Setup process modified to generate AGENTS.md during project initialization
- ✅ Content boundaries validated against distribution table
- ✅ Cross-references implemented in both files

**Validation:**
- All Phase 1-3 acceptance criteria met
- Content distribution matches ADR specification
- Pragmatic score maintained: 0.43 (complexity/necessity ratio)
- Implementation time within estimates

**Phase 4 Status**: Deferred, tracking trigger conditions:
- First non-Claude adopter feedback
- 3+ questions about file boundaries
- 2+ assistants actively using framework
- User requests for comprehensive cross-assistant guide

**Next Steps**:
- Monitor Phase 4 trigger conditions
- Gather feedback from new framework installations
- Track adoption across different AI assistants
- Update documentation based on real usage patterns
