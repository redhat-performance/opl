# Architecture Review: CLAUDE.md Best Practices from HumanLayer Article

**Review Date**: 2025-12-04
**Review Type**: External Best Practices Analysis
**Source**: [HumanLayer Blog - Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
**Context**: Analysis of industry best practices for CLAUDE.md documentation to inform our AI Software Architect framework

## Executive Summary

This review analyzes HumanLayer's recommendations for writing effective CLAUDE.md files through the lens of our architecture team. The article presents research-backed insights on LLM instruction capacity, documentation structure, and practical guidelines that have significant implications for our framework's approach to AI assistant onboarding.

**Key Findings**:
- LLMs have limited instruction-following capacity (~150-200 instructions)
- Claude Code's system prompt already consumes ~50 instructions
- File length consensus: under 300 lines, with best practices under 60 lines
- Progressive disclosure through separate files is superior to comprehensive single files
- Tool-based enforcement (linters, formatters) should replace documentation-based style guidance
- Manual curation is critical for this "highest leverage point" in AI workflows

---

## Individual Member Reviews

### AI Engineer - LLM Integration & Effectiveness

**Perspective**: As an AI Engineer specializing in LLM application design, I evaluate these recommendations through the lens of practical AI system performance and user experience.

#### Critical Findings

**1. Instruction Capacity Constraints (CRITICAL)**
The article's revelation about LLM instruction limits (~150-200 total) is fundamental:
- Claude Code already uses ~50 instructions in system prompt
- Leaves only 100-150 instructions for project-specific guidance
- Our current CLAUDE.md has 572 lines with extensive procedural instructions
- **Risk**: We're likely exceeding optimal instruction density, causing degraded performance

**Measurement**: Our CLAUDE.md contains approximately:
- 7 major request recognition patterns (Setup, Update, Implementation, Reviews, Pragmatic Mode)
- Each pattern has 5-10 detailed steps
- Estimated 70-100 discrete instructions
- **Assessment**: At upper boundary of optimal range, but includes redundancy

**2. Claude Code's System Reminder Behavior (HIGH PRIORITY)**
The article reveals Claude Code injects: "may or may not be relevant to tasks"
- Claude actively filters out non-universally-applicable instructions
- Explains why task-specific "hotfixes" often fail
- Our framework includes setup/update procedures that are rarely relevant during normal work
- **Impact**: Setup instructions consuming instruction budget without delivering value

**3. Progressive Disclosure Pattern (BEST PRACTICE)**
Recommendation to separate task-specific guidance into `agent_docs/` files:
- Reduces main file instruction density
- Allows targeted loading of relevant context
- Aligns with how Claude Code's Task tool works
- **Opportunity**: Restructure our extensive request recognition patterns

#### Recommendations

1. **Immediate**: Separate infrequently-used patterns (Setup, Update) into `agent_docs/setup-guide.md`
2. **High Priority**: Reduce Implementation Command Recognition from 100+ lines to pointer reference
3. **Best Practice**: Create modular documentation structure:
   - `CLAUDE.md`: Core concepts, 50-100 lines
   - `agent_docs/setup.md`: Setup procedures
   - `agent_docs/implementation.md`: Implementation methodology details
   - `agent_docs/reviews.md`: Review process details
   - `agent_docs/pragmatic-mode.md`: Pragmatic mode mechanics

4. **Measurement**: Track actual instruction effectiveness through user feedback

#### Trade-offs

**Restructuring Benefits**:
- Clearer cognitive load for Claude
- Faster initial context processing
- Better alignment with Claude Code's filtering behavior
- More maintainable documentation

**Restructuring Costs**:
- Migration effort for existing users
- Need to update documentation to reference new structure
- Potential confusion if not communicated clearly

**Recommendation**: Benefits significantly outweigh costs. This is a critical optimization.

---

### Maintainability Expert - Documentation Quality

**Perspective**: As a Maintainability Expert, I assess these recommendations against long-term documentation health, developer comprehension, and maintenance burden.

#### Critical Findings

**1. File Length Anti-Pattern (HIGH PRIORITY)**
Our current CLAUDE.md at 572 lines significantly exceeds recommendations:
- HumanLayer consensus: < 300 lines
- HumanLayer's own file: < 60 lines
- Industry best practice: focused, relevant context over comprehensive coverage
- **Impact**: Reduced Claude comprehension, slower processing, maintenance burden

**Root Cause Analysis**:
- Comprehensive procedural documentation for all scenarios
- Detailed step-by-step instructions for each request type
- Examples and edge cases inline
- No separation between "always relevant" and "sometimes relevant" content

**2. Progressive Disclosure Pattern (BEST PRACTICE)**
The recommendation for separate markdown files addresses multiple maintainability concerns:
- **Findability**: Specific topics in dedicated files easier to locate
- **Updateability**: Changes scoped to single concern
- **Testability**: Easier to validate specific guidance in isolation
- **Reusability**: Task-specific docs can be referenced by multiple contexts

**3. Reference vs Embedding Pattern (CRITICAL)**
Article's guidance on `file:line` pointers vs code snippets:
- Embedded code becomes stale (maintenance burden)
- File references stay current automatically
- Reduces duplication and version skew
- **Assessment**: We currently use descriptive text, not code snippets, so partially compliant

#### Recommendations

1. **Restructure for Maintainability**:
   ```
   CLAUDE.md (60-100 lines)
   ├── Core principles (what/why/how)
   ├── Project overview
   ├── Quick reference links to agent_docs/
   └── Critical-always-relevant guidelines

   agent_docs/
   ├── setup-guide.md (full setup procedures)
   ├── implementation-guide.md (methodology details)
   ├── review-workflows.md (review processes)
   ├── pragmatic-mode-guide.md (YAGNI enforcement)
   └── troubleshooting.md (common issues)
   ```

2. **Maintenance Protocol**:
   - Review CLAUDE.md quarterly for relevance
   - Track which sections are actually used (user feedback)
   - Remove or relocate underutilized content
   - Maintain < 100 line target for main file

3. **Documentation Quality Standards**:
   - Every instruction must be universally applicable
   - No task-specific workarounds in main file
   - All examples moved to separate guides
   - Clear pointer references to detailed documentation

#### Trade-offs

**Current State Benefits**:
- Everything in one place
- No ambiguity about what's available
- Comprehensive coverage

**Current State Costs**:
- Exceeds LLM instruction capacity
- Difficult to maintain
- Slower processing
- Some content filtered by Claude Code

**Recommended State Benefits**:
- Optimal instruction density
- Better maintainability
- Faster processing
- Aligned with Claude Code behavior

**Recommended State Costs**:
- Learning curve for modular structure
- Need to know where to look
- More files to manage

**Recommendation**: Strongly favor restructuring. The maintenance and performance benefits are substantial.

---

### Systems Architect - Overall System Coherence

**Perspective**: As a Systems Architect, I evaluate how these recommendations affect the overall architecture documentation system and cross-assistant compatibility.

#### Critical Findings

**1. CLAUDE.md Role in System Architecture (CRITICAL)**
The article positions CLAUDE.md as a "highest leverage point":
- Affects every Claude Code interaction
- Primary onboarding mechanism for AI assistants
- Disproportionate impact on all downstream work
- **Insight**: This validates our investment in comprehensive CLAUDE.md but suggests we're over-investing in the wrong way

**Current Architecture**:
```
CLAUDE.md (572 lines, comprehensive)
  ├── Setup procedures (rarely used)
  ├── Update procedures (rarely used)
  ├── Implementation guidance (sometimes used)
  ├── Review workflows (frequently used)
  └── Pragmatic mode (sometimes used)
```

**Optimal Architecture** (based on article):
```
CLAUDE.md (60-100 lines, high-leverage content)
  ├── Project essence (what/why/how)
  ├── Architecture framework overview
  └── Pointers to detailed guides

agent_docs/ (detailed, context-specific)
  ├── setup-guide.md
  ├── implementation-guide.md
  ├── review-workflows.md
  └── pragmatic-mode-guide.md
```

**2. Cross-Assistant Compatibility (MEDIUM PRIORITY)**
Our framework supports Claude, Cursor, and Copilot:
- Article is Claude-specific
- Other assistants may have different instruction capacities
- Progressive disclosure pattern is universally beneficial
- **Consideration**: AGENTS.md remains the cross-platform core

**System Coherence**:
- AGENTS.md: Cross-platform principles (unchanged)
- CLAUDE.md: Claude-optimized quick reference
- agent_docs/: Detailed task-specific guides (universal)
- .architecture/: Architecture artifacts (unchanged)

**3. Integration with Existing Architecture Documentation (HIGH PRIORITY)**
Our `.architecture/` directory already follows modular pattern:
- ADRs in separate files
- Reviews in separate files
- Templates in separate directory
- **Insight**: We already practice progressive disclosure for architecture artifacts, just not for assistant instructions

**Alignment Opportunity**: Apply same modular principles to CLAUDE.md that we use for architecture documentation.

#### Recommendations

1. **Architectural Refactoring**:
   - Treat CLAUDE.md as "index" not "encyclopedia"
   - Move detailed procedures to agent_docs/
   - Maintain coherence with AGENTS.md (cross-platform core)
   - Keep .architecture/ modular structure (no changes needed)

2. **System Integration**:
   - Reference agent_docs/ from CLAUDE.md
   - Agent docs can reference .architecture/ when needed
   - Maintain clear separation of concerns:
     - AGENTS.md: What the framework does (cross-platform)
     - CLAUDE.md: How Claude accesses it (Claude-specific)
     - agent_docs/: Detailed procedures (universal)
     - .architecture/: Architecture artifacts (domain content)

3. **Version Management**:
   - CLAUDE.md version stays aligned with framework version
   - agent_docs/ can version independently if needed
   - Clear documentation of which versions are compatible

#### Trade-offs

**System Coherence Benefits**:
- Clear separation of concerns
- Modular, maintainable structure
- Scales with framework growth
- Aligns with existing architecture patterns

**System Coherence Costs**:
- More moving parts
- Need clear navigation
- Documentation of documentation needed

**Recommendation**: Refactor CLAUDE.md to match the modular architecture we already use successfully in .architecture/. This brings system coherence and aligns with article recommendations.

---

### Pragmatic Enforcer - Simplicity & YAGNI

**Perspective**: As the Pragmatic Enforcer, I evaluate whether these recommendations align with YAGNI principles and whether we're over-engineering our documentation.

#### Critical Findings

**1. Documentation Over-Engineering (CRITICAL)**
Our 572-line CLAUDE.md is a classic example of premature optimization:
- **"But what if..."**: We documented every possible request pattern
- **"For completeness..."**: We included comprehensive step-by-step instructions
- **"Just in case..."**: We added examples and edge cases
- **Reality Check**: How often are Setup instructions actually used? Once per project.

**YAGNI Analysis**:
- Setup procedures: Used once, consume ~100 lines, take ~20 instructions
- Update procedures: Used rarely, consume ~60 lines, take ~10 instructions
- Implementation details: Used sometimes, consume ~170 lines, take ~30 instructions
- **Waste**: ~330 lines (57%) used infrequently but loaded always

**2. Linter Anti-Pattern (HIGH PRIORITY)**
Article explicitly recommends: "Don't Use Linters" in CLAUDE.md
- Style enforcement should be tool-based, not instruction-based
- We don't currently include linter instructions, but we include extensive style guidance in Implementation section
- **Question**: Do we need methodology instructions in CLAUDE.md, or should configuration files + tool hooks handle this?

**Pragmatic Challenge**:
```yaml
# Instead of 170 lines of implementation methodology in CLAUDE.md:
implementation:
  methodology: "TDD"
  influences:
    - "Kent Beck"
    - "Sandi Metz"
  # ... (in .architecture/config.yml)
```

Plus a simple hook/slash command that applies these during implementation.

**3. Manual Curation Value (MEDIUM PRIORITY)**
Article states: "Avoid Auto-Generation" - this is a "highest leverage point"
- **Agreement**: We advocate manual curation
- **But**: Is 572 lines of manual curation better than 60 lines?
- **YAGNI Principle**: Manual curation doesn't mean comprehensive curation

#### Recommendations

**Necessity Assessment**:

| Content | Current Need (0-10) | Future Need (0-10) | Cost of Waiting (0-10) |
|---------|---------------------|--------------------|-----------------------|
| Setup procedures in CLAUDE.md | 1 (once per project) | 1 | 0 (can reference separate doc) |
| Update procedures in CLAUDE.md | 1 (rarely used) | 1 | 0 (can reference separate doc) |
| Implementation methodology details | 4 (sometimes) | 6 | 2 (losing context) |
| Review workflows overview | 8 (frequently) | 9 | 7 (core workflow) |
| Pragmatic mode overview | 6 (when enabled) | 7 | 4 (important feature) |

**Complexity Assessment**:

| Content | Added Complexity (0-10) | Maintenance Burden (0-10) | Learning Curve (0-10) |
|---------|-------------------------|---------------------------|-----------------------|
| Current CLAUDE.md | 8 (cognitive overload) | 9 (must maintain all) | 7 (too much to absorb) |
| Proposed structure | 4 (clear separation) | 5 (more files, but scoped) | 5 (need to navigate) |

**Simpler Alternative**:
```markdown
# CLAUDE.md (60 lines)

## About This Project
AI Software Architect: Architecture documentation framework for AI coding assistants.

## Structure
- `.architecture/`: Architecture decisions, reviews, recalibration
- `agent_docs/`: Detailed guidance for AI assistants
- `AGENTS.md`: Cross-platform instructions

## Key Workflows
- **Architecture Reviews**: See agent_docs/review-workflows.md
- **Create ADRs**: See agent_docs/adr-creation.md
- **Setup Framework**: See agent_docs/setup-guide.md
- **Implementation**: See agent_docs/implementation-guide.md

## Quick Reference
Members: .architecture/members.yml
Principles: .architecture/principles.md
Config: .architecture/config.yml
```

**Recommendation by Section**:
1. **Setup/Update procedures**: DEFER to agent_docs/ (0% need in normal workflow)
2. **Implementation methodology details**: SIMPLIFY to config + pointer (20% current size)
3. **Review workflows**: KEEP but simplify to essentials + pointer (50% current size)
4. **Pragmatic mode**: KEEP but simplify to essentials + pointer (50% current size)

**Overall Recommendation**: IMPLEMENT NOW
- Clear necessity: Performance and maintainability issues
- Clear benefit: Aligned with LLM capacity and best practices
- Low cost: Refactoring existing content, not creating new
- High value: Affects all AI assistant interactions

#### Trade-offs

**Simplification Benefits**:
- Respects LLM instruction capacity
- Faster processing
- Easier to maintain
- Clearer cognitive model
- Aligns with YAGNI and best practices

**Simplification Costs**:
- Need to navigate to agent_docs/ for details
- More files to manage
- Learning curve for new structure

**Justification**: The costs are minimal and the benefits are substantial. This is exactly the kind of simplification pragmatic mode advocates for.

---

### Domain Expert - Business Logic & User Needs

**Perspective**: As a Domain Expert, I evaluate these recommendations against the needs of our actual users: developers setting up and using the AI Software Architect framework.

#### Critical Findings

**1. User Journey Mismatch (HIGH PRIORITY)**
Analyzing typical user interactions with CLAUDE.md:

**Frequency Analysis**:
- **One-time**: Setup framework (once per project)
- **Rare**: Update framework (quarterly or less)
- **Occasional**: Understand implementation methodology (when questions arise)
- **Frequent**: Request architecture reviews (multiple times per project)
- **Frequent**: Create ADRs (multiple times per project)
- **Occasional**: Enable/use pragmatic mode (once, then forget)

**Current Structure vs. User Needs**:
- CLAUDE.md loads all content for every interaction
- Setup instructions (one-time) consume same attention as reviews (frequent)
- No prioritization based on actual usage patterns
- **Impact**: User needs not aligned with content structure

**2. Semantic Boundaries (MEDIUM PRIORITY)**
The article's WHAT/WHY/HOW framework reveals our semantic confusion:

**Current CLAUDE.md mixes**:
- WHAT: Framework structure and capabilities (good)
- WHY: Architectural principles (good)
- HOW: Detailed procedures (too detailed, should reference elsewhere)

**Optimal Semantic Model**:
```
CLAUDE.md:
  - WHAT: AI Software Architect framework overview
  - WHY: Structured architecture documentation
  - HOW: Pointer references to detailed guides

agent_docs/:
  - Detailed HOW for specific tasks
```

**3. Mental Model Alignment (HIGH PRIORITY)**
Users mental model: "I want to [do task]"
- Current: Read 572 lines to find task guidance
- Optimal: See task in quick reference, follow pointer

**Domain Language Clarity**:
The article recommends progressive disclosure aligns with how users think:
- "I need to set up the framework" → agent_docs/setup-guide.md
- "I want an architecture review" → agent_docs/review-workflows.md
- "I need to create an ADR" → agent_docs/adr-creation.md

This matches domain language better than monolithic documentation.

#### Recommendations

1. **User-Centric Restructuring**:
   ```markdown
   # CLAUDE.md - Organized by user journey frequency

   ## Always Relevant (loaded every interaction)
   - Project overview (WHAT/WHY)
   - Directory structure
   - Core principles

   ## Frequently Used (quick reference + pointer)
   - Architecture reviews → agent_docs/review-workflows.md
   - ADR creation → agent_docs/adr-creation.md
   - Pragmatic mode → agent_docs/pragmatic-mode-guide.md

   ## Occasionally Used (pointer only)
   - Setup → agent_docs/setup-guide.md
   - Update → agent_docs/update-guide.md
   - Implementation → agent_docs/implementation-guide.md
   ```

2. **Domain Language Alignment**:
   - Use user's task language in quick reference
   - Match file names to user intents
   - Provide examples in domain terms (not technical abstractions)

3. **User Feedback Loop**:
   - Track which agent_docs are accessed most
   - Identify gaps in quick reference
   - Iterate on pointer descriptions for clarity

#### Trade-offs

**User-Centric Benefits**:
- Matches how users actually think and work
- Faster task completion
- Less cognitive load
- Better discovery of available features

**User-Centric Costs**:
- Need to educate users on new structure
- Potential initial confusion
- More files to navigate

**Recommendation**: Strongly favor user-centric restructuring. The domain model will be clearer and more aligned with actual usage patterns.

---

## Collaborative Discussion

### Convergent Findings

All architecture members converge on several critical points:

**1. UNANIMOUS: File Length Reduction Critical**
- **AI Engineer**: Exceeds LLM instruction capacity
- **Maintainability Expert**: Maintenance burden and comprehension issues
- **Systems Architect**: Violates modular architecture principles
- **Pragmatic Enforcer**: Over-engineering, YAGNI violation
- **Domain Expert**: Doesn't match user needs

**Consensus**: Reduce CLAUDE.md to < 100 lines, move detailed procedures to agent_docs/

**2. UNANIMOUS: Progressive Disclosure Best Practice**
All members recognize benefits of modular documentation:
- Better performance (AI Engineer)
- Better maintainability (Maintainability Expert)
- Better architecture (Systems Architect)
- Simpler (Pragmatic Enforcer)
- User-centric (Domain Expert)

**Consensus**: Implement agent_docs/ structure immediately

**3. MAJORITY: Tool-Based Enforcement Over Documentation**
- **AI Engineer**: Saves instruction capacity
- **Pragmatic Enforcer**: Simpler, more reliable
- **Systems Architect**: Better separation of concerns
- **Note**: Maintainability Expert and Domain Expert neutral

**Consensus**: Move style/methodology enforcement to config files + hooks/slash commands

### Divergent Perspectives

**1. Granularity of agent_docs/ Files**
- **Maintainability Expert**: More files = better maintainability
- **Pragmatic Enforcer**: Too many files = over-engineering
- **Resolution**: Balance - one file per major workflow, combined files for related tasks

**2. Quick Reference Verbosity**
- **Domain Expert**: More context in quick reference for user clarity
- **AI Engineer**: Minimal quick reference to preserve instruction capacity
- **Resolution**: Brief description (1-2 sentences) + pointer, details in agent_docs

**3. Migration Strategy**
- **Pragmatic Enforcer**: YAGNI - just do it
- **Systems Architect**: Careful migration with version compatibility
- **Resolution**: Immediate refactoring with clear communication and backwards-compatible pointers

---

## Consolidated Recommendations

### Critical Priority (Implement Immediately)

**1. Restructure CLAUDE.md to < 100 Lines**
- **Action**: Move 80% of current content to agent_docs/
- **Retain**: Project overview, quick reference, high-leverage guidance
- **Move**: Setup, update, detailed procedures
- **Timeline**: Single refactoring session
- **Impact**: Dramatic improvement in Claude Code performance

**2. Create Progressive Disclosure Structure**
- **Action**: Create agent_docs/ directory with modular guides
- **Structure**:
  ```
  agent_docs/
  ├── setup-guide.md (setup procedures)
  ├── review-workflows.md (architecture reviews)
  ├── adr-creation.md (ADR creation)
  ├── implementation-guide.md (methodology details)
  ├── pragmatic-mode-guide.md (YAGNI enforcement)
  └── troubleshooting.md (common issues)
  ```
- **Timeline**: Reorganize existing content
- **Impact**: Better maintainability, clearer user paths

**3. Document Instruction Capacity Constraints**
- **Action**: Create ADR documenting LLM instruction limits
- **Content**: Research findings, implications for framework
- **Reference**: HumanLayer article, instruction capacity research
- **Timeline**: Immediate
- **Impact**: Informs all future documentation decisions

### High Priority (Implement Soon)

**4. Move Style Enforcement to Configuration**
- **Action**: Leverage .architecture/config.yml for implementation methodology
- **Enhancement**: Create slash commands or hooks for enforcement
- **Benefit**: Saves instruction capacity, more reliable enforcement
- **Timeline**: Next enhancement cycle

**5. Establish Documentation Quality Standards**
- **Action**: Create guidelines for CLAUDE.md and agent_docs/ content
- **Standards**:
  - CLAUDE.md < 100 lines
  - Each agent_docs file < 200 lines
  - Only universally-applicable instructions in CLAUDE.md
  - Task-specific guidance in agent_docs/
  - Quarterly review of relevance
- **Timeline**: Document after restructuring

### Medium Priority (Consider)

**6. User Feedback Mechanism**
- **Action**: Track which agent_docs are accessed
- **Benefit**: Data-driven documentation improvement
- **Method**: User surveys, usage analytics
- **Timeline**: After restructuring stabilizes

**7. Cross-Assistant Documentation Review**
- **Action**: Ensure agent_docs/ structure works for Cursor, Copilot
- **Consideration**: Different instruction capacities
- **Timeline**: After CLAUDE.md restructuring complete

---

## Implementation Roadmap

### Phase 1: Immediate Refactoring (1-2 days)

1. **Create agent_docs/ Directory Structure**
   - Set up directory
   - Create placeholder files

2. **Extract Content from CLAUDE.md**
   - Move setup procedures → agent_docs/setup-guide.md
   - Move update procedures → agent_docs/update-guide.md
   - Move implementation details → agent_docs/implementation-guide.md
   - Move review details → agent_docs/review-workflows.md
   - Move pragmatic mode details → agent_docs/pragmatic-mode-guide.md

3. **Rewrite CLAUDE.md as Quick Reference**
   - Project overview (WHAT/WHY)
   - Directory structure
   - Quick reference with pointers
   - Target: < 100 lines

4. **Create ADR for Instruction Capacity**
   - Document research findings
   - Document restructuring decision
   - Reference HumanLayer article

### Phase 2: Enhancement (1 week)

5. **Create Enforcement Mechanisms**
   - Slash commands for common workflows
   - Hooks for style enforcement
   - Leverage existing config.yml

6. **Documentation Quality Standards**
   - Document guidelines
   - Review existing agent_docs/ against standards
   - Refine as needed

### Phase 3: Validation (Ongoing)

7. **User Feedback**
   - Monitor user experience
   - Track agent_docs/ usage
   - Iterate on structure

8. **Cross-Assistant Testing**
   - Verify with Cursor
   - Verify with Copilot
   - Adjust as needed

---

## Success Metrics

**Performance Metrics**:
- CLAUDE.md line count: Target < 100 (currently 572)
- Estimated instruction count: Target < 30 (currently ~100)
- Content separation: 80% task-specific content moved to agent_docs/

**Quality Metrics**:
- Documentation findability: User survey (target > 8/10)
- Task completion time: Measure before/after refactoring
- Maintenance burden: Track documentation update frequency

**Adoption Metrics**:
- agent_docs/ access frequency
- User feedback on new structure
- Issue reports related to documentation

---

## Conclusion

The HumanLayer article provides research-backed guidance that reveals critical issues with our current CLAUDE.md structure. All architecture members agree on the need for immediate restructuring:

**Critical Issues**:
1. File length (572 lines) exceeds LLM instruction capacity
2. Instruction density (~100) at upper boundary of optimal range
3. Task-specific content loaded for every interaction
4. Maintenance burden from monolithic structure

**Recommended Solution**:
1. Reduce CLAUDE.md to < 100 lines (quick reference)
2. Create agent_docs/ with progressive disclosure
3. Move tool enforcement to configuration + hooks
4. Document instruction capacity constraints in ADR

**Expected Benefits**:
- Improved Claude Code performance
- Better maintainability
- Clearer user experience
- Alignment with industry best practices

**Next Steps**:
1. Implement Phase 1 refactoring immediately
2. Create ADR documenting instruction capacity constraints
3. Create ADR documenting progressive disclosure pattern
4. Update documentation to reference new structure

This restructuring aligns with our existing modular architecture patterns, respects LLM capabilities, and serves our users' actual needs more effectively.
