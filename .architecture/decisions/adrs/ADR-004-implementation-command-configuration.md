# ADR-004: Implementation Command with Configuration

## Status

Accepted

**Implementation Date**: 2025-11-20

## Context

Users of the AI Software Architect framework currently need to specify implementation methodology, coding influences, and practices in every implementation session through lengthy prompts.

### Current User Workflow

A typical implementation request looks like:

> "Implement the next steps iteratively as the software architects, specifically the pragmatic enforcer. Follow TDD taking inspiration from Gary Bernhardt (from Destroy All Software). Refactor as needed following best-practices taking inspiration from Sandi Metz, Kent Beck, and Martin Fowler. Glean ruby design inspiration from Jeremy Evans and Vladimir Dementyev."

**Characteristics:**
- **Verbose**: 40+ words to specify methodology and influences
- **Repetitive**: Same guidance needed every implementation session
- **Inconsistent**: Easy to forget key influences or practices
- **Context Loss**: Preferences don't persist between sessions
- **Manual**: Requires careful prompt crafting each time

### Problem Impact

**User Pain Points:**
1. **Prompt Fatigue**: Typing long prompts repeatedly
2. **Inconsistency**: Different sessions may omit influences
3. **Context Loss**: No memory of successful approaches
4. **Onboarding Friction**: New team members don't know team standards
5. **Quality Variance**: Implementation quality depends on prompt completeness

**Time Cost:**
- Average prompt: ~40 words, ~30 seconds to type
- Multiple implementations per day
- Cumulative: Hours per week on repetitive prompting

### Desired Workflow

**Simple command:**
```
"Implement authentication as the architects"
```

**AI behavior:**
1. Recognizes implementation command
2. Reads `.architecture/config.yml` implementation section
3. Applies configured methodology (TDD, BDD, etc.)
4. References configured influences (Kent Beck, Sandi Metz, etc.)
5. Uses language-specific practices
6. Implements with full context automatically

**Result:**
- 90% reduction in prompt length (40 words → 4 words)
- 100% consistency (config always applied)
- Zero context loss (config persists)
- Better quality (systematic application of best practices)

### Existing Pattern in Framework

This follows the **pragmatic_mode** pattern in config.yml:

```yaml
# Existing: Pragmatic Mode
pragmatic_mode:
  enabled: true
  intensity: balanced
  apply_to:
    individual_reviews: true
```

```yaml
# New: Implementation Configuration
implementation:
  enabled: true
  methodology: "TDD"
  influences: [...]
```

Same structure, same file, same configuration-driven behavior pattern.

## Decision Drivers

* **Real User Need**: User has this workflow today (not speculative)
* **High Value**: 90% reduction in prompt length, consistent quality
* **Low Complexity**: Follows existing config.yml pattern
* **Backward Compatible**: Optional feature, doesn't affect existing projects
* **Cross-Assistant**: Works with all AI assistants via AGENTS.md
* **Quality Improvement**: Systematic application of best practices
* **Knowledge Capture**: Team standards documented in config
* **Pragmatic Assessment**: Necessity 8/10, Complexity 3/10, Ratio 0.375 ✅

## Decision

We will implement an **"Implement as the Architects" command** backed by configuration in `.architecture/config.yml` that specifies:

1. **Development Methodology**: TDD, BDD, DDD, Test-Last, Exploratory, or custom
2. **Coding Influences**: Thought leaders and authorities (Kent Beck, Sandi Metz, etc.)
3. **Language-Specific Practices**: Idioms, conventions, frameworks
4. **Testing Approach**: Framework, style, coverage goals
5. **Refactoring Guidelines**: When and how to refactor
6. **Quality Standards**: Definition of done
7. **Security Practices**: Mandatory security requirements

**Command Recognition:**
- "Implement X as the architects" → Apply configuration
- "Implement as the architects" → Apply with prior context
- "Implement X as [specific architect]" → Use member's methodology

**Configuration-Driven Behavior:**
```
User Command → Read config.yml → Extract implementation section → Apply methodology + influences + practices → Implement
```

**Architectural Components Affected:**
* `.architecture/templates/config.yml` - Add implementation section
* `CLAUDE.md` - Add command recognition and application logic
* `AGENTS.md` - Document cross-platform usage
* `.architecture/members.yml` - Optional: methodology fields for members

**Interface Changes:**
* New command pattern recognized by AI assistants
* Configuration controls implementation behavior
* Optional per-project customization
* Integration with existing architecture process

## Implementation

### Phase 1: Core Feature (Implement Now - ~1 hour)

**Deliverable 1: Enhanced config.yml Template** (20 minutes)

Add implementation section to `.architecture/templates/config.yml`:

```yaml
# ==============================================================================
# IMPLEMENTATION GUIDANCE
# ==============================================================================
# Configure how AI assistants implement features when you use:
# "Implement X as the architects"

implementation:
  enabled: true
  methodology: "TDD"  # TDD, BDD, DDD, Test-Last, Exploratory

  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR, 99 Bottles"
    - "Martin Fowler - Refactoring"

  languages:
    ruby:
      style_guide: "Rubocop"
      idioms: "Blocks over loops, meaningful names"

  quality:
    definition_of_done:
      - "Tests passing"
      - "Code refactored"
      - "Code reviewed"
```

**Deliverable 2: Command Recognition in CLAUDE.md** (20 minutes)

Add "Implementation Command Recognition" section:
- Pattern recognition logic
- Configuration reading process
- Methodology application guidance
- Examples of usage

**Deliverable 3: Cross-Platform Documentation in AGENTS.md** (20 minutes)

Add "Implementing Features with Configured Methodology" section:
- How to configure
- How to use commands
- Example configurations for common workflows
- Cross-assistant compatibility notes

**Timeline:** 1 hour total

### Phase 2: Deferred Enhancements

**Track Trigger Conditions:**

**Global User Configuration** (~/.architecture/config.yml)
- **Trigger**: 3+ users request personal defaults across projects
- **Trigger**: "How do I set this for all my projects?"
- **Effort**: ~2 hours

**Member Methodology Fields** (members.yml)
- **Trigger**: Users want "Implement X as [specific member]"
- **Trigger**: Need different methodologies per architect
- **Effort**: ~1 hour

**Implementation Validation/Reporting**
- **Trigger**: Users request compliance checking
- **Trigger**: "Verify TDD was followed"
- **Effort**: ~4 hours

**Language-Specific Profiles**
- **Trigger**: Multi-language projects need per-language configs
- **Trigger**: "Different methodology for frontend vs backend"
- **Effort**: ~3 hours

## Configuration Structure

### Minimal Configuration (Quick Start)

```yaml
implementation:
  enabled: true
  methodology: "TDD"
  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR"
```

### Complete Configuration (Full Options)

```yaml
implementation:
  enabled: true

  # Primary development methodology
  methodology: "TDD"

  # Coding influences
  influences:
    - "Kent Beck - TDD by Example (methodology)"
    - "Gary Bernhardt - Destroy All Software (TDD techniques)"
    - "Sandi Metz - POODR, 99 Bottles (OO design)"
    - "Martin Fowler - Refactoring (patterns)"
    - "Jeremy Evans - Roda, Sequel (Ruby idioms)"
    - "Vladimir Dementyev - Modern Ruby practices"

  # Language-specific practices
  languages:
    ruby:
      style_guide: "Rubocop"
      idioms: "Prefer blocks, meaningful names, Ruby 3+ features"
      frameworks:
        rails: "Follow conventions, service objects for complex logic"

  # Testing approach
  testing:
    framework: "RSpec"
    style: "Outside-in TDD (Detroit school)"
    approach: "Mock judiciously, prefer real objects"
    speed: "Fast unit tests (<100ms)"

  # Refactoring guidelines
  refactoring:
    when:
      - "After tests green (red-green-REFACTOR)"
      - "When code smells emerge"
      - "Rule of Three: refactor on third occurrence"
    principles:
      - "Small methods (≤5 lines per Sandi Metz)"
      - "Clear names over comments"

  # Quality standards
  quality:
    definition_of_done:
      - "Tests passing"
      - "Code refactored"
      - "No code smells"
      - "Code reviewed"
    priorities:
      - "Clarity first"
      - "Simplicity second"
      - "Performance third"

  # Security practices (always applied)
  security:
    mandatory_practices:
      - "Input validation"
      - "Output encoding"
      - "Parameterized queries"
```

### Example: User's Ruby TDD Workflow

```yaml
implementation:
  enabled: true
  methodology: "TDD"

  influences:
    - "Kent Beck - TDD by Example"
    - "Gary Bernhardt - Destroy All Software"
    - "Sandi Metz - POODR, 99 Bottles"
    - "Martin Fowler - Refactoring"
    - "Jeremy Evans - Roda, Sequel patterns"
    - "Vladimir Dementyev - Modern Ruby"

  languages:
    ruby:
      style_guide: "Rubocop"
      idioms: "Blocks over loops, meaningful names"

  testing:
    framework: "RSpec"
    style: "Outside-in TDD"

  refactoring:
    when: ["After tests green", "When smells emerge"]
    principles: ["Small methods", "Clear names"]

  quality:
    definition_of_done:
      - "Tests passing"
      - "Code refactored"
      - "Code reviewed"
```

## Alternatives Considered

### Alternative 1: Do Nothing (Status Quo)

**Description**: Continue with manual prompts each session

**Pros:**
* Zero implementation effort
* No added complexity
* No maintenance burden

**Cons:**
* User continues repetitive prompting forever
* Quality inconsistency continues
* No team standards documentation
* Context loss between sessions

**Rejected**: Doesn't solve user's real, ongoing pain point

### Alternative 2: Documentation File (implementation.md)

**Description**: Create markdown file with implementation guidance for AI to read

**Pros:**
* Human-readable prose
* Can include detailed examples
* Flexible format

**Cons:**
* Harder for AI to parse than YAML
* Separate file to maintain
* Not configuration-driven (less structured)
* Doesn't follow existing patterns

**Rejected**: More complex than config approach, doesn't leverage existing patterns

### Alternative 3: Member Enhancement Only

**Description**: Add methodology fields to members.yml, no separate config

**Pros:**
* Single file modification
* Leverages existing member system

**Cons:**
* Mixes architecture members with implementation preferences
* Less flexible (tied to member roles)
* Doesn't fit user's workflow (they want general config, not member-specific)

**Rejected**: Conflates two concerns (architecture perspective vs implementation methodology)

### Alternative 4: Configuration Approach (Selected)

**Description**: Add implementation section to config.yml, following pragmatic_mode pattern

**Pros:**
* Follows existing pattern (pragmatic_mode)
* Leverages existing config system
* Clear, structured YAML (easy AI parsing)
* Optional (backward compatible)
* Simple to maintain
* Low implementation effort (~1 hour)

**Cons:**
* One more configuration section
* Requires documentation

**Selected**: Best balance of simplicity, effectiveness, and consistency with existing framework

## Consequences

### Positive

* **Dramatic Efficiency Gain**: 90% reduction in prompt length (40 words → 4 words)
* **Consistent Quality**: Methodology applied systematically to all implementations
* **Knowledge Preservation**: Team standards documented in version control
* **Better Onboarding**: New developers see documented practices
* **Context Persistence**: Preferences don't get lost between sessions
* **Cross-Session Consistency**: Same approach across all implementations
* **Team Alignment**: Shared configuration ensures team consistency
* **Quality Improvement**: Best practices (Metz, Fowler, Beck) applied systematically
* **Faster Implementation**: Less time crafting prompts, more time building
* **Backward Compatible**: Existing projects unaffected (optional feature)
* **Simple Implementation**: 1 hour effort for high-value feature
* **Follows Existing Pattern**: Consistent with pragmatic_mode design
* **Cross-Assistant Compatible**: Works with Claude, Cursor, Copilot, etc.

### Negative

* **Configuration Overhead**: Users must configure once (small one-time cost)
* **Learning Curve**: Users need to understand config structure (mitigated by examples)
* **Maintenance**: Config needs updates as practices evolve (natural evolution)
* **Potential Rigidity**: Config might feel constraining (mitigated by optional flag)
* **AI Dependency**: Relies on AI reading/applying config correctly (testable)

### Neutral

* **New Command Pattern**: Adds to framework's command vocabulary
* **Configuration Growth**: config.yml gains another section (follows existing pattern)
* **Documentation Addition**: AGENTS.md and CLAUDE.md gain new sections
* **Usage Evolution**: Changes how users interact with framework during implementation

## Pragmatic Enforcer Analysis

**Mode**: Balanced

**Overall Decision Complexity Assessment**:
This decision adds a configuration section following an existing pattern (pragmatic_mode). Minimal implementation (~1 hour) for high user value (90% prompt reduction). Solves a real, current user pain point with a simple, proven approach.

**Decision Challenge**: None - this is appropriately scoped

**Proposed Decision**: "Add implementation command with config.yml configuration"

**Necessity Assessment**: 8/10
- **Current need**: User has this workflow today (repetitive prompts)
- **Future need**: Team standards documentation, onboarding support
- **Cost of waiting**: Ongoing pain, quality inconsistency
- **Evidence of need**: User explicitly requests, describes actual workflow

**Complexity Assessment**: 3/10
- **Added complexity**: Single config section (~50 lines)
- **Maintenance burden**: Update config as preferences evolve (natural)
- **Learning curve**: Similar to pragmatic_mode (existing pattern)
- **Dependencies introduced**: None (uses existing config system)

**Alternative Analysis**:
- Status quo: Simpler (zero effort) but doesn't solve problem
- Documentation file: More complex (new file, parsing prose)
- Member enhancement: Conflates concerns
- **Configuration: Simplest solution that solves problem**

**Simpler Alternative Proposal**: None - this is already minimal

**Recommendation**: ✅ Approve decision as proposed

**Justification**:
This is pragmatic engineering - solving a real current need with minimal implementation following existing patterns. High value (90% prompt reduction) for low cost (1 hour, simple config section). Not over-engineering because:
- Solves actual user workflow (not speculation)
- Follows existing pattern (configuration-driven)
- Minimal scope (just config + command)
- Defers enhancements until triggered

**Pragmatic Score**:
- **Necessity**: 8/10
- **Complexity**: 3/10
- **Ratio**: 3/8 = 0.375 ✅ (well below 1.5 threshold for balanced mode)

**Overall Assessment**:
Appropriate engineering for real need. Simple, effective, pragmatic.

## Validation

**Acceptance Criteria:**

**Phase 1 (Core Feature):**
- [ ] implementation section exists in `.architecture/templates/config.yml`
- [ ] Command recognition documented in CLAUDE.md
- [ ] Cross-platform usage documented in AGENTS.md
- [ ] Example provided for Ruby TDD workflow
- [ ] All fields properly commented and explained
- [ ] AI assistants can read and apply configuration
- [ ] User can say "Implement X as the architects" and it works
- [ ] No breaking changes to existing projects
- [ ] Setup process optionally customizes implementation config

**Phase 2 (Deferred):**
- [ ] Global configuration (trigger conditions met)
- [ ] Member methodology fields (trigger conditions met)
- [ ] Validation/reporting (trigger conditions met)
- [ ] Language profiles (trigger conditions met)

**Testing Approach:**

**Manual Testing:**
1. Configure implementation section with Ruby TDD example
2. Issue command: "Implement authentication as the architects"
3. Verify AI reads configuration
4. Verify AI applies TDD methodology
5. Verify AI references influences (Kent Beck, Sandi Metz, etc.)
6. Verify tests written first
7. Verify refactoring after tests green
8. Verify Ruby idioms used

**Evidence of Correct Application:**
- Test files exist (TDD followed)
- Tests written before implementation (git history)
- Refactoring commits separate from feature commits
- Small methods, clear names (Sandi Metz principles)
- Ruby idioms present (blocks, meaningful names)
- Rubocop passing (if configured)

**Success Metrics:**
- Prompt length reduced from 40 words to 4 words (90% reduction)
- User satisfaction (subjective feedback)
- Code quality improvement (test coverage, style compliance)
- Consistency across implementations (code review verification)

## References

* [Architecture Review: Implementation Command Configuration](../../reviews/feature-implementation-command-configuration.md)
* [Architectural Principles](../../principles.md) - Pragmatic Simplicity
* [ADR-002: Pragmatic Guard Mode](./ADR-002-pragmatic-guard-mode.md) - Related configuration pattern
* [Configuration File](../../config.yml) - Existing pragmatic_mode pattern

## Future Considerations

The following enhancements are deferred until triggered by real usage:

### Global User Configuration (Deferred)

Allow users to set personal defaults in `~/.architecture/config.yml`:
- **Trigger**: 3+ users request "how do I set this for all my projects?"
- **Effort**: ~2 hours
- **Value**: Personal preferences across projects

### Member Methodology Integration (Deferred)

Add methodology fields to members.yml for "Implement as [member]":
- **Trigger**: Users want specific architect implementation approaches
- **Effort**: ~1 hour
- **Value**: Architect-specific implementation styles

### Implementation Validation (Deferred)

Verify methodology adherence via git history and code analysis:
- **Trigger**: Users request "verify TDD was followed"
- **Effort**: ~4 hours
- **Value**: Compliance checking, learning feedback

### Language-Specific Profiles (Deferred)

Complex multi-language projects with per-language configurations:
- **Trigger**: "Different methodology for frontend vs backend"
- **Effort**: ~3 hours
- **Value**: Polyglot project support

---

**Decision Date**: 2025-11-20
**Implementation Date**: 2025-11-20
**Status**: Accepted - Phase 1 In Progress
**Author**: Collaborative architectural analysis (all 7 architecture team members)
**Next Steps**: Implement Phase 1 (config.yml, CLAUDE.md, AGENTS.md)
